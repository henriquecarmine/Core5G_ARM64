# OAI 5G Core — Imagens arm64 pré-compiladas

Imagens Docker do OAI 5G Core Control Plane compiladas para `linux/arm64`
(Apple Silicon / AWS Graviton2). As imagens oficiais do DockerHub são
`amd64`-only; estes arquivos são o resultado do build nativo neste projeto.

## Download

Os `.tar` não estão versionados no Git (tamanho > 100 MB). Baixe pelo Google Drive:

**[oai-images-arm64.tar.gz — Google Drive](https://drive.google.com/file/d/1fPaqfkM7CzhliUmx8DzMD0kkD0-U3adg/view?usp=sharing)**

## Arquivos

| Arquivo | Componente | Função 3GPP | Tamanho |
|---|---|---|---|
| `oai-amf.tar` | oai-amf:v1.5.1 | Access and Mobility Management Function | ~63 MB |
| `oai-smf.tar` | oai-smf:v1.5.1 | Session Management Function | ~60 MB |
| `oai-nrf.tar` | oai-nrf:v1.5.1 | Network Repository Function | ~60 MB |
| `oai-udr.tar` | oai-udr:v1.5.1 | Unified Data Repository | ~61 MB |
| `oai-udm.tar` | oai-udm:v1.5.1 | Unified Data Management | ~59 MB |
| `oai-ausf.tar` | oai-ausf:v1.5.1 | Authentication Server Function | ~59 MB |

Cada `.tar` é gerado por `docker save` e contém todas as camadas da imagem
Docker final (binário do componente + bibliotecas `.so` mínimas, base Ubuntu
20.04). Não há compressão adicional — o formato é o padrão do Docker.

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

## O que NÃO está incluído

- `oai-upf-vpp` — depende de `libhyperscan-dev` (Intel-only, inexistente no
  Ubuntu arm64). O lab usa o UPF do Open5GS no lugar.

## Referências

- Guia de build e lista de bugs corrigidos: [`docs/OAI-CORE-ARM64.md`](../../server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md)
- Script de build: [`build-oai-arm64.sh`](../../build-oai-arm64.sh)
