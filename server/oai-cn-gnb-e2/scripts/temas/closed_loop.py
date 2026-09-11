#!/usr/bin/env python3
"""closed_loop.py - o closed loop A1 das aulas 05 e 06, offline, sobre a telemetria KPM.

Disciplina "Analise de Dados em Redes de Telecom" (Prof. Dr. Jonas A. Kunzler,
CESAR School). Aula 05 (27/08/2026, aula05-closed-loop-a1-open-ran.pdf) e
Aula 06 (03/09/2026, aula06-consolidacao_projetos.pdf).

O deck fecha o laco que o projeto so recomenda:

    KPM E2 -> store -> MAD -> decision -> policy A1 -> PMS/Mediator -> consumer
           -> action_request -> actuator -> KPM after -> effect_report -> rollback

e a aula 06 o demonstra num roteiro de 8 passos (slide 23): pre-checagem,
baseline calmo, stress, decisao, A1, atuacao, after + report, rollback.

Este script percorre os 8 passos com os DADOS de verdade (os mesmos dos 7
temas), no mesmo formato dos artefatos do lab do professor
(oai-cn-gnb-nonrt-nearrt: model.json, decision.json, policy.json,
action_request.json, actuator_events.jsonl, effect_report.json), e para cada
passo diz o que aconteceria ao vivo e o que aconteceu aqui.

O QUE ESTE MODO NAO FAZ (e diz isso na tela):
  * nao executa nada: o rate-limit (tc tbf na oaitun_ue1) e o rollback sao
    impressos, nunca rodados - este arquivo nem importa subprocess;
  * nao envia a politica ao PMS nem passa por A1 Mediator/RMR/consumer;
  * o "depois" do effect_report e a fase seguinte do MESMO experimento
    (recovery), gravada sem rate-limit nenhum. A diferenca antes/depois NAO e
    efeito da atuacao. O modo offline do lab do professor faz a mesma troca
    (run_closed_loop_lab.sh --offline: "after ~ baseline"); aqui ela vem
    escrita no relatorio ("causal": false), porque e exatamente a pergunta do
    slide 73: uma KPM nova e diferente, sozinha, prova causalidade?

Decisao: a regra do ai_policy_pipeline.py do professor - janela das ultimas
TEMA_WINDOW amostras da fase de carga, "apply" se a MAIORIA dos votos for
anomala (score > TEMA_SCORE_THR em >= TEMA_MIN_FEAT metricas). O p2-tema-t2 e
mais exigente (janela inteira anomala).

Uso:
    closed_loop.py --file kpm.jsonl|kpm.csv [--out DIR]

Ambiente (impresso na saida):
    TEMA_MAD_FLOOR / TEMA_SCORE_THR / TEMA_MIN_FEAT / TEMA_WINDOW  [1.0/3.5/2/5]
    CL_RATE_KBIT   limite de subida da politica emulada, em kbit/s    [8000]
    CL_IFACE       interface do UE onde o tc atuaria ao vivo          [oaitun_ue1]

Somente biblioteca padrao (roda no servidor ARM64 sem venv).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from temas_projeto import (  # noqa: E402  (o sys.path acima e proposital)
    B, DIM, RST, Data, env_f, f1, formula, info, kv, load, mad, mean, median,
    ok, section, step, table, warn,
)
from temas_projeto import LIM as LIM_TEMAS  # noqa: E402

FEATS = [("thp", "DRB.UEThpUl", "kbps"), ("delay", "DRB.RlcSduDelayDl", "us"), ("prb", "RRU.PrbTotUl", "%")]
NOME = {k: n for k, n, _ in FEATS}

CFG = {
    "score_threshold": LIM_TEMAS["score_thr"],
    "min_anomalous_features": LIM_TEMAS["min_feat"],
    "mad_floor": LIM_TEMAS["mad_floor"],
    "window": LIM_TEMAS["window"],
    "rate_kbit": int(env_f("CL_RATE_KBIT", 8000)),
    "iface": os.environ.get("CL_IFACE", "oaitun_ue1"),
    "policytype_id": "1",
    "ric_id": "ric-oran",
    "service_id": "closed-loop-ue-tp-rapp",
}

# A execucao AO VIVO mostrada nos slides (run 20260827T1207Z, modo emulate):
# numeros copiados dos slides 24-28 e 67-73 da aula 05, nao recalculados aqui.
AULA = {
    "thp": {"antes_media": 135.8, "antes_mediana": 84.1, "depois_media": 39.0, "depois_mediana": 8.08, "u": "Mbit/s"},
    "prb": {"antes_media": 91.5, "antes_mediana": 99.0, "depois_media": 18.1, "depois_mediana": 19.0, "u": "%"},
    "artefato": {"thp_rel": -71.26, "prb_rel": -80.24, "prb_pp": -73.42},
    "iperf_mbit": 7.81, "alvo_mbit": 8.0,
}


def rel(antes, depois):
    """Variacao relativa em %, ou None quando o 'antes' e zero."""
    return None if not antes else 100.0 * (depois - antes) / antes


def fpct(x):
    return "-" if x is None else f"{x:+.1f}%"


def agora():
    return datetime.now().astimezone().isoformat(timespec="seconds")


# ---- os calculos (sem impressao: e o que os testes conferem) ----------------
def fases(phases):
    """baseline = 1a fase; carga ('antes') = 2a; 'depois' = 3a, se houver."""
    return (phases[0],
            phases[1] if len(phases) > 1 else None,
            phases[2] if len(phases) > 2 else None)


def treinar(d, base):
    feats = {}
    for k, nome, _ in FEATS:
        v = d.col(k, base)
        m = median(v)
        feats[nome] = {"median": m, "mad": mad(v), "min": min(v), "max": max(v)}
    return {"schema_version": 1, "algorithm": "robust-baseline-mad", "trained_at": agora(),
            "training_phase": base, "sample_count": d.n(base), "features": feats,
            "score_threshold": CFG["score_threshold"],
            "min_anomalous_features": CFG["min_anomalous_features"],
            "mad_floor": CFG["mad_floor"]}


def inferir(model, amostra):
    scores, anomalas = {}, []
    for k, nome, _ in FEATS:
        f = model["features"][nome]
        s = abs(amostra[k] - f["median"]) / max(f["mad"], model["mad_floor"])
        scores[nome] = s
        if s > model["score_threshold"]:
            anomalas.append(nome)
    decisao = "apply" if len(anomalas) >= model["min_anomalous_features"] else "observe"
    return {"decision": decisao, "anomalous_features": anomalas, "scores": scores,
            "sample": {nome: amostra[k] for k, nome, _ in FEATS}}


def avaliar(d, carga, model):
    janela = d.by[carga][-CFG["window"]:]
    votos = [inferir(model, a) for a in janela]
    n_apply = sum(1 for v in votos if v["decision"] == "apply")
    return {"evaluated_at": agora(), "phase": carga, "window_size": len(janela),
            "apply_votes": n_apply,
            "decision": "apply" if n_apply > len(janela) / 2 else "observe",
            "rule": "apply se votos 'apply' > metade da janela (ai_policy_pipeline.py)",
            "latest": votos[-1] if votos else None,
            "decision_id": str(uuid.uuid4())}


def politica(avaliacao, run_id):
    if avaliacao["decision"] != "apply":
        return None
    return {"policy_id": f"cl-ue-tp-{run_id}", "policytype_id": CFG["policytype_id"],
            "ric_id": CFG["ric_id"], "service_id": CFG["service_id"],
            "policy_data": {"scope": {"ueId": "ue-any", "qosId": "qos-lab"},
                            "qosObjectives": {"priorityLevel": 10}},
            "actuation": {"mode": "emulate", "emulate": {"rate_kbit": CFG["rate_kbit"],
                                                         "iface_prefix": CFG["iface"].rstrip("0123456789")}},
            "lab_context": {"decision_id": avaliacao["decision_id"],
                            "anomalous_features": (avaliacao["latest"] or {}).get("anomalous_features", [])}}


def pedido_de_acao(pol):
    return {"action_id": str(uuid.uuid4()), "action": "rate_limit", "mode": "emulate",
            "parameters": {"rate_kbit": CFG["rate_kbit"]},
            "target": {"interface": CFG["iface"], "direction": "uplink"},
            "policy_id": pol["policy_id"], "decision_id": pol["lab_context"]["decision_id"]}


def comandos_tc(iface, rate):
    return {"apply": f"sudo tc qdisc add dev {iface} root tbf rate {rate}kbit burst 32kbit latency 400ms",
            "rollback": f"sudo tc qdisc del dev {iface} root"}


def efeito(d, carga, depois, offline=True):
    def resumo(fase):
        return {nome: {"count": d.n(fase), "mean": mean(d.col(k, fase)), "median": median(d.col(k, fase))}
                for k, nome, _ in FEATS}
    antes_s, depois_s = resumo(carga), resumo(depois)
    rep = {"generated_at": agora(), "mode": "offline" if offline else "emulate",
           "before_phase": carga, "after_phase": depois,
           "before": antes_s, "after": depois_s,
           "delta_mean": {}, "relative_delta_mean_pct": {}, "relative_delta_median_pct": {},
           "delta_pp_mean": {NOME["prb"]: depois_s[NOME["prb"]]["mean"] - antes_s[NOME["prb"]]["mean"]},
           "causal": not offline}
    for _, nome, _u in FEATS:
        b, a = antes_s[nome], depois_s[nome]
        rep["delta_mean"][nome] = a["mean"] - b["mean"]
        rep["relative_delta_mean_pct"][nome] = rel(b["mean"], a["mean"])
        rep["relative_delta_median_pct"][nome] = rel(b["median"], a["median"])
    if offline:
        rep["note"] = (f"OFFLINE: 'after' e a fase '{depois}' do mesmo experimento, gravada sem rate-limit. "
                       "A diferenca nao e efeito da atuacao (nenhum tc foi executado).")
    return rep


def recuperacao(x_antes, x_atuacao, x_pos_rollback):
    """Fracao recuperada apos o rollback: 1.0 = voltou ao nivel de antes da atuacao."""
    faixa = x_antes - x_atuacao
    return None if not faixa else (x_pos_rollback - x_atuacao) / faixa


# ---- a narrativa na tela ----------------------------------------------------
def js(obj):
    for linha in json.dumps(obj, ensure_ascii=False, indent=2).splitlines():
        print(f"    {DIM}{linha}{RST}")


def main():
    ap = argparse.ArgumentParser(description="Aulas 05-06 - closed loop A1 offline sobre o KPM do lab")
    ap.add_argument("--file", required=True, help="kpm.jsonl, CSV largo ou CSV do kpm_analytics")
    ap.add_argument("--out", help="diretorio onde gravar os artefatos (model.json, decision.json, ...)")
    a = ap.parse_args()

    rows, phases, fmt, inferred = load(a.file)
    d_ue = Data(rows, phases)
    d = d_ue.celula() if d_ue.multi else d_ue
    run_id = datetime.now().strftime("%Y%m%dT%H%M%S")
    base, carga, depois = fases(phases)
    eventos, artefatos = [], {}

    def evento(nome, **campos):
        eventos.append({"ts": agora(), "event": nome, **campos})

    section("Aulas 05-06 - Closed loop A1: telemetria -> decisao -> policy -> atuacao -> evidencia")
    info("Roteiro da demo (slide 23 da aula 06), passo a passo, com os artefatos do lab do professor.")
    kv("disciplina", "Analise de Dados em Redes de Telecom (Prof. Dr. Jonas A. Kunzler)")
    kv("slides", "aula05-closed-loop-a1-open-ran.pdf (27/08) · aula06-consolidacao_projetos.pdf (03/09)")
    kv("modo", f"{B}OFFLINE{RST}: nada e aplicado na RAN; cada passo diz o que aconteceria ao vivo")
    kv("run_id", run_id)
    from cenarios_kpm import explicar
    explicar(d_ue, d, "closed")

    # 1 -----------------------------------------------------------------------
    section("1. Pre-checagem")
    info("Ao vivo o roteiro exige: Near-RT RIC no ar, PMS respondendo em /a1-policy/v2/status, xApp rodando, nrUE com oaitun_ue1.")
    ok("offline nenhum deles e necessario: a entrada e o arquivo de medicoes")
    kv("dados", f"{a.file} ({len(rows)} amostras, formato {fmt})")
    kv("fases", " · ".join(f"{p} ({d.n(p)})" for p in phases))
    if inferred:
        warn("o arquivo nao tem coluna de fase: as primeiras 20% viraram baseline e o resto 'observacao'")
    kv("papeis", f"baseline = '{base}' · antes (carga) = '{carga or '-'}' · depois = '{depois or '-'}'")
    kv("contrato", f"score > {CFG['score_threshold']:g} em >= {CFG['min_anomalous_features']} metricas; "
                   f"janela {CFG['window']}; piso do MAD {CFG['mad_floor']:g}")

    # 2 -----------------------------------------------------------------------
    section("2. Baseline calmo: treino do MAD")
    info("Ao vivo: KPM_TRAFFIC=0, sem iperf. O baseline tem de descrever o normal; treinado com carga, a anomalia vira referencia.")
    formula("MAD", "MAD = mediana(|x - mediana(x)|), por metrica, so no baseline", "unidade da metrica")
    formula("score", f"score = |x - mediana_baseline| / max(MAD, {CFG['mad_floor']:g})", "adimensional")
    model = treinar(d, base)
    table(["metrica", "unidade", "mediana", "MAD", "MAD efetivo"],
          [[nome, u, f1(model["features"][nome]["median"]), f1(model["features"][nome]["mad"]),
            f1(max(model["features"][nome]["mad"], CFG["mad_floor"]))] for _, nome, u in FEATS])
    if any(model["features"][n]["mad"] == 0 for _, n, _u in FEATS):
        warn(f"MAD 0 em alguma metrica: o piso {CFG['mad_floor']:g} evita divisao por zero e deixa o score enorme sob carga")
    artefatos["model.json"] = model

    if carga is None:
        warn("os dados tem uma fase so: sem janela de carga, nao ha o que decidir")
        print("\nVeredito: dados sem fase de carga - o loop para no treino")
        return 0

    # 3 -----------------------------------------------------------------------
    section("3. Stress: a janela 'antes'")
    info("Ao vivo: iperf UDP de subida pela oaitun_ue1 e captura do kpm_before. Aqui: a fase de carga do arquivo.")
    table(["metrica", f"baseline mediana", f"'{carga}' media", f"'{carga}' mediana"],
          [[nome, f1(median(d.col(k, base))), f1(mean(d.col(k, carga))), f1(median(d.col(k, carga)))] for k, nome, _ in FEATS])

    # 4 -----------------------------------------------------------------------
    section("4. Decisao: MAD -> decision.json")
    formula("regra de decisao", f"apply se votos 'apply' > {CFG['window']}/2 nas ultimas {CFG['window']} amostras de '{carga}'", "-")
    info("E a regra do ai_policy_pipeline.py do professor; o p2-tema-t2 exige a janela inteira anomala.")
    aval = avaliar(d, carga, model)
    lat = aval["latest"]
    table(["metrica", "ultima amostra", "score", "anomala?"],
          [[nome, f1(lat["sample"][nome]), f1(lat["scores"][nome]), "sim" if nome in lat["anomalous_features"] else "nao"]
           for _, nome, _u in FEATS])
    kv("votos", f"{aval['apply_votes']}/{aval['window_size']} amostras 'apply' na janela")
    kv("decision_id", aval["decision_id"])
    artefatos["decision.json"] = {"evaluation": aval, "policy": None}
    evento("decision", decision=aval["decision"], votes=aval["apply_votes"], window=aval["window_size"])
    if aval["decision"] != "apply":
        ok("decision = observe: sem politica, sem atuacao. Um laco que nao age quando nao precisa tambem e um laco que funciona.")
        _grava(a.out, artefatos, eventos)
        print(f"\nVeredito: decision observe ({aval['apply_votes']}/{aval['window_size']} votos) - nada a aplicar")
        return 0
    warn(f"decision = apply ({aval['apply_votes']}/{aval['window_size']} votos): a carga saiu do normal de forma sustentada")

    # 5 -----------------------------------------------------------------------
    section("5. A1: policy -> PMS -> A1 Mediator -> consumer")
    pol = politica(aval, run_id)
    artefatos["decision.json"]["policy"] = pol
    artefatos["policy.json"] = pol
    step("Policy A1 candidata (DRY-RUN: nao foi enviada ao PMS):")
    js(pol)
    info("Ao vivo: PUT /a1-policy/v2/policies no PMS -> A1 Mediator -> RMR 20010 -> consumer valida -> RMR 20011 -> ENFORCED.")
    info("No nosso P2 o p2-test-a1 prova o trecho PMS -> A1 -> simulador (a1-sim); nao temos A1 Mediator, RMR nem consumer.")
    warn("ENFORCED prova aceitacao no caminho A1, nao mutacao no gNB (slide 21 da aula 06)")
    evento("a1_dry_run", policy_id=pol["policy_id"], policytype_id=pol["policytype_id"])

    # 6 -----------------------------------------------------------------------
    section("6. Atuacao: action_request -> actuator")
    acao = pedido_de_acao(pol)
    artefatos["action_request.json"] = acao
    step("action_request (a traducao concreta da policy):")
    js(acao)
    tc = comandos_tc(CFG["iface"], CFG["rate_kbit"])
    kv("ao vivo seria", tc["apply"])
    info("tbf na saida da oaitun_ue1 = o que o UE manda para a rede: limita a subida (ACTUATION_MODE=emulate).")
    ok("offline: comando NAO executado (dry-run)")
    evento("emulate_dry_run", action="tc-tbf", iface=CFG["iface"], rate_kbit=CFG["rate_kbit"], action_id=acao["action_id"])
    kv("correlacao", f"decision {aval['decision_id'][:8]}… -> policy {pol['policy_id']} -> action {acao['action_id'][:8]}…")
    info("decision != policy != action_request != actuation: cada camada tem dono, contrato e evidencia (slide 22 da aula 06).")

    # 7 -----------------------------------------------------------------------
    section("7. Depois: nova KPM e effect_report")
    if depois is None:
        warn("os dados nao tem uma fase depois da carga: sem 'after', nao ha effect_report")
        print("\nVeredito: cadeia ate a atuacao em dry-run; sem janela 'depois', o efeito nao pode ser medido")
        _grava(a.out, artefatos, eventos)
        return 0
    rep = efeito(d, carga, depois, offline=True)
    artefatos["effect_report.json"] = rep
    formula("variacao relativa (relative_delta)", "100 * (media_depois - media_antes) / media_antes", "%")
    formula("variacao absoluta de uma porcentagem", "media_depois - media_antes", "pp (pontos percentuais)")
    table(["metrica", "antes media", "depois media", "delta", "relativo (media)", "relativo (mediana)"],
          [[nome, f1(rep["before"][nome]["mean"]), f1(rep["after"][nome]["mean"]), f1(rep["delta_mean"][nome]),
            fpct(rep["relative_delta_mean_pct"][nome]), fpct(rep["relative_delta_median_pct"][nome])] for _, nome, _u in FEATS])
    kv("PRB em pp", f"{rep['delta_pp_mean'][NOME['prb']]:+.1f} pp  (nao confundir com o {fpct(rep['relative_delta_mean_pct'][NOME['prb']])} relativo)")
    print()
    warn(f"{B}NAO E EFEITO DA ATUACAO.{RST} O 'depois' e a fase '{depois}' do mesmo experimento, gravada sem rate-limit:")
    warn("a queda e a carga que acabou. effect_report.json sai com \"causal\": false.")
    info("E a pergunta do slide 73: uma KPM nova e diferente, sozinha, prova causalidade? Nao - precisa de antes/depois")
    info("com a acao aplicada, uma medida independente (iperf contra o alvo) e a recuperacao depois do rollback.")
    evento("effect_report", causal=False, before_phase=carga, after_phase=depois,
           relative_delta_mean_pct=rep["relative_delta_mean_pct"])

    step("Referencia: a execucao AO VIVO dos slides (aula 05, slides 24-28 e 67-73; numeros do slide, nao recalculados)")
    t, p = AULA["thp"], AULA["prb"]
    table(["metrica", "antes media", "antes mediana", "depois media", "depois mediana", "relativo (media)", "relativo (mediana)"],
          [["DRB.UEThpUl (Mbit/s)", f1(t["antes_media"]), f"{t['antes_mediana']:g}", f1(t["depois_media"]), f"{t['depois_mediana']:g}",
            fpct(rel(t["antes_media"], t["depois_media"])), fpct(rel(t["antes_mediana"], t["depois_mediana"]))],
           ["RRU.PrbTotUl (%)", f1(p["antes_media"]), f"{p['antes_mediana']:g}", f1(p["depois_media"]), f"{p['depois_mediana']:g}",
            fpct(rel(p["antes_media"], p["depois_media"])), fpct(rel(p["antes_mediana"], p["depois_mediana"]))]])
    kv("artefato da aula", f"UEThp {AULA['artefato']['thp_rel']:+.2f}% · PRB {AULA['artefato']['prb_rel']:+.2f}% "
                           f"relativo · PRB {AULA['artefato']['prb_pp']:+.2f} pp")
    kv("aderencia ao alvo", f"iperf {AULA['iperf_mbit']:g} / alvo {AULA['alvo_mbit']:g} Mbit/s = "
                            f"{100 * AULA['iperf_mbit'] / AULA['alvo_mbit']:.1f}% (medida independente da KPM)")
    info("Media x mediana: a 1a amostra de cada serie e um transiente (~705 antes, ~380 depois, no grafico) e puxa a media; "
         "com n = 12, a mediana descreve o regime.")

    # 8 -----------------------------------------------------------------------
    section("8. Rollback e verificacao")
    kv("ao vivo seria", tc["rollback"])
    ok("offline: comando NAO executado (dry-run)")
    formula("recuperacao", "100 * (x_pos_rollback - x_com_acao) / (x_antes - x_com_acao)", "% (100% = voltou ao nivel de antes)")
    info("Precisa de uma 4a janela, depois do rollback; o arquivo nao tem, entao a recuperacao nao e medida aqui.")
    evento("rollback_dry_run", action="tc-del", iface=CFG["iface"])

    # SEHAL ---------------------------------------------------------------------
    section("Recomendacao no molde SEHAL (aula 05, slide 34)")
    prb_b, prb_c = median(d.col("prb", base)), median(d.col("prb", carga))
    thp_b, thp_c = median(d.col("thp", base)), median(d.col("thp", carga))
    sobem_juntos = prb_c > prb_b and thp_c > thp_b
    kv("S  Situacao", f"na fase '{carga}', PRB UL mediano {f1(prb_c)}% e vazao UL mediana {f1(thp_c)} kbps "
                      f"(baseline: {f1(prb_b)}% e {f1(thp_b)} kbps)")
    kv("E  Evidencia", f"{aval['apply_votes']}/{aval['window_size']} votos 'apply'; anomalas na ultima amostra: "
                       f"{', '.join(lat['anomalous_features']) or 'nenhuma'}")
    kv("H  Hipotese", "capacidade: PRB e vazao sobem juntos; interferencia descartada por falta de KPI espectral"
                      if sobem_juntos else "a hipotese de capacidade nao fecha (PRB e vazao nao sobem juntos): investigar canal/RF")
    kv("A  Acao", f"policy {pol['policy_id']} (priorityLevel 10) + rate_limit {CFG['rate_kbit']} kbit na {CFG['iface']}, em dry-run")
    sint = bool(rows and rows[0].get("cenario"))
    kv("L  Limitacao", "offline: nada foi aplicado e o 'depois' e outra fase; "
                       + (f"DADOS SINTETICOS ({d.n_ue} celular(es), cenario sugerido pelo servidor); " if sint
                          else ("RFSIM, 1 UE; " if d.n_ue == 1 else f"RFSIM, {d.n_ue} UEs; "))
                       + "unidade do atraso em disputa no curso (us no log da aula 01, ms nas aulas 04-06)")

    _grava(a.out, artefatos, eventos)
    print(f"\nVeredito: cadeia completa em dry-run - decision apply ({aval['apply_votes']}/{aval['window_size']}), "
          f"policy {pol['policy_id']}, rate_limit {CFG['rate_kbit']} kbit; effect_report nao causal (fases diferentes)")
    return 0


def _grava(out, artefatos, eventos):
    if not out:
        return
    os.makedirs(out, exist_ok=True)
    for nome, conteudo in artefatos.items():
        with open(os.path.join(out, nome), "w", encoding="utf-8") as fh:
            json.dump(conteudo, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(out, "actuator_events.jsonl"), "w", encoding="utf-8") as fh:
        for e in eventos:
            fh.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")
    section("Artefatos gravados")
    kv("diretorio", out)
    kv("arquivos", " · ".join(list(artefatos) + ["actuator_events.jsonl"]))


if __name__ == "__main__":
    sys.exit(main())
