# external/cesar-school-repo — o repositório do Prof. Jonas Kunzler

O repositório oficial das disciplinas do Prof. Dr. **Jonas A. Kunzler**
([`jakunzler/cesar-school-repo`](https://github.com/jakunzler/cesar-school-repo))
vive aqui como **submódulo git** em `external/cesar-school-repo`, pinado num
commit conhecido — o nosso repo guarda só a referência (~200 bytes), não os
57 mil arquivos dele.

## Como usar

```bash
# clone novo do Core5G_ARM64 (o submódulo NÃO vem por padrão):
git submodule update --init external/cesar-school-repo

# sincronizar com o professor (ele atualiza durante a disciplina):
git submodule update --remote external/cesar-school-repo
git add external/cesar-school-repo && git commit   # pina a nova versão
```

> O servidor **não precisa** do submódulo: nada de `deploy.sh`/`infra/` o
> referencia. É material de estudo local.

## Mapa: trilhas dele × disciplinas nossas

Cada trilha tem `bibliography/ code/ docs/ slides/`:

| Pasta dele | Disciplina | Nossa pasta |
|---|---|---|
| `oran/` | Open RAN (anterior ao nosso ingresso no lab) | — |
| `ric/` | RAN Intelligent Controller | [`pdfs/01-ric/`](../pdfs/01-ric/) |
| `data/` | **Análise de Dados em Redes de Telecom** (atual) | [`pdfs/03-dados-telecom/`](../pdfs/03-dados-telecom/) |

(A disciplina 02, do Prof. Tesolin, não faz parte deste repositório.)

`*/slides/` está **vazio** — os slides saem só pela plataforma; seguem sendo
arquivados em `pdfs/`.

## O que interessa para a disciplina atual (`data/`)

**Documentos do projeto integrador** — `data/docs/`:

- `briefing-projeto.md` · `temas-grupos.md` · `guia-aluno.md` ·
  `PROJETO_PRATICO.md` · `briefing-plataforma.md`
- `plano-ensino-analise-dados-telecom.pdf`

**O lab** — `data/code/oai-cn-gnb-nonrt-nearrt/` (OAI CN5G + gNB + FlexRIC +
UERANSIM + vendor):

- `scripts/run_ue_tp_experiment.sh` + `scripts/kpm_store.py` — regeneram os
  artefatos KPM da **trilha offline** (a obrigatória) do projeto
- `tests/test_ai_policy_pipeline.py` · `tests/test_closed_loop.py` — pytest do
  pipeline completo
- `docs/FASES_ORAN_LAB.md` — o roteiro em fases do lab

**Fases do lab dele × nossa discussão de Non-RT RIC**
(ver [non-rt-ric.md](non-rt-ric.md)): as fases 2 e 3
(`FASE2_ORAN_SC_A1.md`, `FASE3_IA_A1.md`, `FASE3_CLOSED_LOOP.md`,
`EXPLORAR_NONRT_RIC.md`) montam o caminho Non-RT → A1 → closed loop com
componentes O-RAN SC — ler antes de desenhar o nosso build ARM64 do Non-RT
("Projeto 3"), para alinhar com o que o professor já estruturou.

## Versão pinada

| Data | Commit | Nota |
|---|---|---|
| 08/08/2026 | `75e16fb9` | "doc: adiciona plano de ensino" |
