"""
Painel de controle do Core5G_ARM64 — versão SERVER-SIDE.

Roda DIRETO NO SERVIDOR (diferente de client/server.py, que roda na estação
local e fala com o servidor via SSH/deploy.sh). Aqui não tem SSH nenhum: os
comandos chamam os scripts locais (../scripts/*.sh) direto, porque o painel
já está na mesma máquina.

Autenticação (usuário/senha) NÃO é feita aqui — fica a cargo do Caddy
(basic_auth + HTTPS) na frente deste processo, que só escuta em 127.0.0.1.
O Caddyfile injeta o usuário autenticado no header `X-Remote-User`; este
processo só usa esse header para decidir permissão (admin vs. guest), nunca
para autenticar — quem autentica é o Caddy.

`sync`/`sync-oai`/`bootstrap` não existem aqui: esses comandos levam código
do laptop pro servidor, não fazem sentido executados a partir do próprio
servidor. Para isso, use `./deploy.sh` na sua máquina local.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Iterator

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

SERVER_DIR = Path(__file__).resolve().parent.parent  # ~/server
STATIC_DIR = Path(__file__).resolve().parent / "static"
_VERSION = (Path(__file__).resolve().parent / "VERSION").read_text().strip()

# Usuário guest é só-leitura: não tem permissão pra rodar nenhum comando.
# Qualquer outro usuário autenticado pelo Caddy (ex.: admin) tem acesso total.
GUEST_USER = os.environ.get("PANEL_GUEST_USER", "guest")

app = FastAPI(title="Core5G_ARM64 — Painel (servidor)")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

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


def read_group_status(containers: list[dict]) -> dict[str, bool]:
    """Estado on/off dos toggles do painel: Projeto 1 via docker (containers
    do compose), Projeto 2 via docker (core) + processo nativo (gNB/RIC, que
    não roda em container)."""
    names = [c["name"] for c in containers]
    return {
        "p1-core": any("open5gs-nrf" in n for n in names),
        "p1-ran": any(n == "ueransim" for n in names),
        "p2-core": any(n == "oai-amf" for n in names),
        "p2-e2lab": process_running("nr-softmodem") or process_running("nearRT-RIC"),
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
        containers = read_container_stats()
        payload = {"host": host, "containers": containers, "groups": read_group_status(containers)}
        yield json.dumps(payload) + "\n"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/version")
def version_endpoint() -> JSONResponse:
    return JSONResponse({"version": _VERSION})


@app.get("/api/whoami")
def whoami(x_remote_user: str | None = Header(default=None)) -> JSONResponse:
    role = "guest" if x_remote_user == GUEST_USER else "admin"
    return JSONResponse({"user": x_remote_user, "role": role})


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
def delete_subscriber(imsi: str, x_remote_user: str | None = Header(default=None)) -> StreamingResponse:
    if x_remote_user == GUEST_USER:
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
def configure_channel(payload: dict, x_remote_user: str | None = Header(default=None)) -> StreamingResponse:
    if x_remote_user == GUEST_USER:
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
def run_throughput(payload: dict, x_remote_user: str | None = Header(default=None)) -> StreamingResponse:
    if x_remote_user == GUEST_USER:
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
def add_subscriber(payload: dict, x_remote_user: str | None = Header(default=None)) -> StreamingResponse:
    if x_remote_user == GUEST_USER:
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
def run_command(command: str, x_remote_user: str | None = Header(default=None)) -> StreamingResponse:
    if x_remote_user == GUEST_USER:
        raise HTTPException(status_code=403, detail="Usuário guest só pode visualizar, não pode executar comandos.")
    spec = COMMANDS.get(command)
    if spec is None:
        return StreamingResponse(
            iter([f"Comando desconhecido: {command}\n"]), media_type="text/plain"
        )
    return StreamingResponse(
        stream_command(spec["cmd"], spec["cwd"]), media_type="text/plain"
    )
