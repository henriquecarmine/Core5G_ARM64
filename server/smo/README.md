# smo/ — SMO do O-RAN SC (OAM) em ARM64 nativo

Service Management and Orchestration da O-RAN Software Community: a solução
docker compose do repositório [`o-ran-sc/oam`](https://github.com/o-ran-sc/oam)
(`solution/`), rodando no Graviton. É a ferramenta estudada na cadeira de
Gestão, Orquestração e Automação em Redes OpenRAN
([pdfs/04-gestao-orquestracao](../../pdfs/04-gestao-orquestracao/README.md)).

```bash
./build_arm64.sh     # constrói as imagens que só existem em amd64 (1ª vez: ~15–25 min)
./up_smo.sh          # common → usuários no Keycloak → oam → simuladores
./down_smo.sh        # derruba na ordem inversa (--limpar apaga a cópia de trabalho)
```

## O que roda

| Camada | Contêiner | Papel no SMO | Imagem |
|---|---|---|---|
| common | `gateway` | Traefik: termina HTTPS e o NETCONF call home | oficial multi-arch |
| common | `identity`, `identitydb` | Keycloak + PostgreSQL: usuários e papéis | oficial multi-arch |
| common | `persistence` | MariaDB do controlador | oficial multi-arch |
| common | `zookeeper`, `kafka`, `kafka-bridge`, `kafka-ui` | barramento de mensagens | oficial multi-arch |
| common | `topology` | servidor de topologia (NTSim-NG + OpenDaylight, TAPI) | **compilada aqui** |
| oam | `controller` | SDN-R / OpenDaylight: cliente NETCONF da O1 | **troca de base aqui** |
| oam | `odlux` | interface web do controlador | **troca de base aqui** |
| oam | `ves-collector` | recebe eventos VES (falhas, medidas, notificações) | **troca de base aqui** |
| network | `pynts-o-du-o1` | simulador de O-DU com O1 | **compilada aqui** |
| network | `pynts-o-ru-hybrid`, `pynts-o-ru-hierarchical` | simuladores de O-RU (M-plane do Open Fronthaul) | **compilada aqui** |

## Por que há build

As imagens do O-RAN SC para o SMO são publicadas só para amd64 (verificado
com `skopeo inspect` em 11/09/2026). Duas estratégias:

- **Troca de base** (`Dockerfile.sdnr`, `Dockerfile.sdnr-web`, `Dockerfile.ves`):
  controlador, web e VES são Java ou arquivos estáticos sobre uma base x86. O
  Dockerfile copia os diretórios da aplicação da imagem oficial (só `COPY`,
  nada amd64 é executado) para a mesma família de base em aarch64.
- **Compilação da fonte**: topologia e simuladores têm binários C (libyang,
  sysrepo, libnetconf2, netopeer2, ntsim-ng). Usa os Dockerfiles do próprio
  O-RAN SC, cujas bases Ubuntu são multi-arch.

Versões fixadas no `build_arm64.sh`: controlador 13.0.1, VES 1.12.5, NTSim-NG
1.5.2 (as que o compose do `oam` referencia), `oam` @ `bfdfa32`, pynts @ `1212417`.

## Ajustes para este servidor

O upstream supõe uma VM dedicada. Aqui o host já usa 80/443 (Caddy do painel),
então:

- o gateway publica só `127.0.0.1:8443`, e não 80/443/4334/4335; quem fala com a
  internet é o Caddy do painel (ver *Acesso pelo navegador*);
- a rede `dcn` ganha uma sub-rede IPv4 e o gateway o IP fixo `10.250.50.10`, que
  ocupa o lugar do IP do host na configuração: é por ele que simuladores e
  controlador chegam ao Traefik;
- o gateway também ganha IP fixo na rede `dmz` (`10.250.51.10`); controlador e
  kafka-ui acham `identity.<domínio>` por esses IPs, já que não há o DNS do upstream;
- o script de realm do Keycloak roda num contêiner na rede `dmz`.

Tudo isso está em `smo.env` e `compose/*.override.yaml`; os arquivos do upstream
não são editados (a cópia de trabalho em `run/solution` é gerada pelo `up_smo.sh`).

## Problemas encontrados na montagem (11/09/2026)

Nenhum deles é de ARM64: todos apareceriam num x86 com o mesmo software de hoje.

| Sintoma | Causa | Correção |
|---|---|---|
| topologia `unhealthy`, RESTCONF não abre; `karaf.log`: `Invalid CEN header` | o OpenJDK 11 atual do Ubuntu 20.04 valida o campo extra ZIP64 dos jars (JDK-8302483, desde 11.0.20); os jars do Karaf 4.3.3 / OpenDaylight 15.1.0 não passam. A imagem oficial de 2023 tinha um JDK anterior | `EXTRA_JAVA_OPTS=-Djdk.util.zip.disableZip64ExtraFieldValidation=true` embutido na imagem (`build_arm64.sh`) |
| tudo no gateway responde 404; OAuth do controlador falha (`Unable to configure OAuth service`), kafka-ui cai | o Traefik v3.3.6 fixa a API 1.24 do Docker; o Docker 29 aceita a partir da 1.40 (`client version 1.24 is too old`) e o Traefik fica sem rotas. `DOCKER_API_VERSION` não tem efeito nessa versão | Traefik `v3.6.25`, que negocia a versão (`TRAEFIK_IMAGE` em `smo.env`) |
| `identity/config.py` cai com `getpwuid(): uid not found` | o script cria um usuário com o nome do usuário Unix, e o UID do host não existe no contêiner | `USER` passado ao contêiner (`up_smo.sh`) |

### Na troca para o domínio público (11/09/2026)

| Sintoma | Causa | Correção |
|---|---|---|
| controlador `unhealthy`, ODLUX não sobe | com o E2 lab do P2 ligado (carga 11–15 em 4 vCPU), a instalação de certificados levou 210 s e o healthcheck desistiu antes de a porta 8181 abrir | esperar ficar saudável e rodar `./up_smo.sh` de novo (idempotente) |
| login do ODLUX ainda mandava para `identity.smo.o-ran-sc.org` | o `oauth-provider.config.json` é montado da cópia de trabalho com o domínio fixo; `sed -i` por dentro dá `Resource busy`, e por fora troca o inode que o contêiner prende | a troca de domínio cobre os arquivos montados e reescreve o conteúdo no mesmo arquivo |
| kafka-ui cai com `PKIX path building failed` | para os nomes novos o Traefik servia o certificado genérico dele | o autoassinado do upstream vira `defaultCertificate` (`up_smo.sh`) |
| kafka-ui cai com `Unable to resolve Configuration with the provided Issuer` | a descoberta OIDC confere o nome do certificado | kafka-ui vai ao Keycloak pelo Caddy (`compose/common.override.yaml`) |
| público responde 404 em tudo | o Caddy mandava ao Traefik o Host do upstream (127.0.0.1) | `header_up Host {host}` |
| `up_smo.sh` sai com 1 sem escrever nada | sem ocorrência do domínio antigo, o `grep` sai com 1 e o `pipefail` encerra o script | `{ grep … \|\| true; }` |
| gateway e kafka-ui perderiam os certificados | a troca ampla reescreveu também `certs-selfsigned/smo.o-ran-sc.org.crt` no compose | linhas com `certs-selfsigned/` ficam como estão |

## Operação

- `./smo_ao_vivo.sh` imprime o retrato do SMO em JSON (elementos sob gerência,
  conexões, alarmes, barramento Kafka, contêineres). É o que o painel mostra no
  modal **SMO ao vivo** (cadeira 5, ou `/smo`), sem túnel. Só leitura; ~3 s.
- `./test_smo.sh` confere o SMO pelo gateway e serve de evidência: realm do
  Keycloak, controlador pronto, nós NETCONF conectados (O-DU com 154 e O-RU com
  114 capacidades YANG em 11/09/2026), heartbeat aceito pelo VES (202) e
  publicado no Kafka, registro de PNF dos simuladores.
- O O-RU `hierarchical` não aparece no controlador, e isso é esperado: no modelo
  hierárquico do M-plane o O-RU é gerenciado pelo O-DU, e só o `hybrid` fala
  direto com o SMO.
- Os simuladores fazem call home só ao iniciar. Se o controlador reiniciar,
  rode `./up_smo.sh network` (recria só os simuladores).
- Para recriar um serviço isolado, use `--no-deps`: `--force-recreate` sozinho
  recria também as dependências (o odlux derruba o controlador junto).

### Acesso pelo navegador

O console abre direto, sem túnel nem nada instalado na máquina de quem acessa:
**https://odlux.oam.smo.core5g-arm64.duckdns.org** (login em
`identity.smo.core5g-arm64.duckdns.org`, certificado válido).

- `HTTP_DOMAIN` em `smo.env` é subdomínio do host do painel, e o DuckDNS resolve
  qualquer nível abaixo dele. O `up_smo.sh` troca o domínio de exemplo do
  upstream (`smo.o-ran-sc.org`) na cópia de trabalho: `.env`, realm do Keycloak
  e kafka-ui. Certificados autoassinados e READMEs ficam como estão.
- O `infra/server-bootstrap.sh` (roda a cada `./deploy.sh panel`) acrescenta ao
  Caddy só esses dois nomes, com proxy para o Traefik em `127.0.0.1:8443` e o
  `Host` original (o Traefik roteia pelo nome; sem `header_up Host {host}` tudo
  dava 404). O Caddy recusa:
  - **Basic auth**: o nginx do ODLUX repassa ao controlador tudo o que não é
    arquivo, e o RESTCONF aceita a senha padrão do admin;
  - o **formulário local do ODLUX** (`/oauth/login`), que emite token para o
    admin do controlador com essa mesma senha — em 11/09/2026 funcionou pela
    internet antes do bloqueio;
  - o `/admin` e o `/realms/master` do Keycloak.

  O login pelo Keycloak usa só `/oauth/providers`, `/oauth/login/identity` e
  `/oauth/redirect/identity`, e depois o console chama o RESTCONF com o token.
- Kafka-ui, painel do Traefik e VES não são publicados. Para eles, túnel SSH
  (`sudo ssh -i <chave, caminho absoluto> -L 443:127.0.0.1:8443 ubuntu@core5g-arm64.duckdns.org`)
  e os nomes `<serviço>.smo.core5g-arm64.duckdns.org` apontando para 127.0.0.1
  no `/etc/hosts`.
- O controlador continua indo ao Keycloak pelo gateway, pelo IP fixo. O
  certificado do gateway é o autoassinado do upstream, com o nome antigo (agora
  o padrão do Traefik para qualquer nome), e passa porque o controlador usa
  `trustAll`. O kafka-ui não aceitaria — a descoberta OIDC do Spring confere o
  nome, e o `disableHostnameVerification` do upstream só vale para o cliente
  HTTP do JDK —, então vai ao Keycloak pelo Caddy, com o truststore padrão da JVM
  (`compose/common.override.yaml`).

**Quem entra.** O `smo_acesso_web.sh` (idempotente; o `up_smo.sh` roda no fim do
smo/common) fecha o realm `onap` antes de ele ir para a internet. Encontrado em
11/09/2026: auto-cadastro aberto, "esqueci a senha" ligado sem e-mail, sem
proteção contra força bruta e seis usuários ativos — os cinco do upstream, com a
senha pública `Default4SDN!`, e o que o `config.py` cria com o nome do usuário
Unix. Agora cadastro e recuperação estão desligados, a força bruta protegida, os
endereços de retorno do login seguem o domínio novo e só um operador fica ativo
(`martin.skorupski`, papel `administration`), com senha forte gerada uma vez e
guardada em `server/smo/.odlux-acesso` (fora do git). Os testes do painel não
usam usuários do Keycloak: vão ao controlador por dentro, com o `ADMIN_USERNAME`
de `smo/oam/.env`.

ODLUX e Keycloak mandam `X-Frame-Options: SAMEORIGIN` e
`frame-ancestors 'self'`: não abrem dentro de um iframe do painel. Para a turma,
o painel tem o **SMO ao vivo** (só leitura, mesmos dados).

## Limites

- Fora o operador do ODLUX, as senhas continuam as padrão do upstream (admin do
  Keycloak, controlador, VES, bancos). Por isso só o console e o login vão para
  a internet, e o Caddy barra Basic auth e o admin do Keycloak.
- O gNB OAI monolítico não tem O1: a O1 é demonstrada com os simuladores.
- Não roda junto com a pilha do P2 (OAI + RIC): memória. O upstream testou em
  4 núcleos, 16 GB e 50 GB de disco, o mesmo porte deste servidor.
