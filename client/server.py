"""
Backend local do painel de controle do Core5G_ARM64.

Serve uma UI simples e executa `deploy.sh` (na raiz do projeto), streamando
a saída em tempo real. Não reimplementa nada de SSH/rsync — deploy.sh
continua sendo a única fonte de verdade para falar com o servidor.

Uso: ./run.sh (instala deps num venv e sobe em http://127.0.0.1:8765)
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterator

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

ROOT_DIR = Path(__file__).resolve().parent.parent
DEPLOY_SH = ROOT_DIR / "deploy.sh"
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Core5G_ARM64 — Painel de Controle")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Mapa de comando exposto na UI -> argumentos passados pro deploy.sh.
# Nada de string livre vindo do cliente: só estas chaves fixas são aceitas.
COMMANDS: dict[str, list[str]] = {
    "bootstrap": ["bootstrap"],
    "sync": ["sync"],
    "sync-oai": ["sync-oai"],
    "up-core": ["up", "core"],
    "up-ran": ["up", "ran"],
    "up-all": ["up", "all"],
    "down-core": ["down", "core"],
    "down-ran": ["down", "ran"],
    "down-all": ["down", "all"],
    "status": ["status"],
}


def stream_deploy(args: list[str]) -> Iterator[str]:
    if not DEPLOY_SH.exists():
        yield f"ERRO: {DEPLOY_SH} não encontrado.\n"
        return
    process = subprocess.Popen(
        [str(DEPLOY_SH), *args],
        cwd=ROOT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None
    yield f"$ ./deploy.sh {' '.join(args)}\n\n"
    for line in process.stdout:
        yield line
    process.wait()
    yield f"\n[processo encerrado, exit code {process.returncode}]\n"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/run/{command}")
def run_command(command: str) -> StreamingResponse:
    args = COMMANDS.get(command)
    if args is None:
        return StreamingResponse(
            iter([f"Comando desconhecido: {command}\n"]), media_type="text/plain"
        )
    return StreamingResponse(stream_deploy(args), media_type="text/plain")
