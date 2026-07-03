#!/usr/bin/env python3
"""Verificador de paridade das TRADUÇÕES de documentação (docs/i18n/<lang>/).

Convenções que ele fiscaliza:
- Cada arquivo traduzido espelha um canônico em pt. O caminho relativo dentro
  de docs/i18n/<lang>/ é resolvido tentando, nesta ordem:
    1. <raiz>/<rel>            (docs da raiz, ex.: core5g-arm64-bible.md)
    2. <raiz>/docs/<rel>       (docs de docs/, ex.: POLITICA-DE-CUSTOS.md, labs/…)
  Arquivo sem canônico correspondente = ÓRFÃO (erro).
- Toda tradução começa com o cabeçalho de sincronização:
      > ... synced with commit `<hash>` ...
  Se o canônico tiver commits mais novos que o hash citado, a tradução está
  DEFASADA (erro — atualize a tradução e o hash, ou abra issue "tradução
  pendente" e cite-a no cabeçalho com `outdated-ok: #<issue>`).
- READMEs traduzidos da raiz (README.en.md etc.) são verificados também.

Uso: python3 docs/i18n/check-parity.py   (na raiz do repo; CI-friendly)
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
I18N = ROOT / "docs" / "i18n"
LANGS = ["en", "es", "fr"]
# Marcador independente de idioma (preferido): <!-- sync: <hash|vX.Y.Z> -->
# Fallback: prosa em inglês "synced with commit `<hash>`".
SYNC_RE = re.compile(
    r"<!--\s*sync:\s*(?:v[\d.]+|([0-9a-f]{7,40}))\s*-->"
    r"|synced?\s+with\s+(?:commit\s+)?`?(?:v[\d.]+|([0-9a-f]{7,40}))`?", re.I)
OK_RE = re.compile(r"outdated-ok:\s*#\d+")

errors, notes = [], []


def canonical_for(rel: Path):
    for cand in (ROOT / rel, ROOT / "docs" / rel):
        if cand.is_file():
            return cand
    return None


def last_commit(path: Path) -> str:
    out = subprocess.run(["git", "log", "-1", "--format=%H", "--", str(path)],
                         capture_output=True, text=True, cwd=ROOT)
    return out.stdout.strip()


def is_ancestor(a: str, b: str) -> bool:
    """True se a é ancestral de (ou igual a) b."""
    r = subprocess.run(["git", "merge-base", "--is-ancestor", a, b],
                       capture_output=True, cwd=ROOT)
    return r.returncode == 0


def check(translated: Path, canonical: Path, label: str):
    head = translated.read_text(errors="replace")[:600]
    m = SYNC_RE.search(head)
    if not m:
        errors.append(f"{label}: sem cabeçalho de sincronização ('synced with commit `<hash>`')")
        return
    cited = m.group(1) or m.group(2)
    canon_last = last_commit(canonical)
    if not canon_last:
        notes.append(f"{label}: canônico sem histórico git (novo?)")
        return
    if cited is None:
        # Cabeçalho cita versão (vX.Y.Z) em vez de hash — aceito para READMEs,
        # mas sem checagem automática de defasagem.
        notes.append(f"{label}: cita versão (sem hash) — defasagem não verificável automaticamente")
        return
    if not is_ancestor(canon_last, cited) and not is_ancestor(cited, canon_last):
        errors.append(f"{label}: hash citado ({cited[:8]}) não pertence ao histórico")
    elif cited != canon_last and not canon_last.startswith(cited):
        if is_ancestor(cited, canon_last) and not OK_RE.search(head):
            errors.append(f"{label}: DEFASADA — canônico avançou até {canon_last[:8]} (citado: {cited[:8]})")


def main():
    # 1) árvore docs/i18n/<lang>/
    coverage = {}
    for lang in LANGS:
        base = I18N / lang
        files = [p for p in base.rglob("*.md") if p.name != "INDEX.md"] if base.is_dir() else []
        coverage[lang] = len(files)
        for f in files:
            rel = f.relative_to(base)
            canon = canonical_for(rel)
            if canon is None:
                errors.append(f"{lang}/{rel}: ÓRFÃO — nenhum canônico em <raiz>/{rel} nem docs/{rel}")
            else:
                check(f, canon, f"{lang}/{rel}")

    # 2) READMEs da raiz
    for lang in LANGS:
        t = ROOT / f"README.{lang}.md"
        if t.is_file():
            check(t, ROOT / "README.md", f"README.{lang}.md")
            coverage[lang] += 1
        else:
            notes.append(f"README.{lang}.md ausente")

    print("== Paridade de documentação i18n ==")
    for lang in LANGS:
        print(f"  {lang}: {coverage[lang]} documento(s) traduzido(s)")
    for n in notes:
        print("  nota:", n)
    for e in errors:
        print("  ERRO:", e)
    if not errors:
        print("  OK — sem órfãos e sem traduções defasadas")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
