#!/usr/bin/env bash
# Fecha o Keycloak do SMO antes de o console ir para a internet (o Caddy do
# painel publica o ODLUX e o login: ver infra/server-bootstrap.sh). Idempotente;
# o up_smo.sh roda no fim do smo/common, e dá para rodar sozinho.
#
#   1. Os endereços de retorno do login seguem o domínio do SMO (smo.env): o
#      realm foi importado uma vez com o domínio de exemplo do upstream.
#   2. Realm onap sem auto-cadastro nem "esqueci a senha" (não há e-mail), e com
#      proteção contra força bruta. Em 11/09/2026 o cadastro estava aberto.
#   3. Um único operador ativo (papel administration). Usuário e senha vêm de
#      .odlux-acesso (fora do git); sem o arquivo, gera uma senha forte para o
#      martin.skorupski do upstream. Um operador que ainda não existe no realm é
#      criado, com o perfil preenchido para o Keycloak não pedir atualização no
#      primeiro login. Os outros usuários — os do upstream, com a senha pública
#      Default4SDN!, e o que o config.py cria com o nome do usuário Unix — ficam
#      desativados.
set -euo pipefail
cd "$(dirname "$0")"
. ./lib.sh

ACESSO=.odlux-acesso
if [ ! -f "$ACESSO" ]; then
    ( umask 077
      printf 'ODLUX_USUARIO=martin.skorupski\nODLUX_SENHA=%s\n' "$(openssl rand -base64 30 | tr -dc 'A-Za-z0-9' | cut -c1-20)" > "$ACESSO" )
fi
. "./$ACESSO"

# kcadm dentro do contêiner do Keycloak: a senha do admin não sai de lá.
docker exec -i -e DOM="$HTTP_DOMAIN" -e OP="$ODLUX_USUARIO" -e SENHA="$ODLUX_SENHA" identity sh -s <<'KC'
set -e
K=/opt/bitnami/keycloak/bin/kcadm.sh
# config própria de cada execução: duas rodando juntas (uma que parecia morta
# pelo timeout do ssh) apagavam a config uma da outra — "No server specified"
C="$(mktemp /tmp/kcadm-core5g.XXXXXX)"
trap 'rm -f "$C"' EXIT
$K config credentials --server http://localhost:8080 --realm master \
    --user "$KC_BOOTSTRAP_ADMIN_USERNAME" --password "$KC_BOOTSTRAP_ADMIN_PASSWORD" --config "$C" >/dev/null
for par in odlux.app:odlux.oam kafka-ui.app:kafka-ui; do
    id="$($K get clients -r onap -q clientId="${par%%:*}" --fields id --format csv --noquotes --config "$C")"
    $K update "clients/$id" -r onap -s "redirectUris=[\"https://${par#*:}.$DOM/*\"]" --config "$C"
done
$K update realms/onap -s registrationAllowed=false -s resetPasswordAllowed=false -s bruteForceProtected=true --config "$C"
# administration é o papel de realm que o upstream dá aos seus administradores
if [ -z "$($K get users -r onap -q username="$OP" -q exact=true --fields id --format csv --noquotes --config "$C")" ]; then
    $K create users -r onap -s username="$OP" -s enabled=true -s firstName="$OP" -s lastName=SMO \
        -s email="$OP@smo.local" -s emailVerified=true --config "$C" >/dev/null
    $K add-roles -r onap --uusername "$OP" --rolename administration --config "$C"
    echo "operador $OP criado no realm onap (papel administration)"
fi
ativos=0
for u in $($K get users -r onap --fields username --format csv --noquotes --config "$C"); do
    id="$($K get users -r onap -q username="$u" -q exact=true --fields id --format csv --noquotes --config "$C")"
    if [ "$u" = "$OP" ]; then
        $K set-password -r onap --userid "$id" --new-password "$SENHA" --config "$C"
        $K update "users/$id" -r onap -s enabled=true -s 'requiredActions=[]' --config "$C"
        ativos=$((ativos + 1))
    else
        $K update "users/$id" -r onap -s enabled=false --config "$C"
    fi
done
[ "$ativos" = 1 ] || { echo "ERRO: operador $OP não existe no realm onap" >&2; exit 1; }
echo "Keycloak fechado: retorno em https://odlux.oam.$DOM · sem cadastro · força bruta protegida · só $OP ativo"
KC
echo "Credenciais do operador em server/smo/$ACESSO (fora do git)."
