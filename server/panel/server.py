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
import hashlib
import hmac
import json
import os
import re
import secrets
import shutil
import subprocess
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


def make_session_token(user: str) -> str:
    payload = base64.urlsafe_b64encode(user.encode()).decode()
    return f"{payload}.{_sign(payload)}"


def read_session_token(token: str | None) -> str | None:
    if not token or "." not in token:
        return None
    payload, sig = token.rsplit(".", 1)
    if not hmac.compare_digest(sig, _sign(payload)):
        return None
    try:
        return base64.urlsafe_b64decode(payload).decode()
    except ValueError:
        return None


def current_user(request: Request) -> str | None:
    return read_session_token(request.cookies.get(SESSION_COOKIE))


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
    "p2-up-core": {"cmd": ["./scripts/up_core.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-down-core": {"cmd": ["./scripts/down_core.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-up-e2-lab": {"cmd": ["./scripts/up_e2_lab.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-down-e2-lab": {"cmd": ["./scripts/down_e2_lab.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-test-e2-sm": {"cmd": ["./scripts/test_e2_sm.sh", "all"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-test-e2-kpm": {"cmd": ["./scripts/test_e2_kpm.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-test-e2-rc": {"cmd": ["./scripts/test_e2_rc_attach.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
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


def stream_telemetry() -> Iterator[str]:
    prev_idle, prev_total = read_cpu_times()
    while True:
        time.sleep(2)
        idle, total = read_cpu_times()
        d_idle, d_total = idle - prev_idle, total - prev_total
        cpu_pct = round(100 * (1 - d_idle / d_total), 1) if d_total else 0.0
        prev_idle, prev_total = idle, total

        host = read_host_metrics()
        host["cpu_pct"] = cpu_pct
        # Junta o status estável (docker ps -a) com CPU/RAM (docker stats só
        # tem dos que estão rodando). Lista todos os containers, marcando o
        # estado visual de cada um.
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
        payload = {"host": host, "containers": containers, "groups": read_group_status(states)}
        yield json.dumps(payload) + "\n"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/login")
def login(request: Request):
    if current_user(request) is not None:
        return RedirectResponse("/")
    html = (STATIC_DIR / "login.html").read_text()
    html = html.replace("__VERSION__", _VERSION)
    return HTMLResponse(html)


def _set_session(response: JSONResponse, user: str) -> JSONResponse:
    response.set_cookie(
        SESSION_COOKIE,
        make_session_token(user),
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=True,
    )
    return response


@app.post("/api/login")
def do_login(payload: dict) -> JSONResponse:
    user = str(payload.get("user", ""))
    password = str(payload.get("pass", ""))
    valid = (user in ADMIN_USERS and password == ADMIN_USERS[user]) or (
        user == GUEST_USER and password == GUEST_PASSWORD
    )
    if not valid:
        raise HTTPException(401, "Usuário ou senha inválidos.")
    role = "guest" if user == GUEST_USER else "admin"
    return _set_session(JSONResponse({"user": user, "role": role}), user)


@app.post("/api/login/guest")
def do_login_guest() -> JSONResponse:
    return _set_session(JSONResponse({"user": GUEST_USER, "role": "guest"}), GUEST_USER)


@app.post("/api/logout")
def do_logout() -> JSONResponse:
    response = JSONResponse({"ok": True})
    response.delete_cookie(SESSION_COOKIE)
    return response


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


@app.get("/api/topology/gnb-stats")
def topology_gnb_stats() -> JSONResponse:
    """Métricas de RAN ao vivo extraídas do log do gNB (PHY/MAC reais do UE
    simulado): SNR, MCS, PRBs, BLER. Alimenta o card do gNB na topologia."""
    import re as _re
    log = SERVER_DIR / "oai-cn-gnb-e2" / "logs" / "gnb_oai.log"
    if not process_running("nr-softmodem") or not log.exists():
        return JSONResponse({"up": False})
    try:
        lines = log.read_text(errors="replace").splitlines()
    except OSError:
        return JSONResponse({"up": False})
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
    return JSONResponse(stats)


@app.get("/api/topology")
def topology_endpoint() -> JSONResponse:
    """Devolve a topologia (openran-topology.json) enriquecida com o status
    ao vivo de cada nó — base dos modos visual e de troubleshooting."""
    try:
        data = json.loads((STATIC_DIR / "openran-topology.json").read_text())
    except (OSError, json.JSONDecodeError) as e:
        raise HTTPException(500, f"Falha ao ler topologia: {e}")
    data["live_status"] = topology_status(data.get("nodes", []))
    return JSONResponse(data)


@app.get("/api/version")
def version_endpoint() -> JSONResponse:
    return JSONResponse({"version": _VERSION})


@app.get("/api/whoami")
def whoami(request: Request) -> JSONResponse:
    user = current_user(request)
    role = "guest" if user == GUEST_USER else "admin"
    return JSONResponse({"user": user, "role": role})


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
    if current_user(request) == GUEST_USER:
        raise HTTPException(status_code=403, detail="Usuário guest não pode executar comandos.")
    if not re.fullmatch(r"\d{6,15}", imsi):
        return StreamingResponse(iter(["IMSI inválido\n"]), media_type="text/plain")
    env = os.environ.copy()
    env["SUB_IMSI"] = imsi
    return StreamingResponse(
        stream_command(["./scripts/remove-subscriber.sh"], SERVER_DIR, env=env),
        media_type="text/plain",
    )


@app.post("/api/channel")
def configure_channel(payload: dict, request: Request) -> StreamingResponse:
    if current_user(request) == GUEST_USER:
        raise HTTPException(status_code=403, detail="Usuário guest não pode executar comandos.")
    distance = str(payload.get("distance", "none"))
    interference = str(payload.get("interference", "none"))
    if distance not in _VALID_DISTANCES or interference not in _VALID_INTERFERENCES:
        return StreamingResponse(iter(["Parâmetros de canal inválidos\n"]), media_type="text/plain")
    return StreamingResponse(
        stream_command(["./scripts/test_channel.sh", distance, interference], SERVER_DIR),
        media_type="text/plain",
    )


_VALID_DURATIONS = {5, 10, 30, 60}


@app.post("/api/throughput")
def run_throughput(payload: dict, request: Request) -> StreamingResponse:
    if current_user(request) == GUEST_USER:
        raise HTTPException(status_code=403, detail="Usuário guest não pode executar comandos.")
    try:
        duration = int(payload.get("duration", 10))
    except (TypeError, ValueError):
        duration = 10
    if duration not in _VALID_DURATIONS:
        duration = 10
    env = os.environ.copy()
    env["IPERF_DURATION"] = str(duration)
    return StreamingResponse(
        stream_command(["./scripts/test_throughput.sh"], SERVER_DIR, env=env),
        media_type="text/plain",
    )


@app.post("/api/switch/{target}")
def switch_project(target: str, request: Request) -> StreamingResponse:
    """Alterna entre os projetos de forma exclusiva (p1 | p2 | off): desliga o
    que estiver no ar e sobe só o escolhido. Emite PHASE|/STEP|/DONE| para o
    painel mostrar progresso."""
    if current_user(request) == GUEST_USER:
        raise HTTPException(status_code=403, detail="Usuário guest não pode executar comandos.")
    if target not in ("p1", "p2", "off"):
        raise HTTPException(status_code=400, detail="Alvo inválido (use p1, p2 ou off).")
    return StreamingResponse(
        stream_command(["./scripts/switch_project.sh", target], SERVER_DIR),
        media_type="text/plain",
    )


@app.post("/api/demo-e2e")
def demo_e2e(request: Request) -> StreamingResponse:
    """Demonstração E2E (Projeto 1): UE → sessão PDU → internet → throughput.
    Emite linhas STEP|status|título|detalhe que o painel monta como relatório."""
    if current_user(request) == GUEST_USER:
        raise HTTPException(status_code=403, detail="Usuário guest não pode executar comandos.")
    return StreamingResponse(
        stream_command(["./scripts/demo_e2e.sh"], SERVER_DIR),
        media_type="text/plain",
    )


@app.get("/api/services")
def services_endpoint() -> JSONResponse:
    return JSONResponse({"services": sorted(list_services().keys())})


@app.get("/api/telemetry")
def telemetry() -> StreamingResponse:
    return StreamingResponse(stream_telemetry(), media_type="text/plain")


@app.get("/api/logs/{service}")
def logs(service: str) -> StreamingResponse:
    cwd = list_services().get(service)
    if cwd is None:
        return StreamingResponse(
            iter([f"Serviço desconhecido: {service}\n"]), media_type="text/plain"
        )
    cmd = ["docker", "compose", "logs", "-f", "--timestamps", "--tail", "200", service]
    return StreamingResponse(stream_command(cmd, cwd), media_type="text/plain")


@app.post("/api/subscriber")
def add_subscriber(payload: dict, request: Request) -> StreamingResponse:
    if current_user(request) == GUEST_USER:
        raise HTTPException(status_code=403, detail="Usuário guest só pode visualizar, não pode executar comandos.")

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
        stream_command(["./scripts/add-subscriber.sh"], SERVER_DIR, env=env), media_type="text/plain"
    )


@app.post("/api/run/{command}")
def run_command(command: str, request: Request) -> StreamingResponse:
    if current_user(request) == GUEST_USER:
        raise HTTPException(status_code=403, detail="Usuário guest só pode visualizar, não pode executar comandos.")
    spec = COMMANDS.get(command)
    if spec is None:
        return StreamingResponse(
            iter([f"Comando desconhecido: {command}\n"]), media_type="text/plain"
        )
    return StreamingResponse(
        stream_command(spec["cmd"], spec["cwd"]), media_type="text/plain"
    )
