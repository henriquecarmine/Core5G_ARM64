# Indicadores (KPIs/KQIs) — Projeto Integrador

**Tema (provável): G6 — Economia de energia (só intenção).** _A confirmar com o
grupo._ Os dois indicadores abaixo seguem o card do G6 (fração de baixa carga +
vazão/atraso nessas janelas). Se o tema for outro (G1–G5/G7), trocam-se as
fórmulas mantendo o mesmo pipeline.

> Estado no **Checkpoint 1 (25/08)**: indicadores **preliminares** já calculados
> (`eda_cp1.py`). No Checkpoint 2 (27/08) eles ficam formais (fórmula fechada,
> unidade, granularidade) e ligados às visualizações.

## Fonte comum

Zona **silver** do mini-lake — `data/silver/kpm.sqlite`, tabela `kpm`
(`thp_ul` = DRB.UEThpUl · `delay_dl` = DRB.RlcSduDelayDl · `prb_ul` = RRU.PrbTotUl),
100 amostras a 1 medição/amostra, fases baseline(20)/stress(60)/recovery(20).
Telemetria sintética RFSIM (sem dados pessoais).

## Indicador 1 — Fração do tempo em baixa carga

- **Fórmula:** `100 · (nº de amostras com prb_ul ≤ L) / (nº total de amostras)`
- **Limiar `L` = 10 PRBs** — justificado pelos dados: baseline/recovery operam com
  ~2–3 PRBs e o stress com ~97; `L=10` separa "idle/baixa" de "carga" com folga.
- **Unidade:** % de amostras (proxy de % do tempo, amostragem regular).
- **Granularidade:** global e por fase (`GROUP BY phase`).
- **Valor (CP1):** **40,0%** global · baseline 100% · stress 1,7% · recovery 95%.
- **Lê como:** quanto do experimento a rádio esteve ociosa o bastante para
  *cogitar* economia de energia (janela candidata a uma política A1 de sleep).

## Indicador 2 — Desempenho nas janelas de baixa carga

- **Fórmula:** `média(thp_ul | prb_ul ≤ L)` e `média(delay_dl | prb_ul ≤ L)`
- **Unidade:** vazão em kbps · atraso em ms.
- **Granularidade:** global (e por fase, se útil).
- **Valor (CP1):** vazão média **≈ 4,0 kbps** · atraso médio **≈ 69,6 ms** nas
  janelas de baixa carga.
- **Lê como:** confirma que, quando a carga é baixa, o serviço segue leve
  (vazão baixa, atraso contido) — ou seja, uma eventual economia de energia
  nessas janelas **não** sacrificaria uma demanda alta.

## O que os indicadores NÃO provam

- Não medem **energia** de verdade — o lab **não** controla potência de RU; a
  economia é **intenção simulada** (política A1 em dry-run), não atuação física.
- 1 `run_id`, **poucos UEs** (RFSIM): estatística didática, não de campus real.
- `delay_dl` é **proxy** de qualidade — não há MOS de aplicativo.
