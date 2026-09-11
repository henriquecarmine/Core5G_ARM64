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

- o gateway publica só `127.0.0.1:8443` (acesso por túnel SSH), e não 80/443/4334/4335;
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

## Operação

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

As URLs usam o nome do serviço na porta 443 (inclusive o redirecionamento do
login para o Keycloak), então o túnel precisa ocupar a 443 da máquina local:

```bash
sudo ssh -i <chave> -L 443:127.0.0.1:8443 ubuntu@core5g-arm64.duckdns.org
```

e, no `/etc/hosts` da máquina local:

```text
127.0.0.1  odlux.oam.smo.o-ran-sc.org identity.smo.o-ran-sc.org kafka-ui.smo.o-ran-sc.org gateway.smo.o-ran-sc.org
```

Depois: `https://odlux.oam.smo.o-ran-sc.org` (certificado autoassinado).

## Limites

- As senhas são as padrão do upstream (públicas). Por isso nada é publicado fora
  do localhost.
- O gNB OAI monolítico não tem O1: a O1 é demonstrada com os simuladores.
- Não roda junto com a pilha do P2 (OAI + RIC): memória. O upstream testou em
  4 núcleos, 16 GB e 50 GB de disco, o mesmo porte deste servidor.
