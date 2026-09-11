#!/usr/bin/env python3
"""Testes do cenarios_kpm.py e da visao da celula (so biblioteca padrao).

O que precisa continuar verdade:
  * o gerador e deterministico e cada linha se declara sintetica;
  * PRB entre 0 e 100, vazao e atraso nao negativos;
  * 1 celular a 100 m sem interferencia reproduz a amostra real do professor;
  * mais celulares -> menos vazao POR usuario, com a soma perto da capacidade;
  * mais distancia -> menos vazao, mesmo PRB;
  * interferencia -> vazao cai SO na janela, com o PRB inalterado (a assinatura
    de jammer da aula 05);
  * a visao da celula tem 1 linha por instante e a soma bate;
  * os 3 scripts rodam em todos os cenarios sem quebrar e imprimem a explicacao.

Uso: python3 test_cenarios.py
"""
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import cenarios_kpm as cen  # noqa: E402
from temas_projeto import Data, load, mean, median  # noqa: E402


def para_data(registros):
    fh = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    fh.close()
    cen.escrever(fh.name, registros)
    try:
        rows, phases, _f, _i = load(fh.name)
    finally:
        os.unlink(fh.name)
    return Data(rows, phases)


def carga(registros, ue=None, janela=None):
    out = []
    for r in registros:
        if r["phase"] != "stress" or (ue and r["ue"] != ue):
            continue
        if janela is not None and r["radio"]["interferencia_ativa"] != janela:
            continue
        out.append(r["metrics"]["DRB.UEThpUl"])
    return out


class Gerador(unittest.TestCase):
    def test_deterministico_e_marcado_como_sintetico(self):
        a = cen.gerar(5, "mista", "media")
        b = cen.gerar(5, "mista", "media")
        self.assertEqual(a, b)
        self.assertTrue(all(r["cenario"]["sintetico"] for r in a))
        self.assertEqual(len(a), 100 * 5)

    def test_limites_fisicos(self):
        for n in cen.N_UES:
            for r in cen.gerar(n, "3km", "alta"):
                m = r["metrics"]
                self.assertTrue(0 <= m["RRU.PrbTotUl"] <= 100)
                self.assertGreaterEqual(m["DRB.UEThpUl"], 0)
                self.assertGreaterEqual(m["DRB.RlcSduDelayDl"], 0)

    def test_um_celular_perto_reproduz_a_amostra_real(self):
        d = para_data(cen.gerar(1, "100m", "none"))
        real_rows, real_ph, _f, _i = load(os.path.join(AQUI, "samples", "kpm_ue_tp_sample.jsonl"))
        real = Data(real_rows, real_ph)
        self.assertEqual(d.phases, real.phases)
        for fase in d.phases:
            self.assertEqual(d.n(fase), real.n(fase))
        self.assertAlmostEqual(median(d.col("thp", "stress")) / median(real.col("thp", "stress")), 1, delta=0.05)
        self.assertEqual(median(d.col("prb", "stress")), median(real.col("prb", "stress")))
        self.assertAlmostEqual(median(d.col("thp", "baseline")), median(real.col("thp", "baseline")), delta=0.2)

    def test_mais_celulares_menos_vazao_por_usuario_e_soma_estavel(self):
        por_ue, soma = [], []
        for n in cen.N_UES:
            reg = cen.gerar(n, "100m", "none")
            por_ue.append(median(carga(reg, "ue-01")))
            soma.append(median(carga(reg)) * n)
        self.assertEqual(por_ue, sorted(por_ue, reverse=True))
        for s in soma:
            self.assertAlmostEqual(s / soma[0], 1, delta=0.08)

    def test_mais_distancia_menos_vazao_mesmo_prb(self):
        vaz, prb = [], []
        for dist in ["100m", "500m", "1km", "3km"]:
            reg = cen.gerar(1, dist, "none")
            vaz.append(median(carga(reg)))
            prb.append(median([r["metrics"]["RRU.PrbTotUl"] for r in reg if r["phase"] == "stress"]))
        self.assertEqual(vaz, sorted(vaz, reverse=True))
        self.assertEqual(len(set(prb)), 1)

    def test_interferencia_derruba_a_vazao_so_na_janela_com_prb_igual(self):
        for nivel in ["fraca", "media", "alta"]:
            reg = cen.gerar(2, "100m", nivel)
            fora, dentro = median(carga(reg, "ue-01", False)), median(carga(reg, "ue-01", True))
            self.assertLess(dentro, fora)
            prb_fora = median([r["metrics"]["RRU.PrbTotUl"] for r in reg if r["phase"] == "stress" and not r["radio"]["interferencia_ativa"]])
            prb_dentro = median([r["metrics"]["RRU.PrbTotUl"] for r in reg if r["phase"] == "stress" and r["radio"]["interferencia_ativa"]])
            self.assertEqual(prb_fora, prb_dentro)
        quedas = [median(carga(cen.gerar(1, "100m", n), janela=True)) for n in ["fraca", "media", "alta"]]
        self.assertEqual(quedas, sorted(quedas, reverse=True))

    def test_modelo_bate_com_o_lab_do_ue(self):
        # os valores que o test_channel.sh do P1 imprime
        self.assertAlmostEqual(cen.perda_percurso_db(100), 102.6, delta=0.1)
        self.assertAlmostEqual(cen.perda_percurso_db(500), 129.9, delta=0.1)
        self.assertAlmostEqual(cen.perda_percurso_db(1000), 141.7, delta=0.1)
        self.assertAlmostEqual(cen.rsrp_dbm(100), -44, delta=0.1)

    def test_opcoes_invalidas_recusadas(self):
        for args in [(3, "100m", "none"), (1, "2km", "none"), (1, "100m", "forte")]:
            with self.assertRaises(ValueError):
                cen.validar(*args)


class Celula(unittest.TestCase):
    def test_uma_linha_por_instante_e_soma(self):
        d = para_data(cen.gerar(5, "mista", "none"))
        self.assertTrue(d.multi)
        c = d.celula()
        self.assertFalse(c.multi)
        self.assertEqual(c.n_ue, 5)
        self.assertEqual(len(c.rows), 100)
        r0 = [r for r in d.rows if r["phase"] == "stress" and r["idx"] == 3]
        c0 = [r for r in c.rows if r["phase"] == "stress" and r["idx"] == 3][0]
        self.assertAlmostEqual(c0["thp_soma"], sum(r["thp"] for r in r0))
        self.assertAlmostEqual(c0["thp"], mean([r["thp"] for r in r0]))


class Scripts(unittest.TestCase):
    CENARIOS = [(n, "mista", "media") for n in cen.N_UES] + \
               [(5, d, "none") for d in ["100m", "500m", "1km", "3km"]] + \
               [(5, "100m", i) for i in ["fraca", "alta"]]

    def _roda(self, modulo, argv):
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", [modulo.__file__] + argv), redirect_stdout(buf):
            rc = modulo.main()
        return rc, buf.getvalue()

    def test_os_tres_scripts_em_varios_cenarios(self):
        import aula04_indicadores
        import closed_loop
        import temas_projeto
        for n, dist, interf in self.CENARIOS:
            with self.subTest(n=n, dist=dist, interf=interf), tempfile.TemporaryDirectory() as tmp:
                arq = os.path.join(tmp, "c.jsonl")
                cen.escrever(arq, cen.gerar(n, dist, interf))
                for mod, argv in [(temas_projeto, ["--tema", "all", "--file", arq]),
                                  (aula04_indicadores, ["--file", arq]),
                                  (closed_loop, ["--file", arq, "--out", os.path.join(tmp, "out")])]:
                    rc, saida = self._roda(mod, argv)
                    self.assertEqual(rc, 0, mod.__name__)
                    self.assertIn("DADOS SINTETICOS", saida, mod.__name__)
                    self.assertIn("Veredito", saida, mod.__name__)

    def test_amostra_real_nao_ganha_bloco_de_cenario(self):
        import temas_projeto
        rc, saida = self._roda(temas_projeto, ["--tema", "t1", "--file", os.path.join(AQUI, "samples", "kpm_ue_tp_sample.jsonl")])
        self.assertEqual(rc, 0)
        self.assertNotIn("Cenario sugerido", saida)


if __name__ == "__main__":
    unittest.main(verbosity=2)
