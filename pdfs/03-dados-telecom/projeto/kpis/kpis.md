# Indicadores (KPIs/KQIs) - Grupo 6

Tema 1, Vazão do usuário (UE-TP). Integrantes: Henrique Carmine, Kelvin de Lima
Gabriel e Klinger Carneiro Júnior.

A pergunta do grupo é se a vazão do UE (`DRB.UEThpUl`) sobe e desce junto com o
uso de PRB (`RRU.PrbTotUl`) e com o atraso (`DRB.RlcSduDelayDl`).

No Checkpoint 1 (25/08) os indicadores já estão calculados sobre os dados (pelo
`eda_cp1.py`). No CP final entram a recomendação/A1 e a análise fecha.

## Fonte comum

Zona silver do mini-lake, o arquivo `data/silver/kpm.sqlite`, tabela `kpm`
(onde `thp_ul` = DRB.UEThpUl, `prb_ul` = RRU.PrbTotUl e `delay_dl` =
DRB.RlcSduDelayDl). São 100 amostras, fases baseline (20), stress (60) e recovery
(20). Telemetria sintética de RFSIM do lab `oai-cn-gnb-nonrt-nearrt`, sem dados
pessoais.

## Indicador 1 - Vazão UL por fase

Fórmula: `média(thp_ul)` e `p95(thp_ul)` agrupando por `phase`. Unidade em kbps,
granularidade por fase (`GROUP BY phase`).

| fase | vazão média | vazão p95 |
|------|------------:|----------:|
| baseline | 3,7 | 3,8 |
| stress | 78 383,8 | 82 189,5 |
| recovery | 8 619,3 (mediana 3,7) | 8 619,4 |

A vazão do usuário salta de ~4 pra ~78 mil na carga e volta pro piso no recovery.
No recovery a média engana (uma amostra ficou com um pico residual), e a mediana
de 3,7 mostra que o usuário já tinha voltado pro idle. Por isso reportamos a
mediana junto.

## Indicador 2 - Utilização de PRB UL por fase

Fórmula: `média(prb_ul)` agrupando por `phase`. Unidade em % dos PRB, por fase.

Valores no CP1: baseline 2,0, stress 97,3 e recovery 3,0. O recurso de rádio
segue a mesma forma da vazão (idle, satura, volta pro idle).

## O que os dois indicadores dizem juntos (a resposta do tema)

A correlação de Pearson global (nas 100 amostras) dá vazão × PRB = 0,924 e
vazão × atraso = 0,484. Só que a global mistura as fases (idle contra carga).
Pra responder direito a gente olhou dentro de cada fase:

| fase | vazão × PRB | vazão × atraso |
|------|:-----------:|:--------------:|
| baseline | PRB constante = 2 | 0,11 |
| stress | 0,979 | 0,16 |
| recovery | 1,00 | -0,08 |

A vazão acompanha o PRB de verdade: a relação se mantém mesmo dentro do stress
(0,98). Já a de vazão × atraso fica perto de zero dentro de cada fase, então
aquele 0,48 global é confundimento (as duas só sobem juntas entre as fases, não
porque uma puxa a outra). Dizer que "a vazão anda com o atraso" seria uma leitura
errada. Dá pra ver isso no `figures/cp1_vazao_x_prb.png`.

## Recomendação (dry-run, fecha no CP final)

Se a vazão cair enquanto o PRB estiver alto (rádio cheio mas usuário mal servido),
a ideia é propor priorização ou alívio de carga numa política A1 simulada, sem
atuar de fato na RAN.

## Limitações e o que os indicadores não provam

- A correlação de vazão × atraso (0,48) vem do contraste entre fases; dentro da
  fase é ~0. Só a de vazão × PRB se sustenta dentro da fase.
- As unidades são as do E2SM-KPM, como o xApp do FlexRIC imprime e o slide 66 da
  aula 01 mostra: kbps, µs e % dos PRB (numa versão anterior deste texto a gente
  tinha escrito ms e PRBs; corrigido).
- O `ingested_at` não é a hora da medição, é o carimbo de ingestão em lote
  (04/08 UTC); o experimento é de jun/25 (ver `source_path`). A ordem no tempo é
  o `sample_index`, não tem relógio de medição por amostra.
- A média do recovery engana (um pico residual), então reportamos mediana e p95.
- É 1 só `run_id` e poucos UEs (RFSIM): estatística didática, não de campus real.
- O `delay_dl` é um proxy de qualidade, não tem MOS de aplicativo; e a vazão é
  sintética do RFSIM, não medida de rede em produção.
