# Tarefa pendente — build das imagens OAI core para ARM64

## Contexto

Projeto 2 (OAI 5GC + gNB RFSIM + E2 agent + FlexRIC near-RT RIC + xApps) já tem
o build nativo concluído no servidor AWS ARM64 (gNB/nrUE/E2 agent via
`build_e2.sh`, RIC+xApps via `build_flexric_tools.sh`).

Bloqueio atual: as imagens Docker do OAI 5G Core no Docker Hub
(`oaisoftwarealliance/oai-{amf,smf,nrf,udr,udm,ausf,upf-vpp}:v1.5.1`) são
**amd64-only**, sem variante arm64. O servidor AWS (t4g.micro, ARM64) não tem
QEMU/binfmt-misc configurado, então os containers crasham com
`exec /usr/bin/python3: exec format error`.

## Decisão tomada

Buildar essas 7 imagens nativamente para arm64 no Mac (presumivelmente Apple
Silicon), usando os Dockerfiles já vendorizados no repo, e depois transferir
para o servidor AWS (via `docker save`/`scp`/`docker load`, ou push pra um
registry).

## O que falta fazer

1. Acesso SSH ao Mac (host/IP, usuário, senha ou chave).
2. Buildar as 7 imagens para arm64 a partir de:
   `server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-*/docker/Dockerfile.*.ubuntu`
   (amf, smf, nrf, udr, udm, ausf, upf-vpp), tagueando como
   `oaisoftwarealliance/oai-*:v1.5.1` (mesmo nome que `docker-compose-basic-vpp-nrf.yaml`
   espera).
3. Transferir as imagens para o servidor AWS e substituir os pulls amd64
   quebrados.
4. Re-rodar `up_core.sh` no servidor e confirmar que todos os NFs sobem
   saudáveis (sem `exec format error`, sem `Exited (255)`).
5. Continuar a validação E2E: `up_e2_lab.sh` → `test_e2_sm.sh all` →
   `test_e2_kpm.sh` → `test_e2_rc_attach.sh` → `verify_e2_lab.sh`.
6. Religar o Projeto 1 (`up_core.sh`/`up_ran.sh` ou pelos toggles do painel),
   que ficou desligado pra liberar RAM durante o build do Projeto 2.

## Restrições do workflow (importante)

- Tudo deve viver no repo e ser versionado; o servidor só roda serviços já
  configurados. Mudanças passam por `./deploy.sh`, não por tweaks manuais via
  SSH direto no servidor.
- SSH direto só se justifica para *executar* builds/compilações nativas que
  não podem ser "deployadas" como artefato estático (ex.: compilar no Mac,
  compilar no servidor) — não para configurar coisas que deveriam estar no
  repo.
- `.env` e a chave SSH (`ssl/core5g_openran_arm64.pem`) contêm segredos reais
  — nunca commitar, nunca colar em lugares compartilhados. O mesmo cuidado
  vale para qualquer credencial nova do Mac.

## Prazo

Apresentação em 2026-06-20, 08:00–11:00 (Aula 06) — esse bloqueio é urgente.
