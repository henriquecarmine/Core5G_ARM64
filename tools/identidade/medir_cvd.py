# -*- coding: utf-8 -*-
"""Separação das cores de estado sob visão normal e sob as três dicromacias.

Simulação de Viénot/Brettel sobre RGB linear; distância em OKLab (x100), que é
perceptualmente uniforme — ao contrário de comparar hex a olho.
Alvos: >=8 entre pares sob daltonismo; >=15 sob visão normal.
"""
import math, sys, itertools

def s2l(c):
    c/=255
    return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def l2s(u):
    u=max(0.0,min(1.0,u))
    return 12.92*u if u<=0.0031308 else 1.055*(u**(1/2.4))-0.055
def hex2lin(h):
    h=h.lstrip("#"); return [s2l(int(h[i:i+2],16)) for i in (0,2,4)]
def oklab(lin):
    r,g,b=lin
    l=0.4122214708*r+0.5363325363*g+0.0514459929*b
    m=0.2119034982*r+0.6806995451*g+0.1073969566*b
    s=0.0883024619*r+0.2817188376*g+0.6299787005*b
    l,m,s=l**(1/3) if l>0 else 0,m**(1/3) if m>0 else 0,s**(1/3) if s>0 else 0
    return (0.2104542553*l+0.7936177850*m-0.0040720468*s,
            1.9779984951*l-2.4285922050*m+0.4505937099*s,
            0.0259040371*l+0.7827717662*m-0.8086757660*s)
def dE(a,b):
    A,B=oklab(a),oklab(b)
    return 100*math.sqrt(sum((A[i]-B[i])**2 for i in range(3)))

def lms(lin):
    r,g,b=lin
    return (17.8824*r+43.5161*g+4.11935*b,
            3.45565*r+27.1554*g+3.86714*b,
            0.0299566*r+0.184309*g+1.46709*b)
def rgb(L,M,S):
    return (0.080944*L-0.130504*M+0.116721*S,
           -0.010248*L+0.054019*M-0.113614*S,
           -0.000365*L-0.004121*M+0.693513*S)
def simula(lin,tipo):
    L,M,S=lms(lin)
    if tipo=="protanopia":   L=2.02344*M-2.52581*S
    elif tipo=="deuteranopia": M=0.494207*L+1.24827*S
    else:                     S=-0.395913*L+0.801109*M
    return [max(0.0,min(1.0,x)) for x in rgb(L,M,S)]

def checa(nome,cores,rotulos):
    print(f"\n===== {nome} =====")
    pior=99
    for modo in ("visão normal","protanopia","deuteranopia","tritanopia"):
        vals=[]
        for (i,a),(j,b) in itertools.combinations(enumerate(cores),2):
            la,lb=hex2lin(a),hex2lin(b)
            if modo!="visão normal":
                la,lb=simula(la,modo),simula(lb,modo)
            d=dE(la,lb); vals.append((d,rotulos[i],rotulos[j]))
        vals.sort()
        alvo=15 if modo=="visão normal" else 8
        d,ra,rb=vals[0]
        sit="OK   " if d>=alvo else ("PISO " if d>=6 else "FALHA")
        print(f"  {sit} pior par sob {modo:13}: {d:5.1f}  ({ra} x {rb})   alvo {alvo}")
        if modo!="visão normal": pior=min(pior,d)
    return pior

ROT=["acento","bom","atenção","falha"]
checa("TEMA CLARO — sólidos de estado", ["#7e7aef","#3ba45a","#b68103","#e5554c"], ROT)
checa("TEMA ESCURO — sólidos de estado", ["#8f8dfb","#4fb56b","#ca9105","#f36c61"], ROT)
checa("CLARO — texto colorido (degrau 11)", ["#5e5cb4","#2c7b43","#896100","#ac4039"], ROT)
checa("ESCURO — texto colorido (degrau 11)", ["#adb0ff","#7dce8f","#e2af53","#fe988d"], ROT)
