# nonrt-ric/ — Non-RT RIC em ARM64 nativo (par mínimo A1)

O que não existia na pilha ([docs/non-rt-ric.md](../../docs/non-rt-ric.md)):
a camada **Non-RT**, bloqueada porque as imagens O-RAN SC são amd64. Aqui ela
é **construída da fonte, nativamente, no Graviton**: A1 Policy Management
Service (Java, tag 2.9.0) + A1 Simulator (Python, tag 2.8.0) — o layout da
**Fase 1 do lab do Prof. Kunzler** (mesmos nomes de serviço, rede e testdata).

```bash
./build_arm64.sh     # clona fontes pinadas + docker build (1ª vez: ~5–10 min)
./up_nonrt.sh        # PMS :8081 + a1-sim OSC/STD/STD-v2 :30001–30006
./test_a1_flow.sh    # smoke: política criada no PMS e verificada no simulador
./down_nonrt.sh
```

Passo a passo completo, decisões e limites:
**[docs/instalacao-nonrt-arm64.md](../../docs/instalacao-nonrt-arm64.md)**.

| Arquivo | Papel |
|---|---|
| `Dockerfile.a1pms` | Build 3 estágios (Maven → jlink → debian-slim), UID 1000 |
| `build_arm64.sh` | Clona fontes por tag e constrói as 2 imagens |
| `docker-compose.yml` | PMS + 3 simuladores (espelho da Fase 1 do docente) |
| `application_configuration.json` | ric1/2/3 → simuladores (managedElement `oai_gnb_lab`) |
| `testdata/` | policy type do docente + service/política do smoke |

> **Limite arquitetural** (inalterado): o FlexRIC não tem terminação A1, então
> esta camada conversa com os simuladores, não com o gNB real. Fechar a ponta
> = Fase 2 do docente (near-RT O-RAN SC com A1 Mediator).
