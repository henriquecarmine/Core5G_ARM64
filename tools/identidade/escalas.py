# -*- coding: utf-8 -*-
"""Gera as escalas da identidade em OKLCH e imprime em sRGB (hex).

Só biblioteca padrão — a conversão OKLab→sRGB é a do Björn Ottosson.
Cada família tem 12 degraus com PAPEL fixo (convenção Radix):
  1-2 fundo · 3-5 fundo de componente · 6-8 traço · 9-10 sólido · 11-12 texto
Claro e escuro NÃO são inversão: cada tema tem a sua curva de lightness e de
croma, porque o olho não lê os dois do mesmo jeito.
"""
import math, json

def oklch_to_srgb(L, C, H):
    a = C * math.cos(math.radians(H)); b = C * math.sin(math.radians(H))
    l_ = L + 0.3963377774*a + 0.2158037573*b
    m_ = L - 0.1055613458*a - 0.0638541728*b
    s_ = L - 0.0894841775*a - 1.2914855480*b
    l, m, s = l_**3, m_**3, s_**3
    r = +4.0767416621*l - 3.3077115913*m + 0.2309699292*s
    g = -1.2684380046*l + 2.6097574011*m - 0.3413193965*s
    bb = -0.0041960863*l - 0.7034186147*m + 1.7076147010*s
    def enc(u):
        u = 12.92*u if u <= 0.0031308 else 1.055*(max(u, 0.0)**(1/2.4)) - 0.055
        return max(0, min(255, round(u*255)))
    return (enc(r), enc(g), enc(bb))

def hexof(L, C, H):
    return "#%02x%02x%02x" % oklch_to_srgb(L, C, H)

def dentro(L, C, H):
    """A cor cabe no sRGB sem cortar canal?"""
    a = C*math.cos(math.radians(H)); b = C*math.sin(math.radians(H))
    l_=L+0.3963377774*a+0.2158037573*b; m_=L-0.1055613458*a-0.0638541728*b; s_=L-0.0894841775*a-1.2914855480*b
    l,m,s=l_**3,m_**3,s_**3
    r=+4.0767416621*l-3.3077115913*m+0.2309699292*s
    g=-1.2684380046*l+2.6097574011*m-0.3413193965*s
    bb=-0.0041960863*l-0.7034186147*m+1.7076147010*s
    return all(-0.0005 <= u <= 1.0005 for u in (r, g, bb))

def ajusta(L, C, H):
    """Baixa o croma até caber no sRGB — mantém a lightness, que é o que
    carrega o contraste."""
    while C > 0 and not dentro(L, C, H):
        C -= 0.002
    return max(C, 0)

# Lightness por degrau. O claro anda de quase-branco a quase-preto; o escuro
# parte de 0.18 (não de preto puro: preto puro cansa a vista) e sobe.
L_CLARO  = [0.993,0.977,0.955,0.933,0.909,0.880,0.842,0.784,0.640,0.590,0.520,0.300]
L_ESCURO = [0.178,0.208,0.248,0.279,0.312,0.352,0.410,0.497,0.640,0.694,0.784,0.936]
# Croma relativo por degrau: pico no 9 (o sólido da marca), fraco nas pontas.
K = [0.10,0.16,0.30,0.42,0.52,0.60,0.72,0.88,1.00,0.96,0.80,0.46]

FAMILIAS = {
    #            hue   croma-pico  (croma-pico do escuro)
    "n":  dict(H=262, C=0.020, Ce=0.024),   # neutro frio — o cinza é levemente azulado
    "a":  dict(H=282, C=0.170, Ce=0.165),   # ACENTO: azul-violeta, a cor do produto
    "g":  dict(H=150, C=0.145, Ce=0.150),   # bom / no ar
    "w":  dict(H=80,  C=0.150, Ce=0.155),   # atenção
    "r":  dict(H=27,  C=0.180, Ce=0.175),   # falha / perigo
}

def escala(fam, tema):
    f = FAMILIAS[fam]
    Ls = L_CLARO if tema == "claro" else L_ESCURO
    Cmax = f["C"] if tema == "claro" else f["Ce"]
    return [hexof(Ls[i], ajusta(Ls[i], Cmax*K[i], f["H"]), f["H"]) for i in range(12)]

saida = {t: {f: escala(f, t) for f in FAMILIAS} for t in ("claro", "escuro")}
for tema in saida:
    print(f"\n===== TEMA {tema.upper()} =====")
    for fam, cores in saida[tema].items():
        print(f"  {fam}: " + " ".join(cores))
open("/tmp/claude-1000/-home-henriquecarmine-Projetos-Core5G-ARM64/b971934c-422c-4ac5-81d0-c9f7cd1c0920/scratchpad/id/escalas.json","w").write(json.dumps(saida, indent=1))
