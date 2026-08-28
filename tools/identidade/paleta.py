# -*- coding: utf-8 -*-
"""A paleta do Core5G_ARM64 — a receita, num lugar só.

Colorimetria a serviço da programação visual: cada cor é descrita por matiz,
lightness e croma em OKLCH, e o hex sai daí. Ninguém escolhe hex à mão.

Regras que valem para os dois temas:
  · 12 degraus por família, com PAPEL fixo (convenção Radix):
      1-2 fundo · 3-5 componente · 6-8 traço · 9-10 sólido · 11-12 texto
  · claro e escuro NÃO são inversão: cada um tem a sua curva
  · o escuro parte de #111112, não de preto puro (preto puro cansa a vista)
"""

# matiz de cada família, em graus OKLCH
HUE = {
    "n": 262,   # neutro — croma baixo: cinza levemente azulado, nunca morto
    "a": 282,   # acento — azul-violeta: a cor do produto, nunca um estado
    "g": 150,   # bom
    "w": 80,    # atenção
    "r": 27,    # falha
    "c": 200,   # contraponto — o SEGUNDO acento. Existe porque o Lab de IA
                # opõe duas categorias o tempo todo (supervisionado x não
                # supervisionado) e um par precisa de dois matizes.
    "l": 350,   # ao vivo — a aula sendo transmitida. Não é estado da rede nem
                # o acento: é o único momento em que a sala inteira está vendo
                # a mesma tela, e merece cor própria.
}

# croma de pico por família e tema
CROMA = {
    "n": {"claro": 0.020, "escuro": 0.024},
    "a": {"claro": 0.170, "escuro": 0.165},
    "g": {"claro": 0.145, "escuro": 0.150},
    "w": {"claro": 0.150, "escuro": 0.155},
    "r": {"claro": 0.180, "escuro": 0.175},
    "c": {"claro": 0.120, "escuro": 0.125},
    "l": {"claro": 0.170, "escuro": 0.170},
}

# curva de lightness dos 12 degraus
L = {
    "claro":  [0.993, 0.977, 0.955, 0.933, 0.909, 0.880, 0.842, 0.784, 0.640, 0.590, 0.520, 0.300],
    "escuro": [0.178, 0.208, 0.248, 0.279, 0.312, 0.352, 0.410, 0.497, 0.640, 0.694, 0.784, 0.936],
}

# croma relativo por degrau: pico no 9 (o sólido da marca), fraco nas pontas
K = [0.10, 0.16, 0.30, 0.42, 0.52, 0.60, 0.72, 0.88, 1.00, 0.96, 0.80, 0.46]

# O degrau 9 é o sólido de sinalização e NÃO segue a curva: cada cor recebe a
# lightness em que ela PARECE a cor padrão. Âmbar a 0.640 vira mostarda;
# vermelho claro demais vira rosa. É escolha de sinalização, não de rampa.
SOLIDO_L = {
    "claro":  {"a": 0.62, "g": 0.62, "w": 0.78, "r": 0.58, "c": 0.60, "l": 0.60},
    "escuro": {"a": 0.66, "g": 0.68, "w": 0.82, "r": 0.62, "c": 0.68, "l": 0.66},
}

# ---- rampa CATEGÓRICA -------------------------------------------------
# A topologia precisa distinguir 8 DOMÍNIOS de rede (RAN, core plano de
# controle, core plano de usuário, non-RT RIC, O-RAN SC, externo, admin). Cor
# ali é IDENTIDADE, não estado — por isso sai de uma rampa própria e nunca do
# verde/âmbar/vermelho de sinalização.
#
# Oito matizes igualmente espaçados (45°), começando no acento: a separação
# máxima possível para oito categorias. A ordem é FIXA — categoria nova entra
# no próximo slot, nunca se recicla matiz.
CAT_HUE = [282, 237, 192, 147, 102, 57, 12, 327]
CAT_L   = {"claro": 0.56, "escuro": 0.68}
CAT_C   = {"claro": 0.150, "escuro": 0.135}


def categoricas(tema):
    from oklch import hexof, croma_max
    L, C = CAT_L[tema], CAT_C[tema]
    return [hexof(L, croma_max(L, h, C), h) for h in CAT_HUE]


NOMES = {"n": "neutro", "a": "acento", "g": "bom", "w": "atenção", "r": "falha", "c": "contraponto", "l": "ao vivo"}
FUNDO = {"claro": 0, "escuro": 0}      # o fundo é sempre o degrau 1 do neutro


# Quando o degrau 9 sai da curva (sinalização), o 10 sai junto: ele é o estado
# de passagem do mouse do 9, não um ponto qualquer da rampa. No claro escurece;
# no escuro clareia. Sem isso a rampa deixa de ser monótona — o 10 ficava mais
# claro que o 9 no âmbar e no vermelho.
HOVER = {"claro": -0.05, "escuro": +0.06}


def escala(fam, tema):
    from oklch import hexof, croma_max
    pico = CROMA[fam][tema]
    solido = SOLIDO_L[tema].get(fam)
    fora = []
    for i in range(12):
        if i == 8 and solido is not None:
            li, ci = solido, pico
        elif i == 9 and solido is not None:
            li, ci = solido + HOVER[tema], pico * K[9]
        else:
            li, ci = L[tema][i], pico * K[i]
        fora.append(hexof(li, croma_max(li, HUE[fam], ci), HUE[fam]))
    return fora


def todas():
    return {t: {f: escala(f, t) for f in HUE} for t in ("claro", "escuro")}


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    for tema, fams in todas().items():
        print(f"\n===== TEMA {tema.upper()} =====")
        for f, cores in fams.items():
            print(f"  {NOMES[f]:11} " + " ".join(cores))
        print(f"  {'categórica':11} " + " ".join(categoricas(tema)))
