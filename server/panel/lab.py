"""
Camada DIDÁTICA do painel (ver docs/plano-duas-camadas-painel.md).

As páginas do Lab de RIC com IA (aulas por técnica de ML + projeto final) e o
canal de dúvidas aluno→professor. Consome o `core` (sessão) e, no navegador,
as APIs da camada operacional (ex.: testes de ML ao vivo via /api/run) — a
operacional nunca importa daqui.

Fase C (v0.64.0): Estudos por cadeira — hub `/lab/estudo/{n}` e aulas
`/lab/estudo/{n}/aula/{k}` renderizados de JSON plugável em
static/lab/estudos/ (ver docs/estudos-por-cadeira.md).
"""
from __future__ import annotations

import json
import threading
import time

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse

from core import (
    ADMIN_USERS,
    NO_CACHE,
    RESULTS_DIR,
    STATIC_DIR,
    current_user,
    parse_session,
)

router = APIRouter()

LAB_DIR = STATIC_DIR / "lab"


# Lab de RIC com IA — cards didáticos (mini-labs por técnica de ML). Servidos
# como páginas autenticadas (fora de PUBLIC_PATHS), no mesmo molde da topologia.
@router.get("/lab")
def lab_hub_page() -> FileResponse:
    return FileResponse(LAB_DIR / "lab-hub.html", headers=NO_CACHE)


@router.get("/lab/fundamentos")
def lab_fundamentos_page() -> FileResponse:
    return FileResponse(LAB_DIR / "lab-fundamentos.html", headers=NO_CACHE)


@router.get("/lab/regressao")
def lab_regressao_page() -> FileResponse:
    return FileResponse(LAB_DIR / "lab-regressao.html", headers=NO_CACHE)


@router.get("/lab/classificacao")
def lab_classificacao_page() -> FileResponse:
    return FileResponse(LAB_DIR / "lab-classificacao.html", headers=NO_CACHE)


# Casos do artigo (Ngo et al. 2024) sobre os dados reais do SUTD — classificadores.
@router.get("/lab/localizacao")
def lab_localizacao_page() -> FileResponse:
    return FileResponse(LAB_DIR / "lab-localizacao.html", headers=NO_CACHE)


@router.get("/lab/manutencao")
def lab_manutencao_page() -> FileResponse:
    return FileResponse(LAB_DIR / "lab-manutencao.html", headers=NO_CACHE)


@router.get("/lab/clustering")
def lab_clustering_page() -> FileResponse:
    return FileResponse(LAB_DIR / "lab-clustering.html", headers=NO_CACHE)


@router.get("/lab/anomalia")
def lab_anomalia_page() -> FileResponse:
    return FileResponse(LAB_DIR / "lab-anomalia.html", headers=NO_CACHE)


@router.get("/lab/pca")
def lab_pca_page() -> FileResponse:
    return FileResponse(LAB_DIR / "lab-pca.html", headers=NO_CACHE)


# Projeto final: página de fechamento — escolher o caso, rodar o teste, gerar o relatório.
@router.get("/lab/projeto")
def lab_projeto_page() -> FileResponse:
    return FileResponse(LAB_DIR / "lab-projeto.html", headers=NO_CACHE)


# Fase C — Estudos por cadeira. Conteúdo plugável: static/lab/estudos/index.json
# (catálogo: 4 cadeiras, exercícios, os 7 temas) + <id>.json por aula
# (extraído dos slides). Duas páginas genéricas leem o caminho e renderizam.
@router.get("/lab/estudo/{n}")
def lab_estudo_page(n: int) -> FileResponse:
    if n not in (1, 2, 3, 4):
        raise HTTPException(404, "estudo inexistente")
    return FileResponse(LAB_DIR / "lab-estudo.html", headers=NO_CACHE)


@router.get("/lab/estudo/{n}/aula/{k}")
def lab_aula_page(n: int, k: int) -> FileResponse:
    if n not in (1, 2, 4) or not (1 <= k <= 6):
        raise HTTPException(404, "aula inexistente")
    return FileResponse(LAB_DIR / "lab-aula.html", headers=NO_CACHE)


# Dúvidas do Lab de IA: aluno/professor envia "não entendi" com a pergunta;
# o professor lê a lista no hub do lab. Armazenamento simples em JSONL.
_LAB_Q_FILE = RESULTS_DIR / "lab_questions.jsonl"
_lab_q_lock = threading.Lock()


@router.post("/api/lab/question")
def lab_question(payload: dict, request: Request) -> JSONResponse:
    user, _, email, name = parse_session(request)
    if not user:
        raise HTTPException(401, "sessão inválida")
    lesson = str(payload.get("lesson", ""))[:40]
    text = str(payload.get("text", "")).strip()[:500]
    if not text:
        raise HTTPException(400, "dúvida vazia")
    rec = {"ts": time.time(), "user": user, "name": name or user,
           "email": email, "lesson": lesson, "text": text}
    with _lab_q_lock:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(_LAB_Q_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return JSONResponse({"ok": True})


@router.get("/api/lab/questions")
def lab_questions(request: Request) -> JSONResponse:
    user = current_user(request)
    if user is None or user not in ADMIN_USERS:
        raise HTTPException(403, "somente professor")
    items: list[dict] = []
    try:
        for line in _LAB_Q_FILE.read_text(encoding="utf-8").splitlines()[-100:]:
            try:
                items.append(json.loads(line))
            except ValueError:
                pass
    except FileNotFoundError:
        pass
    items.reverse()
    return JSONResponse({"questions": items})
