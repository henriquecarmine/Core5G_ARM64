#!/bin/bash
# Build das imagens OAI 5G Core para linux/arm64 no Mac (Apple Silicon),
# exporta como .tar e carrega no servidor AWS ARM64.
# 6 imagens: AMF SMF NRF UDR UDM AUSF (oai-upf-vpp excluído: Intel-only)
#
# Uso: ./build-oai-arm64.sh [build|save|upload|load|all]
#   build   — compila as 6 imagens localmente
#   save    — exporta as imagens em .tar em /tmp/oai-images/
#   upload  — faz scp dos .tar pro servidor
#   load    — executa docker load no servidor para cada .tar
#   all     — executa tudo em sequência (padrão)

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "ERRO: .env não encontrado em $SCRIPT_DIR" >&2
  exit 1
fi
# shellcheck source=/dev/null
. "$ENV_FILE"

SSH_HOST="${AWS_SERVER_HOST}"
SSH_USER="${AWS_SERVER_USER:-ubuntu}"
SSH_KEY="$SCRIPT_DIR/${AWS_SSH_KEY_PATH#./}"

OAI_ROOT="$SCRIPT_DIR/server/oai-cn-gnb-e2/oai-cn5g-fed/component"
TAG="v1.5.1"
PLATFORM="linux/arm64"
OUT_DIR="/tmp/oai-images"
SSH_OPTS=(-i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=10)

# Lista de componentes (nome do diretório = nome da imagem = target do Dockerfile)
# oai-upf-vpp excluído: requer libhyperscan (Intel-only) e caminhos x86_64 hardcoded
COMPONENTS="oai-amf oai-smf oai-nrf oai-udr oai-udm oai-ausf"

do_build() {
  echo "════════════════════════════════════════════════════"
  echo "BUILD — 6 imagens OAI para $PLATFORM"
  echo "════════════════════════════════════════════════════"
  for comp in $COMPONENTS; do
    image="oaisoftwarealliance/$comp:$TAG"
    ctx="$OAI_ROOT/$comp"
    shortname="${comp#oai-}"   # remove prefixo "oai-" → amf, smf, upf-vpp, etc.
    dockerfile="$ctx/docker/Dockerfile.${shortname}.ubuntu"

    if [ ! -f "$dockerfile" ]; then
      echo "⚠  Dockerfile não encontrado: $dockerfile — pulando $comp"
      continue
    fi

    echo ""
    echo "▶ Building $image ..."
    docker build \
      --platform "$PLATFORM" \
      --build-arg BASE_IMAGE=ubuntu:focal \
      --target "$comp" \
      -t "$image" \
      -f "$dockerfile" \
      "$ctx"
    echo "✔ $image OK"
  done
  echo ""
  echo "Build concluído."
}

do_save() {
  echo "════════════════════════════════════════════════════"
  echo "SAVE — exportando imagens para $OUT_DIR"
  echo "════════════════════════════════════════════════════"
  mkdir -p "$OUT_DIR"
  for comp in $COMPONENTS; do
    image="oaisoftwarealliance/$comp:$TAG"
    tar_file="$OUT_DIR/${comp}.tar"
    echo "▶ Salvando $image → $tar_file ..."
    docker save "$image" -o "$tar_file"
    sz=$(du -sh "$tar_file" | cut -f1)
    echo "✔ $sz  $tar_file"
  done
  echo ""
  echo "Total em $OUT_DIR:"
  du -sh "$OUT_DIR"
}

do_upload() {
  echo "════════════════════════════════════════════════════"
  echo "UPLOAD — enviando .tar para $SSH_USER@$SSH_HOST"
  echo "════════════════════════════════════════════════════"
  for comp in $COMPONENTS; do
    tar_file="$OUT_DIR/${comp}.tar"
    if [ ! -f "$tar_file" ]; then
      echo "⚠  $tar_file não encontrado — rode './build-oai-arm64.sh save' primeiro"
      continue
    fi
    echo "▶ Enviando ${comp}.tar ..."
    scp "${SSH_OPTS[@]}" "$tar_file" "$SSH_USER@$SSH_HOST:~/"
    echo "✔ ${comp}.tar enviado"
  done
  echo ""
  echo "Upload concluído."
}

do_load() {
  echo "════════════════════════════════════════════════════"
  echo "LOAD — docker load no servidor"
  echo "════════════════════════════════════════════════════"
  for comp in $COMPONENTS; do
    echo "▶ Carregando ${comp}.tar ..."
    ssh "${SSH_OPTS[@]}" "$SSH_USER@$SSH_HOST" "docker load -i ~/${comp}.tar && rm ~/${comp}.tar"
    echo "✔ $comp carregado"
  done
  echo ""
  echo "Imagens no servidor:"
  ssh "${SSH_OPTS[@]}" "$SSH_USER@$SSH_HOST" "docker images | grep oaisoftwarealliance"
}

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
