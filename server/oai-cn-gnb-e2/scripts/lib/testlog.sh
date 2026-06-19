# shellcheck shell=bash
# testlog.sh — colorimetria ISO/ANSI + resumo didático, compartilhado por
# todos os testes do painel. O painel converte os códigos ANSI em cor; num
# terminal comum também renderiza. Minimalista e consistente.
#
# Uso:
#   source "$(dirname "${BASH_SOURCE[0]}")/lib/testlog.sh"
#   section "Título"; ok "deu certo"; warn "atenção"; err "falhou"
#   info "informação"; step "passo"; kv "Rótulo" "valor"
#   summary "o que o teste fez" "veredito do resultado" ok|warn|err

# Paleta (SGR). Sempre emite ANSI (o painel não é TTY, mas renderiza ANSI).
_RST=$'\033[0m'; _B=$'\033[1m'; _DIM=$'\033[90m'
_RED=$'\033[31m'; _GRN=$'\033[32m'; _YEL=$'\033[33m'; _BLU=$'\033[34m'; _CYN=$'\033[36m'

section() { printf '\n%s%s── %s ──%s\n' "$_B" "$_CYN" "$1" "$_RST"; }
ok()      { printf '%s✓%s %s\n' "$_GRN" "$_RST" "$1"; }
warn()    { printf '%s!%s %s\n' "$_YEL" "$_RST" "$1"; }
err()     { printf '%s✗%s %s\n' "$_RED" "$_RST" "$1"; }
info()    { printf '%s•%s %s\n' "$_BLU" "$_RST" "$1"; }
step()    { printf '%s→%s %s\n' "$_CYN" "$_RST" "$1"; }
kv()      { printf '  %s%-22s%s %s\n' "$_DIM" "$1" "$_RST" "$2"; }

# Resumo didático padronizado: o que o teste fez + veredito colorido.
#   $1 = explicação (o que o teste fez)
#   $2 = veredito (resultado em uma frase)
#   $3 = status: ok | warn | err  (cor do veredito)
summary() {
    local what="$1" verdict="$2" status="${3:-ok}" color="$_GRN"
    case "$status" in warn) color="$_YEL" ;; err) color="$_RED" ;; esac
    printf '\n%s%s── Resumo ──%s\n' "$_B" "$_CYN" "$_RST"
    printf '  %sO que fez:%s %s\n' "$_B" "$_RST" "$what"
    printf '  %sResultado:%s %s%s%s\n' "$_B" "$_RST" "$color" "$verdict" "$_RST"
}
