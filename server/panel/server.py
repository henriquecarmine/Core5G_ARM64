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

ARQUITETURA EM DUAS CAMADAS (docs/plano-duas-camadas-painel.md):

    server.py   bootstrap — app, middleware de sessão, login/logout,
                sala de aula ao vivo (vaga de Professor, espectadores,
                presença/roster, navegação espelhada)
    core.py     infra compartilhada, sem rotas (sessão, LiveBuffer,
                resultados, streaming de comandos, i18n do servidor)
    ops.py      camada OPERACIONAL (serviços, telemetria, topologia,
                logs, assinantes, testes, comandos)
    lab.py      camada DIDÁTICA (páginas /lab/*, dúvidas do lab)

O entrypoint segue `uvicorn server:app` — nada muda no systemd/deploy.
"""
from __future__ import annotations

import secrets
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
)
from fastapi.staticfiles import StaticFiles

import lab
import ops
from core import (
    ACTIVE_ADMIN,
    ADMIN_USERS,
    EMAIL_RE,
    GUEST_ENABLED,
    GUEST_PASSWORD,
    GUEST_USER,
    LIVE,
    NO_CACHE,
    PUBLIC_PATHS,
    ROSTER_FILE,
    SESSION_COOKIE,
    SESSION_MAX_AGE,
    STATIC_DIR,
    VERSION,
    current_session,
    current_user,
    drop_viewer,
    is_active_admin,
    live_viewers,
    make_session_token,
    parse_session,
    record_attendance,
    req_lang,
    seat_free,
    srv_msg,
    state_lock,
    touch_admin,
    touch_viewer,
    viewer_count,
)

app = FastAPI(title="Core5G_ARM64 — Painel (servidor)")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def require_session(request: Request, call_next):
    path = request.url.path
    if path in PUBLIC_PATHS or path.startswith("/static/"):
        return await call_next(request)
    if current_user(request) is None:
        if path == "/" or not path.startswith("/api/"):
            return RedirectResponse("/login")
        return JSONResponse({"detail": srv_msg("not_auth_401", req_lang(request))}, status_code=401)
    return await call_next(request)


@app.get("/i18n.js")
def i18n_js() -> FileResponse:
    # Mesmo racional do no-cache dos HTML: dicionários mudam a cada release.
    return FileResponse(STATIC_DIR / "i18n.js", media_type="application/javascript", headers=NO_CACHE)


@app.get("/login")
def login(request: Request):
    if current_user(request) is not None:
        return RedirectResponse("/")
    html = (STATIC_DIR / "login.html").read_text()
    html = html.replace("__VERSION__", VERSION)
    html = html.replace("__GUEST_ENABLED__", "true" if GUEST_ENABLED else "false")
    return HTMLResponse(html, headers=NO_CACHE)


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


@app.post("/api/login")
def do_login(payload: dict, request: Request) -> JSONResponse:
    user = str(payload.get("user", ""))
    password = str(payload.get("pass", ""))
    is_guest = GUEST_ENABLED and user == GUEST_USER and password == GUEST_PASSWORD
    is_admin = user in ADMIN_USERS and password == ADMIN_USERS[user]
    if not (is_guest or is_admin):
        raise HTTPException(401, srv_msg("bad_credentials_401", req_lang(request)))
    if is_admin:
        now = time.time()
        with state_lock:
            # Trava de "um Professor por vez": bloqueia um SEGUNDO usuário enquanto
            # houver um professor ativo. O MESMO usuário pode reassumir (reconexão
            # de outra aba/dispositivo). A vaga só libera por logout — ou após
            # ADMIN_TAKEOVER_GRACE (10min) sem heartbeat, caso o Professor suma.
            if not seat_free(now) and ACTIVE_ADMIN["user"] != user:
                raise HTTPException(
                    409,
                    srv_msg("seat_taken_409", req_lang(request), user=ACTIVE_ADMIN["user"]),
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
    record_attendance(name, email)   # presença persistida (controle unitário)
    return _set_session(
        JSONResponse({"user": GUEST_USER, "role": "guest", "name": name, "email": email}),
        GUEST_USER, sid, email=email, name=name,
    )


@app.post("/api/logout")
def do_logout(request: Request) -> JSONResponse:
    _, sid = current_session(request)
    if sid:
        with state_lock:
            if ACTIVE_ADMIN["sid"] == sid:
                ACTIVE_ADMIN.update(user=None, sid=None, ts=0.0)
        drop_viewer(sid)
    response = JSONResponse({"ok": True})
    # A remoção PRECISA repetir os mesmos atributos do set_cookie (Secure,
    # HttpOnly, SameSite, Path). O token é stateless (assinado, sem store no
    # servidor), então só "encerra a sessão" de verdade se o navegador descartar
    # o cookie — e navegadores estritos ignoram a remoção se os atributos não
    # baterem, deixando o aluno "logado" ao voltar pra /.
    response.delete_cookie(
        SESSION_COOKIE, path="/", httponly=True, samesite="lax", secure=True
    )
    return response


@app.post("/api/heartbeat")
def heartbeat(request: Request) -> JSONResponse:
    """Professor: mantém a vaga viva. Front chama a cada ~5s."""
    user, sid = current_session(request)
    now = time.time()
    active = False
    if user is not None and user != GUEST_USER and sid:
        with state_lock:
            if ACTIVE_ADMIN["sid"] == sid:
                ACTIVE_ADMIN["ts"] = now
                active = True
            elif seat_free(now):
                # Vaga livre (ninguém a tem, ou o dono sumiu / o painel reiniciou):
                # a aba do professor REASSUME sozinha no próximo heartbeat — sem
                # precisar relogar. Não rouba de um professor ativo (só pega o que
                # já está livre), então a trava de "um por vez" segue valendo.
                ACTIVE_ADMIN.update(user=user, sid=sid, ts=now)
                active = True
    with state_lock:
        holder = None if seat_free(now) else ACTIVE_ADMIN["user"]
    return JSONResponse({"active_admin": holder, "is_active": active, "viewers": viewer_count()})


@app.get("/api/live")
def live(request: Request, since: int = 0) -> JSONResponse:
    """Aluno: puxa os eventos novos (>since) do buffer ao vivo + estado da sessão
    e da navegação do Professor. Também registra presença (contagem)."""
    user, sid, email, name = parse_session(request)
    touch_viewer(user, sid, email, name)
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
    import json as _json

    _require_admin(request)
    agg: dict[str, dict] = {}
    if ROSTER_FILE.exists():
        try:
            for line in ROSTER_FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    r = _json.loads(line)
                except _json.JSONDecodeError:
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
    touch_admin(sid)
    return JSONResponse({"ok": True})


@app.get("/api/version")
def version_endpoint() -> JSONResponse:
    return JSONResponse({"version": VERSION})


@app.get("/api/whoami")
def whoami(request: Request) -> JSONResponse:
    user, sid = current_session(request)
    role = "guest" if user == GUEST_USER else "admin"
    active = is_active_admin(user, sid) if role == "admin" else False
    return JSONResponse({"user": user, "role": role, "is_active": active})


# As duas camadas entram por último: rotas próprias do bootstrap (auth/aula ao
# vivo) acima têm precedência, e o contrato de rotas permanece idêntico ao do
# server.py monolítico (verificado por diff na Fase A).
app.include_router(ops.router)
app.include_router(lab.router)
