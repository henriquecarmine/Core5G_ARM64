"""
Painel de controle do Core5G_ARM64 — versão SERVER-SIDE.

Roda DIRETO NO SERVIDOR (diferente de client/server.py, que roda na estação
local e fala com o servidor via SSH/deploy.sh). Aqui não tem SSH nenhum: os
comandos chamam os scripts locais (../scripts/*.sh) direto, porque o painel
já está na mesma máquina.

Autenticação (usuário/senha) é feita AQUI via sessão por cookie assinado
(HMAC). O Caddy só termina TLS e faz reverse proxy — não autentica mais
(basic_auth removido porque o popup nativo do navegador não dava pra
substituir por uma tela de login customizada). Login: POST /api/login
(usuário/senha) ou POST /api/login/guest (sem senha, role read-only).

`sync`/`sync-oai`/`bootstrap` não existem aqui: esses comandos levam código
do laptop pro servidor, não fazem sentido executados a partir do próprio
servidor. Para isso, use `./deploy.sh` na sua máquina local.
"""
from __future__ import annotations

import base64
import collections
import hashlib
import hmac
import json
import os
import re
import secrets
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Iterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles

SERVER_DIR = Path(__file__).resolve().parent.parent  # ~/server
STATIC_DIR = Path(__file__).resolve().parent / "static"
_VERSION = (Path(__file__).resolve().parent / "VERSION").read_text().strip()

# Usuário guest é só-leitura: não tem permissão pra rodar nenhum comando.
# Qualquer outro usuário autenticado (ex.: admin) tem acesso total.
ADMIN_USER = os.environ.get("PANEL_USER", "admin")
ADMIN_PASSWORD = os.environ.get("PANEL_PASSWORD", "admin")
GUEST_USER = os.environ.get("PANEL_GUEST_USER", "guest")
GUEST_PASSWORD = os.environ.get("PANEL_GUEST_PASSWORD", "guest")
# Guest é OPT-IN: só existe se PANEL_GUEST_USER vier preenchido (.env). Com as
# variáveis em branco, o acesso de convidado fica desabilitado e só os admins
# (PANEL_USER + PANEL_EXTRA_USERS) entram. Trava "só hcarmine".
GUEST_ENABLED = bool(GUEST_USER.strip())

# Usuários admin (acesso total). Inclui o admin do ambiente e usuários extras
# do laboratório vindos do .env via PANEL_EXTRA_USERS="user1:pass1,user2:pass2".
ADMIN_USERS = {ADMIN_USER: ADMIN_PASSWORD}
for _entry in os.environ.get("PANEL_EXTRA_USERS", "").split(","):
    if ":" in _entry:
        _u, _p = _entry.split(":", 1)
        if _u.strip():
            ADMIN_USERS[_u.strip()] = _p

# Assina o cookie de sessão. Se PANEL_SECRET não vier do ambiente, gera um
# valor aleatório por processo — sessões caem a cada restart do serviço,
# o que é aceitável para um painel de laboratório.
SECRET_KEY = os.environ.get("PANEL_SECRET") or secrets.token_hex(32)
SESSION_COOKIE = "core5g_session"
SESSION_MAX_AGE = 8 * 3600  # 8h

# Rotas acessíveis sem sessão válida (tela de login e seus endpoints).
PUBLIC_PATHS = {"/login", "/api/login", "/api/login/guest", "/api/version"}

app = FastAPI(title="Core5G_ARM64 — Painel (servidor)")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _sign(value: str) -> str:
    return hmac.new(SECRET_KEY.encode(), value.encode(), hashlib.sha256).hexdigest()


# O token carrega: usuário + sid (id de sessão único por login) + a IDENTIDADE do
# Aluno (e-mail e nome). O sid distingue sessões (trava de Professor único e
# contagem de espectadores); a identidade dá o "controle unitário" da turma
# (quem é quem) sem manter estado no servidor — vai assinada no cookie.
_SID_SEP = "\x1f"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def make_session_token(user: str, sid: str, email: str = "", name: str = "") -> str:
    raw = _SID_SEP.join([user, sid, email or "", name or ""])
    payload = base64.urlsafe_b64encode(raw.encode()).decode()
    return f"{payload}.{_sign(payload)}"


def _read_session_raw(token: str | None) -> str | None:
    if not token or "." not in token:
        return None
    payload, sig = token.rsplit(".", 1)
    if not hmac.compare_digest(sig, _sign(payload)):
        return None
    try:
        return base64.urlsafe_b64decode(payload).decode()
    except ValueError:
        return None


def _parse_session(request: Request) -> tuple[str | None, str | None, str, str]:
    """(usuário, sid, email, nome). Tolera tokens legados (sem sid/identidade)."""
    raw = _read_session_raw(request.cookies.get(SESSION_COOKIE))
    if raw is None:
        return (None, None, "", "")
    parts = raw.split(_SID_SEP)
    user = parts[0] if parts else None
    sid = parts[1] if len(parts) > 1 else None
    email = parts[2] if len(parts) > 2 else ""
    name = parts[3] if len(parts) > 3 else ""
    return (user, sid, email, name)


def current_session(request: Request) -> tuple[str | None, str | None]:
    """(usuário, sid) — compat com o resto do código."""
    user, sid, _, _ = _parse_session(request)
    return (user, sid)


def current_ident(request: Request) -> tuple[str, str]:
    """(email, nome) do Aluno, se houver."""
    _, _, email, name = _parse_session(request)
    return (email, name)


def current_user(request: Request) -> str | None:
    return _parse_session(request)[0]


# ===========================================================================
# Sala de aula: 1 Professor (admin) ativo por vez + espectadores (Alunos) que
# acompanham ao vivo. Estado em memória do processo (cai em restart, ok no lab).
# ===========================================================================
_state_lock = threading.RLock()
# A vaga de Professor é PEGAJOSA: enquanto a aba do Professor estiver aberta, o
# heartbeat (5s) renova a posse e nenhum outro admin entra. A vaga só libera por
# LOGOUT explícito — ou, como válvula de segurança caso o Professor suma (laptop
# desligado / queda de rede prolongada), após ADMIN_TAKEOVER_GRACE sem heartbeat.
# Isso impede um aluno de "roubar" a vaga numa janela curta no meio da aula.
ADMIN_TAKEOVER_GRACE = 600.0       # 10 min sem heartbeat ⇒ outro admin pode assumir
VIEWER_TIMEOUT = 12.0              # s sem polling ⇒ o Aluno deixa de contar
# Professor ativo no momento (quem pode executar e cuja saída é transmitida).
ACTIVE_ADMIN: dict = {"user": None, "sid": None, "ts": 0.0}
_VIEWERS: dict[str, dict] = {}     # sid -> {"user", "ts"} (alunos acompanhando)


def _seat_free(now: float) -> bool:
    """Vaga disponível para OUTRO usuário assumir? Só se ninguém a tem ou se o
    dono sumiu por mais que a tolerância (laptop morto). Logout zera na hora."""
    return ACTIVE_ADMIN["sid"] is None or (now - ACTIVE_ADMIN["ts"]) > ADMIN_TAKEOVER_GRACE


def is_active_admin(user: str | None, sid: str | None) -> bool:
    """É o dono atual da vaga? Posse por sid — NÃO depende de heartbeat recente,
    pra um soluço de rede não derrubar o Professor no meio da demonstração. Ele
    só perde a vaga por logout, por reconexão (novo sid) ou por takeover (10min)."""
    return (
        user is not None and user != GUEST_USER and sid is not None
        and ACTIVE_ADMIN["sid"] == sid
    )


def _touch_admin(sid: str | None) -> None:
    if not sid:
        return
    with _state_lock:
        if ACTIVE_ADMIN["sid"] == sid:
            ACTIVE_ADMIN["ts"] = time.time()


def _touch_viewer(user: str | None, sid: str | None, email: str = "", name: str = "") -> None:
    if not sid:
        return
    with _state_lock:
        v = _VIEWERS.get(sid) or {"first": time.time()}
        v.update(user=user, email=email or v.get("email", ""), name=name or v.get("name", ""), ts=time.time())
        _VIEWERS[sid] = v


def viewer_count() -> int:
    now = time.time()
    with _state_lock:
        for k in [k for k, v in _VIEWERS.items() if now - v["ts"] > VIEWER_TIMEOUT]:
            _VIEWERS.pop(k, None)
        return len(_VIEWERS)


def live_viewers() -> list[dict]:
    """Alunos conectados agora (nome + e-mail), para o Professor ver quem é quem."""
    now = time.time()
    out = []
    with _state_lock:
        for v in _VIEWERS.values():
            if now - v["ts"] <= VIEWER_TIMEOUT:
                out.append({"name": v.get("name") or "—", "email": v.get("email") or "—",
                            "since": round(v.get("first", v["ts"]), 1)})
    out.sort(key=lambda x: (x["name"].lower(), x["email"]))
    return out


class LiveBuffer:
    """Ring-buffer compartilhado: a saída dos comandos do Professor é publicada
    aqui com nº de sequência; os Alunos fazem polling de /api/live?since=N. Quem
    entra atrasado puxa o histórico recente sem o Professor refazer nada."""

    def __init__(self, maxlen: int = 2000) -> None:
        self.events: collections.deque = collections.deque(maxlen=maxlen)
        self.seq = 0
        self.lock = threading.Lock()
        self.session = {"active": False, "label": None, "by": None, "started": 0.0}
        self.nav = {"screen": None, "label": None, "by": None, "ts": 0.0}

    def push(self, typ: str, **kw) -> int:
        with self.lock:
            self.seq += 1
            ev = {"seq": self.seq, "type": typ, "ts": round(time.time(), 3)}
            ev.update(kw)
            self.events.append(ev)
            return self.seq

    def snapshot(self, since: int) -> tuple[list, int, dict, dict]:
        with self.lock:
            evs = [e for e in self.events if e["seq"] > since]
            return evs, self.seq, dict(self.session), dict(self.nav)


LIVE = LiveBuffer()

# Arquivo persistente de Resultados (Fase 2): cada execução do Professor é
# salva em disco e pode ser revista/reproduzida depois (sobrevive a restart).
# Fica FORA da árvore sincronizada pelo deploy (server/panel/) — não é
# sobrescrito por `deploy.sh panel`.
RESULTS_DIR = SERVER_DIR / "panel_results"
MAX_RESULTS = 120           # mantém os N mais recentes
MAX_RESULT_LINES = 6000     # teto de linhas por resultado (evita arquivo gigante)


def _result_id(started: float) -> str:
    return time.strftime("%Y%m%d-%H%M%S", time.localtime(started)) + "-" + secrets.token_hex(2)


def _prune_results() -> None:
    files = sorted(RESULTS_DIR.glob("*.json"))
    for f in files[: max(0, len(files) - MAX_RESULTS)]:
        f.unlink(missing_ok=True)


def _save_result(rec: dict) -> None:
    try:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        (RESULTS_DIR / f"{rec['id']}.json").write_text(json.dumps(rec, ensure_ascii=False))
        _prune_results()
    except OSError:
        pass


def tee_to_live(
    it: Iterator[str], label: str, by: str | None, persist: bool = True, cmd: str | None = None
) -> Iterator[str]:
    """Encaminha a saída ao requisitante E publica no buffer ao vivo (begin/line/
    end), para os Alunos espelharem em tempo real. Se persist=True, grava a
    execução inteira no arquivo de Resultados ao terminar."""
    started = time.time()
    with LIVE.lock:
        LIVE.session.update(active=True, label=label, by=by, started=started)
    LIVE.push("begin", label=label, by=by)
    status = "ok"
    lines: list[str] = []
    try:
        for chunk in it:
            LIVE.push("line", text=chunk)
            if persist and len(lines) < MAX_RESULT_LINES:
                lines.append(chunk)
            yield chunk
    except BaseException:
        status = "error"
        raise
    finally:
        LIVE.push("end", label=label, status=status)
        with LIVE.lock:
            LIVE.session.update(active=False)
        if persist:
            ended = time.time()
            _save_result({
                "id": _result_id(started), "label": label, "cmd": cmd or label, "by": by,
                "started": round(started, 3), "ended": round(ended, 3),
                "duration": round(ended - started, 1), "status": status, "lines": lines,
            })


def ensure_can_run(request: Request) -> str:
    """Só o Professor ATIVO executa. Aluno: 403. Admin sem a vaga (assumida por
    outro / expirada): 409. Retorna o usuário ao chamador."""
    user, sid = current_session(request)
    if user is None or user == GUEST_USER:
        raise HTTPException(status_code=403, detail="Aluno só pode visualizar, não executar comandos.")
    if not is_active_admin(user, sid):
        raise HTTPException(
            status_code=409,
            detail="Sua sessão de professor não está ativa (outro professor assumiu ou ela expirou). Recarregue e entre de novo.",
        )
    _touch_admin(sid)
    return user


@app.middleware("http")
async def require_session(request: Request, call_next):
    path = request.url.path
    if path in PUBLIC_PATHS or path.startswith("/static/"):
        return await call_next(request)
    if current_user(request) is None:
        if path == "/" or not path.startswith("/api/"):
            return RedirectResponse("/login")
        return JSONResponse({"detail": "Não autenticado."}, status_code=401)
    return await call_next(request)

# Comando exposto na UI -> script local (relativo a SERVER_DIR) + cwd.
COMMANDS: dict[str, dict] = {
    "up-core": {"cmd": ["./scripts/up.sh"], "cwd": SERVER_DIR},
    "up-ran": {"cmd": ["./scripts/up_ran.sh"], "cwd": SERVER_DIR},
    "up-all": {"cmd": ["bash", "-c", "./scripts/up.sh && ./scripts/up_ran.sh"], "cwd": SERVER_DIR},
    "down-core": {"cmd": ["./scripts/down_core.sh"], "cwd": SERVER_DIR},
    "down-ran": {"cmd": ["./scripts/down_ran.sh"], "cwd": SERVER_DIR},
    "down-all": {"cmd": ["bash", "-c", "./scripts/down_ran.sh; ./scripts/down_core.sh"], "cwd": SERVER_DIR},
    "status": {"cmd": ["./scripts/healthcheck.sh"], "cwd": SERVER_DIR},
    "test-throughput": {"cmd": ["./scripts/test_throughput.sh"], "cwd": SERVER_DIR},
    "test-system-status": {"cmd": ["./scripts/test-system-status.sh"], "cwd": SERVER_DIR},
    "test-ue-connection": {"cmd": ["./scripts/test_ue_connection.sh"], "cwd": SERVER_DIR},
    "test-upf-failover": {"cmd": ["./scripts/test_upf_failover.sh"], "cwd": SERVER_DIR},
    # Testes do roteiro do professor (aula01 — fluxo de registro / checklist):
    "test-ng-setup": {"cmd": ["./scripts/test_ng_setup.sh"], "cwd": SERVER_DIR},
    "test-registration": {"cmd": ["./scripts/test_registration.sh"], "cwd": SERVER_DIR},
    "test-config-coherence": {"cmd": ["./scripts/test_config_coherence.sh"], "cwd": SERVER_DIR},
    # Projeto 2 usa o core OAI v2 (oai-cn5g-v2, v2.2.1). Os scripts v1
    # (up_core.sh/down_core.sh → oai-cn5g-fed) NÃO mexem nos containers v2 que
    # de fato rodam, por isso o "desligar" não obedecia. Apontar para o v2:
    "p2-up-core": {"cmd": ["./up_core_v2.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2" / "oai-cn5g-v2"},
    "p2-down-core": {"cmd": ["./down_core_v2.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2" / "oai-cn5g-v2"},
    "p2-up-e2-lab": {"cmd": ["./scripts/up_e2_lab_v2.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-down-e2-lab": {"cmd": ["./scripts/down_e2_lab.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-test-e2-sm": {"cmd": ["./scripts/test_e2_sm.sh", "all"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-test-e2-kpm": {"cmd": ["./scripts/test_e2_kpm.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-test-e2-rc": {"cmd": ["./scripts/test_e2_rc_attach.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    # Variante KPM com tráfego (aula04, slide 43): ping ao DN sobe o throughput
    # medido nas indicações E2SM-KPM.
    "p2-test-e2-kpm-traffic": {"cmd": ["bash", "-c", "KPM_TRAFFIC=1 ./scripts/test_e2_kpm.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
}

_VALID_DISTANCES = {"none", "100m", "500m", "1km", "3km", "off"}
_VALID_INTERFERENCES = {"none", "fraca", "media", "alta"}


def stream_command(cmd: list[str], cwd: Path, env: dict | None = None) -> Iterator[str]:
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
    )
    assert process.stdout is not None
    yield f"$ {' '.join(cmd)}  (em {cwd})\n\n"
    for line in process.stdout:
        yield line
    process.wait()
    yield f"\n[processo encerrado, exit code {process.returncode}]\n"


def list_services() -> dict[str, Path]:
    """Descobre os serviços dos dois docker-compose (core + RAN) em runtime,
    em vez de manter uma lista hardcoded que pode ficar desatualizada."""
    services: dict[str, Path] = {}
    compose_dirs = [
        SERVER_DIR,
        SERVER_DIR / "ueransim",
        SERVER_DIR / "oai-cn-gnb-e2" / "oai-cn5g-fed" / "docker-compose",
    ]
    for cwd in compose_dirs:
        if not cwd.is_dir():
            continue
        try:
            out = subprocess.run(
                ["docker", "compose", "config", "--services"],
                cwd=cwd, capture_output=True, text=True, timeout=10, check=True,
            ).stdout
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            continue
        for name in out.splitlines():
            name = name.strip()
            if name:
                services[name] = cwd
    return services


_CPU_MODEL_CACHE: str | None = None


def read_cpu_model() -> str:
    """Nome do processador (estático, lido uma vez e cacheado). No ARM o
    /proc/cpuinfo não tem "model name" — só o lscpu resolve isso de forma
    portável entre x86 e aarch64."""
    global _CPU_MODEL_CACHE
    if _CPU_MODEL_CACHE is None:
        _CPU_MODEL_CACHE = "desconhecido"
        try:
            out = subprocess.run(
                ["lscpu"], capture_output=True, text=True, timeout=5, check=True
            ).stdout
            for line in out.splitlines():
                if line.startswith("Model name:"):
                    _CPU_MODEL_CACHE = line.split(":", 1)[1].strip()
                    break
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass
    return _CPU_MODEL_CACHE


def read_cpu_times() -> tuple[int, int]:
    with open("/proc/stat") as f:
        values = list(map(int, f.readline().split()[1:]))
    idle = values[3] + values[4]  # idle + iowait
    return idle, sum(values)


def read_host_metrics() -> dict:
    meminfo = {}
    with open("/proc/meminfo") as f:
        for line in f:
            key, _, value = line.partition(":")
            meminfo[key] = int(value.strip().split()[0])  # kB
    mem_total = meminfo.get("MemTotal", 0)
    mem_used = mem_total - meminfo.get("MemAvailable", 0)
    swap_total = meminfo.get("SwapTotal", 0)
    swap_used = swap_total - meminfo.get("SwapFree", 0)
    disk = shutil.disk_usage("/")
    load1, _, _ = os.getloadavg()
    return {
        "mem_total_mb": round(mem_total / 1024),
        "mem_used_mb": round(mem_used / 1024),
        "mem_pct": round(100 * mem_used / mem_total, 1) if mem_total else 0,
        "swap_total_mb": round(swap_total / 1024),
        "swap_used_mb": round(swap_used / 1024),
        "disk_total_gb": round(disk.total / 1024**3, 1),
        "disk_used_gb": round(disk.used / 1024**3, 1),
        "disk_pct": round(100 * disk.used / disk.total, 1) if disk.total else 0,
        "load1": round(load1, 2),
        "cpu_count": os.cpu_count(),
        "cpu_model": read_cpu_model(),
    }


def read_container_stats() -> list[dict]:
    try:
        out = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "{{json .}}"],
            capture_output=True, text=True, timeout=5, check=True,
        ).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []
    containers = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        containers.append({
            "name": data.get("Name", ""),
            "cpu_pct": data.get("CPUPerc", ""),
            "mem_usage": data.get("MemUsage", ""),
        })
    return containers


def process_running(pattern: str) -> bool:
    try:
        return subprocess.run(
            ["pgrep", "-f", pattern], capture_output=True, timeout=3
        ).returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def read_container_states() -> dict[str, dict]:
    """Estado de TODOS os containers (inclusive parados), via docker ps -a —
    fonte estável (não oscila como o docker stats durante o boot). Retorna
    name -> {state, health}."""
    try:
        out = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}|{{.State}}|{{.Status}}"],
            capture_output=True, text=True, timeout=5, check=True,
        ).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return {}
    states: dict[str, dict] = {}
    for line in out.splitlines():
        parts = line.strip().split("|")
        if len(parts) < 3:
            continue
        name, state, status = parts[0], parts[1], parts[2]
        if "(healthy)" in status:
            health = "healthy"
        elif "health: starting" in status:
            health = "starting"
        elif "(unhealthy)" in status:
            health = "unhealthy"
        else:
            health = "none"
        states[name] = {"state": state, "health": health}
    return states


def container_status(state: str, health: str) -> str:
    """Reduz state+health a 3 estados visuais: up (verde), loading (âmbar),
    down (cinza/parado). 'up' só quando running e não em starting/unhealthy."""
    if state == "running":
        if health in ("starting", "unhealthy"):
            return "loading"
        return "up"
    if state in ("created", "restarting"):
        return "loading"
    return "down"


def read_group_status(states: dict[str, dict]) -> dict[str, str]:
    """Estado tri-state dos toggles do painel ('on' | 'loading' | 'off').
    Projeto 1/2 via docker (containers do compose); E2 lab via processo
    nativo (gNB/RIC, que não roda em container)."""
    def group_of(pred) -> str:
        matched = [v for k, v in states.items() if pred(k)]
        if not matched:
            return "off"
        st = [container_status(m["state"], m["health"]) for m in matched]
        if "up" in st:
            return "on"
        if "loading" in st:
            return "loading"
        return "off"

    return {
        "p1-core": group_of(lambda n: "open5gs-nrf" in n),
        "p1-ran": group_of(lambda n: n == "ueransim"),
        "p2-core": group_of(lambda n: n == "oai-amf"),
        "p2-e2lab": "on" if (process_running("nr-softmodem") or process_running("nearRT-RIC")) else "off",
    }


# ===========================================================================
# Telemetria com COLETOR ÚNICO em background (escala p/ a sala de aula).
# Antes era um stream infinito POR CLIENTE, e cada aluno rodava `docker stats`
# (pesado) a cada 2s + prendia uma thread do pool — 30 alunos derrubariam o box
# de 2 vCPU. Agora UMA thread coleta a cada 2s, guarda em cache, e todos os
# clientes (Professor + N Alunos) leem o mesmo snapshot via GET barato.
# Custo no servidor: O(1), independente do nº de alunos.
# ===========================================================================
_TELE: dict = {"data": None, "ts": 0.0}
_tele_lock = threading.Lock()
_tele_prev = {"idle": 0, "total": 0}


def collect_telemetry() -> dict:
    idle, total = read_cpu_times()
    d_idle, d_total = idle - _tele_prev["idle"], total - _tele_prev["total"]
    cpu_pct = round(100 * (1 - d_idle / d_total), 1) if d_total else 0.0
    _tele_prev["idle"], _tele_prev["total"] = idle, total
    host = read_host_metrics()
    host["cpu_pct"] = cpu_pct
    # Junta o status estável (docker ps -a) com CPU/RAM (docker stats só tem dos
    # que estão rodando). Lista todos os containers com o estado visual de cada.
    states = read_container_states()
    stats = {c["name"]: c for c in read_container_stats()}
    containers = []
    for name in sorted(states):
        s = stats.get(name, {})
        containers.append({
            "name": name,
            "cpu_pct": s.get("cpu_pct", ""),
            "mem_usage": s.get("mem_usage", ""),
            "status": container_status(states[name]["state"], states[name]["health"]),
        })
    return {"host": host, "containers": containers, "groups": read_group_status(states)}


def _telemetry_loop() -> None:
    _tele_prev["idle"], _tele_prev["total"] = read_cpu_times()
    time.sleep(2)  # 1ª janela p/ o delta de CPU
    while True:
        try:
            data = collect_telemetry()
            with _tele_lock:
                _TELE["data"] = data
                _TELE["ts"] = time.time()
        except Exception:
            pass
        time.sleep(2)


# Sobe o coletor único (daemon) uma vez, no import do módulo.
threading.Thread(target=_telemetry_loop, daemon=True, name="telemetry-collector").start()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/login")
def login(request: Request):
    if current_user(request) is not None:
        return RedirectResponse("/")
    html = (STATIC_DIR / "login.html").read_text()
    html = html.replace("__VERSION__", _VERSION)
    html = html.replace("__GUEST_ENABLED__", "true" if GUEST_ENABLED else "false")
    return HTMLResponse(html)


def _set_session(response: JSONResponse, user: str, sid: str, email: str = "", name: str = "") -> JSONResponse:
    response.set_cookie(
        SESSION_COOKIE,
        make_session_token(user, sid, email, name),
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=True,
    )
    return response


# Roster de presença: cada entrada de Aluno é registrada (append) num arquivo
# fora da árvore do deploy — o "controle unitário" da turma (quem é quem),
# disponível para atividades futuras. É dado pessoal: fica só no servidor.
ROSTER_FILE = RESULTS_DIR / "_roster.jsonl"


def _record_attendance(name: str, email: str) -> None:
    try:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        with ROSTER_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": round(time.time(), 1), "name": name, "email": email}, ensure_ascii=False) + "\n")
    except OSError:
        pass


@app.post("/api/login")
def do_login(payload: dict) -> JSONResponse:
    user = str(payload.get("user", ""))
    password = str(payload.get("pass", ""))
    is_guest = GUEST_ENABLED and user == GUEST_USER and password == GUEST_PASSWORD
    is_admin = user in ADMIN_USERS and password == ADMIN_USERS[user]
    if not (is_guest or is_admin):
        raise HTTPException(401, "Usuário ou senha inválidos.")
    if is_admin:
        now = time.time()
        with _state_lock:
            # Trava de "um Professor por vez": bloqueia um SEGUNDO usuário enquanto
            # houver um professor ativo. O MESMO usuário pode reassumir (reconexão
            # de outra aba/dispositivo). A vaga só libera por logout — ou após
            # ADMIN_TAKEOVER_GRACE (10min) sem heartbeat, caso o Professor suma.
            if not _seat_free(now) and ACTIVE_ADMIN["user"] != user:
                raise HTTPException(
                    409,
                    f"Já há um professor conectado ({ACTIVE_ADMIN['user']}) e a vaga é única. "
                    f"Entre como aluno para acompanhar a aula ao vivo — ou peça para o professor "
                    f"sair (logout) para liberar a vaga.",
                )
            sid = secrets.token_hex(8)
            ACTIVE_ADMIN.update(user=user, sid=sid, ts=now)
        return _set_session(JSONResponse({"user": user, "role": "admin"}), user, sid)
    sid = secrets.token_hex(8)
    return _set_session(JSONResponse({"user": user, "role": "guest"}), user, sid)


@app.post("/api/login/guest")
def do_login_guest(payload: dict | None = None) -> JSONResponse:
    if not GUEST_ENABLED:
        raise HTTPException(403, "Acesso de aluno desabilitado neste servidor.")
    payload = payload or {}
    name = str(payload.get("name", "")).strip()[:80]
    email = str(payload.get("email", "")).strip().lower()[:120]
    if len(name) < 2:
        raise HTTPException(400, "Informe seu nome completo para entrar como aluno.")
    if not EMAIL_RE.match(email):
        raise HTTPException(400, "Informe um e-mail válido para entrar como aluno.")
    sid = secrets.token_hex(8)
    _record_attendance(name, email)   # presença persistida (controle unitário)
    return _set_session(
        JSONResponse({"user": GUEST_USER, "role": "guest", "name": name, "email": email}),
        GUEST_USER, sid, email=email, name=name,
    )


@app.post("/api/logout")
def do_logout(request: Request) -> JSONResponse:
    _, sid = current_session(request)
    if sid:
        with _state_lock:
            if ACTIVE_ADMIN["sid"] == sid:
                ACTIVE_ADMIN.update(user=None, sid=None, ts=0.0)
            _VIEWERS.pop(sid, None)
    response = JSONResponse({"ok": True})
    response.delete_cookie(SESSION_COOKIE)
    return response


@app.post("/api/heartbeat")
def heartbeat(request: Request) -> JSONResponse:
    """Professor: mantém a vaga viva. Front chama a cada ~5s."""
    user, sid = current_session(request)
    now = time.time()
    active = False
    if user is not None and user != GUEST_USER and sid:
        with _state_lock:
            if ACTIVE_ADMIN["sid"] == sid:
                ACTIVE_ADMIN["ts"] = now
                active = True
            elif _seat_free(now):
                # Vaga livre (ninguém a tem, ou o dono sumiu / o painel reiniciou):
                # a aba do professor REASSUME sozinha no próximo heartbeat — sem
                # precisar relogar. Não rouba de um professor ativo (só pega o que
                # já está livre), então a trava de "um por vez" segue valendo.
                ACTIVE_ADMIN.update(user=user, sid=sid, ts=now)
                active = True
    with _state_lock:
        holder = None if _seat_free(now) else ACTIVE_ADMIN["user"]
    return JSONResponse({"active_admin": holder, "is_active": active, "viewers": viewer_count()})


@app.get("/api/live")
def live(request: Request, since: int = 0) -> JSONResponse:
    """Aluno: puxa os eventos novos (>since) do buffer ao vivo + estado da sessão
    e da navegação do Professor. Também registra presença (contagem)."""
    user, sid, email, name = _parse_session(request)
    _touch_viewer(user, sid, email, name)
    evs, seq, session, nav = LIVE.snapshot(since)
    return JSONResponse({"events": evs, "seq": seq, "session": session, "nav": nav, "viewers": viewer_count()})


def _require_admin(request: Request) -> str:
    user, _ = current_session(request)
    if user is None or user == GUEST_USER:
        raise HTTPException(403, "Apenas o professor pode ver esta informação.")
    return user


@app.get("/api/viewers")
def viewers(request: Request) -> JSONResponse:
    """Professor: quem está assistindo AGORA (nome + e-mail). Só o professor vê."""
    _require_admin(request)
    vs = live_viewers()
    return JSONResponse({"viewers": vs, "count": len(vs)})


@app.get("/api/roster")
def roster(request: Request) -> JSONResponse:
    """Professor: lista de presença acumulada (controle unitário da turma),
    agregada por e-mail — quem entrou, quantas vezes e quando foi visto pela 1ª/
    última vez. Base para atividades futuras."""
    _require_admin(request)
    agg: dict[str, dict] = {}
    if ROSTER_FILE.exists():
        try:
            for line in ROSTER_FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                email = r.get("email", "")
                if not email:
                    continue
                a = agg.get(email)
                if a is None:
                    agg[email] = {"email": email, "name": r.get("name", ""), "entries": 1,
                                  "first": r.get("ts"), "last": r.get("ts")}
                else:
                    a["entries"] += 1
                    a["name"] = r.get("name", "") or a["name"]
                    a["last"] = r.get("ts")
        except OSError:
            pass
    out = sorted(agg.values(), key=lambda x: (x["name"].lower(), x["email"]))
    return JSONResponse({"roster": out, "count": len(out)})


@app.post("/api/nav")
def nav(payload: dict, request: Request) -> JSONResponse:
    """Professor avisa qual tela/ação abriu, para os Alunos verem no banner."""
    user, sid = current_session(request)
    if not is_active_admin(user, sid):
        return JSONResponse({"ok": False})
    screen = str(payload.get("screen", ""))[:60]
    label = str(payload.get("label", ""))[:90]
    with LIVE.lock:
        LIVE.nav.update(screen=screen, label=label, by=user, ts=time.time())
    LIVE.push("nav", screen=screen, label=label, by=user)
    _touch_admin(sid)
    return JSONResponse({"ok": True})


@app.get("/api/results")
def list_results() -> JSONResponse:
    """Resultados salvos (mais recentes primeiro). Aberto a Professor e Aluno."""
    out: list[dict] = []
    if RESULTS_DIR.exists():
        for f in sorted(RESULTS_DIR.glob("*.json"), reverse=True):
            try:
                d = json.loads(f.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            out.append({
                "id": d.get("id"), "label": d.get("label"), "cmd": d.get("cmd"),
                "by": d.get("by"), "started": d.get("started"), "duration": d.get("duration"),
                "status": d.get("status"), "lines": len(d.get("lines", [])),
                "note": d.get("note", ""),
            })
    return JSONResponse({"results": out})


@app.get("/api/results/{rid}")
def get_result(rid: str) -> JSONResponse:
    if not re.fullmatch(r"[0-9A-Za-z\-]{1,40}", rid):
        raise HTTPException(400, "id inválido")
    f = RESULTS_DIR / f"{rid}.json"
    if not f.exists():
        raise HTTPException(404, "resultado não encontrado")
    try:
        return JSONResponse(json.loads(f.read_text()))
    except (OSError, json.JSONDecodeError):
        raise HTTPException(500, "falha ao ler resultado")


@app.delete("/api/results/{rid}")
def delete_result(rid: str, request: Request) -> JSONResponse:
    user, _ = current_session(request)
    if user is None or user == GUEST_USER:
        raise HTTPException(403, "Aluno não pode apagar resultados.")
    if not re.fullmatch(r"[0-9A-Za-z\-]{1,40}", rid):
        raise HTTPException(400, "id inválido")
    (RESULTS_DIR / f"{rid}.json").unlink(missing_ok=True)
    return JSONResponse({"ok": True})


@app.post("/api/results/delete")
def delete_results_bulk(payload: dict, request: Request) -> JSONResponse:
    """Exclui vários resultados de uma vez (Professor-only). payload: {ids:[...]}.
    Usado pelo modo 'Selecionar' e pelo 'Limpar tudo' do modal de Resultados."""
    user, _ = current_session(request)
    if user is None or user == GUEST_USER:
        raise HTTPException(403, "Aluno não pode apagar resultados.")
    ids = payload.get("ids")
    if not isinstance(ids, list):
        raise HTTPException(400, "ids inválido")
    removed = 0
    for rid in ids:
        if isinstance(rid, str) and re.fullmatch(r"[0-9A-Za-z\-]{1,40}", rid):
            f = RESULTS_DIR / f"{rid}.json"
            if f.exists():
                f.unlink(missing_ok=True)
                removed += 1
    return JSONResponse({"ok": True, "removed": removed})


@app.post("/api/results/{rid}/note")
def set_result_note(rid: str, payload: dict, request: Request) -> JSONResponse:
    """Salva uma observação livre no resultado (Professor-only), pra lembrar
    do que era aquele relatório. Limite de 200 caracteres."""
    user, _ = current_session(request)
    if user is None or user == GUEST_USER:
        raise HTTPException(403, "Aluno não pode editar resultados.")
    if not re.fullmatch(r"[0-9A-Za-z\-]{1,40}", rid):
        raise HTTPException(400, "id inválido")
    f = RESULTS_DIR / f"{rid}.json"
    if not f.exists():
        raise HTTPException(404, "resultado não encontrado")
    note = str(payload.get("note", ""))[:200].strip()
    try:
        d = json.loads(f.read_text())
        d["note"] = note
        f.write_text(json.dumps(d))
    except (OSError, json.JSONDecodeError):
        raise HTTPException(500, "falha ao salvar a observação")
    return JSONResponse({"ok": True, "note": note})


@app.get("/topology")
def topology_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "topology.html")


def running_container_names() -> set[str]:
    """Nomes dos containers que estão de fato 'Up' (running)."""
    try:
        out = subprocess.run(
            ["docker", "ps", "--filter", "status=running", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=5, check=True,
        ).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return set()
    return {n.strip() for n in out.splitlines() if n.strip()}


def service_active(unit: str) -> bool:
    try:
        out = subprocess.run(
            ["systemctl", "is-active", unit], capture_output=True, text=True, timeout=3
        ).stdout.strip()
        return out == "active"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def topology_status(nodes: list[dict]) -> dict[str, str]:
    """Sobrepõe o status REAL (running/stopped) a cada nó do diagrama,
    a partir do statusKey: container=<nome>, native=proc:<padrão>,
    systemd=svc:<unit>. Nós 'external' ou planned ficam sem status vivo."""
    running = running_container_names()
    status: dict[str, str] = {}
    for node in nodes:
        key = node.get("statusKey")
        if not key:
            continue
        if key.startswith("proc:"):
            ok = process_running(key[len("proc:"):])
        elif key.startswith("svc:"):
            ok = service_active(key[len("svc:"):])
        else:
            ok = key in running
        status[node["id"]] = "running" if ok else "stopped"
    return status


def _docker_logs(container: str, tail: int = 12) -> list[str]:
    try:
        out = subprocess.run(
            ["docker", "logs", "--tail", str(tail), container],
            capture_output=True, text=True, timeout=5,
        )
        lines = (out.stdout + out.stderr).splitlines()
        return [l for l in lines if l.strip()][-tail:]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def _tail_file(path: Path, tail: int = 14, grep: str | None = None) -> list[str]:
    try:
        lines = path.read_text(errors="replace").splitlines()
    except OSError:
        return []
    if grep:
        import re as _re
        rx = _re.compile(grep, _re.I)
        lines = [l for l in lines if rx.search(l)]
    # remove códigos ANSI de cor que poluem o log nativo do OAI
    import re as _re2
    ansi = _re2.compile(r"\x1b\[[0-9;]*m")
    return [ansi.sub("", l) for l in lines if l.strip()][-tail:]


@app.get("/api/topology/logs")
def topology_logs() -> JSONResponse:
    """Logs recentes organizados por componente para a tela de topologia.
    Containers via `docker logs`; gNB/RIC (nativos) via arquivos de log."""
    oai_logs = SERVER_DIR / "oai-cn-gnb-e2" / "logs"
    sections = [
        {"title": "gNB (E2 Agent)", "comp": "gnb",
         "lines": _tail_file(oai_logs / "gnb_oai.log", 16, r"E2|RIC|SETUP|NGAP|registr|error|PDU")},
        {"title": "near-RT RIC", "comp": "ric",
         "lines": _tail_file(oai_logs / "nearRT-RIC.log", 14)},
        {"title": "AMF (Mobilidade)", "comp": "amf", "lines": _docker_logs("oai-amf", 10)},
        {"title": "SMF (Sessão)", "comp": "smf", "lines": _docker_logs("oai-smf", 8)},
        {"title": "AUSF (Autenticação)", "comp": "ausf", "lines": _docker_logs("oai-ausf", 8)},
        {"title": "NRF (Descoberta)", "comp": "nrf", "lines": _docker_logs("oai-nrf", 6)},
    ]
    return JSONResponse({"sections": [s for s in sections if s["lines"]]})


def _compute_gnb_stats() -> dict:
    import re as _re
    log = SERVER_DIR / "oai-cn-gnb-e2" / "logs" / "gnb_oai.log"
    if not process_running("nr-softmodem") or not log.exists():
        return {"up": False}
    try:
        lines = log.read_text(errors="replace").splitlines()
    except OSError:
        return {"up": False}
    stats: dict = {"up": True}
    for line in reversed(lines[-400:]):
        if "SNR" not in line:
            continue
        m_snr = _re.search(r"SNR\s+([0-9.]+)\s*dB", line)
        m_mcs = _re.search(r"MCS\s*\(\d+\)\s*(\d+)", line)
        m_prb = _re.search(r"NPRB\s+(\d+)", line)
        m_bler = _re.search(r"BLER\s+([0-9.]+)", line)
        if m_snr:
            stats["snr"] = float(m_snr.group(1))
            if m_mcs: stats["mcs"] = int(m_mcs.group(1))
            if m_prb: stats["prb"] = int(m_prb.group(1))
            if m_bler: stats["bler"] = float(m_bler.group(1))
            break
    return stats


_GNB: dict = {"data": {"up": False}, "ts": 0.0}
_gnb_lock = threading.Lock()
GNB_MIN_INTERVAL = 1.4  # 1 leitura de log compartilhada por janela (sala de aula)


@app.get("/api/topology/gnb-stats")
def topology_gnb_stats() -> JSONResponse:
    """Métricas de RAN ao vivo do log do gNB (SNR/MCS/PRB/BLER). Cacheada: se N
    alunos pedem na mesma janela, faz UMA leitura de log e serve todos do cache."""
    now = time.time()
    with _gnb_lock:
        if now - _GNB["ts"] < GNB_MIN_INTERVAL and _GNB["ts"] > 0:
            return JSONResponse(_GNB["data"])
    data = _compute_gnb_stats()
    with _gnb_lock:
        _GNB["data"] = data
        _GNB["ts"] = now
    return JSONResponse(data)


@app.get("/api/topology")
def topology_endpoint(proj: str = "p2") -> JSONResponse:
    """Devolve a topologia do projeto pedido (?proj=p1|p2) enriquecida com o
    status ao vivo de cada nó. Padrão p2 (compat: openran-topology.json é a do
    Projeto 2)."""
    fname = "openran-topology-p1.json" if proj == "p1" else "openran-topology.json"
    try:
        data = json.loads((STATIC_DIR / fname).read_text())
    except (OSError, json.JSONDecodeError) as e:
        raise HTTPException(500, f"Falha ao ler topologia: {e}")
    data["live_status"] = topology_status(data.get("nodes", []))
    return JSONResponse(data)


@app.get("/api/version")
def version_endpoint() -> JSONResponse:
    return JSONResponse({"version": _VERSION})


@app.get("/api/whoami")
def whoami(request: Request) -> JSONResponse:
    user, sid = current_session(request)
    role = "guest" if user == GUEST_USER else "admin"
    active = is_active_admin(user, sid) if role == "admin" else False
    return JSONResponse({"user": user, "role": role, "is_active": active})


@app.get("/api/subscribers")
def list_subscribers_endpoint() -> JSONResponse:
    try:
        out = subprocess.run(
            ["./scripts/list-subscribers.sh"],
            cwd=SERVER_DIR, capture_output=True, text=True, timeout=10, check=True,
        ).stdout.strip()
        subscribers = json.loads(out) if out else []
        return JSONResponse({"subscribers": subscribers})
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return JSONResponse({"subscribers": [], "error": "MongoDB indisponível"})
    except json.JSONDecodeError:
        return JSONResponse({"subscribers": [], "error": "Erro ao parsear resposta"})


@app.delete("/api/subscriber/{imsi}")
def delete_subscriber(imsi: str, request: Request) -> StreamingResponse:
    by = ensure_can_run(request)
    if not re.fullmatch(r"\d{6,15}", imsi):
        return StreamingResponse(iter(["IMSI inválido\n"]), media_type="text/plain")
    env = os.environ.copy()
    env["SUB_IMSI"] = imsi
    return StreamingResponse(
        tee_to_live(stream_command(["./scripts/remove-subscriber.sh"], SERVER_DIR, env=env), f"remover assinante {imsi}", by),
        media_type="text/plain",
    )


@app.post("/api/channel")
def configure_channel(payload: dict, request: Request) -> StreamingResponse:
    by = ensure_can_run(request)
    distance = str(payload.get("distance", "none"))
    interference = str(payload.get("interference", "none"))
    if distance not in _VALID_DISTANCES or interference not in _VALID_INTERFERENCES:
        return StreamingResponse(iter(["Parâmetros de canal inválidos\n"]), media_type="text/plain")
    return StreamingResponse(
        tee_to_live(stream_command(["./scripts/test_channel.sh", distance, interference], SERVER_DIR), "configurar canal de rádio", by),
        media_type="text/plain",
    )


_VALID_DURATIONS = {5, 10, 30, 60}


@app.post("/api/throughput")
def run_throughput(payload: dict, request: Request) -> StreamingResponse:
    by = ensure_can_run(request)
    try:
        duration = int(payload.get("duration", 10))
    except (TypeError, ValueError):
        duration = 10
    if duration not in _VALID_DURATIONS:
        duration = 10
    env = os.environ.copy()
    env["IPERF_DURATION"] = str(duration)
    return StreamingResponse(
        tee_to_live(stream_command(["./scripts/test_throughput.sh"], SERVER_DIR, env=env), f"teste de throughput ({duration}s)", by),
        media_type="text/plain",
    )


@app.post("/api/switch/{target}")
def switch_project(target: str, request: Request) -> StreamingResponse:
    """Alterna entre os projetos de forma exclusiva (p1 | p2 | off): desliga o
    que estiver no ar e sobe só o escolhido. Emite PHASE|/STEP|/DONE| para o
    painel mostrar progresso."""
    by = ensure_can_run(request)
    if target not in ("p1", "p2", "off"):
        raise HTTPException(status_code=400, detail="Alvo inválido (use p1, p2 ou off).")
    _LABEL = {"p1": "alternar para o Projeto 1", "p2": "alternar para o Projeto 2", "off": "desligar tudo"}
    return StreamingResponse(
        tee_to_live(stream_command(["./scripts/switch_project.sh", target], SERVER_DIR), _LABEL[target], by),
        media_type="text/plain",
    )


@app.post("/api/demo-e2e")
def demo_e2e(request: Request) -> StreamingResponse:
    """Demonstração E2E (Projeto 1): UE → sessão PDU → internet → throughput.
    Emite linhas STEP|status|título|detalhe que o painel monta como relatório."""
    by = ensure_can_run(request)
    return StreamingResponse(
        tee_to_live(stream_command(["./scripts/demo_e2e.sh"], SERVER_DIR), "Demonstração E2E (Projeto 1)", by),
        media_type="text/plain",
    )


# Fontes de log dos DOIS projetos, por NOME DE CONTAINER (estável, à prova do
# descompasso v1/v2 que deixava o log do P2 em branco) + processos nativos por
# arquivo. A aba de Logs lista só as fontes ATIVAS no momento.
LOG_SOURCES: list[dict] = [
    # Projeto 1 — Open5GS (5GC) + UERANSIM
    {"key": "amf",     "label": "AMF · mobilidade (N1/N2 · NGAP)",   "container": "open5gs-amf-containerized"},
    {"key": "smf",     "label": "SMF · sessão PDU (N4 · PFCP)",      "container": "open5gs-smf-containerized"},
    {"key": "upf-a",   "label": "UPF-A · plano de dados (N3/N6)",    "container": "open5gs-upf-containerized-a"},
    {"key": "upf-b",   "label": "UPF-B · plano de dados (backup)",   "container": "open5gs-upf-containerized-b"},
    {"key": "ausf",    "label": "AUSF · autenticação (5G-AKA)",      "container": "open5gs-ausf-containerized"},
    {"key": "udm",     "label": "UDM · perfil do assinante",        "container": "open5gs-udm-containerized"},
    {"key": "udr",     "label": "UDR · repositório de dados",       "container": "open5gs-udr-containerized"},
    {"key": "pcf",     "label": "PCF · política/QoS",               "container": "open5gs-pcf-containerized"},
    {"key": "bsf",     "label": "BSF · binding de sessão",          "container": "open5gs-bsf-containerized"},
    {"key": "nssf",    "label": "NSSF · seleção de slice",          "container": "open5gs-nssf-containerized"},
    {"key": "nrf",     "label": "NRF · registro de NFs (SBI)",      "container": "open5gs-nrf-containerized"},
    {"key": "scp",     "label": "SCP · proxy SBI",                  "container": "open5gs-scp-containerized"},
    {"key": "mongodb", "label": "MongoDB · banco de assinantes",    "container": "open5gs-mongodb-containerized"},
    {"key": "dn",      "label": "DN · internet/iperf3 (N6)",        "container": "open5gs-dn-containerized"},
    {"key": "webui",   "label": "WebUI · admin de assinantes",      "container": "open5gs-webui-containerized"},
    {"key": "ueransim","label": "UERANSIM · gNB + UE (RAN)",        "container": "ueransim"},
    # Projeto 2 — OAI 5GC v2 (oai-cn5g-v2)
    {"key": "oai-amf",   "label": "AMF (OAI) · mobilidade",         "container": "oai-amf"},
    {"key": "oai-smf",   "label": "SMF (OAI) · sessão PDU",         "container": "oai-smf"},
    {"key": "oai-upf",   "label": "UPF (OAI) · plano de dados",     "container": "oai-upf"},
    {"key": "oai-ausf",  "label": "AUSF (OAI) · autenticação",      "container": "oai-ausf"},
    {"key": "oai-udm",   "label": "UDM (OAI)",                      "container": "oai-udm"},
    {"key": "oai-udr",   "label": "UDR (OAI)",                      "container": "oai-udr"},
    {"key": "oai-nrf",   "label": "NRF (OAI) · registro de NFs",    "container": "oai-nrf"},
    {"key": "oai-ext-dn","label": "DN externo (OAI) · iperf3",      "container": "oai-ext-dn"},
    {"key": "mysql",     "label": "MySQL · assinantes (OAI)",       "container": "mysql"},
    # Projeto 2 — processos nativos (host), por arquivo de log
    {"key": "gnb", "label": "gNB (OAI RFSIM · E2 agent)", "file": "oai-cn-gnb-e2/logs/gnb_oai.log"},
    {"key": "ric", "label": "near-RT RIC (FlexRIC)",      "file": "oai-cn-gnb-e2/logs/nearRT-RIC.log"},
]


def available_log_sources() -> list[dict]:
    """Só as fontes que existem AGORA: container rodando ou arquivo não-vazio."""
    running = running_container_names()
    out = []
    for s in LOG_SOURCES:
        if "container" in s:
            if s["container"] in running:
                out.append(s)
        else:
            p = SERVER_DIR / s["file"]
            try:
                if p.exists() and p.stat().st_size > 0:
                    out.append(s)
            except OSError:
                pass
    return out


@app.get("/api/services")
def services_endpoint() -> JSONResponse:
    return JSONResponse({"services": [
        {"key": s["key"], "label": s["label"]} for s in available_log_sources()
    ]})


@app.get("/api/telemetry")
def telemetry() -> JSONResponse:
    """GET barato: devolve o último snapshot do coletor único (sem subprocess por
    cliente, sem prender thread). N alunos custam o mesmo que 1."""
    with _tele_lock:
        data = _TELE["data"]
    if data is None:  # antes da 1ª coleta (≤2s no boot): host parcial, sem travar
        host = read_host_metrics()
        host.setdefault("cpu_pct", 0.0)
        data = {"host": host, "containers": [], "groups": {}}
    return JSONResponse(data)


@app.get("/api/logs/{service}")
def logs(service: str, request: Request) -> StreamingResponse:
    """Snapshot (finito) das últimas linhas — encerra para o painel exibir a
    explicação didática no fim. Container via `docker logs`; nativo via arquivo.
    Se quem abre é o Professor ativo, o log também vai pro buffer ao vivo (Alunos)."""
    src = next((s for s in LOG_SOURCES if s["key"] == service), None)
    if src is None:
        return StreamingResponse(iter([f"Serviço desconhecido: {service}\n"]), media_type="text/plain")
    if "container" in src:
        if src["container"] not in running_container_names():
            gen: Iterator[str] = iter([f"(container {src['container']} não está rodando — sem logs)\n"])
        else:
            cmd = ["docker", "logs", "--timestamps", "--tail", "300", src["container"]]
            gen = stream_command(cmd, SERVER_DIR)
    else:
        lines = _tail_file(SERVER_DIR / src["file"], tail=300)
        body = ("\n".join(lines) + "\n") if lines else f"(sem logs em {src['file']})\n"
        gen = iter([body])
    user, sid = current_session(request)
    if is_active_admin(user, sid):
        # logs vão pro ao vivo (Alunos veem), mas NÃO pro arquivo (são efêmeros).
        gen = tee_to_live(gen, f"ver logs · {src['label']}", user, persist=False)
    return StreamingResponse(gen, media_type="text/plain")


@app.post("/api/subscriber")
def add_subscriber(payload: dict, request: Request) -> StreamingResponse:
    by = ensure_can_run(request)

    imsi = str(payload.get("imsi", "")).strip()
    if not re.fullmatch(r"\d{6,15}", imsi):
        return StreamingResponse(
            iter(["IMSI inválido: precisa ter entre 6 e 15 dígitos numéricos.\n"]), media_type="text/plain"
        )

    env = os.environ.copy()
    env["SUB_IMSI"] = imsi
    hex_fields = {"k": "SUB_K", "opc": "SUB_OPC"}
    for field, env_key in hex_fields.items():
        value = str(payload.get(field, "")).strip().upper()
        if value:
            if not re.fullmatch(r"[0-9A-F]{32}", value):
                return StreamingResponse(
                    iter([f"Campo {field.upper()} inválido: precisa ter 32 caracteres hexadecimais.\n"]),
                    media_type="text/plain",
                )
            env[env_key] = value
    for field, env_key in (("msisdn", "SUB_MSISDN"), ("amf", "SUB_AMF")):
        value = str(payload.get(field, "")).strip()
        if value:
            env[env_key] = value

    return StreamingResponse(
        tee_to_live(stream_command(["./scripts/add-subscriber.sh"], SERVER_DIR, env=env), f"cadastrar assinante {imsi}", by),
        media_type="text/plain",
    )


@app.post("/api/run/{command}")
def run_command(command: str, request: Request) -> StreamingResponse:
    by = ensure_can_run(request)
    spec = COMMANDS.get(command)
    if spec is None:
        return StreamingResponse(
            iter([f"Comando desconhecido: {command}\n"]), media_type="text/plain"
        )
    return StreamingResponse(
        tee_to_live(stream_command(spec["cmd"], spec["cwd"]), command, by, cmd=command),
        media_type="text/plain",
    )
