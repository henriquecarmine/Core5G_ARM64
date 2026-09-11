#!/usr/bin/env python3
"""cenarios_kpm.py - cenarios de telemetria KPM SUGERIDOS PELO SERVIDOR.

Os 7 temas, a aula 04 e o closed loop rodam sobre a amostra real do professor:
1 celular, sem distancia nem interferencia. Este gerador cria, no MESMO formato
(JSONL com "metrics", "phase", "sample_index", "ue"), variacoes que a amostra
nao tem - 1, 2, 5 ou 10 celulares, a 100 m, 500 m, 1 km, 3 km ou em distancias
misturadas, com interferencia fraca, media ou alta - para que o aluno veja o
que muda em cada indicador e por que.

OS DADOS SAO SINTETICOS. Cada linha carrega "cenario": {"sintetico": true, ...}
e os testes avisam isso na tela. O objetivo e didatico: a mesma cadeia de
modelos do Lab do UE do Projeto 1 (test_channel.sh), calibrada na amostra real,
com cada formula impressa. Nao e simulacao de propagacao nem de escalonador.

A cadeia do modelo, por celular:

  1. perda de percurso (3GPP TR 38.901, UMa NLOS, f_c = 3,5 GHz, h_UT = 1,5 m)
        PL(d) = 13,54 + 39,08*log10(d) + 20*log10(f_c) - 0,6*(h_UT - 1,5)   [dB]
  2. RSRP = P_ref - PL, com P_ref = 58,6 dBm (a calibracao do Lab do UE:
     RSRP(100 m) = -44 dBm)                                                   [dBm]
  3. SNR = min(30, 0,65*(RSRP + 105))  - mapa didatico das faixas usuais de
     drive test (-44 excelente ... -102 borda da celula)                      [dB]
  4. interferencia como C/I (os mesmos niveis do Lab do UE: fraca 20 dB,
     media 15 dB, alta 5 dB):  SINR = 1 / (1/SNR + 1/(C/I))  em linear       [dB]
  5. eficiencia espectral (Shannon, com o teto pratico do NR ~ 256QAM)
        eta = min(7,4 ; log2(1 + SINR))                                        [bit/s/Hz]
  6. escalonamento justo: os N celulares dividem os PRB da celula por igual
        vazao_UE = (C_ref / N) * eta / eta_ref                                [kbps]
     C_ref = 80 023,7 kbps (mediana da carga na amostra real, 1 UE, PRB 99%)
  7. atraso RLC (fila): cresce com N e com a eficiencia menor
        atraso_UE = 158,9 * (1 + 0,35*(N - 1)) * sqrt(eta_ref / eta)          [us]

Fases iguais as da amostra: baseline 20, stress 60, recovery 20 amostras. A
interferencia, quando pedida, fica ativa nas amostras 20 a 44 do stress: o
mesmo arquivo mostra a carga sem e com o sinal interferente, e e ai que aparece
a assinatura de jammer da aula 05 (PRB estavel, vazao caindo).

Uso:
    cenarios_kpm.py --ues 1|2|5|10 --distancia 100m|500m|1km|3km|mista
                    --interferencia none|fraca|media|alta [--seed N] --out arquivo.jsonl

Somente biblioteca padrao (roda no servidor ARM64 e e importado pelo painel).
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from datetime import datetime, timedelta

VERSAO = "cenarios_kpm v1"
N_UES = (1, 2, 5, 10)
DISTANCIAS = {"100m": 100, "500m": 500, "1km": 1000, "3km": 3000}
MISTA = (100, 500, 1000, 3000)
CIR_DB = {"none": None, "fraca": 20.0, "media": 15.0, "alta": 5.0}
ROTULO_DIST = {"100m": "todos a 100 m", "500m": "todos a 500 m", "1km": "todos a 1 km",
               "3km": "todos a 3 km (borda)", "mista": "distancias misturadas (100 m, 500 m, 1 km, 3 km)"}
ROTULO_INTERF = {"none": "sem interferencia", "fraca": "interferencia fraca (C/I 20 dB)",
                 "media": "interferencia media (C/I 15 dB)", "alta": "interferencia alta (C/I 5 dB)"}

F_GHZ, H_UT = 3.5, 1.5
P_REF_DBM = 58.6
SNR_MAX_DB = 30.0
ETA_MAX = 7.4
C_REF_KBPS = 80023.7
PRB_CARGA = 99.0
PRB_REPOUSO_UE = 2.0
THP_REPOUSO = 3.72
DELAY_CARGA_US = 158.9
FASES = (("baseline", 20), ("stress", 60), ("recovery", 20))
JANELA_INTERF = (20, 45)
SEED = 20260911


# ---- a cadeia do modelo --------------------------------------------------------
def perda_percurso_db(d_m):
    return 13.54 + 39.08 * math.log10(d_m) + 20 * math.log10(F_GHZ) - 0.6 * (H_UT - 1.5)


def rsrp_dbm(d_m):
    return P_REF_DBM - perda_percurso_db(d_m)


def snr_db(d_m):
    return min(SNR_MAX_DB, 0.65 * (rsrp_dbm(d_m) + 105.0))


def sinr_db(snr, cir):
    if cir is None:
        return snr
    return 10 * math.log10(1 / (1 / 10 ** (snr / 10) + 1 / 10 ** (cir / 10)))


def eficiencia(sinr):
    return min(ETA_MAX, math.log2(1 + 10 ** (sinr / 10)))


ETA_REF = eficiencia(snr_db(100))


def distancias_dos_ues(n, distancia):
    if distancia == "mista":
        return [MISTA[i % len(MISTA)] for i in range(n)]
    return [DISTANCIAS[distancia]] * n


def esperado(n, distancia, interferencia):
    """O que o modelo preve para cada celular (sem ruido) - base da comparacao na tela."""
    cir = CIR_DB[interferencia]
    ues = []
    for i, d in enumerate(distancias_dos_ues(n, distancia)):
        snr = snr_db(d)
        s_com = sinr_db(snr, cir)
        eta_sem, eta_com = eficiencia(snr), eficiencia(s_com)
        ues.append({
            "ue": f"ue-{i + 1:02d}", "dist_m": d, "pl_db": perda_percurso_db(d), "rsrp_dbm": rsrp_dbm(d),
            "snr_db": snr, "cir_db": cir, "sinr_com_db": s_com, "eta_sem": eta_sem, "eta_com": eta_com,
            "thp_sem": C_REF_KBPS / n * eta_sem / ETA_REF, "thp_com": C_REF_KBPS / n * eta_com / ETA_REF,
            "delay_sem": DELAY_CARGA_US * (1 + 0.35 * (n - 1)) * math.sqrt(ETA_REF / eta_sem),
            "delay_com": DELAY_CARGA_US * (1 + 0.35 * (n - 1)) * math.sqrt(ETA_REF / eta_com),
        })
    return {"ues": ues, "prb_carga": PRB_CARGA, "prb_repouso": min(PRB_CARGA, PRB_REPOUSO_UE * n),
            "soma_sem": sum(u["thp_sem"] for u in ues), "soma_com": sum(u["thp_com"] for u in ues)}


def validar(n, distancia, interferencia):
    if n not in N_UES:
        raise ValueError(f"numero de celulares deve ser um de {N_UES}")
    if distancia not in list(DISTANCIAS) + ["mista"]:
        raise ValueError("distancia deve ser 100m, 500m, 1km, 3km ou mista")
    if interferencia not in CIR_DB:
        raise ValueError("interferencia deve ser none, fraca, media ou alta")


def gerar(n, distancia, interferencia, seed=SEED):
    """Lista de registros JSON (1 por celular por amostra), deterministica pela semente."""
    validar(n, distancia, interferencia)
    rng = random.Random(f"{seed}-{n}-{distancia}-{interferencia}")
    exp = esperado(n, distancia, interferencia)
    meta = {"sintetico": True, "gerador": VERSAO, "n_ue": n, "distancia": distancia,
            "interferencia": interferencia, "seed": seed,
            "janela_interferencia": list(JANELA_INTERF) if interferencia != "none" else None}
    run_id = f"sugerido-{n}ue-{distancia}-{interferencia}"
    t0 = datetime(2026, 9, 11, 10, 0, 0)
    out, k = [], 0
    for fase, qtd in FASES:
        for i in range(qtd):
            ativa = fase == "stress" and interferencia != "none" and JANELA_INTERF[0] <= i < JANELA_INTERF[1]
            if fase == "stress":
                prb = PRB_CARGA if rng.random() > 0.1 else PRB_CARGA - 1
            elif fase == "recovery" and i == 0:
                prb = 21.0          # resto de carga: a amostra real tambem tem esse pico na volta
            else:
                prb = exp["prb_repouso"]
            for u in exp["ues"]:
                if fase == "stress":
                    thp = (u["thp_com"] if ativa else u["thp_sem"]) * (1 + rng.uniform(-0.04, 0.04))
                    dl = (u["delay_com"] if ativa else u["delay_sem"]) * (1 + rng.uniform(-0.08, 0.08))
                elif fase == "recovery" and i == 0:
                    thp = u["thp_sem"] * 2.15
                    dl = u["delay_sem"] * 0.5
                else:
                    thp = THP_REPOUSO * (1 + rng.uniform(-0.02, 0.02))
                    dl = rng.uniform(50, 220) if rng.random() < 0.05 else 0.0
                out.append({
                    "run_id": run_id, "phase": fase, "sample_index": i, "ue": u["ue"],
                    "ingested_at": (t0 + timedelta(seconds=k)).isoformat(),
                    "metrics": {"DRB.UEThpUl": round(thp, 2), "DRB.RlcSduDelayDl": round(dl, 2), "RRU.PrbTotUl": prb},
                    "radio": {"dist_m": u["dist_m"], "sinr_db": round(u["sinr_com_db"] if ativa else u["snr_db"], 2),
                              "interferencia_ativa": ativa},
                    "cenario": meta,
                })
            k += 1
    return out


def escrever(caminho, registros):
    with open(caminho, "w", encoding="utf-8") as fh:
        for r in registros:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


# ---- a explicacao na tela --------------------------------------------------------
LEITURA = {
    "t1": ("Vazao do usuario", [
        "a vazao de cada celular e a FATIA dele: com N celulares espere perto de 1/N da vazao de 1 celular, com o PRB igual (99%).",
        "distancia e interferencia derrubam a eficiencia (bits por PRB): a vazao cai SEM o PRB cair - e o sintoma 'PRB alto, vazao baixa' que a regra do T1 procura.",
        "com varios celulares o T1 roda sobre a vazao MEDIA por usuario em cada instante; a tabela por celular abaixo mostra quem ficou mal servido."]),
    "t2": ("Anomalia de carga", [
        "o MAD e treinado no baseline; com mais celulares o PRB de repouso sobe (sinalizacao de cada um), mas continua baixo perto dos 99% da carga.",
        "na carga as tres metricas saem do normal e a janela vira 'apply'; a janela com interferencia continua anomala porque o PRB segue alto e a vazao muda."]),
    "t3": ("Latencia e QoE", [
        "o atraso RLC cresce com N (fila dividida) e com a eficiencia menor (mais transmissoes por bit): distancia e interferencia empurram o atraso para cima.",
        "o limiar do T3 marca mudanca de regime em relacao ao repouso, nao experiencia: e o valor relativo que importa (a unidade do atraso esta em disputa no curso)."]),
    "t4": ("Risco de congestionamento", [
        "o indice exige PRB alto E vazao baixa ao mesmo tempo: 1 celular perto sem interferencia enche o radio entregando, e o risco fica em zero.",
        "o limiar de 'vazao baixa' e 50% do p95 do proprio arquivo: a janela de interferencia (ou uma celula so de celulares distantes) e o que o faz disparar."]),
    "t5": ("Visao da celula", [
        "aqui a soma importa: a vazao da celula e a soma dos usuarios, perto da capacidade vezes a eficiencia media, e nao cresce com N - cada um recebe menos.",
        "o PRB da celula e o mesmo para todos os celulares no instante: e um indicador de celula, nao de usuario."]),
    "t6": ("Economia de energia", [
        "baixa carga so aparece no baseline e no recovery; com mais celulares o PRB de repouso sobe e a janela de economia pode encolher.",
        "distancia e interferencia nao mudam o repouso: o que decide economia e a carga, nao o canal."]),
    "t7": ("QoS / steering", [
        "a regra dispara com atraso alto OU com PRB alto e vazao baixa: interferencia e distancia acionam a segunda parte mesmo sem o atraso passar do limiar.",
        "a persistencia (3 amostras seguidas) separa a janela de interferencia de um pico isolado."]),
    "all": ("Os 7 temas", [
        "os mesmos dados passam pelas 7 perguntas: o que muda de um cenario para outro e QUAIS temas disparam recomendacao.",
        "compare o veredito de cada tema com a leitura do cenario acima: 1 celular perto e o caso sem problema; muitos celulares, borda ou interferencia sao os casos com decisao."]),
    "aula04": ("Aula 04", [
        "o KPI de rede (PRB) nao muda com a interferencia; o KQI (vazao e atraso por usuario) muda: um KPI bom nao garante um KQI bom, a frase do slide 12 da aula 05.",
        "com varios celulares os indicadores de usuario sao a mediana por usuario; os de celula (PRB) sao de uma linha por instante."]),
    "closed": ("Closed loop", [
        "o MAD decide 'apply' com a carga; o rate-limit da politica e 8 Mbit/s POR celular.",
        "se a fatia de cada celular ja fica abaixo de 8 Mbit/s (muitos celulares, borda ou interferencia), o limite nao corta nada: ao vivo o effect_report mostraria efeito perto de zero. E um caso em que a politica certa e outra."]),
}


def explicar(d_ue, d_cel, teste):
    """Imprime o bloco 'cenario sugerido pelo servidor' antes do teste. Nada acontece com a amostra real."""
    from temas_projeto import B, RST, f1, formula, info, kv, median, ok, section, step, table, warn

    meta = next((r.get("cenario") for r in d_ue.rows if r.get("cenario")), None)
    if not meta:
        return None
    n, dist, interf = meta["n_ue"], meta["distancia"], meta["interferencia"]
    exp = esperado(n, dist, interf)

    section("Cenario sugerido pelo servidor (DADOS SINTETICOS)")
    warn(f"{B}Estes dados foram gerados{RST} pelo {meta.get('gerador', VERSAO)} (semente {meta.get('seed')}), "
         "nao coletados na RAN: servem para ver o que muda nos indicadores, nao para concluir sobre a rede do lab.")
    kv("celulares", f"{n}")
    kv("distancia", ROTULO_DIST[dist])
    kv("interferencia", ROTULO_INTERF[interf] + (f", ativa nas amostras {JANELA_INTERF[0]} a {JANELA_INTERF[1] - 1} do stress"
                                                if interf != "none" else ""))
    kv("amostras", f"{len(d_ue.rows)} linhas = {len(d_cel.rows)} instantes x {n} celular(es)")

    step("A cadeia do modelo, do percurso a vazao (a mesma fisica do Lab do UE do P1)")
    formula("1 perda de percurso", "PL = 13,54 + 39,08*log10(d) + 20*log10(3,5) - 0,6*(1,5 - 1,5)", "dB  (3GPP TR 38.901 UMa NLOS)")
    formula("2 potencia recebida", "RSRP = 58,6 - PL", "dBm  (calibrada no Lab do UE: -44 dBm a 100 m)")
    formula("3 relacao sinal/ruido", "SNR = min(30, 0,65 * (RSRP + 105))", "dB  (mapa didatico das faixas de drive test)")
    formula("4 com interferencia", "SINR = 1 / (1/SNR + 1/(C/I))  em linear", "dB")
    formula("5 eficiencia", "eta = min(7,4 ; log2(1 + SINR))", "bit/s/Hz  (Shannon, teto ~256QAM)")
    formula("6 fatia de cada um", f"vazao_UE = ({f1(C_REF_KBPS)} / N) * eta / {ETA_REF:.2f}", "kbps  (PRB dividido por igual)")
    formula("7 atraso na fila", f"atraso_UE = {DELAY_CARGA_US:g} * (1 + 0,35*(N - 1)) * sqrt({ETA_REF:.2f} / eta)", "us")

    carga = [r for r in d_ue.rows if r["phase"] == "stress"]
    linhas = []
    for u in exp["ues"]:
        fora = [r for r in carga if r["ue"] == u["ue"] and not (r.get("radio") or {}).get("interferencia_ativa")]
        dentro = [r for r in carga if r["ue"] == u["ue"] and (r.get("radio") or {}).get("interferencia_ativa")]
        obs_sem = median([r["thp"] for r in fora]) if fora else float("nan")
        obs_com = median([r["thp"] for r in dentro]) if dentro else None
        linhas.append([u["ue"], f"{u['dist_m']} m", f1(u["pl_db"]), f1(u["rsrp_dbm"]), f1(u["snr_db"]),
                       f"{u['eta_sem']:.2f}", f1(u["thp_sem"]), f1(obs_sem),
                       f1(u["sinr_com_db"]) if interf != "none" else "-",
                       f1(u["thp_com"]) if interf != "none" else "-",
                       f1(obs_com) if obs_com is not None else "-"])
    table(["celular", "dist", "PL dB", "RSRP dBm", "SNR dB", "eta", "vazao esperada", "observada",
           "SINR c/ interf", "esperada c/ interf", "observada c/ interf"], linhas)
    info("'esperada' e o modelo sem ruido; 'observada' e a mediana do arquivo na carga (o gerador soma +-4% de ruido).")

    kv("celula na carga", f"PRB {f1(exp['prb_carga'])}% · vazao somada {f1(exp['soma_sem'])} kbps"
                          + (f" (com interferencia: {f1(exp['soma_com'])} kbps, {100 * (exp['soma_com'] / exp['soma_sem'] - 1):+.0f}%)"
                             if interf != "none" else ""))
    kv("celula em repouso", f"PRB {f1(exp['prb_repouso'])}% ({PRB_REPOUSO_UE:g}% de sinalizacao por celular)")
    fatia_1 = C_REF_KBPS
    pior = min(exp["ues"], key=lambda u: u["thp_com"] if interf != "none" else u["thp_sem"])
    kv("comparado a 1 celular perto", f"cada usuario recebe {100 * (exp['soma_sem'] / n) / fatia_1:.0f}% da vazao de 1 celular a 100 m; "
                                      f"o pior ({pior['ue']}, {pior['dist_m']} m) fica com "
                                      f"{f1(pior['thp_com'] if interf != 'none' else pior['thp_sem'])} kbps")

    titulo, dicas = LEITURA.get(teste, LEITURA["all"])
    step(f"Como ler '{titulo}' neste cenario")
    for dica in dicas:
        info(dica)
    if teste == "closed":
        abaixo = [u for u in exp["ues"] if (u["thp_com"] if interf != "none" else u["thp_sem"]) < 8000]
        if abaixo:
            warn(f"{len(abaixo)} de {n} celular(es) ja ficam abaixo de 8 Mbit/s: para eles o rate-limit nao corta nada")
        else:
            ok("todos os celulares ficam acima de 8 Mbit/s na carga: o rate-limit teria o que cortar")
    if n > 1:
        info("com mais de 1 celular, as regras que olham o tempo (media movel, janela, persistencia) rodam sobre a CELULA: "
             "1 linha por instante, vazao e atraso pela media dos usuarios, PRB da celula.")
    return meta


def main():
    ap = argparse.ArgumentParser(description="Gera um cenario de KPM sugerido pelo servidor (dados sinteticos)")
    ap.add_argument("--ues", type=int, required=True, choices=N_UES)
    ap.add_argument("--distancia", required=True, choices=list(DISTANCIAS) + ["mista"])
    ap.add_argument("--interferencia", required=True, choices=list(CIR_DB))
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    reg = gerar(a.ues, a.distancia, a.interferencia, a.seed)
    escrever(a.out, reg)
    print(f"{len(reg)} linhas gravadas em {a.out} ({a.ues} celular(es), {ROTULO_DIST[a.distancia]}, {ROTULO_INTERF[a.interferencia]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
