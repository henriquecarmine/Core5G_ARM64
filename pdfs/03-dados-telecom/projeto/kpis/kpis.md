# Indicadores (KPIs/KQIs) — Projeto Integrador · Grupo 6

**Tema:** Grupo 6 → **Tema 1 — Vazão do usuário (UE-TP)**.
**Integrantes:** Henrique Carmine · Kelvin de Lima Gabriel · Klinger Carneiro Júnior.

**Pergunta do grupo:** a vazão do UE (`DRB.UEThpUl`) sobe/desce **junto** com o uso
de PRB (`RRU.PrbTotUl`) e com o atraso (`DRB.RlcSduDelayDl`)?

> Estado no **Checkpoint 1 (25/08)**: indicadores calculados sobre os dados
> (`eda_cp1.py`). No CP2/CP final ganham a recomendação/A1 e a análise fecha.

## Fonte comum

Zona **silver** do mini-lake — `data/silver/kpm.sqlite`, tabela `kpm`
(`thp_ul`=DRB.UEThpUl · `prb_ul`=RRU.PrbTotUl · `delay_dl`=DRB.RlcSduDelayDl),
100 amostras, fases baseline(20)/stress(60)/recovery(20). Telemetria sintética
RFSIM do lab `oai-cn-gnb-nonrt-nearrt` — sem dados pessoais.

## Indicador 1 — Vazão UL por fase

- **Fórmula:** `média(thp_ul)` e `p95(thp_ul)` agrupando por `phase`.
- **Unidade:** kbps · **Granularidade:** por fase (`GROUP BY phase`).
- **Valor (CP1):**

  | fase | vazão média | vazão p95 |
  |------|------------:|----------:|
  | baseline | 3,7 | 3,8 |
  | stress | 78 383,8 | 82 189,5 |
  | recovery | 8 619,3 (mediana **3,7**) | 8 619,4 |

- **Lê como:** a vazão do usuário salta ~4 → ~78 mil na carga e volta ao piso no
  recovery. A **média do recovery engana** (puxada por 1 pico residual) — a
  **mediana (3,7)** mostra que o usuário já voltou ao idle.

## Indicador 2 — Utilização de PRB UL por fase

- **Fórmula:** `média(prb_ul)` agrupando por `phase`.
- **Unidade:** PRBs · **Granularidade:** por fase.
- **Valor (CP1):** baseline **2,0** · stress **97,3** · recovery **3,0**.
- **Lê como:** o recurso de rádio segue a mesma forma da vazão (idle → saturado → idle).

## Relação entre os indicadores (a resposta do tema)

Correlação de Pearson **global** (100 amostras): vazão × PRB = **0,924** ·
vazão × atraso = 0,484. **Nota: a correlação global mistura as fases**
(idle × carga). Para responder direito, olhamos **dentro** de cada fase:

| fase | vazão × PRB | vazão × atraso |
|------|:-----------:|:--------------:|
| baseline | — (PRB constante = 2) | 0,11 |
| stress | **0,979** | 0,16 |
| recovery | 1,00 | −0,08 |

**Conclusão honesta:** a vazão **acompanha o PRB de verdade** — a relação se
mantém mesmo **dentro** do stress (0,98). Já vazão × atraso é **~0 dentro de cada
fase**: o 0,48 global é **confundimento** — as duas só sobem juntas *entre* fases,
não porque uma puxa a outra. Dizer "a vazão anda com o atraso" seria uma leitura
**falsa**. Ver `figures/cp1_vazao_x_prb.png`.

## Recomendação (dry-run — a fechar no CP final)

Se a vazão **cair** enquanto o **PRB estiver alto** (rádio cheio mas usuário mal
servido), propor priorização/alívio de carga em **política A1 simulada**
(sem atuação física na RAN).

## Limitações e o que os indicadores NÃO provam

- **Correlação por fase:** vazão × atraso "0,48" vem do **contraste entre fases**
  (dentro da fase é ~0). Só vazão × PRB é relação que se sustenta dentro da fase.
- **Unidades não declaradas** no artefato — kbps/ms/PRBs são **convenção KPM
  O-RAN** assumida por nós, não vêm no dado.
- **`ingested_at` não é a hora da medição:** é carimbo de **ingestão em lote**
  (04/08 UTC); o experimento é de jun/25 (`source_path`). A ordem temporal é o
  `sample_index` — não há relógio de medição por amostra.
- A **média** do recovery engana (1 pico residual) — reportamos também mediana/p95.
- **1 `run_id`**, **poucos UEs** (RFSIM): estatística didática, não de campus real.
- `delay_dl` é **proxy** de qualidade — não há MOS de aplicativo; vazão é sintética
  do RFSIM, não medida de rede em produção.
