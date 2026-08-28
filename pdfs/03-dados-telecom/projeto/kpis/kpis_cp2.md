# Indicadores do Checkpoint 2 — Grupo 6

Tema 1, Vazão do usuário (UE-TP). Integrantes: Henrique Carmine, Kelvin de Lima
Gabriel e Klinger Carneiro Júnior. Professor: Dr. Jonas Augusto Kunzler.

No Checkpoint 1 mostramos **como** os dados foram organizados e olhados. Aqui
fechamos a cadeia que a Aula 04 pede:

```
medida (KPM) → métrica → KPI → KQI → QoS (SLA) → QoE (proxy) → decisão
```

A Aula 04 cobra, para cada indicador: **nome · fórmula · unidade ·
granularidade · fonte · alvo/limiar · interpretação · papel · limite de
validade**. É o que está abaixo, um por um.

## Fonte comum a todos

Zona **silver** do mini-lake (`data/silver/kpm.sqlite`, tabela `kpm`), montada
pelo `etl/build_lake.py` a partir do pacote `kpm-ue-tp-sample` do professor.
São 100 amostras em três fases: repouso (20), carga (60) e recuperação (20).
Telemetria de simulação (RFSIM), sem dados pessoais.

**Correção em relação ao CP1:** as unidades são as do E2SM-KPM, como o xApp do
FlexRIC imprime — `thp_ul` em **kbps**, `delay_dl` em **µs** e `prb_ul` em **%
dos PRB**. No relatório do CP1 usamos ms e contagem de PRBs; está corrigido aqui.

---

## KPI-1 — Vazão UL do usuário

| Campo | Conteúdo |
|---|---|
| **Fórmula** | `mediana(thp_ul)` e `p95(thp_ul)`, agrupando por fase |
| **Unidade** | kbps |
| **Granularidade** | amostra KPM, agregada por fase |
| **Fonte** | coluna `thp_ul` (`DRB.UEThpUl`) |
| **Alvo / limiar** | queda abaixo de metade da mediana do repouso |
| **Interpretação** | o serviço está entregando bits ao usuário? |
| **Papel** | **KPI** — desempenho da rede |
| **Limite de validade** | 1 UE em simulação, 1 execução; a mediana foi escolhida porque um pico isolado na recuperação (172.317 kbps) distorce a média |

Medido: repouso **3,7** · carga **80.023,7** · recuperação **3,7** (medianas).

## KPI-2 — Ocupação de PRB no uplink

| Campo | Conteúdo |
|---|---|
| **Fórmula** | `média(prb_ul)` por fase |
| **Unidade** | % dos PRB |
| **Granularidade** | amostra KPM, agregada por fase |
| **Fonte** | coluna `prb_ul` (`RRU.PrbTotUl`) |
| **Alvo / limiar** | acima de **80%** é pressão de capacidade (referência do slide 35) |
| **Interpretação** | quanto do rádio está ocupado |
| **Papel** | **KPI** — utilização de recurso |
| **Limite de validade** | com 1 UE, ele satura o rádio sozinho; num cenário com vários usuários esse número teria outro significado |

Medido: repouso **2,0%** · carga **97,3%** · recuperação **3,0%**.

## KPI-3 — Atraso RLC no downlink

| Campo | Conteúdo |
|---|---|
| **Fórmula** | `mediana(delay_dl)` e `p95(delay_dl)` por fase |
| **Unidade** | µs |
| **Granularidade** | amostra KPM, agregada por fase |
| **Fonte** | coluna `delay_dl` (`DRB.RlcSduDelayDl`) |
| **Alvo / limiar** | cláusula didática: p95 ≤ 223 µs (o p95 do repouso × 1,2) |
| **Interpretação** | quanto o pacote espera na camada RLC antes de descer |
| **Papel** | **KPI de integridade** |
| **Limite de validade** | é atraso de RLC no downlink, **não** atraso fim-a-fim: não inclui core, transporte nem aplicação |

Medido (mediana / p95): repouso **0,0 / 185,7** · carga **158,9 / 191,2** ·
recuperação **0,0 / 394,0**.

## KQI — Fração do tempo com atraso acima do limiar

| Campo | Conteúdo |
|---|---|
| **Fórmula** | `n(delay_dl > L) / n`, por fase, com **L = 100 µs** |
| **Unidade** | % das amostras |
| **Granularidade** | amostra KPM, agregada por fase |
| **Fonte** | derivado de `delay_dl` |
| **Alvo / limiar** | cláusula didática: ≤ 50% do tempo (o dobro do repouso) |
| **Interpretação** | que fração da janela ficou em regime degradado |
| **Papel** | **KQI** — qualidade do serviço; vira **cláusula de QoS** quando L é tratado como contrato |
| **Limite de validade** | L separa **regimes**, não mede satisfação; a conclusão se sustenta para L entre ~40 e ~150 µs e desaparece acima de 186 µs |

Medido: repouso **25%** · carga **100%** · recuperação **30%**.

---

## Por que L = 100 µs, e não outro número

Testamos L de 20 a 280 µs e medimos a separação entre repouso e carga:

| L (µs) | repouso | carga | separação |
|---|---|---|---|
| 50 | 35% | 100% | 65 pontos |
| **100** | **25%** | **100%** | **75 pontos** |
| 150 | 20% | 83% | 63 pontos |
| 200 | 5% | 2% | −3 pontos |

L = 100 µs é o ponto de maior separação. Acima de 186 µs a separação **inverte**,
porque o p95 do repouso (185,7 µs) ultrapassa o da carga (191,2 µs) — e é esse o
limite de validade do indicador, declarado em vez de escondido.

## O que este KQI **não** é

Não é medida de experiência. Não existe MOS, buffering nem nota de aplicativo
neste artefato; um atraso de RLC abaixo de 1 ms não é "experiência ruim". O que
o indicador mostra é **mudança de regime** em relação ao repouso.
