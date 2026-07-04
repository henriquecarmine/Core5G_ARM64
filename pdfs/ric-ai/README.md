# ric-ai/ — material do laboratório de RIC com IA

Coloque aqui os PDFs de **IA/ML aplicada ao RIC** (papers, slides, notas): base
de referência do lab de RIC com Inteligência Artificial — Near-RT / Non-RT RIC
e o **UE-TP-rApp** (previsão de throughput por UE), o tema do grupo.

Contexto e dependências:

- **Modelo**: esqueleto em `server/oai-cn-gnb-e2/.../xapp_ue_tp_moni.c`; falta o
  modelo de previsão. Wheels do **scikit-learn aarch64** já vendorizadas em
  `server/panel/vendor/` (ver `server/panel/vendor/README.md`).
- **Pipeline de dados**: `kpm_analytics.sh` → CSV (KPM → KPI) já pronto; é o
  insumo do modelo. Guia: [`KPM-ANALYTICS.md`](../../server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md).
- **Bloqueio de hardware**: o lab de IA depende de **4 vCPU** (em 2 vCPU o
  UE + gNB RFSIM não coexistem sob o guardrail anti-freeze). Análise e runbook do
  resize reversível: [`POLITICA-DE-CUSTOS.md §3`](../../docs/POLITICA-DE-CUSTOS.md).

> Curso base (as 6 aulas do Prof. Jonas): [`../base/`](../base/).
