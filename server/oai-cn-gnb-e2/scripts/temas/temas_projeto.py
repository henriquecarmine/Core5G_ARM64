#!/usr/bin/env python3
"""temas_projeto.py - os 7 temas do Projeto Integrador sobre a telemetria KPM.

Disciplina "Analise de Dados em Redes de Telecom" (Prof. Dr. Jonas A. Kunzler,
CESAR School). Todos os grupos usam os MESMOS dados (KPM do lab
oai-cn-gnb-nonrt-nearrt: DRB.UEThpUl, DRB.RlcSduDelayDl, RRU.PrbTotUl, com as
fases baseline / stress / recovery). O que muda de um tema para o outro e a
pergunta, os 2 indicadores e a recomendacao (politica A1 so em dry-run).

Este script calcula, para cada tema, os 2 indicadores obrigatorios do card do
professor (temas-grupos.md), imprime as formulas usadas, a leitura e a
recomendacao candidata. Nada aqui atua na RAN: e analise.

Uso:
    temas_projeto.py --tema t1|t2|...|t7|all [--file kpm.jsonl|kpm.csv]

Entrada aceita (detectada pelo conteudo, nao pela extensao):
  * JSONL do professor: 1 objeto por linha com "metrics": {"DRB.UEThpUl":..,
    "DRB.RlcSduDelayDl":.., "RRU.PrbTotUl":..}, "phase", "run_id", "sample_index".
  * CSV largo: cabecalho com thp_ul, delay_dl, prb_ul (ou os nomes KPM), e
    opcionalmente phase, run_id, sample_index, ue.
  * CSV longo do kpm_analytics.sh (seq,latency_us,ue,measName,value,unit,slice):
    e pivotado por seq (dado REAL coletado da nossa RAN).
Sem coluna de fase, as primeiras 20% amostras viram "baseline" e o resto
"observacao" (o script avisa).

Limiares (todos ajustaveis por variavel de ambiente, impressos na saida):
  TEMA_DELAY_MAX   atraso RLC DL acima do qual consideramos degradacao (us)  [100]
  TEMA_PRB_HIGH    fracao do PRB maximo observado que conta como "radio cheio" [0.8]
  TEMA_THP_LOW     fracao do p95 da vazao abaixo da qual e "vazao baixa"     [0.5]
  TEMA_LOW_LOAD    fracao (do PRB max e do p95 da vazao) que define baixa carga [0.1]
  TEMA_MAD_FLOOR / TEMA_SCORE_THR / TEMA_MIN_FEAT / TEMA_WINDOW  (metodo do
    model.json do professor: robust-baseline-mad)                [1.0/3.5/2/5]
  TEMA_PERSIST     amostras consecutivas para um acionamento "sustentado"   [3]

Somente biblioteca padrao (roda no servidor ARM64 sem venv).
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import sys
from collections import OrderedDict

# ---- colorimetria (mesma paleta do lib/testlog.sh) --------------------------
RST, B, DIM = "\033[0m", "\033[1m", "\033[90m"
RED, GRN, YEL, BLU, CYN = "\033[31m", "\033[32m", "\033[33m", "\033[34m", "\033[36m"


def section(t): print(f"\n{B}{CYN}── {t} ──{RST}")
def ok(t): print(f"{GRN}✓{RST} {t}")
def warn(t): print(f"{YEL}!{RST} {t}")
def err(t): print(f"{RED}✗{RST} {t}")
def info(t): print(f"{BLU}•{RST} {t}")
def step(t): print(f"{CYN}→{RST} {t}")
def kv(k, v): print(f"  {DIM}{k:<22}{RST} {v}")
def formula(nome, expr, unidade): print(f"  {B}{nome}{RST}\n      {expr}   {DIM}[{unidade}]{RST}")


def table(head, rows, right=True):
    """Tabela alinhada, primeira coluna a esquerda, demais a direita."""
    cols = [head] + [[str(c) for c in r] for r in rows]
    w = [max(len(r[i]) for r in cols) for i in range(len(head))]
    def fmt(r, bold=False):
        cells = [r[0].ljust(w[0])] + [(r[i].rjust(w[i]) if right else r[i].ljust(w[i]))
                                      for i in range(1, len(r))]
        line = "  " + "  ".join(cells)
        return f"{B}{line}{RST}" if bold else line
    print(fmt(cols[0], True))
    for r in cols[1:]:
        print(fmt(r))


# ---- estatistica (stdlib) --------------------------------------------------
def mean(v): return sum(v) / len(v) if v else float("nan")
def median(v):
    s = sorted(v); n = len(s)
    if not n: return float("nan")
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2
def pctl(v, p):
    """Percentil com interpolacao linear (o mesmo default do pandas)."""
    s = sorted(v); n = len(s)
    if not n: return float("nan")
    if n == 1: return s[0]
    k = (n - 1) * p / 100.0; f = math.floor(k); c = min(f + 1, n - 1)
    return s[f] + (s[c] - s[f]) * (k - f)
def mad(v):
    m = median(v); return median([abs(x - m) for x in v])
def pearson(x, y):
    n = len(x)
    if n < 2: return None
    mx, my = mean(x), mean(y)
    sxx = sum((a - mx) ** 2 for a in x); syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0: return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / math.sqrt(sxx * syy)
def movavg(v, w):
    out = []
    for i in range(len(v)):
        j = max(0, i - w + 1); out.append(mean(v[j:i + 1]))
    return out
def frac(mask): return (sum(1 for m in mask if m) / len(mask)) if mask else float("nan")
def f1(x): return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:,.1f}".replace(",", " ")
def f3(x): return "-" if x is None else f"{x:.3f}"
def pct(x): return "-" if x is None or math.isnan(x) else f"{100 * x:.0f}%"


# ---- leitura dos dados -----------------------------------------------------
KPM = {"thp": ["thp_ul", "DRB.UEThpUl", "throughput", "thp", "vazao"],
       "delay": ["delay_dl", "DRB.RlcSduDelayDl", "delay", "atraso", "latency"],
       "prb": ["prb_ul", "RRU.PrbTotUl", "prb", "PrbTotUl"]}
PHASE_ORDER = ["baseline", "stress", "recovery"]


def _pick(d, names):
    low = {k.lower(): k for k in d}
    for n in names:
        if n.lower() in low:
            return d[low[n.lower()]]
    return None


def _num(x):
    try: return float(x)
    except (TypeError, ValueError): return None


def load(path):
    text = open(path, encoding="utf-8-sig").read()
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        raise SystemExit("arquivo vazio")
    rows, fmt = [], None
    if lines[0].lstrip().startswith("{"):
        fmt = "jsonl"
        for i, l in enumerate(lines):
            try: o = json.loads(l)
            except json.JSONDecodeError: continue
            m = o.get("metrics", o)
            thp, dl, prb = _pick(m, KPM["thp"]), _pick(m, KPM["delay"]), _pick(m, KPM["prb"])
            if thp is None or dl is None or prb is None: continue
            rows.append({"thp": float(thp), "delay": float(dl), "prb": float(prb),
                         "phase": o.get("phase"), "run": o.get("run_id", "-"),
                         "idx": o.get("sample_index", i), "ue": o.get("ue", o.get("ue_id", "-"))})
    else:
        rd = list(csv.DictReader(io.StringIO("\n".join(lines))))
        hdr = [h.strip() for h in (rd[0].keys() if rd else [])]
        if "measName" in hdr and "value" in hdr:          # CSV longo do kpm_analytics.sh
            fmt = "csv-longo (kpm_analytics)"
            piv = OrderedDict()
            for r in rd:
                key = (r.get("seq", "0"), r.get("ue", "-"))
                piv.setdefault(key, {})[r["measName"].strip()] = _num(r.get("value"))
            for i, ((seq, ue), m) in enumerate(piv.items()):
                thp, dl, prb = _pick(m, KPM["thp"]), _pick(m, KPM["delay"]), _pick(m, KPM["prb"])
                if thp is None or prb is None: continue
                rows.append({"thp": thp, "delay": dl if dl is not None else 0.0, "prb": prb,
                             "phase": None, "run": "kpm-real", "idx": _num(seq) or i, "ue": ue})
        else:                                               # CSV largo (colar/arquivo)
            fmt = "csv"
            for i, r in enumerate(rd):
                thp, dl, prb = _num(_pick(r, KPM["thp"])), _num(_pick(r, KPM["delay"])), _num(_pick(r, KPM["prb"]))
                if thp is None or dl is None or prb is None: continue
                ph = _pick(r, ["phase", "fase"]); run = _pick(r, ["run_id", "run"]) or "-"
                idx = _num(_pick(r, ["sample_index", "seq", "idx", "t"]))
                rows.append({"thp": thp, "delay": dl, "prb": prb, "phase": (ph or "").strip() or None,
                             "run": run, "idx": idx if idx is not None else i, "ue": _pick(r, ["ue", "ue_id"]) or "-"})
    if not rows:
        raise SystemExit("nenhuma amostra com as 3 metricas (thp_ul, delay_dl, prb_ul) encontrada")
    inferred = False
    if any(r["phase"] is None for r in rows):
        inferred = True
        nb = max(1, int(round(0.2 * len(rows))))
        for i, r in enumerate(rows):
            if r["phase"] is None:
                r["phase"] = "baseline" if i < nb else "observacao"
    phases = [p for p in PHASE_ORDER if any(r["phase"] == p for r in rows)]
    phases += [p for p in OrderedDict((r["phase"], 1) for r in rows) if p not in phases]
    rows.sort(key=lambda r: (phases.index(r["phase"]), r["idx"] if isinstance(r["idx"], (int, float)) else 0))
    return rows, phases, fmt, inferred


class Data:
    def __init__(self, rows, phases):
        self.rows, self.phases = rows, phases
        self.by = {p: [r for r in rows if r["phase"] == p] for p in phases}
    def col(self, k, phase=None):
        src = self.by[phase] if phase else self.rows
        return [r[k] for r in src]
    def n(self, p): return len(self.by[p])


# ---- limiares ----------------------------------------------------------------
def env_f(name, default):
    try: return float(os.environ.get(name, default))
    except ValueError: return default


LIM = {
    "delay_max": env_f("TEMA_DELAY_MAX", 100.0),
    "prb_high": env_f("TEMA_PRB_HIGH", 0.8),
    "thp_low": env_f("TEMA_THP_LOW", 0.5),
    "low_load": env_f("TEMA_LOW_LOAD", 0.1),
    "mad_floor": env_f("TEMA_MAD_FLOOR", 1.0),
    "score_thr": env_f("TEMA_SCORE_THR", 3.5),
    "min_feat": int(env_f("TEMA_MIN_FEAT", 2)),
    "window": int(env_f("TEMA_WINDOW", 5)),
    "persist": int(env_f("TEMA_PERSIST", 3)),
}


def thresholds(d):
    """Limiares absolutos derivados dos dados (impressos para o aluno ver)."""
    prb_max = max(d.col("prb")); thp_p95 = pctl(d.col("thp"), 95)
    return {"prb_high": LIM["prb_high"] * prb_max, "thp_low": LIM["thp_low"] * thp_p95,
            "prb_low": LIM["low_load"] * prb_max, "thp_lowload": LIM["low_load"] * thp_p95,
            "delay_max": LIM["delay_max"], "prb_max": prb_max, "thp_p95": thp_p95}


def a1_dryrun(nome, scope, objetivo, motivo):
    """Politica A1 candidata no formato do decision.json do professor (dry-run)."""
    pol = {"policy_id": f"{nome}-candidata", "policytype_id": "1", "ric_id": "ric-oran",
           "service_id": "analise-dados-rapp", "actuation": {"mode": "emulate"},
           "policy_data": {"scope": scope, "qosObjectives": objetivo}, "lab_context": {"motivo": motivo}}
    step("Politica A1 candidata (DRY-RUN, nada e aplicado na RAN):")
    for l in json.dumps(pol, ensure_ascii=False, indent=2).splitlines():
        print(f"    {DIM}{l}{RST}")


def cabecalho_tema(n, titulo, pergunta, onde):
    section(f"Tema {n} - {titulo}")
    info(f"Pergunta do card: {pergunta}")
    kv("Onde no O-RAN", onde)


# =============================================================================
# T1 - Vazao do usuario (UE-TP)
# =============================================================================
def t1(d, th):
    cabecalho_tema(1, "Vazao do usuario (UE-TP)",
                   "a vazao do UE sobe ou desce junto com o uso de PRB e com o atraso?",
                   "gNB (E2SM-KPM) -> xApp -> arquivo; a analise roda no painel; a politica iria pelo A1")
    step("Formulas dos 2 indicadores")
    formula("I1  Vazao UL por fase", "media(thp_ul) e p95(thp_ul), agrupando por fase", "kbps")
    formula("I2  Utilizacao de PRB UL por fase", "media(prb_ul), agrupando por fase", "% dos PRB")
    rows = []
    for p in d.phases:
        t = d.col("thp", p); pr = d.col("prb", p)
        rows.append([p, d.n(p), f1(mean(t)), f1(median(t)), f1(pctl(t, 95)), f1(mean(pr))])
    table(["fase", "n", "vazao media", "mediana", "p95", "PRB medio"], rows)
    step("Relacao entre as metricas (correlacao de Pearson, r = cov(x,y) / (sx * sy))")
    g_pr = pearson(d.col("thp"), d.col("prb")); g_dl = pearson(d.col("thp"), d.col("delay"))
    kv("global (todas as fases)", f"vazao x PRB = {f3(g_pr)}   vazao x atraso = {f3(g_dl)}")
    rows = []
    for p in d.phases:
        cp = pearson(d.col("thp", p), d.col("prb", p)); cd = pearson(d.col("thp", p), d.col("delay", p))
        rows.append([p, f3(cp) if cp is not None else "PRB constante", f3(cd) if cd is not None else "-"])
    table(["dentro da fase", "vazao x PRB", "vazao x atraso"], rows)
    info("A correlacao global mistura as fases (idle x carga). A relacao que se sustenta DENTRO da fase e a que vale.")
    # recomendacao: vazao caiu com PRB alto?
    mp, mt = movavg(d.col("prb"), LIM["window"]), movavg(d.col("thp"), LIM["window"])
    gatilho = [a > th["prb_high"] and b < th["thp_low"] for a, b in zip(mp, mt)]
    fr = frac(gatilho)
    kv("regra do card", f"vazao cai (< {f1(th['thp_low'])} kbps) com PRB alto (> {f1(th['prb_high'])}%) -> priorizar/aliviar carga")
    if fr > 0:
        warn(f"regra disparou em {pct(fr)} das amostras (media movel de {LIM['window']})")
        a1_dryrun("ue-tp-prioridade", {"ueId": "ue-any", "qosId": "qos-lab"}, {"priorityLevel": 10},
                  "vazao baixa com radio cheio: usuario mal servido")
        ver = "vazao caiu com PRB alto: proposta de priorizacao em A1 (dry-run)"
    else:
        ok("regra NAO disparou: a vazao acompanha o PRB (radio cheio, vazao alta). Nada a priorizar.")
        ver = "a vazao acompanha o PRB dentro da fase; vazao x atraso ~0 dentro da fase"
    kv("limitacoes", "1 run, poucos UEs (RFSIM); unidades por convencao KPM; media do recovery e puxada por picos (use mediana/p95)")
    return {"I1": f"media/p95 por fase (stress: {f1(mean(d.col('thp', d.phases[min(1, len(d.phases)-1)])))} kbps)",
            "I2": f"PRB medio por fase", "veredito": ver}


# =============================================================================
# T2 - Deteccao de anomalia de carga (metodo do model.json do professor)
# =============================================================================
def t2(d, th):
    cabecalho_tema(2, "Deteccao de anomalia de carga",
                   "em que momentos a rede sai do comportamento normal de forma sustentada (nao um pico isolado)?",
                   "xApp KPM -> arquivo -> baseline robusto no painel -> decision (fluxo ai_policy_pipeline do lab)")
    base = d.phases[0]
    step(f"Formulas (robust-baseline-mad, o mesmo algoritmo do model.json do professor; baseline = fase '{base}')")
    formula("MAD", "MAD = mediana(|x - mediana(x)|), por metrica, so no baseline", "unidade da metrica")
    formula("score", f"score = |x - mediana_baseline| / max(MAD, {LIM['mad_floor']:g})", "adimensional")
    formula("amostra anomala", f"score > {LIM['score_thr']:g} em pelo menos {LIM['min_feat']} das 3 metricas", "-")
    formula("I1  % de amostras anomalas por fase", "anomalas(fase) / n(fase)", "%")
    formula("I2  Intensidade do desvio na carga", "media e maximo do maior score da amostra, na fase de carga", "adimensional")
    feats = ["thp", "delay", "prb"]
    model = {}
    for f in feats:
        v = d.col(f, base); model[f] = {"med": median(v), "mad": max(mad(v), LIM["mad_floor"])}
    table(["metrica (baseline)", "mediana", "MAD efetivo"],
          [[{"thp": "DRB.UEThpUl", "delay": "DRB.RlcSduDelayDl", "prb": "RRU.PrbTotUl"}[f],
            f1(model[f]["med"]), f1(model[f]["mad"])] for f in feats])
    scores, anom = [], []
    for r in d.rows:
        sc = {f: abs(r[f] - model[f]["med"]) / model[f]["mad"] for f in feats}
        nfe = sum(1 for f in feats if sc[f] > LIM["score_thr"])
        scores.append(max(sc.values())); anom.append(nfe >= LIM["min_feat"])
    rows, i = [], 0
    for p in d.phases:
        n = d.n(p); a = anom[i:i + n]; s = scores[i:i + n]; i += n
        rows.append([p, n, sum(a), pct(frac(a)), f1(mean(s)), f1(max(s))])
    table(["fase", "n", "anomalas", "% anomalas", "score medio", "score max"], rows)
    # decisao por janela (window_size / apply_votes do decision.json)
    w = LIM["window"]; applies = []
    for j in range(w - 1, len(anom)):
        if sum(anom[j - w + 1:j + 1]) >= w: applies.append(j)
    falsos = sum(1 for r, a in zip(d.rows, anom) if a and r["phase"] not in ("stress", "observacao"))
    kv("falsos alarmes", f"{falsos} amostra(s) anomala(s) fora da fase de carga (picos isolados: nao viram decisao)")
    if applies:
        primeiro = d.rows[applies[0]]
        warn(f"decisao 'apply' em {len(applies)} janela(s) de {w}: a 1a na fase '{primeiro['phase']}', amostra {primeiro['idx']}")
        a1_dryrun("ai-load-control", {"ueId": "ue-any", "qosId": "qos-lab"}, {"priorityLevel": 10},
                  "maioria da janela anomala: reduzir congestionamento UL")
        ver = f"anomalia sustentada detectada ({len(applies)} janelas 'apply'); {falsos} falso(s) alarme(s) isolado(s)"
    else:
        ok("nenhuma janela inteira anomala: sem decisao (picos isolados nao contam)")
        ver = "sem anomalia sustentada"
    kv("limitacoes", f"baseline de {d.n(base)} amostras com MAD 0 em varias metricas (piso {LIM['mad_floor']:g}); limiar 3.5 e convencao")
    return {"I1": "% anomalas por fase", "I2": "score medio/max na carga", "veredito": ver}


# =============================================================================
# T3 - Latencia e qualidade percebida (QoE)
# =============================================================================
def t3(d, th):
    cabecalho_tema(3, "Latencia e qualidade percebida (QoE)",
                   "quando o atraso de radio sugere que a experiencia do usuario pode estar ruim?",
                   "DRB.RlcSduDelayDl medido no gNB (RLC) -> KPM -> analise; nao ha MOS de aplicativo no lab")
    step("Formulas dos 2 indicadores")
    formula("I1  Atraso RLC DL por fase", "mediana(delay_dl) e p95(delay_dl), por fase", "us")
    formula("I2  Fracao do tempo em atraso alto", f"n(delay_dl > {th['delay_max']:g} us) / n, por fase", "%")
    kv("limiar justificado", f"{th['delay_max']:g} us: ~3x o p95 do baseline em repouso, marca a MUDANCA de regime; ajustavel por TEMA_DELAY_MAX")
    kv("em valor absoluto", "atraso RLC abaixo de 1 ms nao e experiencia ruim: o indicador mostra o salto relativo ao repouso, nao QoE")
    rows = []
    for p in d.phases:
        dl = d.col("delay", p); t = d.col("thp", p)
        alto = [x > th["delay_max"] for x in dl]
        ruim = [x > th["delay_max"] and y < th["thp_low"] for x, y in zip(dl, t)]
        rows.append([p, d.n(p), f1(median(dl)), f1(pctl(dl, 95)), pct(frac(alto)), pct(frac(ruim))])
    table(["fase", "n", "atraso mediana", "p95", "% atraso alto", "% alto + vazao baixa"], rows)
    info("Atraso alto COM vazao baixa reforca a hipotese de ma experiencia; atraso alto com vazao alta e fila de carga.")
    carga = d.phases[1] if len(d.phases) > 1 else d.phases[0]
    fa = frac([x > th["delay_max"] for x in d.col("delay", carga)])
    if fa >= 0.5:
        warn(f"na fase '{carga}', {pct(fa)} das amostras acima do limiar")
        a1_dryrun("qoe-prioridade", {"ueId": "ue-any", "qosId": "qos-lab"}, {"priorityLevel": 5},
                  "atraso RLC sustentado acima do limiar: priorizar trafego sensivel")
        ver = f"atraso alto em {pct(fa)} da fase de carga: recomendar investigar sessao / priorizar (A1 dry-run)"
    else:
        ok("atraso dentro do limiar na maior parte do tempo")
        ver = "atraso dentro do limiar"
    kv("limitacoes", "o atraso e um PROXY de QoE (nao ha nota MOS); RFSIM, 1 UE; picos isolados no baseline nao sao experiencia ruim")
    return {"I1": "mediana/p95 do atraso por fase", "I2": "% acima do limiar", "veredito": ver}


# =============================================================================
# T4 - Risco de congestionamento
# =============================================================================
def t4(d, th):
    cabecalho_tema(4, "Risco de congestionamento",
                   "os dados mostram saturacao que justifique um alerta de capacidade?",
                   "RRU.PrbTotUl do gNB (E2SM-KPM) -> analise no painel -> alerta / intencao de alivio via A1")
    w = LIM["window"]
    step("Formulas dos 2 indicadores")
    formula("I1  Utilizacao de PRB UL", "media(prb_ul) e p95(prb_ul), por fase", "% dos PRB")
    formula("I2  Indice de risco", f"n(MM{w}(prb) > {f1(th['prb_high'])}% E MM{w}(thp) < {f1(th['thp_low'])} kbps) / n", "%")
    kv("MMk", f"media movel de {w} amostras: olha a tendencia, nao um instante")
    kv("limiares", f"PRB alto = {LIM['prb_high']:g} x PRB max ({f1(th['prb_max'])}%); vazao baixa = {LIM['thp_low']:g} x p95 da vazao ({f1(th['thp_p95'])} kbps)")
    rows, i, risco_g = [], 0, []
    for p in d.phases:
        pr, t = d.col("prb", p), d.col("thp", p)
        mp, mt = movavg(pr, w), movavg(t, w)
        risco = [a > th["prb_high"] and b < th["thp_low"] for a, b in zip(mp, mt)]
        risco_g += risco
        sat = frac([a > th["prb_high"] for a in mp])
        rows.append([p, d.n(p), f1(mean(pr)), f1(pctl(pr, 95)), pct(sat), pct(frac(risco))])
    table(["fase", "n", "PRB medio", "PRB p95", "% radio cheio", "indice de risco"], rows)
    fr = frac(risco_g)
    if fr > 0:
        warn(f"indice de risco global = {pct(fr)}: radio cheio E usuario mal servido")
        a1_dryrun("alivio-de-carga", {"ueId": "ue-any", "qosId": "qos-lab"}, {"priorityLevel": 20},
                  "saturacao de PRB com queda de vazao: alerta de capacidade")
        ver = f"alerta de capacidade: risco em {pct(fr)} das amostras"
    else:
        ok("radio cheio na carga, mas a vazao acompanha: capacidade EM USO, nao em risco (sem alerta)")
        ver = "saturacao sem queda de vazao: sem alerta de capacidade"
    kv("limitacoes", "1 UE em RFSIM satura os PRB sozinho; em campus real o indice pede varios UEs e mais tempo")
    return {"I1": "PRB medio/p95 por fase", "I2": f"indice de risco {pct(fr)}", "veredito": ver}


# =============================================================================
# T5 - Visao agregada da celula
# =============================================================================
def t5(d, th):
    cabecalho_tema(5, "Visao agregada da celula",
                   "como resumir o experimento em indicadores de celula e qual o limite disso no lab?",
                   "agregacao por run_id e fase (o GROUP BY da zona gold do mini-lake), no painel")
    step("Formulas dos 2 indicadores")
    formula("I1  PRB medio da celula por fase", "media(prb_ul) GROUP BY run_id, phase", "% dos PRB")
    formula("I2  Vazao representativa da celula", "media(thp_ul) por fase (e soma = media x n_UE quando ha varios UEs)", "kbps")
    ues = sorted(set(str(r["ue"]) for r in d.rows)); n_ue = len(ues)
    runs = sorted(set(str(r["run"]) for r in d.rows))
    kv("run_id", ", ".join(runs)); kv("UEs distintos", f"{n_ue} ({', '.join(ues[:5])}{'...' if n_ue > 5 else ''})")
    rows = []
    for p in d.phases:
        pr, t, dl = d.col("prb", p), d.col("thp", p), d.col("delay", p)
        rows.append([p, d.n(p), f1(mean(pr)), f1(max(pr)), f1(mean(t)), f1(mean(t) * n_ue), f1(pctl(t, 95)), f1(mean(dl))])
    table(["fase", "n", "PRB medio", "PRB max", "vazao media", "vazao soma", "vazao p95", "atraso medio"], rows)
    info("Comparar fase normal x fase com carga e o resumo 'de celula'. Com 1 UE, media = soma: a agregacao e didatica, nao estatistica de campus.")
    ok(f"indicadores de celula calculados para {len(runs)} run(s) e {len(d.phases)} fase(s)")
    kv("limitacoes", f"{n_ue} UE(s) em RFSIM: nao ha diversidade de usuarios; capacidade real da celula nao e observavel aqui")
    return {"I1": "PRB medio da celula por fase", "I2": "vazao media/soma por fase", "veredito": f"resumo por fase pronto; limite: {n_ue} UE(s)"}


# =============================================================================
# T6 - Economia de energia (so intencao)
# =============================================================================
def t6(d, th):
    cabecalho_tema(6, "Economia de energia (so intencao)",
                   "em que trechos a carga esta baixa o suficiente para pensar em economizar energia, sem desligar nada?",
                   "janelas de PRB/vazao baixos no KPM -> intencao A1 em dry-run; o lab NAO controla potencia da RU")
    step("Formulas dos 2 indicadores")
    formula("baixa carga", f"prb_ul <= {f1(th['prb_low'])}% E thp_ul <= {f1(th['thp_lowload'])} kbps  ({LIM['low_load']:g} x PRB max e x p95 da vazao)", "-")
    formula("I1  Fracao do tempo em baixa carga", "n(baixa carga) / n, por fase e no total", "%")
    formula("I2  Vazao e atraso nessas janelas", "media(thp_ul) e media/mediana(delay_dl) so nas amostras de baixa carga", "kbps / us")
    rows, low_all = [], []
    for p in d.phases:
        pr, t, dl = d.col("prb", p), d.col("thp", p), d.col("delay", p)
        low = [a <= th["prb_low"] and b <= th["thp_lowload"] for a, b in zip(pr, t)]
        low_all += low
        tl = [x for x, m in zip(t, low) if m]; dll = [x for x, m in zip(dl, low) if m]
        rows.append([p, d.n(p), pct(frac(low)), f1(mean(tl)) if tl else "-", f1(median(dll)) if dll else "-",
                     pct(frac([x > th["delay_max"] for x in dll])) if dll else "-"])
    table(["fase", "n", "% baixa carga", "vazao media (baixa)", "atraso mediana (baixa)", "% atraso alto (baixa)"], rows)
    fr = frac(low_all)
    dl_low = [r["delay"] for r, m in zip(d.rows, low_all) if m]
    aceit = frac([x <= th["delay_max"] for x in dl_low]) if dl_low else float("nan")
    kv("total em baixa carga", f"{pct(fr)} do experimento; atraso aceitavel em {pct(aceit)} dessas amostras")
    if fr > 0 and aceit >= 0.5:
        ok("ha janelas de baixa carga com atraso aceitavel: da para PENSAR em economia de energia nelas")
        a1_dryrun("economia-energia", {"cellId": "cell-lab"}, {"energySavingIntent": "candidate"},
                  f"{pct(fr)} do tempo em baixa carga; INTENCAO apenas: sem atuacao fisica na RAN")
        ver = f"{pct(fr)} do tempo em baixa carga com atraso ok: intencao de economia (dry-run)"
    else:
        warn("pouca ou nenhuma janela de baixa carga com atraso aceitavel: sem intencao de economia")
        ver = "sem janela segura de baixa carga"
    kv("limitacoes", "o lab nao controla potencia de RU; 'baixa carga' de 1 UE simulado nao e ociosidade de celula real")
    return {"I1": f"% tempo em baixa carga ({pct(fr)})", "I2": "vazao/atraso nas janelas", "veredito": ver}


# =============================================================================
# T7 - Politica de QoS / steering (candidata)
# =============================================================================
def t7(d, th):
    cabecalho_tema(7, "Politica de QoS / steering (candidata)",
                   "diante de degradacao, que regra de decisao seria segura para propor uma politica de QoS?",
                   "regra avaliada sobre o KPM no painel -> politica A1 desenhada (escopo UE/QoS, prioridade), sem afirmar handover/path")
    k = LIM["persist"]
    step("Formulas dos 2 indicadores")
    formula("regra", f"degradacao = delay_dl > {th['delay_max']:g} us  OU  (prb_ul > {f1(th['prb_high'])}% E thp_ul < {f1(th['thp_low'])} kbps)", "-")
    formula("I1  Tempo em degradacao", "n(regra verdadeira) / n, por fase", "%")
    formula("I2  Acionamentos da politica", f"subidas da regra (falso -> verdadeiro); 'sustentado' = {k} amostras seguidas", "contagem")
    deg = [r["delay"] > th["delay_max"] or (r["prb"] > th["prb_high"] and r["thp"] < th["thp_low"]) for r in d.rows]
    rows, i, tot_edges, tot_sust = [], 0, 0, 0
    for p in d.phases:
        n = d.n(p); m = deg[i:i + n]; i += n
        edges = sum(1 for j in range(n) if m[j] and (j == 0 or not m[j - 1]))
        sust = 0; run = 0
        for x in m:
            run = run + 1 if x else 0
            if run == k: sust += 1
        tot_edges += edges; tot_sust += sust
        strip = "".join("#" if x else "." for x in m)
        rows.append([p, n, pct(frac(m)), edges, sust, strip[:60]])
    table(["fase", "n", "% degradado", "acionam.", "sustentados", "linha do tempo (# = regra verdadeira)"], rows, right=False)
    kv("leitura", f"{tot_edges} acionamento(s) brutos, {tot_sust} sustentado(s) ({k}+ amostras): o filtro de persistencia evita reagir a pico isolado")
    if tot_sust > 0:
        warn("a regra dispararia de forma sustentada: politica candidata abaixo")
        a1_dryrun("qos-steering", {"ueId": "ue-any", "qosId": "qos-lab"}, {"priorityLevel": 5, "steeringCandidate": "cell-neighbor"},
                  "degradacao sustentada; um humano valida antes de automatizar")
        ver = f"{tot_sust} acionamento(s) sustentado(s): politica A1 candidata (dry-run), validacao humana antes de automatizar"
    else:
        ok("a regra nao dispararia de forma sustentada: sem politica candidata")
        ver = "sem degradacao sustentada"
    kv("limitacoes", "limiares sao escolha do grupo (justificar no README); nao afirmamos que handover/path mudaram; RFSIM, 1 UE")
    return {"I1": "% tempo em degradacao", "I2": f"{tot_edges} acionamentos ({tot_sust} sustentados)", "veredito": ver}


TEMAS = OrderedDict([("t1", t1), ("t2", t2), ("t3", t3), ("t4", t4), ("t5", t5), ("t6", t6), ("t7", t7)])
TITULOS = {"t1": "Vazao do usuario", "t2": "Anomalia de carga", "t3": "Latencia / QoE",
           "t4": "Risco de congestionamento", "t5": "Visao da celula", "t6": "Economia de energia", "t7": "QoS / steering"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tema", default="all", choices=list(TEMAS) + ["all"])
    ap.add_argument("--file", required=True, help="kpm.jsonl | kpm.csv | kpm_timeseries.csv")
    a = ap.parse_args()

    section("Fonte dos dados")
    rows, phases, fmt, inferred = load(a.file)
    d = Data(rows, phases)
    kv("arquivo", a.file); kv("formato detectado", fmt)
    kv("amostras", f"{len(rows)}  ({', '.join(f'{p}: {d.n(p)}' for p in phases)})")
    kv("metricas", "thp_ul = DRB.UEThpUl [kbps]   delay_dl = DRB.RlcSduDelayDl [us]   prb_ul = RRU.PrbTotUl [%]")
    kv("unidades", "as do E2SM-KPM, como o xApp do FlexRIC imprime e o slide 66 da aula 01 mostra (kbps, us, %)")
    if inferred:
        warn("sem coluna de fase: as primeiras 20% amostras viraram 'baseline' e o resto 'observacao'")
    th = thresholds(d)
    kv("limiares derivados", f"PRB alto > {f1(th['prb_high'])}  vazao baixa < {f1(th['thp_low'])} kbps  "
                             f"baixa carga: PRB <= {f1(th['prb_low'])}% e vazao <= {f1(th['thp_lowload'])}  atraso > {th['delay_max']:g} us")
    ok("dados carregados: 1 linha = 1 medicao KPM (zona silver)")

    sel = list(TEMAS) if a.tema == "all" else [a.tema]
    res = OrderedDict()
    for t in sel:
        res[t] = TEMAS[t](d, th)

    if len(sel) > 1:
        section("Os 7 temas lado a lado (mesmos dados, perguntas diferentes)")
        table(["tema", "indicador 1", "indicador 2", "veredito"],
              [[f"T{t[1]} {TITULOS[t]}", r["I1"], r["I2"], r["veredito"]] for t, r in res.items()], right=False)
    ult = res[sel[-1]]["veredito"] if len(sel) == 1 else f"{len(sel)} temas calculados sobre {len(rows)} amostras"
    print(f"\n{DIM}Veredito:{RST} {ult}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
