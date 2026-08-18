# pdfs/ — material das disciplinas

Slides, trabalhos e material de referência, **uma pasta por disciplina**, em
ordem cronológica:

| # | Pasta | Disciplina | Professor | Status |
|---|-------|-----------|-----------|--------|
| 00 | [`00-interfaces-oran/`](00-interfaces-oran/) | Interfaces e Protocolos ORAN | **Jonas A. Kunzler** | mar–abr/2026 (só aula01) |
| 01 | [`01-ric/`](01-ric/) | RAN Intelligent Controller | **Jonas A. Kunzler** | concluída |
| 02 | [`02-ric-ai/`](02-ric-ai/) | Aplicações de IA e ML em RIC | **Julio Cesar Cardoso Tesolin** | encerrada — material completo (A01–A06); **projeto final não implementado** |
| 03 | [`03-dados-telecom/`](03-dados-telecom/) | Análise de Dados em Redes de Telecom | **Jonas A. Kunzler** | em andamento (ago/2026) |

## `00-interfaces-oran/` — Interfaces e Protocolos ORAN (Kunzler)

A primeira disciplina de Open RAN da especialização (mar–abr/2026): motivação,
arquitetura, Open Fronthaul, RIC/xApps e IA. Só a **aula01** (`motivacao_oran`)
foi compartilhada como PDF; as demais foram só apresentadas em aula.

## `01-ric/` — RAN Intelligent Controller (Kunzler)

As 6 aulas do curso base de RIC (`aula01`–`aula06`: interfaces O-RAN, OSS/RICs,
A1, xApps, SMO, testes) + resumo de acesso à VM do lab. Fonte histórica de boa
parte da [bíblia](../core5g-arm64-bible.md) (§1).

## `02-ric-ai/` — Aplicações de IA e ML em RIC (Tesolin)

Aulas `MLRAN_A01`–`A06` (SON→RIC, supervisionado, não supervisionado, redes
neurais/RNN/autoencoders, reforço/DQN, bio-inspirados, federado e Open RAN+ML),
datasets por técnica de ML em `Base Fonts RIC/`, reproduções dos casos do artigo
NGO et al. 2024 em `casos-artigo/` e o lab interativo do painel gerado por
`lab-didatico/`. Catálogo completo: [`02-ric-ai/README.md`](02-ric-ai/README.md).

> **Pendência:** implementar o **projeto final**
> (`Trabalho final IA e ML Open Ran.pdf` — caso UE-TP).
> O lab de IA depende do upgrade para 4 vCPU (ver
> [política de custos §3](../docs/POLITICA-DE-CUSTOS.md) e o roadmap no
> [README](../README.md)); as wheels do scikit-learn aarch64 já estão
> vendorizadas em `server/panel/vendor/`.

## `03-dados-telecom/` — Análise de Dados em Redes de Telecom (Kunzler)

Disciplina 9 (6 encontros, 24 h, ago/2026): fontes de dados na rede
(SMO/O1/E2/A1, PM/FM/KPM), lakes/warehouses, EDA/ETL, KPIs/KQIs e capacidade —
com **projeto integrador (50%)** sobre a telemetria KPM do lab
`oai-cn-gnb-nonrt-nearrt` (caso UE-TP / load-anomaly).

Slides na raiz da pasta; projeto integrador em `03-dados-telecom/projeto/`;
exercícios e checkpoints em `03-dados-telecom/trabalhos/`. Catálogo completo:
[`03-dados-telecom/README.md`](03-dados-telecom/README.md).

---

O repositório oficial das disciplinas do Kunzler (briefings, labs, planos de
ensino) está vendorizado como submódulo em `external/cesar-school-repo` — mapa
completo em [docs/repo-professor.md](../docs/repo-professor.md).

As traduções / notas didáticas por idioma (pt/en/es/fr) dos slides ficarão em
subpastas por disciplina quando a fase de tradução dos slides rodar.
