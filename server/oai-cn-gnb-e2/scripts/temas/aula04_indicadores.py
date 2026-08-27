#!/usr/bin/env python3
"""aula04_indicadores.py - a cadeia da Aula 04 sobre a telemetria KPM do lab.

Disciplina "Analise de Dados em Redes de Telecom" (Prof. Dr. Jonas A. Kunzler,
CESAR School), Aula 04 - "Indicadores e qualidade: da medicao de rede a
experiencia percebida" (25/08/2026, aula04-kpis_kqis_qualidade.pdf).

O deck define a cadeia:

    medida/contador (E2 KPM, O1 PM) -> metrica -> KPI -> KQI -> QoS (SLA)
    -> QoE (no lab: so proxy) -> decisao

Este script percorre essa cadeia com os DADOS de verdade (os mesmos dos 7
temas), imprimindo em cada degrau a formula do slide, a unidade, o limiar
justificado e a leitura - e termina no entregavel do Checkpoint 2: a anatomia
de cada indicador (nome, formula, unidade, granularidade, fonte, alvo/limiar,
interpretacao, papel e limite de validade).

O que o artefato KPM do lab permite e o que NAO permite esta explicito: das 6
familias de KPI do slide 23, so Integridade e Utilizacao saem dos dados; as
outras (acessibilidade, retentabilidade, disponibilidade, mobilidade) ficam
como referencia conceitual, porque os contadores de setup/drop/HO nao existem
no artefato UE-TP. Nao ha MOS de aplicativo: QoE aqui e sempre PROXY.

Uso:
    aula04_indicadores.py [--file kpm.jsonl|kpm.csv]

Limiares (ajustaveis por ambiente, impressos na saida):
    A04_DELAY_L    limiar de atraso do KQI, em us                        [100]
    A04_PRB_SLA    teto de utilizacao de PRB da clausula de SLA, em %     [80]
    A04_THP_KEEP   fracao da vazao do baseline que a clausula exige      [0.5]
    A04_SLA_FOLGA  folga sobre o p95 do baseline na clausula de atraso    [1.2]
    A04_KQI_MULT   quantas vezes a fracao do baseline a clausula tolera   [2.0]
    A04_KQI_MAX    teto de tempo acima do limiar quando o baseline e 0   [0.05]

As clausulas de "SLA" sao DIDATICAS e, por padrao, CALIBRADAS NO BASELINE - o
deck cobra limiar justificado (slides 44 e 77). Um limiar absoluto que ja
dispara na fase de repouso nao mede a rede: mede a escolha do limiar.

Somente biblioteca padrao (roda no servidor ARM64 sem venv).
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from temas_projeto import (  # noqa: E402  (o sys.path acima e proposital)
    B, DIM, RST, Data, env_f, f1, f3, formula, frac, info, kv, load, mean,
    median, ok, pctl, pearson, pct, section, step, table, warn,
)

LIM = {
    "delay_l": env_f("A04_DELAY_L", 100.0),
    "prb_sla": env_f("A04_PRB_SLA", 80.0),
    "thp_keep": env_f("A04_THP_KEEP", 0.5),
    "sla_folga": env_f("A04_SLA_FOLGA", 1.2),
    "kqi_mult": env_f("A04_KQI_MULT", 2.0),
    "kqi_max": env_f("A04_KQI_MAX", 0.05),
}


def veredito(cumpre):
    return f"{B}CUMPRE{RST}" if cumpre else f"{B}VIOLA{RST}"


# =============================================================================
# 1. Medida -> metrica: o que o KPM entrega (slides 17, 36 e 45)
# =============================================================================
def bloco_medida(d, fmt, inferred):
    section("1. Medida -> metrica: o que o artefato KPM entrega")
    info("KPM nao e KPI. KPM e a medicao padronizada; KPI e o indicador derivado, "
         "com formula, unidade, alvo e interpretacao (slide 17).")
    table(["medida (KPM)", "significado", "unidade", "camada da historia", "vira"],
          [["RRU.PrbTotUl", "ocupacao de PRB no UL", "%", "capacidade / carga", "KPI de utilizacao"],
           ["DRB.UEThpUl", "vazao UL do UE", "kbps", "integridade / vazao", "KPI de throughput"],
           ["DRB.RlcSduDelayDl", "atraso RLC no DL", "us", "integridade / latencia", "KPI e proxy de KQI"]],
          right=False)
    kv("nao estao no artefato", "RSRP, RSRQ, SINR, CQI, MCS (canal do UE) e contadores de setup/drop/HO")
    kv("consequencia", "cobertura e acesso ficam como referencia conceitual; nao da para afirmar causa de radio")
    table(["fase", "amostras"], [[p, d.n(p)] for p in d.phases])
    kv("formato lido", fmt)
    if inferred:
        warn("o arquivo nao trazia a coluna 'phase': as primeiras 20% viraram baseline e o resto 'observacao'")


# =============================================================================
# 2. KPIs da rede (slides 40-43, 46-48)
# =============================================================================
def bloco_kpi(d):
    section("2. KPI - indicadores de desempenho da rede")
    info("Pergunta do KPI: a rede esta saudavel, capaz, disponivel? (slide 18)")
    formula("KPI-1  Utilizacao de PRB UL", "media(RRU.PrbTotUl) e p95, por fase", "%")
    formula("KPI-2  Vazao UL do UE", "mediana(DRB.UEThpUl) e p95, por fase", "kbps")
    formula("KPI-3  Atraso RLC DL", "mediana(DRB.RlcSduDelayDl) e p95, por fase", "us")
    kv("por que mediana", "resiste aos picos do RFSIM; a media e sensivel a outlier (slide 51)")
    kv("por que p95", "e a cauda - o que o 'pior' usuario sente; a media esconde (slide 42)")
    rows = []
    for p in d.phases:
        prb, thp, dl = d.col("prb", p), d.col("thp", p), d.col("delay", p)
        rows.append([p, d.n(p), f1(mean(prb)), f1(pctl(prb, 95)),
                     f1(median(thp)), f1(pctl(thp, 95)), f1(median(dl)), f1(pctl(dl, 95))])
    table(["fase", "n", "PRB media %", "PRB p95 %", "Thp mediana kbps", "Thp p95 kbps",
           "atraso mediana us", "atraso p95 us"], rows)
    base, carga = d.phases[0], (d.phases[1] if len(d.phases) > 1 else d.phases[0])
    razao = None
    if median(d.col("thp", base)):
        razao = median(d.col("thp", carga)) / median(d.col("thp", base))
        formula("Razao de vazao", f"mediana({carga}) / mediana({base})", "adimensional")
        kv(f"razao {carga}/{base}", (f3(razao) if razao < 100 else f1(razao)) + ("  (vazao SUBIU com a carga)" if razao >= 1 else "  (vazao CAIU)"))
    return {"base": base, "carga": carga, "razao": razao}


# =============================================================================
# 3. KQI (slide 44) - qualidade do servico
# =============================================================================
def bloco_kqi(d, ctx):
    section("3. KQI - indicador de qualidade do servico")
    info("Pergunta do KQI: o servico esta bom o bastante para o usuario / para o SLA? (slide 19)")
    L = LIM["delay_l"]
    formula("KQI-1  Fracao do tempo em atraso alto", f"n(DRB.RlcSduDelayDl > {L:g} us) / n, por fase", "%")
    formula("KQI-2  Atraso alto COM vazao baixa", "n(atraso > L e vazao < mediana do baseline) / n", "%")
    base = ctx["base"]
    p95b = pctl(d.col("delay", base), 95)
    thp_base = median(d.col("thp", base))
    kv("limiar L", f"{L:g} us (ajustavel por A04_DELAY_L)")
    kv("justificativa", f"p95 do atraso no {base} = {f1(p95b)} us; L = {f3(L / p95b) if p95b else '-'}x esse valor, "
                        "marca MUDANCA DE REGIME, nao 'experiencia ruim' (slide 44: sem limiar nao ha KQI formal)")
    rows = []
    for p in d.phases:
        dl, thp = d.col("delay", p), d.col("thp", p)
        alto = [x > L for x in dl]
        ruim = [x > L and y < thp_base for x, y in zip(dl, thp)]
        rows.append([p, d.n(p), pct(frac(alto)), pct(frac(ruim))])
    table(["fase", "n", "KQI-1 % tempo acima de L", "KQI-2 % alto + vazao baixa"], rows)
    kqi = frac([x > L for x in d.col("delay", ctx["carga"])])
    info("Atraso alto COM vazao baixa reforca risco a experiencia; atraso alto com vazao ALTA e fila de carga - "
         "o servico esta entregando (slide 36).")
    return {"L": L, "kqi_carga": kqi, "thp_base": thp_base}


# =============================================================================
# 4. QoS - o KQI confrontado com o contrato (slides 54-56)
# =============================================================================
def bloco_qos(d, ctx, kqi):
    section("4. QoS - o KQI confrontado com o SLA (didatico)")
    warn("Nao ha 5QI nem QoS Flow no artefato: as clausulas abaixo sao DIDATICAS (slide 56) e, por padrao, "
         "calibradas no baseline - limiar sem justificativa nao e SLA, e chute (slides 44 e 77).")
    L, carga, base = kqi["L"], ctx["carga"], ctx["base"]
    dl_p95_base = pctl(d.col("delay", base), 95)
    kqi_base = frac([x > L for x in d.col("delay", base)])
    alvo_dl = env_f("A04_DELAY_SLA", LIM["sla_folga"] * dl_p95_base)
    thp_min = LIM["thp_keep"] * kqi["thp_base"]
    alvo_kqi = 100 * (LIM["kqi_mult"] * kqi_base if kqi_base > 0 else LIM["kqi_max"])
    clausulas = [
        ("C1 latencia", f"p95 do atraso <= {f1(alvo_dl)} us",
         f"p95 do {base} ({f1(dl_p95_base)}) x {LIM['sla_folga']:g}",
         lambda p: pctl(d.col("delay", p), 95), lambda v: v <= alvo_dl),
        ("C2 vazao", f"mediana da vazao >= {f1(thp_min)} kbps",
         f"{LIM['thp_keep']:g}x a mediana do {base}",
         lambda p: median(d.col("thp", p)), lambda v: v >= thp_min),
        ("C3 capacidade", f"media de PRB <= {LIM['prb_sla']:g} %",
         "referencia do slide 35 (PRB > 80% = ruim)",
         lambda p: mean(d.col("prb", p)), lambda v: v <= LIM["prb_sla"]),
        ("C4 qualidade", f"tempo acima de L <= {f1(alvo_kqi)} %",
         (f"{LIM['kqi_mult']:g}x a fracao do {base} ({pct(kqi_base)})" if kqi_base > 0
          else f"teto de {100 * LIM['kqi_max']:g}% (o baseline nunca passa de L)"),
         lambda p: 100 * frac([x > L for x in d.col("delay", p)]), lambda v: v <= alvo_kqi),
    ]
    rows, violadas = [], []
    for nome, alvo, origem, medir, testa in clausulas:
        cells = [nome, alvo, origem]
        for p in d.phases:
            v = medir(p)
            cells.append(f"{f1(v)} {'OK' if testa(v) else 'X'}")
        vc = medir(carga)
        cells.append(veredito(testa(vc)))
        if not testa(vc):
            violadas.append(nome.split()[1])
        rows.append(cells)
    table(["clausula", "alvo", "de onde vem o alvo"] + list(d.phases) + [f"na fase '{carga}'"], rows, right=False)
    kv("leitura", "clausula violada so na fase de carga = evidencia para o CP2; violada tambem no baseline = "
                  "o limiar esta errado, nao a rede")
    kv("no CP2", "diga, por clausula, se ela e requisito de servico (SLA de verdade) ou calibracao do baseline - "
                 "sao coisas diferentes e o deck cobra a distincao (slide 60)")
    return {"violadas": violadas, "alvo_dl": alvo_dl, "alvo_kqi": alvo_kqi}


# =============================================================================
# 5. QoE - so proxy (slides 54, 58 e 60)
# =============================================================================
def bloco_qoe(d, ctx, kqi):
    section("5. QoE - no lab, apenas PROXY")
    warn("Nao existe MOS, buffering nem nota de aplicativo no artefato. Dizer 'a QoE caiu' com esses dados "
         "seria afirmar o que nao foi medido (slide 60).")
    carga = ctx["carga"]
    dl_p95 = pctl(d.col("delay", carga), 95)
    thp_med = median(d.col("thp", carga))
    acima = 100 * frac([x > kqi["L"] for x in d.col("delay", carga)])
    table(["classe / app", "QoS sensivel a", "sintoma se falhar", "proxy no lab", f"medido em '{carga}'"],
          [["eMBB / download", "throughput", "lento, download interminavel", "mediana da vazao UL",
            f"{f1(thp_med)} kbps"],
           ["video streaming", "thp estavel + jitter", "buffering, queda de resolucao", "atraso p95 e % > L",
            f"{f1(dl_p95)} us / {f1(acima)}%"],
           ["voz / conferencia", "latencia + perda", "eco, cortes, MOS baixo", "atraso (proxy fraco)",
            f"{f1(dl_p95)} us"],
           ["URLLC / controle", "latencia extrema", "falha de controle", "fora do escopo do RFSIM", "-"]],
          right=False)
    kv("como escrever no CP2", "'o atraso RLC no p95 subiu Nx na fase de carga, o que E RISCO a experiencia "
                               "de video' - e nao 'a QoE do usuario caiu'")


# =============================================================================
# 6. Diagnostico: capacidade x canal/interferencia (slides 36 e 69)
# =============================================================================
def bloco_diagnostico(d, ctx):
    section("6. Capacidade ou canal? o que os dados sustentam")
    base, carga = ctx["base"], ctx["carga"]
    dprb = mean(d.col("prb", carga)) - mean(d.col("prb", base))
    dthp = median(d.col("thp", carga)) - median(d.col("thp", base))
    ddl = median(d.col("delay", carga)) - median(d.col("delay", base))
    r = pearson(d.col("prb"), d.col("thp"))
    table(["sinal", base, carga, "variacao"],
          [["PRB media %", f1(mean(d.col("prb", base))), f1(mean(d.col("prb", carga))), f"{dprb:+.1f}"],
           ["Thp mediana kbps", f1(median(d.col("thp", base))), f1(median(d.col("thp", carga))), f"{dthp:+.1f}"],
           ["atraso mediano us", f1(median(d.col("delay", base))), f1(median(d.col("delay", carga))), f"{ddl:+.1f}"]])
    if r is not None:
        kv("correlacao PRB x Thp", f3(r) + "  (correlacao NAO e causalidade - slide 51 da aula 03)")
    if dprb > 0 and dthp > 0:
        diag = "CAPACIDADE / carga real: PRB e vazao sobem juntos - a rede esta entregando mais, nao degradando"
        ok(diag)
    elif dthp < 0 and mean(d.col("prb", carga)) >= LIM["prb_sla"]:
        diag = "SATURACAO: vazao cai com PRB alto - hipotese de congestionamento de capacidade"
        warn(diag)
    elif dthp < 0:
        diag = ("vazao cai com PRB BAIXO: a hipotese vai para canal (SINR/MCS), core ou transporte - "
                "e o artefato nao tem RSRP/CQI para fechar essa conta")
        warn(diag)
    else:
        diag = "sem contraste claro entre as fases"
        info(diag)
    table(["sinal", "capacidade", "jammer / interferencia", "aqui"],
          [["PRB", "sobe (satura)", "variavel; nao explica a queda", f"{dprb:+.1f}"],
           ["Thp UL", "sobe com a carga", "cai / colapsa", f"{dthp:+.1f}"],
           ["atraso RLC", "pode subir", "sobe / sessao falha", f"{ddl:+.1f}"],
           ["KPI espectral", "baixo (ar limpo)", "alto (energia anomala)", "nao coletado"]], right=False)
    kv("watchdog IQ", "o KPI espectral (ocupacao anomala, energia no SSB, score de interferencia) e a fonte que "
                      "faltaria para separar jammer de carga - slides 63-69")
    return diag


# =============================================================================
# 7. Familias de KPI: o que o artefato permite (slides 23 e 35)
# =============================================================================
def bloco_familias():
    section("7. As 6 familias de KPI - o que sai destes dados e o que nao sai")
    table(["familia", "o que mede", "formula tipica", "referencia", "no artefato UE-TP"],
          [["Acessibilidade", "sucesso em estabelecer", "sucessos / tentativas x 100", "CSSR > 98%", "NAO (conceito)"],
           ["Retentabilidade", "quedas apos estabelecer", "drops / sessoes x 100", "DCR < 1%", "NAO (conceito)"],
           ["Integridade", "qualidade do fluxo", "thp, delay, perda, BLER", "latencia < 50 ms", "SIM (KPI-2, KPI-3)"],
           ["Disponibilidade", "tempo no ar", "t_up / t_total x 100", "SLA de outage", "NAO (celula sempre up)"],
           ["Utilizacao", "uso de recurso", "usado / capacidade x 100", "PRB < 60% bom, > 80% ruim", "SIM (KPI-1)"],
           ["Mobilidade", "handover / reselecao", "sucesso / tentativas x 100", "HOSR > 98%", "NAO (1 celula)"]],
          right=False)
    kv("por que isso importa", "declarar o que NAO da para medir e parte da entrega: sem os contadores, "
                               "afirmar acessibilidade ou mobilidade seria inventar numero")


# =============================================================================
# 8. Checkpoint 2 - a anatomia de cada indicador (slides 22 e 77)
# =============================================================================
def bloco_cp2(d, ctx, kqi, qos):
    section("8. Checkpoint 2 - anatomia dos indicadores (o entregavel)")
    info("Por indicador: nome, formula, unidade, granularidade, fonte, alvo/limiar, interpretacao, "
         "papel (KPI/KQI/QoS/proxy QoE) e limite de validade (slide 77).")
    carga, L = ctx["carga"], kqi["L"]
    fichas = [
        ("Utilizacao media de PRB UL", "media(RRU.PrbTotUl) por fase", "%", "amostra KPM, agregada por fase",
         "kpm.jsonl / kpm.sqlite - coluna RRU.PrbTotUl", f"alerta se media > {LIM['prb_sla']:g}%",
         "pressao de capacidade UL na celula", "KPI",
         "1 run, RFSIM, poucos UEs; PRB reportado ja vem como utilizacao (0-100)"),
        ("Vazao UL do UE (mediana)", "mediana(DRB.UEThpUl) por fase", "kbps", "amostra KPM, agregada por fase",
         "kpm.jsonl / kpm.sqlite - coluna DRB.UEThpUl", f"queda abaixo de {LIM['thp_keep']:g}x o baseline",
         "o servico esta entregando bits?", "KPI",
         "mediana escolhida por causa dos picos do RFSIM; a media da outro numero"),
        ("Atraso RLC DL (p95)", "p95(DRB.RlcSduDelayDl) por fase", "us", "amostra KPM, agregada por fase",
         "kpm.jsonl / kpm.sqlite - coluna DRB.RlcSduDelayDl", f"clausula didatica: p95 <= {f1(qos['alvo_dl'])} us",
         "cauda do atraso - o que o pior caso sente", "KPI de integridade",
         "atraso de RLC no DL, nao atraso fim-a-fim; nao inclui core nem transporte"),
        (f"Tempo em atraso alto (> {L:g} us)", f"n(delay > {L:g}) / n por fase", "%",
         "amostra KPM, agregada por fase", "derivado de DRB.RlcSduDelayDl",
         f"clausula didatica: <= {f1(qos['alvo_kqi'])}% do tempo",
         "fracao da janela em regime degradado", "KQI (e clausula de QoS quando L e o SLA)",
         "L e limiar de MUDANCA DE REGIME calibrado no baseline, nao requisito de aplicacao"),
    ]
    for nome, form, un, gran, fonte, alvo, interp, papel, lim in fichas:
        print(f"\n  {B}{nome}{RST}")
        for k, v in (("formula", form), ("unidade", un), ("granularidade", gran), ("fonte", fonte),
                     ("alvo / limiar", alvo), ("interpretacao", interp), ("papel", papel),
                     ("limite de validade", lim)):
            print(f"    {DIM}{k:<20}{RST} {v}")
    print()
    step("Checklist do CP2 (slide 77):")
    for item in ("cada indicador tem nome, formula, unidade, granularidade, fonte e interpretacao",
                 "cada indicador esta classificado como KPI, KQI, clausula de QoS ou proxy de QoE",
                 "1 grafico por KPI, com titulo, eixos, unidade e janela temporal",
                 f"o limiar esta justificado (aqui: L = {L:g} us, calibrado no {ctx['base']})",
                 "esta escrito que decisao o indicador habilita",
                 "estao declarados os limites: RFSIM, 1 run, sem RSRP/CQI, sem MOS"):
        print(f"    {DIM}[ ]{RST} {item}")
    if qos["violadas"]:
        kv("nesta rodada", f"clausulas violadas na fase '{carga}': {', '.join(qos['violadas'])} - "
                           "e esse contraste que vai para o checkpoint")


def main():
    ap = argparse.ArgumentParser(description="Aula 04 - medida -> KPI -> KQI -> QoS -> QoE sobre o KPM do lab")
    ap.add_argument("--file", required=True, help="kpm.jsonl, CSV largo ou CSV do kpm_analytics")
    a = ap.parse_args()

    rows, phases, fmt, inferred = load(a.file)
    d = Data(rows, phases)

    section("Aula 04 - Indicadores e qualidade: da medida a experiencia percebida")
    info("Cadeia do slide 55: medida (KPM) -> metrica -> KPI -> KQI -> QoS (SLA) -> QoE (proxy) -> decisao")
    kv("disciplina", "Analise de Dados em Redes de Telecom (Prof. Dr. Jonas A. Kunzler)")
    kv("slides", "aula04-kpis_kqis_qualidade.pdf, 25/08/2026")
    kv("dados", f"{a.file} ({len(rows)} amostras, {len(phases)} fases)")
    kv("unidades", "as do E2SM-KPM como o xApp do FlexRIC imprime: kbps, us, %")

    bloco_medida(d, fmt, inferred)
    ctx = bloco_kpi(d)
    kqi = bloco_kqi(d, ctx)
    qos = bloco_qos(d, ctx, kqi)
    bloco_qoe(d, ctx, kqi)
    diag = bloco_diagnostico(d, ctx)
    bloco_familias()
    bloco_cp2(d, ctx, kqi, qos)

    if qos["violadas"]:
        ver = (f"{len(qos['violadas'])} clausula(s) violada(s) na fase '{ctx['carga']}' "
               f"({', '.join(qos['violadas'])}); {pct(kqi['kqi_carga'])} do tempo acima de {kqi['L']:g} us. {diag}")
    else:
        ver = f"nenhuma clausula didatica violada na fase '{ctx['carga']}'. {diag}"
    print(f"\n{DIM}Veredito:{RST} {ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
