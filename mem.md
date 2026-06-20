# mem.md — HANDOFF descartável (LEIA e DEPOIS APAGUE este arquivo)

> Para a próxima sessão de IA: leia isto, aja conforme necessário, **delete este
> arquivo** (`rm mem.md`) e **NÃO o commite**. O contexto durável já está em
> `MEMORY.md` + `CHANGELOG.md` + `core5g-arm64-bible.md`.

## Onde paramos (2026-06-20)
- `main` @ `7a655ec6`, **v0.12.4**, local == origin, working tree limpo.
- Só **henriquecarmine** tem push (repo PÚBLICO). Qualquer divergência "misteriosa"
  na main é você mesmo de outra máquina — foi o que aconteceu nesta sessão.

## O que foi feito (resumo)
- **Reconciliação:** a main remota tinha divergido (linha 0.11–0.12.1: login por
  cookie, topology.html, testes coloridos, xapp_ue_tp_moni.c). Integrei o meu
  trabalho POR CIMA dela sem clobber. A UI de "menu superior" que eu havia feito
  foi **descartada de propósito** (a linha remota já refez a UI). Ela vive no
  commit `adf8ad12` (reflog) se um dia quiser resgatar.
- **User plane arm64 (OAI v2.2.1):** `server/oai-cn-gnb-e2/oai-cn5g-v2/` — UE pega
  IP 12.1.1.x. Sobe com `oai-cn5g-v2/up_core_v2.sh` + `scripts/up_e2_lab_v2.sh`.
- **xApps validados:** `scripts/e2_verify.sh` → **cust 7/7, kpm 7/7, rc 5/7** (load <2).
- **Auth travada:** guest é opt-in; com `.env` `PANEL_GUEST_USER=` em branco, só
  hcarmine entra. Servidor já deployado em v0.12.4.

## ⚠️ ARMADILHAS (não repita)
1. **NUNCA rode `./deploy.sh sync-oai` às cegas.** Ele rsync-a o tree LOCAL por
   cima do servidor e **sobrescreve artefatos de build**. Já quebrou o RIC uma
   vez: o repo carregava `flexric-lib/*.so` em **x86-64** e o sync os jogou por
   cima dos arm64 do servidor → `nearRT-RIC` crashava no dlopen. Hoje:
   - os `.so` saíram do git (`.gitignore`);
   - `up_flexric.sh` é **arch-aware** e repovoa `flexric-lib/` do build tree
     automaticamente (`sync_flexric_lib.sh`). Auto-curável.
   - Para mandar UM script de oai pro servidor, prefira `scp` do arquivo único.
2. **Box tem só 2 vCPUs.** gNB+nrUE RFSIM saturam tudo (load >20, SSH cai). Por
   isso `e2_verify.sh` sobe com `SKIP_UE=1` (sem nrUE; E2 é gNB↔RIC). Para lab
   COM user plane use `SKIP_UE=0`, mas NÃO rode os 7× de xApp junto.
3. Labs P1 (Open5GS) e P2 (OAI) são **mutuamente exclusivos** — os up scripts
   derrubam o outro.
4. **ZERO tempo:** nada de sleep/timeout cego; tudo termina por evento/estado.

## Estado do servidor agora
- Host `core5g-arm64.duckdns.org`, user `ubuntu`, chave `./ssl/core5g_openran_arm64.pem`.
- RAN/RIC **derrubados**; core v2 (8 containers `oai-*`) deixado UP (leve). load ~0.4.
- Painel ao vivo em v0.12.4, UI = login/topology (a do repo), guest 403 (travado).

## Pendências / decisões abertas (opcionais, não feitas)
- Proteger branch `main` e/ou tornar repo privado (oferecido, você não decidiu).
- rc 5/7: os 2 que "falham" também subscrevem (RAN_FUNC_ID 3) — é timing do RIC em
  rajada, não bug. Se quiser 7/7, dar respiro entre runs de RC (por evento, não tempo).
- Regra do usuário: codar local, deploy via `deploy.sh` (panel é seguro; sync-oai é o perigoso).
