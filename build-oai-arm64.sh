#!/usr/bin/env bash
# Build das imagens OAI 5G Core para linux/arm64 no Mac (Apple Silicon),
# exporta como .tar e carrega no servidor AWS ARM64.
#
# Uso: ./build-oai-arm64.sh [build|save|upload|load|all]
#   build   — compila as 7 imagens localmente
#   save    — exporta as imagens em .tar na pasta /tmp/oai-images/
#   upload  — faz scp dos .tar pro servidor (~/ )
#   load    — executa docker load no servidor para cada .tar
#   all     — executa tudo em sequência (padrão se nenhum argumento)
#
# Requer: Docker Desktop rodando com suporte arm64, ssh/scp com .pem

set -euo pipefail

# ── Configuração ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERRO: .env não encontrado em $SCRIPT_DIR" >&2
  exit 1
fi
source "$ENV_FILE"

SSH_HOST="${AWS_SERVER_HOST}"
SSH_USER="${AWS_SERVER_USER:-ubuntu}"
SSH_KEY="$SCRIPT_DIR/${AWS_SSH_KEY_PATH#./}"

OAI_ROOT="$SCRIPT_DIR/server/oai-cn-gnb-e2/oai-cn5g-fed/component"
TAG="v1.5.1"
PLATFORM="linux/arm64"
OUT_DIR="/tmp/oai-images"
SSH_OPTS="-i $SSH_KEY -o StrictHostKeyChecking=no -o ConnectTimeout=10"

# 7 imagens: nome do componente → target no Dockerfile → nome da imagem
declare -A COMPONENTS=(
  [oai-amf]="oai-amf"
  [oai-smf]="oai-smf"
  [oai-nrf]="oai-nrf"
  [oai-udr]="oai-udr"
  [oai-udm]="oai-udm"
  [oai-ausf]="oai-ausf"
  [oai-upf-vpp]="oai-upf-vpp"
)

# ── Funções ───────────────────────────────────────────────────────────────────
do_build() {
  echo "════════════════════════════════════════════════════════"
  echo "BUILD — 7 imagens OAI para $PLATFORM"
  echo "════════════════════════════════════════════════════════"
  for comp in "${!COMPONENTS[@]}"; do
    target="${COMPONENTS[$comp]}"
    image="oaisoftwarealliance/$comp:$TAG"
    ctx="$OAI_ROOT/$comp"
    dockerfile="$ctx/docker/Dockerfile.${comp}.ubuntu"

    if [[ ! -f "$dockerfile" ]]; then
      echo "⚠  Dockerfile não encontrado: $dockerfile — pulando $comp"
      continue
    fi

    echo ""
    echo "▶ Building $image ..."
    docker build \
      --platform "$PLATFORM" \
      --target "$target" \
      -t "$image" \
      -f "$dockerfile" \
      "$ctx"
    echo "✔ $image OK"
  done
  echo ""
  echo "Build concluído."
}

do_save() {
  echo "════════════════════════════════════════════════════════"
  echo "SAVE — exportando imagens para $OUT_DIR"
  echo "════════════════════════════════════════════════════════"
  mkdir -p "$OUT_DIR"
  for comp in "${!COMPONENTS[@]}"; do
    image="oaisoftwarealliance/$comp:$TAG"
    tar_file="$OUT_DIR/${comp}.tar"
    echo "▶ Salvando $image → $tar_file ..."
    docker save "$image" -o "$tar_file"
    echo "✔ $(du -sh "$tar_file" | cut -f1)  $tar_file"
  done
  echo ""
  echo "Imagens salvas em $OUT_DIR"
}

do_upload() {
  echo "════════════════════════════════════════════════════════"
  echo "UPLOAD — enviando .tar para $SSH_USER@$SSH_HOST:~/"
  echo "════════════════════════════════════════════════════════"
  for comp in "${!COMPONENTS[@]}"; do
    tar_file="$OUT_DIR/${comp}.tar"
    if [[ ! -f "$tar_file" ]]; then
      echo "⚠  $tar_file não encontrado — rode './build-oai-arm64.sh save' primeiro"
      continue
    fi
    echo "▶ Enviando $tar_file ..."
    scp $SSH_OPTS "$tar_file" "$SSH_USER@$SSH_HOST:~/"
    echo "✔ ${comp}.tar enviado"
  done
  echo ""
  echo "Upload concluído."
}

do_load() {
  echo "════════════════════════════════════════════════════════"
  echo "LOAD — executando docker load no servidor"
  echo "════════════════════════════════════════════════════════"
  for comp in "${!COMPONENTS[@]}"; do
    echo "▶ Carregando ${comp}.tar no servidor ..."
    ssh $SSH_OPTS "$SSH_USER@$SSH_HOST" "docker load -i ~/${comp}.tar && rm ~/${comp}.tar"
    echo "✔ $comp carregado"
  done
  echo ""
  # Confirma que as imagens estão disponíveis
  echo "Imagens disponíveis no servidor:"
  ssh $SSH_OPTS "$SSH_USER@$SSH_HOST" "docker images | grep oaisoftwarealliance"
}

# ── Main ──────────────────────────────────────────────────────────────────────
CMD="${1:-all}"
case "$CMD" in
  build)  do_build ;;
  save)   do_save ;;
  upload) do_upload ;;
  load)   do_load ;;
  all)
    do_build
    do_save
    do_upload
    do_load
    ;;
  *)
    echo "Uso: $0 [build|save|upload|load|all]"
    exit 1
    ;;
esac
