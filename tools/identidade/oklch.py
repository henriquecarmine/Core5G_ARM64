# -*- coding: utf-8 -*-
"""OKLCH -> sRGB e contraste WCAG. Só biblioteca padrão.

A conversão OKLab->sRGB é a de Björn Ottosson. Trabalhamos em OKLCH porque o
`L` é perceptualmente uniforme: mexer nele muda o brilho de forma previsível em
qualquer matiz — em HSL, o mesmo `L` em amarelo e em azul dá contrastes
completamente diferentes.
"""
import math


def _lin(L, C, H):
    a = C * math.cos(math.radians(H))
    b = C * math.sin(math.radians(H))
    l_ = L + 0.3963377774*a + 0.2158037573*b
    m_ = L - 0.1055613458*a - 0.0638541728*b
    s_ = L - 0.0894841775*a - 1.2914855480*b
    l, m, s = l_**3, m_**3, s_**3
    return (+4.0767416621*l - 3.3077115913*m + 0.2309699292*s,
            -1.2684380046*l + 2.6097574011*m - 0.3413193965*s,
            -0.0041960863*l - 0.7034186147*m + 1.7076147010*s)


def hexof(L, C, H):
    def enc(u):
        u = 12.92*u if u <= 0.0031308 else 1.055*(max(u, 0.0)**(1/2.4)) - 0.055
        return max(0, min(255, round(u*255)))
    return "#%02x%02x%02x" % tuple(enc(u) for u in _lin(L, C, H))


def na_gama(L, C, H):
    """A cor cabe no sRGB sem cortar canal?"""
    return all(-0.0005 <= u <= 1.0005 for u in _lin(L, C, H))


def croma_max(L, H, teto):
    """Maior croma que cabe no sRGB — a lightness é preservada, porque é ela
    que carrega o contraste."""
    C = teto
    while C > 0 and not na_gama(L, C, H):
        C -= 0.002
    return max(C, 0.0)


def luminancia(h):
    h = h.lstrip("#")
    def canal(c):
        c = int(c, 16) / 255
        return c/12.92 if c <= 0.04045 else ((c + 0.055)/1.055)**2.4
    return 0.2126*canal(h[0:2]) + 0.7152*canal(h[2:4]) + 0.0722*canal(h[4:6])


def contraste(a, b):
    la, lb = luminancia(a), luminancia(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)
