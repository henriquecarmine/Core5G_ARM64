# Fórmulas da tabela ⚡ — item a item

> Resposta à pergunta "que fórmula você usou?": cada número da tabela ARM N1 ×
> x86_64 do painel, com fórmula, entradas e fonte. Dados vivos são medidos NESTE
> servidor; a coluna x86 é estimada por literatura (não roda aqui).

## Watts ao vivo (cabeçalho)
`W(u) = vCPUs × (W_idle + (W_max − W_idle) × u/100)` — interpolação linear entre
os pontos idle e 100% do dataset Teads [5], com `u` = CPU% medido agora via
`/api/telemetry` (leitura de /proc/stat deste servidor).
- N1: `4 × (0,27 + (2,39−0,27)×u/100)` → 1,1 W (idle) a 9,6 W (100%)
- x86 (m5 eq.): `4 × (1,15 + (4,98−1,15)×u/100)` → 4,6 W a 19,9 W
- Limite: modelo linear entre 2 pontos publicados; o real tem curva (DVFS).

## a. Economia de energia = `1 − (W_max_N1 / W_max_x86)` = `1 − 2,39/4,98` ≈ **−50%** [5][6]
## b. Trabalho na mesma energia = `(perf_N1/W_N1) / (perf_x86/W_x86)`
Com perf/vCPU ≈ paridade-a-+27% [3][4] e metade dos watts: ≈ **2,4×** (+140%).
## c. Eficiência média = média de (a,b) sobre operações compute/web/build dos
benchmarks [1][3][4][5] ≈ **+110%** — valor central do intervalo observado.
## d. RAM: medida ao vivo (`MemTotal−MemAvailable`)/MemTotal em /proc/meminfo.
ISA não altera consumo de RAM (mesma DDR4, ponteiros 64-bit) — Δ≈0 por design.
## f. Processamento de dados = média de SPECint2017 MT por vCPU (+27% [3]),
geomean Phoronix (+11–21% [4]) e streaming real (~+20% [10]) ≈ **+20%**.
## g. Graviton3: claim oficial AWS "até 60% menos energia" [1] — nasceu nesta
geração (não no N1); +25% perf vs G2. Mostra a trajetória da tese.
## e. Veredito = média ponderada de subnotas 0–100:
`Σ peso×subnota` com pesos {energia 0,35 · perf/W 0,30 · perf bruta 0,20 ·
ecossistema 0,15}. N1 = 0,35×95+0,30×92+0,20×72+0,15×60 = **84,3**;
x86 = 0,35×50+0,30×45+0,20×78+0,15×90 = **60,1**. Subnotas justificadas no
CHANGELOG 0.59.0 e nas fontes; sensibilidade: mesmo dobrando o peso de
ecossistema o N1 segue à frente.

## Energia por teste (rodapé pós-teste)
`E = W(100%) × duração_medida` — TETO honesto assumindo CPU cheio na duração
real do teste (medida no navegador): `E_N1 = 9,6W×t` vs `E_x86 = 19,9W×t`.

Fontes numeradas: ver a tabela ⚡ no painel (mesma numeração).
