"""
Infra COMPARTILHADA do painel (camada transversal, sem rotas).

Tudo que as duas camadas usam: configuração/ambiente, sessão por cookie
assinado (HMAC), a vaga única de Professor + espectadores (sala de aula ao
vivo), o buffer de transmissão (LiveBuffer), a persistência de Resultados,
o streaming de comandos e o i18n do servidor.

Regra de dependência (ver docs/plano-duas-camadas-painel.md): `ops` e `lab`
importam daqui; este módulo não conhece nenhum dos dois.
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
import subprocess
import threading
import time
from pathlib import Path

from fastapi.responses import HTMLResponse
from typing import Iterator

from fastapi import HTTPException, Request

SERVER_DIR = Path(__file__).resolve().parent.parent  # ~/server
STATIC_DIR = Path(__file__).resolve().parent / "static"
VERSION = (Path(__file__).resolve().parent / "VERSION").read_text().strip()

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
# /i18n.js é público: a PÁGINA DE LOGIN depende dele (dicionários pt/en/es/fr)
# — atrás do auth, o redirect 307 quebra o <script> e trava o login inteiro.
PUBLIC_PATHS = {"/login", "/api/login", "/api/login/guest", "/api/version", "/i18n.js"}


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


def parse_session(request: Request) -> tuple[str | None, str | None, str, str]:
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
    user, sid, _, _ = parse_session(request)
    return (user, sid)


def current_ident(request: Request) -> tuple[str, str]:
    """(email, nome) do Aluno, se houver."""
    _, _, email, name = parse_session(request)
    return (email, name)


def current_user(request: Request) -> str | None:
    return parse_session(request)[0]


# ===========================================================================
# Sala de aula: 1 Professor (admin) ativo por vez + espectadores (Alunos) que
# acompanham ao vivo. Estado em memória do processo (cai em restart, ok no lab).
# ===========================================================================
state_lock = threading.RLock()
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


def seat_free(now: float) -> bool:
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


def touch_admin(sid: str | None) -> None:
    if not sid:
        return
    with state_lock:
        if ACTIVE_ADMIN["sid"] == sid:
            ACTIVE_ADMIN["ts"] = time.time()


def touch_viewer(user: str | None, sid: str | None, email: str = "", name: str = "") -> None:
    if not sid:
        return
    with state_lock:
        v = _VIEWERS.get(sid) or {"first": time.time()}
        v.update(user=user, email=email or v.get("email", ""), name=name or v.get("name", ""), ts=time.time())
        _VIEWERS[sid] = v


def drop_viewer(sid: str) -> None:
    with state_lock:
        _VIEWERS.pop(sid, None)


def viewer_count() -> int:
    now = time.time()
    with state_lock:
        for k in [k for k, v in _VIEWERS.items() if now - v["ts"] > VIEWER_TIMEOUT]:
            _VIEWERS.pop(k, None)
        return len(_VIEWERS)


def live_viewers() -> list[dict]:
    """Alunos conectados agora (nome + e-mail), para o Professor ver quem é quem."""
    now = time.time()
    out = []
    with state_lock:
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
        raise HTTPException(status_code=403, detail=srv_msg("guest_403", req_lang(request)))
    if not is_active_admin(user, sid):
        raise HTTPException(
            status_code=409,
            detail=srv_msg("seat_lost_409", req_lang(request)),
        )
    touch_admin(sid)
    return user


def stream_command(cmd: list[str], cwd: Path, env: dict | None = None, lang: str = "pt") -> Iterator[str]:
    # LAB_LANG: os scripts (testlog.sh) traduzem a própria saída fixa por ele.
    full_env = dict(env) if env is not None else dict(os.environ)
    full_env["LAB_LANG"] = lang
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=full_env,
    )
    assert process.stdout is not None
    yield f"$ {' '.join(cmd)}  ({srv_msg('in_dir', lang)} {cwd})\n\n"
    for line in process.stdout:
        yield line
    process.wait()
    yield f"\n[{srv_msg('proc_end', lang)} {process.returncode}]\n"


# HTML sempre com no-cache: sem isso o navegador aplica cache heurístico e
# segura versões velhas do painel depois de cada deploy (o professor via bugs
# já corrigidos). no-cache = revalida a cada load (304 quando não mudou).
NO_CACHE = {"Cache-Control": "no-cache, must-revalidate"}


# ---- página HTML com o cache-buster resolvido -----------------------------
# `?v=%VER%` nas páginas vira `?v=<VERSION>` aqui. Antes cada página carregava
# um número escrito à mão, e eles se separaram: o painel pedia o tokens.css da
# 0.75.0 quando o projeto já estava na 0.80.3, e o navegador — que cacheia
# /static normalmente — continuava servindo a folha antiga. A tela "não mudava"
# depois do deploy, e não havia como saber olhando.
_PAG_CACHE: dict = {}


def pagina(caminho) -> HTMLResponse:
    """Serve um HTML trocando %VER% pela versão. Relê só quando o arquivo muda."""
    chave = str(caminho)
    mtime = caminho.stat().st_mtime
    guardado = _PAG_CACHE.get(chave)
    if not guardado or guardado[0] != mtime:
        html = caminho.read_text(encoding="utf-8").replace("%VER%", VERSION)
        _PAG_CACHE[chave] = (mtime, html)
        guardado = _PAG_CACHE[chave]
    return HTMLResponse(guardado[1], headers=NO_CACHE)

# ---- i18n do servidor (F5): idioma vem do cookie que o painel grava ----
LANGS = ("pt", "en", "es", "fr")
SRV_MSG = {
    "guest_403": {
        "pt": "Aluno só pode visualizar, não executar comandos.",
        "en": "Students can only watch, not run commands.",
        "es": "El alumno solo puede ver, no ejecutar comandos.",
        "fr": "L'étudiant peut seulement regarder, pas exécuter de commandes.",
    },
    "seat_lost_409": {
        "pt": "Sua sessão de professor não está ativa (outro professor assumiu ou ela expirou). Recarregue e entre de novo.",
        "en": "Your professor session is not active (another professor took over or it expired). Reload and sign in again.",
        "es": "Tu sesión de profesor no está activa (otro profesor la asumió o expiró). Recarga y entra de nuevo.",
        "fr": "Votre session de professeur n'est pas active (un autre professeur a pris la main ou elle a expiré). Rechargez et reconnectez-vous.",
    },
    "not_auth_401": {
        "pt": "Não autenticado.",
        "en": "Not authenticated.",
        "es": "No autenticado.",
        "fr": "Non authentifié.",
    },
    "bad_credentials_401": {
        "pt": "Usuário ou senha inválidos.",
        "en": "Invalid username or password.",
        "es": "Usuario o contraseña inválidos.",
        "fr": "Utilisateur ou mot de passe invalide.",
    },
    "seat_taken_409": {
        "pt": "Já há um professor conectado ({user}) e a vaga é única. Entre como aluno para acompanhar a aula ao vivo — ou peça para o professor sair (logout) para liberar a vaga.",
        "en": "A professor is already connected ({user}) and there is a single slot. Join as a student to watch the class live — or ask the professor to sign out to free the slot.",
        "es": "Ya hay un profesor conectado ({user}) y el puesto es único. Entra como alumno para seguir la clase en vivo — o pídele al profesor que salga para liberar el puesto.",
        "fr": "Un professeur est déjà connecté ({user}) et la place est unique. Entrez comme étudiant pour suivre le cours en direct — ou demandez au professeur de se déconnecter.",
    },
    "proc_end": {
        "pt": "processo encerrado, exit code",
        "en": "process finished, exit code",
        "es": "proceso terminado, exit code",
        "fr": "processus terminé, exit code",
    },
    "in_dir": {"pt": "em", "en": "in", "es": "en", "fr": "dans"},
    "unknown_cmd": {
        "pt": "Comando desconhecido",
        "en": "Unknown command",
        "es": "Comando desconocido",
        "fr": "Commande inconnue",
    },
}


def req_lang(request: Request) -> str:
    lang = request.cookies.get("c5g-lang", "pt")
    return lang if lang in LANGS else "pt"


def srv_msg(key: str, lang: str, **params: str) -> str:
    return SRV_MSG[key].get(lang, SRV_MSG[key]["pt"]).format(**params)


# Roster de presença: cada entrada de Aluno é registrada (append) num arquivo
# fora da árvore do deploy — o "controle unitário" da turma (quem é quem),
# disponível para atividades futuras. É dado pessoal: fica só no servidor.
ROSTER_FILE = RESULTS_DIR / "_roster.jsonl"


def record_attendance(name: str, email: str) -> None:
    try:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        with ROSTER_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": round(time.time(), 1), "name": name, "email": email}, ensure_ascii=False) + "\n")
    except OSError:
        pass
