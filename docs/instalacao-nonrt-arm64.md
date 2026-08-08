# Runbook — Non-RT RIC em ARM64 nativo (do zero ao A1 funcionando)

> Complementa o [non-rt-ric.md](non-rt-ric.md) (o diagnóstico: por que não
> existia e o que bloqueava). Este documento é o **como se faz**: cada passo,
> o que esperar de cada um, e como saber que deu certo. Artefatos em
> [`server/nonrt-ric/`](../server/nonrt-ric/).

## 0. Contexto em 30 segundos

- As 7 imagens do Non-RT RIC do O-RAN SC (Release K) são **amd64 puro** — não
  rodam no Graviton (§3 do non-rt-ric.md), e emular JVM via QEMU num box
  compartilhado seria caro demais.
- Mas os serviços são **Java e Python** — nada é específico de arquitetura. O
  bloqueio é só o CI deles, que não publica multi-arch.
- Solução: **construir da fonte, nativamente, no próprio servidor arm64** — o
  mesmo movimento que este projeto fez com a OAI.
- Escopo: o **par mínimo A1** (PMS + A1 Simulators), espelhando a **Fase 1 do
  lab do Prof. Kunzler** (`config/nonrtric/` no submódulo) — nomes de serviço,
  rede `oran-nonrt-net`, 3 sabores de simulador e testdata compatíveis.

## 1. Pré-requisitos

| Item | Como verificar | Esperado |
|---|---|---|
| Servidor arm64 | `uname -m` | `aarch64` |
| Docker + compose v2 | `docker compose version` | qualquer 2.x |
| Espaço em disco | `df -h /` | ≥ 3 GB livres (fontes + camadas + Maven cache) |
| Saída para internet | — | GitHub (fontes) + Docker Hub (bases) + Maven Central |
| Portas livres | `ss -ltn` | 8081 e 30001–30006 |

RAM em execução: ~400–600 MB (1 JVM com JRE jlink + 3 Flasks). Não subir
junto com o lab E2 sob carga num box de 2 vCPU — conferir a
[política de custos](POLITICA-DE-CUSTOS.md).

## 2. Levar os artefatos ao servidor

O diretório [`server/nonrt-ric/`](../server/nonrt-ric/) viaja com o deploy
normal do projeto:

```bash
./deploy.sh sync          # na máquina local (precisa do .env com AWS_*)
./deploy.sh ssh           # entra no servidor
```

(Sem o deploy: `scp -r server/nonrt-ric ubuntu@<host>:~/server/` faz o mesmo.)

## 3. Build nativo (1ª vez: ~5–10 min)

```bash
cd ~/server/nonrt-ric
./build_arm64.sh
```

O que acontece, na ordem:

1. **Clona as fontes pinadas** (shallow) em `src/`:
   `nonrtric-plt-a1policymanagementservice` tag **2.9.0** (a versão que já
   validamos ponta a ponta em x86 — §4.2 do non-rt-ric.md) e
   `sim-a1-interface` tag **2.8.0**.
2. **PMS**: build em 3 estágios no `Dockerfile.a1pms` —
   `maven:3.9-eclipse-temurin-17` compila o jar (é aqui que os minutos vão:
   Maven baixa as dependências na 1ª vez), `jlink` gera um JRE enxuto, e o
   runtime final é `debian:12-slim`. **Diferença deliberada da imagem
   oficial: usuário `nonrtric` com UID 1000** — o UID 120957 deles estoura a
   faixa de subuid de podman rootless (o obstáculo do §4.1).
3. **Simulador**: o Dockerfile oficial (`alpine:3.17`) já é multi-arch —
   build direto, sem modificação.

Sinal de sucesso: as duas imagens listadas ao final —
`core5g/nonrt-a1pms:2.9.0-arm64` e `core5g/nonrt-a1sim:2.8.0-arm64`.

Para trocar de versão no futuro:
`rm -rf src/ && PMS_TAG=2.13.0 SIM_TAG=2.8.1 ./build_arm64.sh` (e teste — o
2.9.0/2.8.0 é o par validado).

## 4. Subir

```bash
./up_nonrt.sh
```

Sobe pelo `docker-compose.yml`: **PMS** (`nonrt-policy-agent`, :8081) e os
**3 A1 Simulators** — `a1-sim-OSC` (:30001, A1 OSC_2.1.0), `a1-sim-STD`
(:30003, STD_1.1.3), `a1-sim-STD-v2` (:30005, STD_2.0.0) — na rede
`oran-nonrt-net`. O script espera o healthcheck do PMS (Spring Boot sobe em
~10–30 s no Graviton; healthcheck via `/dev/tcp` porque a imagem não tem
curl, herança do lab do docente).

O `application_configuration.json` (montado no PMS) declara ric1/2/3
apontando para os 3 simuladores, com `managedElementIds: [oai_gnb_lab]` —
idêntico ao do professor, então os roteiros dele funcionam aqui.

## 5. Provar que funciona — o smoke A1 ponta a ponta

```bash
./test_a1_flow.sh
```

O teste percorre o ciclo completo de política A1 e diz onde parou se falhar:

| Passo | O que prova |
|---|---|
| 1. `GET /a1-policy/v2/status` → `success` | PMS vivo |
| 2. `GET /a1-policy/v2/rics` lista ric1/2/3 | PMS enxerga os 3 "near-RT" |
| 3. `PUT /a1-p/policytypes/1` no a1-sim-OSC | policy type do docente carregado no simulador |
| 4. type "1" aparece no PMS (poll ≤ 90 s) | sincronização periódica nonRT ← nearRT |
| 5. `PUT /services` + `PUT /policies` no PMS | política criada **pela camada nonRT** |
| 6. política listada **no simulador** | ela desceu pelo **A1 de verdade** |
| 7. `DELETE` | ciclo completo, ambiente limpo |

Saída final esperada:
`✔ Caminho A1 completo: PMS (nonRT) → A1 → simulador (nearRT), em ARM64 nativo.`

## 5b. Alternativa: compilar no Mac (arm64) e transferir as imagens

Quando o servidor estiver desligado (política de custos) ou sem folga de CPU,
dá para construir **num Mac Apple Silicon** — mesma arquitetura — e levar as
imagens prontas. Runtime usado: **colima** (VM Linux arm64 leve, sem Docker
Desktop):

```bash
brew install colima docker
colima start --cpu 4 --memory 4 --disk 30
cd server/nonrt-ric
./build_arm64.sh                      # mesmas imagens, linux/arm64
./up_nonrt.sh && ./test_a1_flow.sh    # smoke completo LOCAL antes de subir
./down_nonrt.sh

# empacota (~200–400 MB) e transfere
mkdir -p dist
docker save core5g/nonrt-a1pms:2.9.0-arm64 | gzip > dist/nonrt-a1pms-2.9.0-arm64.tar.gz
docker save core5g/nonrt-a1sim:2.8.0-arm64 | gzip > dist/nonrt-a1sim-2.8.0-arm64.tar.gz
scp -i <chave.pem> dist/*.tar.gz ubuntu@<host>:~/server/nonrt-ric/dist/

# no servidor: carrega e sobe (sem compilar nada lá)
gunzip -c dist/nonrt-a1pms-2.9.0-arm64.tar.gz | docker load
gunzip -c dist/nonrt-a1sim-2.8.0-arm64.tar.gz | docker load
./up_nonrt.sh && ./test_a1_flow.sh
```

`docker save/load` preserva a imagem byte a byte — o que passou no smoke
local é o que roda no Graviton. (`colima stop` libera a RAM do Mac depois.)

> **Executado em 08/08/2026 (Mac M-series, colima 4 CPU/4 GB):** build OK após
> 2 ajustes de pipeline (suíte de testes exige S3 → `-Dmaven.test.skip=true`,
> registrados 232/233 testes passando em ARM64; fabric8 docker-maven-plugin →
> `-Ddocker.skip=true`) e **smoke A1 7/7 verde** — política criada no PMS e
> confirmada dentro do a1-sim-OSC. Tarballs: `dist/nonrt-a1pms-…tar.gz`
> (198 MB) + `dist/nonrt-a1sim-…tar.gz` (47 MB), prontos para o `scp`.

## 6. Operação

```bash
./down_nonrt.sh                       # para tudo (imagens ficam)
docker logs -f nonrt-policy-agent     # logs do PMS
docker compose ps                     # estado dos 4 containers
```

## 7. Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| Maven falha em `S3ObjectStoreTest` | o pom ignora `-DskipTests` e roda a suíte (233 testes); esse exige S3 | já resolvido no Dockerfile (`-Dmaven.test.skip=true`). Registro: 232/233 testes passaram em ARM64 nativo na 1ª tentativa |
| Maven falha baixando deps | sem saída p/ Maven Central | conferir rede/proxy; rerodar (cache retoma) |
| `COPY .../target/*.jar` não casa | build Maven falhou antes | ver log do estágio `build` |
| PMS `unhealthy` | config JSON inválida / porta ocupada | `docker logs nonrt-policy-agent`; `ss -ltn | grep 8081` |
| rics `UNAVAILABLE` no passo 2 | simuladores ainda subindo | aguardar ~30 s; `docker compose ps` |
| type não sincroniza (passo 4) | PUT do passo 3 falhou / rede | `curl localhost:30001/a1-p/policytypes` direto no sim |

## 8. Limites e próximos passos

- **O que isto entrega**: a camada Non-RT real (PMS de verdade, API
  `/a1-policy/v2`) + o ciclo A1 completo contra simuladores — autocontido,
  didático, e o *dry-run* do projeto da disciplina 03 pode apontar para um
  endpoint A1 real da casa.
- **O que NÃO entrega** (inalterado do non-rt-ric.md §5): integração com o
  gNB real — o FlexRIC não tem terminação A1. Fechar a ponta = **Fase 2 do
  docente** (`FASE2_ORAN_SC_A1.md`: near-RT O-RAN SC com `ric_a1mediator`,
  E2 na :36422, gNB `nr-softmodem-oran-sc`) — porte grande, avaliar depois.
- **Candidatos de próxima iteração**: gateway + control panel (Angular/nginx,
  mesmos moldes de build); testes `p3-*` no painel (camada operacional) com
  cena FlowStrip própria (`PMS → A1 → sim → 💾`); rApp Python do §6 do
  non-rt-ric.md apontando para este PMS.
