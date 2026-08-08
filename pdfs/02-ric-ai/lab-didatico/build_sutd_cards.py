#!/usr/bin/env python3
"""
Constrói as aulas Localization e Predictive Maintenance a partir do template do
card de Classificação (o card é genérico sobre o DSC), aplicando substituições
de texto controladas + injetando o datasets_config.json de cada uma.

Gera, por slug:
  <slug>/card-<slug>.tpl.html         (template com __DSC_JSON__, p/ provenance)
  <slug>/card-<slug>.html             (DSC injetado — artefato)
  server/panel/static/lab/lab-<slug>.html (card + "← Painel" + lab-stepper.js)

Rode `gen_sutd_labs.py` antes (produz os datasets_config.json).
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC_TPL = HERE / "classificacao" / "card-classificacao.tpl.html"
STATIC = HERE.parent.parent.parent / "server" / "panel" / "static" / "lab"

BACKLINK = ('      <a href="/" style="display:inline-block;margin-bottom:10px;'
            'font-size:.8rem;font-weight:600;color:var(--accent);'
            'text-decoration:none">← Painel</a>\n')
STEPPER = '\n<script src="/static/lab/lab-stepper.js"></script>\n'


def repls(slug):
    """(old, new) por slug. Cada 'old' deve casar exatamente uma parte do tpl."""
    if slug == "localizacao":
        tec, badge, tab, pct = "Localização", "📍", "3", "84,4%"
        d = [
            ("<title>Lab RIC-IA · Classificação (estado da célula)</title>",
             "<title>Lab RIC-IA · Localização (andar do UE)</title>"),
            ('<div class="eyebrow">Lab RIC · IA — Aula 2 de 6</div>',
             '<div class="eyebrow">Lab RIC · IA — Caso do artigo · Localization</div>'),
            ("<h1>Classificação: em que estado está a célula?</h1>",
             "<h1>Localização: em que andar está o UE?</h1>"),
            ('O segundo tipo de IA, com os <b>datasets rotulados do Prof. Tesolin</b>. Em vez de um número,\n'
             '        prevemos uma <b>categoria</b> — é o que um xApp usa para o RIC agir.',
             'Caso real do artigo de referência (Ngo et al. 2024) sobre o <b>walk test 5G do SUTD</b>:\n'
             '        o RIC estima <b>em que andar</b> (4/5/6) o UE está só com as KPMs de rádio — sem GPS.'),
            ("Datasets rotulados pelo professor. Cada um é um problema de classificação diferente.",
             "Dados reais do walk test do SUTD — 3 trilhas (andares 4/5/6) com os 2 RRUs ativos, 7 KPMs por amostra."),
            ('<span class="youare">aqui</span> xApp Classificação <small>classifica → decide</small>',
             '<span class="youare">aqui</span> xApp Localização <small>estima o andar</small>'),
        ]
    else:  # manutencao
        tec, badge, tab, pct = "Manutenção preditiva", "🛠️", "7", "92,6%"
        d = [
            ("<title>Lab RIC-IA · Classificação (estado da célula)</title>",
             "<title>Lab RIC-IA · Manutenção preditiva (RRU perdida)</title>"),
            ('<div class="eyebrow">Lab RIC · IA — Aula 2 de 6</div>',
             '<div class="eyebrow">Lab RIC · IA — Caso do artigo · Predictive Maintenance</div>'),
            ("<h1>Classificação: em que estado está a célula?</h1>",
             "<h1>Manutenção preditiva: a célula perdeu uma RRU?</h1>"),
            ('O segundo tipo de IA, com os <b>datasets rotulados do Prof. Tesolin</b>. Em vez de um número,\n'
             '        prevemos uma <b>categoria</b> — é o que um xApp usa para o RIC agir.',
             'Caso real do artigo (Ngo et al. 2024) sobre o <b>walk test 5G do SUTD</b>: detectar, pelo lado\n'
             '        do UE, se a célula está com <b>2 RRUs (normal) ou 1 (defeito)</b> — mesmo com o EMS dizendo que está OK.'),
            ("Datasets rotulados pelo professor. Cada um é um problema de classificação diferente.",
             "Dados reais do SUTD no andar 6: a MESMA rota com 2 RRUs ativas (normal) e com 1 RRU (defeito), 7 KPMs."),
            ('<span class="youare">aqui</span> xApp Classificação <small>classifica → decide</small>',
             '<span class="youare">aqui</span> rApp Manutenção <small>detecta RRU perdida</small>'),
        ]
    # comuns aos dois (usam tec/badge/tab/pct)
    d += [
        ('<span class="srcbadge src-prof">BASE DO PROFESSOR</span>',
         '<span class="srcbadge src-prof">DADOS REAIS · SUTD</span>'),
        ('<b>Protótipo de design</b> — card “Classificação” (família) do lab de RIC-IA. Usa os\n'
         '    datasets <b>rotulados pelo Prof. Tesolin</b> (Base Fonts RIC, valores e rótulos originais). Preditor ao vivo:\n'
         '    Regressão Logística interpretável; a tabela compara 7 classificadores. Faltam kNN/Naive Bayes/SVM (tabelas largas).',
         f'<b>Caso do artigo</b> — {tec}-rApp sobre os dados reais do <b>walk test SUTD</b> (Ngo et al. 2024).\n'
         '    Preditor ao vivo: Regressão Logística interpretável; a tabela compara 7 classificadores no\n'
         f'    <b>split temporal 70:30</b> (recorte Instance). O campeão reproduz o XGBoost da Tabela {tab} do artigo (~{pct}).'),
        (f'const REP={{tec:"Classificação",badge:"🚦",fam:"aprendizado supervisionado",slug:()=>"classificacao-"+cur,',
         f'const REP={{tec:"{tec}",badge:"{badge}",fam:"aprendizado supervisionado · {tec}-rApp",slug:()=>"{slug}-"+cur,'),
        ("— base rotulada do professor, ${D.n_rows} linhas.",
         "— dados reais do walk test SUTD, ${D.n_rows} amostras."),
        ('limites(){return [`Base pequena (${D.n_rows} linhas) — ótima para aprender, curta para produção.`,\n'
         '  `Os rótulos são do professor; num RIC real viriam de eventos medidos na rede.`,\n'
         '  `Próximo passo: classificar com <b>KPM real</b> (PRB/throughput por célula via E2).`];},',
         'limites(){return [`Recorte <b>Instance</b> (1 amostra); a variante <i>sequence</i> (janela de 10) sobe mais, mas fica fora da abordagem designada.`,\n'
         '  `O <b>split temporal 70:30</b> evita o vazamento que o split aleatório causa a 2 Hz (senão a acurácia infla).`,\n'
         '  `Próximo passo: rodar o mesmo caso com <b>KPM real</b> (via E2) no console do painel.`];},'),
        ("por validação cruzada estratificada, medindo",
         "num split temporal 70:30 (honesto para amostras a 2 Hz), medindo"),
        ("Para o estado da célula, os KPIs separam bem as classes, o que a torna uma escolha adequada e explicável.",
         "Aqui as KPMs de rádio (RSRP/RSRQ/SINR à frente) carregam a assinatura de cada classe, o que torna a logística adequada e explicável."),
        ("# Script da entrega — Classificação (${D.label})\n"
         "# Coloque ao lado o CSV do professor (colunas: ${D.features.map(f=>f.key).join(\", \")}, ${D.target_name})",
         f"# Script — {tec} (${{D.label}}) · dados reais do walk test SUTD (Ngo et al. 2024)\n"
         "# CSV com colunas: ${D.features.map(f=>f.key).join(\", \")}, ${D.target_name}"),
    ]
    if slug == "localizacao":
        d.append(('const LESSON="classificacao", NEXT="/lab/clustering";',
                  'const LESSON="localizacao", NEXT="/lab/manutencao";'))
    else:
        d.append(('const LESSON="classificacao", NEXT="/lab/clustering";',
                  'const LESSON="manutencao", NEXT="/lab/clustering";'))
    return d


def build(slug):
    txt = SRC_TPL.read_text(encoding="utf-8")
    for old, new in repls(slug):
        if txt.count(old) != 1:
            raise SystemExit(f"[{slug}] âncora não única/ausente ({txt.count(old)}x):\n  {old[:90]!r}")
        txt = txt.replace(old, new)

    outdir = HERE / slug
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / f"card-{slug}.tpl.html").write_text(txt, encoding="utf-8")

    dsc = (outdir / "datasets_config.json").read_text(encoding="utf-8")
    if "__DSC_JSON__" not in txt:
        raise SystemExit(f"[{slug}] placeholder __DSC_JSON__ ausente no tpl")
    card = txt.replace("__DSC_JSON__", dsc.strip())
    (outdir / f"card-{slug}.html").write_text(card, encoding="utf-8")

    # página servida = card + backlink (antes do 1º .eyebrow) + stepper no fim
    anchor = '      <div class="eyebrow">'
    page = card.replace(anchor, BACKLINK + anchor, 1)
    page = page.rstrip("\n") + STEPPER
    (STATIC / f"lab-{slug}.html").write_text(page, encoding="utf-8")
    print(f"{slug:<12s} -> card-{slug}.html + static/lab-{slug}.html "
          f"({len(page)} bytes)")


if __name__ == "__main__":
    for s in ("localizacao", "manutencao"):
        build(s)
