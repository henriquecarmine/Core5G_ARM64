# OAI 5G Core — Imagens arm64 pré-compiladas

Imagens Docker do OAI 5G Core Control Plane compiladas para `linux/arm64`
(Apple Silicon / AWS Graviton2). As imagens oficiais do DockerHub são
`amd64`-only; estes arquivos são o resultado do build nativo neste projeto.

## Download

Os `.tar` não estão versionados no Git (tamanho > 100 MB). Baixe o pacote completo
(**`oai_all_arm64.zip`** — as 7 imagens, ~500 MB) pelo Google Drive:

**[oai_all_arm64.zip — Google Drive](https://drive.google.com/file/d/1fPaqfkM7CzhliUmx8DzMD0kkD0-U3adg/view?usp=sharing)**

## Arquivos

| Arquivo | Componente | Função 3GPP | Tamanho |
|---|---|---|---|
| `oai-amf.tar` | oai-amf:v1.5.1 | Access and Mobility Management Function | ~63 MB |
| `oai-smf.tar` | oai-smf:v1.5.1 | Session Management Function | ~60 MB |
| `oai-nrf.tar` | oai-nrf:v1.5.1 | Network Repository Function | ~60 MB |
| `oai-udr.tar` | oai-udr:v1.5.1 | Unified Data Repository | ~61 MB |
| `oai-udm.tar` | oai-udm:v1.5.1 | Unified Data Management | ~59 MB |
| `oai-ausf.tar` | oai-ausf:v1.5.1 | Authentication Server Function | ~59 MB |
| `oai-upf-vpp.tar` | oai-upf-vpp:v1.5.1 | User Plane Function (dataplane VPP) | ~138 MB |

Cada `.tar` é gerado por `docker save` e contém todas as camadas da imagem
Docker final (binário do componente + bibliotecas `.so` mínimas, base Ubuntu
20.04). Não há compressão adicional — o formato é o padrão do Docker.

> **`oai_all_arm64.zip`** empacota **as 7 imagens** acima (6 do Control Plane +
> `oai-upf-vpp`) num único arquivo para distribuição. Descompacte e faça
> `docker load -i` em cada `.tar`.

## Como usar

```bash
# carregar uma imagem no Docker local:
docker load -i oai-amf.tar

# verificar que é realmente arm64:
docker run --rm oaisoftwarealliance/oai-amf:v1.5.1 uname -m
# esperado: aarch64

# enviar para um servidor e carregar lá:
scp -i sua-chave.pem oai-amf.tar ubuntu@<servidor>:~/
ssh -i sua-chave.pem ubuntu@<servidor> "docker load -i ~/oai-amf.tar && rm ~/oai-amf.tar"
```

## `oai-upf-vpp` em arm64 — portado com Vectorscan

O UPF-VPP era tido como "não portável" porque o plugin UPF da Travelping exige
**Hyperscan** (`libhs`), e o `libhyperscan-dev` upstream é **Intel-only**
(SSE/AVX), inexistente no Ubuntu arm64. A solução: o plugin usa
`pkg_check_modules(HS libhs)` — pkg-config puro — então o **[Vectorscan](https://github.com/VectorCamp/vectorscan)**
(fork portável do Hyperscan, ARM NEON 100% funcional, mesmo SONAME `libhs.so.5`)
é **drop-in**. Compilamos o Vectorscan no próprio Dockerfile e o VPP/plugin o
encontram automaticamente (`Found libhs, version 5.4.12`, GTP UPF habilitado).

Build via [`docker/Dockerfile.upf-vpp.ubuntu.arm64`](../../server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-upf-vpp/docker/Dockerfile.upf-vpp.ubuntu.arm64).
O lab principal continua usando o UPF do Open5GS (P1) e o `oai-upf` simple_switch
(P2, core v2.2.1); esta imagem fica disponível para quem quiser o dataplane VPP.

## Referências

- Guia de build e lista de bugs corrigidos: [`docs/OAI-CORE-ARM64.md`](../../server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md)
- Script de build: [`build-oai-arm64.sh`](../../build-oai-arm64.sh)
