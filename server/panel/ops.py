"""
Camada OPERACIONAL do painel (ver docs/plano-duas-camadas-painel.md).

Tudo que observa e comanda a infraestrutura 5G do servidor: serviços e
containers dos Projetos 1/2, telemetria de host, topologia ao vivo, logs,
assinantes, testes e a execução de comandos (COMMANDS). Consome só o `core`
(sessão, vaga de professor, buffer ao vivo) — nunca o `lab`.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Iterator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, StreamingResponse

from core import (
    GUEST_USER,
    NO_CACHE,
    RESULTS_DIR,
    SERVER_DIR,
    STATIC_DIR,
    current_session,
    ensure_can_run,
    is_active_admin,
    req_lang,
    srv_msg,
    stream_command,
    tee_to_live,
)

router = APIRouter()

OPS_DIR = STATIC_DIR / "ops"

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
    # Análise de dados (aula06, slide 46): parseia o log KPM bruto → série temporal
    # CSV + KPIs por UE + sparkline (Coleta→ETL→KPI→Viz→Decisão), didático.
    "p2-kpm-analytics": {"cmd": ["./scripts/kpm_analytics.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    # Coleta KPM com TRÁFEGO REAL: resiliente, 100% por evento (sem tempo), com
    # heartbeat ("não travou"), auto-retry e auto-revert do cpuset. Conclui sempre.
    "p2-kpm-real": {"cmd": ["./scripts/kpm_collect_real.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    # Testes de ML por caso de uso (trabalho final RIC-IA, Prof. Julio Tesolin):
    # rodam o experimento scikit-learn sobre os dados REAIS do walk test SUTD e
    # streamam a tabela de métricas (recorte Instance; GradientBoosting≈XGBoost).
    "p2-ml-uetp": {"cmd": ["./scripts/p2_ml_uetp.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-ml-localizacao": {"cmd": ["./scripts/p2_ml_localizacao.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-ml-pm": {"cmd": ["./scripts/p2_ml_pm.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    # Análise de Dados em Redes de Telecom (Kunzler) — os 7 temas do projeto
    # integrador sobre a telemetria KPM (stdlib; amostra do professor ou dado
    # enviado/colado no painel, ver /api/lab-data/kpm). Não precisa da RAN no ar.
    "p2-kpi-qoe": {"cmd": ["./scripts/p2_aula04.sh"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-tema-t1": {"cmd": ["./scripts/p2_temas.sh", "t1"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-tema-t2": {"cmd": ["./scripts/p2_temas.sh", "t2"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-tema-t3": {"cmd": ["./scripts/p2_temas.sh", "t3"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-tema-t4": {"cmd": ["./scripts/p2_temas.sh", "t4"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-tema-t5": {"cmd": ["./scripts/p2_temas.sh", "t5"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-tema-t6": {"cmd": ["./scripts/p2_temas.sh", "t6"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-tema-t7": {"cmd": ["./scripts/p2_temas.sh", "t7"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    "p2-tema-all": {"cmd": ["./scripts/p2_temas.sh", "all"], "cwd": SERVER_DIR / "oai-cn-gnb-e2"},
    # Non-RT RIC — completa a pilha O-RAN do Projeto 2 (server/nonrt-ric/,
    # imagens ARM64 locais via docker load; docs/instalacao-nonrt-arm64.md).
    # Leve (~0,5 GB): o switch p/ P2 sobe junto; toggle dá o controle manual.
    "p2-up-nonrt": {"cmd": ["./up_nonrt.sh"], "cwd": SERVER_DIR / "nonrt-ric"},
    "p2-down-nonrt": {"cmd": ["./down_nonrt.sh"], "cwd": SERVER_DIR / "nonrt-ric"},
    "p2-test-a1": {"cmd": ["./test_a1_flow.sh"], "cwd": SERVER_DIR / "nonrt-ric"},
}

_VALID_DISTANCES = {"none", "100m", "500m", "1km", "3km", "off"}
_VALID_INTERFERENCES = {"none", "fraca", "media", "alta"}


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


def process_running(name: str) -> bool:
    """Processo vivo, pelo NOME exato do binario (pgrep -x).

    Era `pgrep -f`, que casa a linha de comando inteira: um `tail -f
    nr-softmodem.log`, um `pkill -f nr-softmodem` do proprio script de
    desligar ou qualquer shell de aluno com a palavra na linha acendiam o
    botao do painel como se o lab estivesse no ar. Todos os chamadores passam
    nome de binario (nr-softmodem, nr-uesoftmodem, nearRT-RIC), que e como os
    scripts up_*.sh tambem conferem.
    """
    try:
        return subprocess.run(
            ["pgrep", "-x", name], capture_output=True, timeout=3
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


# A que CONJUNTO cada container pertence. Sem isto o painel só sabe dizer
# "está parado", e não sabe se isso é incidente ou se o conjunto inteiro
# simplesmente não foi levantado — que é uma diferença enorme para quem lê.
CONJUNTOS = (
    ("p1", lambda n: n.startswith("open5gs") or n == "ueransim"),
    ("p2-core", lambda n: n.startswith("oai-") or n == "mysql"),
    # o agrupamento segue as BANDAS da topologia (openran-topology.json):
    # `a1sim` e `nonrt-pms` são da banda "nonrt"; `a1mediator` é da "oransc".
    # Aqui já esteve o a1-sim junto do ric_, e a tela concluiu que dois
    # containers parados havia duas semanas eram irmãos caídos de um conjunto
    # no ar — alarme falso nascido de agrupamento chutado.
    ("p2-nonrt", lambda n: n.startswith("nonrt") or n.lower().startswith("a1-sim")),
    ("p2-oransc", lambda n: n.startswith("ric_")),
)


def container_group(nome: str) -> str:
    for chave, pred in CONJUNTOS:
        if pred(nome):
            return chave
    return "outro"


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
        "p2-nonrt": group_of(lambda n: n == "nonrt-policy-agent"),
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
            "grupo": container_group(name),
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


@router.get("/")
def index() -> FileResponse:
    return FileResponse(OPS_DIR / "index.html", headers=NO_CACHE)


@router.get("/topology")
def topology_page() -> FileResponse:
    return FileResponse(OPS_DIR / "topology.html", headers=NO_CACHE)


@router.get("/analise")
def analise_page() -> FileResponse:
    """Analisador do laboratório: telemetria, rádio, serviços, testes e a
    leitura do que tudo isso quer dizer. Lê os mesmos endpoints do painel —
    não coleta nada por conta própria."""
    return FileResponse(OPS_DIR / "analise.html", headers=NO_CACHE)


@router.get("/api/results")
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


@router.get("/api/results/{rid}")
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


@router.delete("/api/results/{rid}")
def delete_result(rid: str, request: Request) -> JSONResponse:
    user, _ = current_session(request)
    if user is None or user == GUEST_USER:
        raise HTTPException(403, "Aluno não pode apagar resultados.")
    if not re.fullmatch(r"[0-9A-Za-z\-]{1,40}", rid):
        raise HTTPException(400, "id inválido")
    (RESULTS_DIR / f"{rid}.json").unlink(missing_ok=True)
    return JSONResponse({"ok": True})


@router.post("/api/results/delete")
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


@router.post("/api/results/{rid}/note")
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
        if out.returncode != 0:
            return []  # container inexistente/parado: sem logs (não vaza erro do daemon)
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


@router.get("/api/topology/logs")
def topology_logs(proj: str = "p2") -> JSONResponse:
    """Logs recentes por componente para a tela de topologia, conforme o projeto
    ativo (?proj=p1|p2). Containers via `docker logs`; gNB/RIC nativos do P2 via
    arquivos de log. Só volta seções com conteúdo (componente parado some)."""
    if proj == "p1":
        # Projeto 1 — Open5GS (5GC) + UERANSIM (RAN)
        sections = [
            {"title": "UERANSIM (gNB + UE)", "comp": "ran", "lines": _docker_logs("ueransim", 16)},
            {"title": "AMF (Mobilidade)", "comp": "amf", "lines": _docker_logs("open5gs-amf-containerized", 10)},
            {"title": "SMF (Sessão)", "comp": "smf", "lines": _docker_logs("open5gs-smf-containerized", 8)},
            {"title": "AUSF (Autenticação)", "comp": "ausf", "lines": _docker_logs("open5gs-ausf-containerized", 8)},
            {"title": "NRF (Descoberta)", "comp": "nrf", "lines": _docker_logs("open5gs-nrf-containerized", 6)},
        ]
    else:
        # Projeto 2 — OAI 5GC v2 + gNB/RIC nativos (host)
        oai_logs = SERVER_DIR / "oai-cn-gnb-e2" / "logs"
        # gNB/RIC são nativos no host: só mostra se o processo está vivo, senão
        # o _tail_file devolveria conteúdo velho da última sessão (log no disco).
        gnb_lines = _tail_file(oai_logs / "gnb_oai.log", 16, r"E2|RIC|SETUP|NGAP|registr|error|PDU") \
            if process_running("nr-softmodem") else []
        ric_lines = _tail_file(oai_logs / "nearRT-RIC.log", 14) \
            if process_running("nearRT-RIC") else []
        sections = [
            {"title": "gNB (E2 Agent)", "comp": "gnb", "lines": gnb_lines},
            {"title": "near-RT RIC", "comp": "ric", "lines": ric_lines},
            {"title": "Non-RT RIC (PMS · A1)", "comp": "nonrt-pms", "lines": _docker_logs("nonrt-policy-agent", 8)},
            {"title": "A1 Simulator (OSC)", "comp": "a1sim", "lines": _docker_logs("a1-sim-OSC", 6)},
            {"title": "A1 Mediator (O-RAN SC · A1 real)", "comp": "a1mediator", "lines": _docker_logs("ric_a1mediator", 8)},
            {"title": "dbaas (Redis · SDL)", "comp": "dbaas", "lines": _docker_logs("ric_dbaas", 5)},
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
    # Idade da última escrita no log: o gNB pode estar VIVO e ter parado de
    # reportar (UE caiu, RAN travada). Sem isto o painel mostraria o último
    # número com a bolinha pulsando, fingindo que é ao vivo.
    try:
        stats["age"] = round(time.time() - log.stat().st_mtime, 1)
    except OSError:
        pass
    # Total de PRBs da célula: vem do próprio gNB ("Init: N_RB_DL 51"), não de
    # um número escrito na tela. Se a banda mudar no config, o painel acompanha.
    for line in lines[:400]:
        m_nrb = _re.search(r"N_RB_DL[ =]+(\d+)", line)
        if m_nrb:
            stats["nrb"] = int(m_nrb.group(1))
            break
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


@router.get("/api/topology/gnb-stats")
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


@router.get("/api/topology")
def topology_endpoint(proj: str = "p2") -> JSONResponse:
    """Devolve a topologia do projeto pedido (?proj=p1|p2) enriquecida com o
    status ao vivo de cada nó. Padrão p2 (compat: openran-topology.json é a do
    Projeto 2)."""
    fname = "openran-topology-p1.json" if proj == "p1" else "openran-topology.json"
    try:
        data = json.loads((OPS_DIR / fname).read_text())
    except (OSError, json.JSONDecodeError) as e:
        raise HTTPException(500, f"Falha ao ler topologia: {e}")
    data["live_status"] = topology_status(data.get("nodes", []))
    return JSONResponse(data)


@router.get("/api/subscribers")
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


@router.delete("/api/subscriber/{imsi}")
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


@router.post("/api/channel")
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


@router.post("/api/throughput")
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


@router.post("/api/switch/{target}")
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


@router.post("/api/demo-e2e")
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
    # Projeto 2 — Non-RT RIC (camada SMO, containers ARM64 próprios)
    {"key": "nonrt-pms", "label": "Non-RT RIC · PMS (políticas A1)", "container": "nonrt-policy-agent"},
    {"key": "a1-sim",    "label": "A1 Simulator (OSC) · near-RT sim", "container": "a1-sim-OSC"},
    {"key": "a1mediator", "label": "A1 Mediator (O-RAN SC) · A1 real",  "container": "ric_a1mediator"},
    {"key": "dbaas",      "label": "dbaas (Redis/SDL) · banco do RIC",  "container": "ric_dbaas"},
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


@router.get("/api/services")
def services_endpoint() -> JSONResponse:
    return JSONResponse({"services": [
        {"key": s["key"], "label": s["label"]} for s in available_log_sources()
    ]})


@router.get("/api/telemetry")
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


@router.get("/api/logs/{service}")
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


@router.post("/api/subscriber")
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



# ---- Fonte de dados dos labs de ML: sugerida (servidor) × CSV do professor --
# O upload substitui os 4 cenários SUTD (os wrappers p2_ml_*.sh honram
# SUTD_DIR); o exemplo para download vem do dataset real. Professor-only
# para mudar; qualquer um pode consultar/baixar o exemplo.
LABDATA_DIR = SERVER_DIR / "panel_uploads" / "labdata" / "sutd"
SUTD_DEFAULT_DIR = SERVER_DIR / "oai-cn-gnb-e2" / "data" / "sutd"
SUTD_SCENARIOS = ["Lvl4_AllRRUOn_Anomaly_label.csv", "Lvl5_AllRRUOn_Anomaly_label.csv",
                  "Lvl6_AllRRUOn_Anomaly_label.csv", "Lvl6_1RRUOn_Anomaly_label.csv"]
_LABDATA_STATE = SERVER_DIR / "panel_uploads" / "labdata" / "state.json"


def _labdata_state() -> dict:
    try:
        return json.loads(_LABDATA_STATE.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _labdata_save(st: dict) -> None:
    _LABDATA_STATE.parent.mkdir(parents=True, exist_ok=True)
    _LABDATA_STATE.write_text(json.dumps(st))


def _only_professor(request: Request) -> None:
    user, _ = current_session(request)
    if user is None or user == GUEST_USER:
        raise HTTPException(403, "Somente o professor pode mudar a fonte de dados.")


@router.get("/api/lab-data/sutd")
def labdata_status() -> JSONResponse:
    st = _labdata_state()
    return JSONResponse({
        "source": st.get("sutd", "default"),
        "has_custom": (LABDATA_DIR / SUTD_SCENARIOS[0]).exists(),
    })


@router.get("/api/lab-data/sutd/example")
def labdata_example() -> PlainTextResponse:
    """Modelo de CSV: cabeçalho + primeiras linhas do dataset real."""
    src = SUTD_DEFAULT_DIR / SUTD_SCENARIOS[0]
    try:
        lines = src.read_text(errors="replace").splitlines()[:6]
    except OSError:
        raise HTTPException(404, "dataset sugerido não encontrado no servidor")
    return PlainTextResponse("\n".join(lines) + "\n", headers={
        "Content-Disposition": "attachment; filename=exemplo_sutd.csv",
        "Content-Type": "text/csv"})


@router.post("/api/lab-data/sutd/source")
def labdata_source(payload: dict, request: Request) -> JSONResponse:
    _only_professor(request)
    source = payload.get("source")
    if source not in ("default", "custom"):
        raise HTTPException(400, "source deve ser default|custom")
    if source == "custom" and not (LABDATA_DIR / SUTD_SCENARIOS[0]).exists():
        raise HTTPException(400, "nenhum CSV enviado ainda")
    st = _labdata_state(); st["sutd"] = source; _labdata_save(st)
    return JSONResponse({"ok": True, "source": source})


@router.post("/api/lab-data/sutd/upload")
async def labdata_upload(request: Request) -> JSONResponse:
    """Corpo cru text/csv (sem multipart — sem dependência nova). O MESMO CSV
    vira os 4 cenários — didático: seus dados, mesma metodologia."""
    _only_professor(request)
    body = await request.body()
    if len(body) > 8_000_000:
        raise HTTPException(413, "CSV grande demais (limite 8 MB)")
    try:
        text = body.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(400, "arquivo não é texto UTF-8 — envie um .csv")
    rows = [l for l in text.splitlines() if l.strip()]
    if len(rows) < 10 or "," not in rows[0]:
        raise HTTPException(400, "CSV inválido: preciso de cabeçalho com vírgulas e ≥10 linhas (baixe o exemplo)")
    ncols = rows[0].count(",")
    if any(abs(r.count(",") - ncols) > 0 for r in rows[1:5]):
        raise HTTPException(400, "número de colunas inconsistente nas primeiras linhas")
    LABDATA_DIR.mkdir(parents=True, exist_ok=True)
    for name in SUTD_SCENARIOS:
        (LABDATA_DIR / name).write_text(text)
    st = _labdata_state(); st["sutd"] = "custom"; _labdata_save(st)
    return JSONResponse({"ok": True, "rows": len(rows) - 1, "source": "custom"})


# ---- Fonte de dados dos 7 temas (Análise de Dados): amostra do professor × ----
# dado enviado/colado. O upload aceita JSONL (formato do professor) ou CSV
# (largo: thp_ul,delay_dl,prb_ul[,phase,...]; ou o longo do kpm_analytics).
# Um arquivo só; os wrappers p2_temas.sh honram KPM_FILE.
KPM_DIR = SERVER_DIR / "panel_uploads" / "labdata" / "kpm"
KPM_CUSTOM = KPM_DIR / "kpm_custom.txt"
KPM_SAMPLE = SERVER_DIR / "oai-cn-gnb-e2" / "scripts" / "temas" / "samples" / "kpm_ue_tp_sample.jsonl"
_KPM_ALIASES = {"thp": ("thp_ul", "drb.uethpul", "throughput", "thp", "vazao"),
                "delay": ("delay_dl", "drb.rlcsdudelaydl", "delay", "atraso", "latency"),
                "prb": ("prb_ul", "rru.prbtotul", "prb", "prbtotul")}


def _kpm_validate(text: str) -> int:
    """Devolve o nº de amostras válidas ou levanta HTTPException explicando."""
    rows = [l for l in text.splitlines() if l.strip()]
    if len(rows) < 5:
        raise HTTPException(400, "preciso de pelo menos 5 amostras")
    if rows[0].lstrip().startswith("{"):
        n = 0
        for l in rows:
            try:
                o = json.loads(l)
            except json.JSONDecodeError:
                continue
            m = o.get("metrics", o)
            low = {k.lower() for k in m}
            if all(any(a in low for a in _KPM_ALIASES[f]) for f in _KPM_ALIASES):
                n += 1
        if n < 5:
            raise HTTPException(400, "JSONL sem as 3 métricas (DRB.UEThpUl, DRB.RlcSduDelayDl, RRU.PrbTotUl) em pelo menos 5 linhas")
        return n
    if "," not in rows[0]:
        raise HTTPException(400, "CSV inválido: preciso de um cabeçalho com vírgulas (baixe o exemplo)")
    hdr = [h.strip().lower() for h in rows[0].split(",")]
    if "measname" in hdr and "value" in hdr:
        return len(rows) - 1
    faltam = [f for f in _KPM_ALIASES if not any(a in hdr for a in _KPM_ALIASES[f])]
    if faltam:
        raise HTTPException(400, f"CSV sem coluna de {', '.join(faltam)} (use thp_ul, delay_dl, prb_ul; baixe o exemplo)")
    return len(rows) - 1


@router.get("/api/lab-data/kpm")
def kpmdata_status() -> JSONResponse:
    st = _labdata_state()
    return JSONResponse({"source": st.get("kpm", "default"), "has_custom": KPM_CUSTOM.exists(),
                         "rows": st.get("kpm_rows")})


@router.get("/api/lab-data/kpm/preview")
def kpmdata_preview() -> JSONResponse:
    """As primeiras linhas do dado que o teste VAI usar, para a tela de pré-voo.

    A aula 03 insiste que ninguém analisa o que não olhou: antes de rodar, o
    aluno vê o arquivo de verdade (a fonte em uso, quantas amostras, quais
    fases e as primeiras medições), não um exemplo decorativo. Serve tanto para
    a amostra do professor quanto para o arquivo enviado/colado no painel.
    """
    st = _labdata_state()
    usa_custom = st.get("kpm") == "custom" and KPM_CUSTOM.exists()
    path = KPM_CUSTOM if usa_custom else KPM_SAMPLE
    origem = ("arquivo que você enviou/colou no painel" if usa_custom
              else "amostra oficial do professor (kpm-ue-tp-sample)")
    linhas: list[dict] = []
    fases: dict[str, int] = {}
    total = 0
    try:
        with path.open(errors="replace") as fh:
            for i, raw in enumerate(fh):
                raw = raw.strip()
                if not raw:
                    continue
                total += 1
                if raw.startswith("{"):
                    try:
                        o = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    m = o.get("metrics", o)
                    fase = str(o.get("phase") or "-")
                    reg = {"i": o.get("sample_index", i), "fase": fase,
                           "thp": m.get("DRB.UEThpUl"), "delay": m.get("DRB.RlcSduDelayDl"),
                           "prb": m.get("RRU.PrbTotUl")}
                else:  # CSV: devolve a linha crua; a tela mostra como texto
                    fase = "-"
                    reg = {"i": i, "fase": fase, "raw": raw[:160]}
                fases[fase] = fases.get(fase, 0) + 1
                if len(linhas) < 6:
                    linhas.append(reg)
    except OSError:
        raise HTTPException(404, "dado do lab não encontrado no servidor")
    return JSONResponse({
        "origem": origem,
        "arquivo": path.name,
        "total": total,
        "fases": fases,
        "linhas": linhas,
        "colunas": [
            {"k": "DRB.UEThpUl", "nome": "vazão UL do UE", "un": "kbps",
             "o": "quantos bits o usuário conseguiu subir naquele instante"},
            {"k": "DRB.RlcSduDelayDl", "nome": "atraso RLC no DL", "un": "µs",
             "o": "quanto tempo o pacote esperou na camada RLC antes de descer"},
            {"k": "RRU.PrbTotUl", "nome": "ocupação de PRB no UL", "un": "%",
             "o": "quanto do rádio (blocos de recurso) estava sendo usado"},
        ],
    }, headers=NO_CACHE)


@router.get("/api/lab-data/kpm/example")
def kpmdata_example() -> PlainTextResponse:
    """Modelo em CSV largo (as 3 métricas + fase + índice), tirado da amostra do professor."""
    out = ["thp_ul,delay_dl,prb_ul,phase,sample_index"]
    try:
        for l in KPM_SAMPLE.read_text(errors="replace").splitlines():
            if len(out) > 6:
                break
            try:
                o = json.loads(l)
            except json.JSONDecodeError:
                continue
            m = o.get("metrics", {})
            out.append(f"{m.get('DRB.UEThpUl')},{m.get('DRB.RlcSduDelayDl')},{m.get('RRU.PrbTotUl')},"
                       f"{o.get('phase', '')},{o.get('sample_index', '')}")
    except OSError:
        raise HTTPException(404, "amostra do professor não encontrada no servidor")
    return PlainTextResponse("\n".join(out) + "\n", headers={
        "Content-Disposition": "attachment; filename=exemplo_kpm.csv", "Content-Type": "text/csv"})


@router.post("/api/lab-data/kpm/source")
def kpmdata_source(payload: dict, request: Request) -> JSONResponse:
    _only_professor(request)
    source = payload.get("source")
    if source not in ("default", "custom"):
        raise HTTPException(400, "source deve ser default|custom")
    if source == "custom" and not KPM_CUSTOM.exists():
        raise HTTPException(400, "nenhum dado enviado ainda")
    st = _labdata_state(); st["kpm"] = source; _labdata_save(st)
    return JSONResponse({"ok": True, "source": source})


@router.post("/api/lab-data/kpm/upload")
async def kpmdata_upload(request: Request) -> JSONResponse:
    """Corpo cru (text/csv ou JSONL; colado ou arquivo). Sem multipart."""
    _only_professor(request)
    body = await request.body()
    if len(body) > 8_000_000:
        raise HTTPException(413, "arquivo grande demais (limite 8 MB)")
    try:
        text = body.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(400, "não é texto UTF-8 — envie .csv ou .jsonl")
    n = _kpm_validate(text)
    KPM_DIR.mkdir(parents=True, exist_ok=True)
    KPM_CUSTOM.write_text(text)
    st = _labdata_state(); st["kpm"] = "custom"; st["kpm_rows"] = n; _labdata_save(st)
    return JSONResponse({"ok": True, "rows": n, "source": "custom"})


@router.post("/api/run/{command}")
def run_command(command: str, request: Request) -> StreamingResponse:
    by = ensure_can_run(request)
    lang = req_lang(request)
    spec = COMMANDS.get(command)
    if spec is None:
        return StreamingResponse(
            iter([f"{srv_msg('unknown_cmd', lang)}: {command}\n"]), media_type="text/plain"
        )
    env = None
    if command.startswith("p2-ml-") and _labdata_state().get("sutd") == "custom":
        env = os.environ.copy()
        env["SUTD_DIR"] = str(LABDATA_DIR)
    if (command.startswith("p2-tema-") or command == "p2-kpi-qoe") and _labdata_state().get("kpm") == "custom" and KPM_CUSTOM.exists():
        env = env or os.environ.copy()
        env["KPM_FILE"] = str(KPM_CUSTOM)
    return StreamingResponse(
        tee_to_live(stream_command(spec["cmd"], spec["cwd"], env=env, lang=lang), command, by, cmd=command),
        media_type="text/plain",
    )
