#!/usr/bin/env python3
"""Testes do closed_loop.py (so biblioteca padrao).

O que precisa continuar verdade:
  * sobre a amostra do professor, a decisao sai 'apply' e a cadeia inteira
    gera os artefatos no formato do lab (policy, action_request, effect_report);
  * o effect_report offline NUNCA se declara causal;
  * sem carga, a decisao e 'observe' e nao nasce politica nem acao;
  * sem fase 'depois', nao ha effect_report;
  * o modo offline nao consegue executar comando nenhum (nem importa subprocess).

Uso: python3 test_closed_loop.py
"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import closed_loop as cl  # noqa: E402
from temas_projeto import Data, load  # noqa: E402

AMOSTRA = os.path.join(AQUI, "samples", "kpm_ue_tp_sample.jsonl")


def dados(caminho=AMOSTRA):
    rows, phases, _fmt, _inf = load(caminho)
    return Data(rows, phases)


def roda(argv):
    buf = io.StringIO()
    with mock.patch.object(sys, "argv", ["closed_loop.py"] + argv), redirect_stdout(buf):
        rc = cl.main()
    return rc, buf.getvalue()


class Calculos(unittest.TestCase):
    def test_amostra_decide_apply_e_monta_a_cadeia(self):
        d = dados()
        base, carga, depois = cl.fases(d.phases)
        self.assertEqual((base, carga, depois), ("baseline", "stress", "recovery"))
        model = cl.treinar(d, base)
        self.assertEqual(model["algorithm"], "robust-baseline-mad")
        aval = cl.avaliar(d, carga, model)
        self.assertEqual(aval["decision"], "apply")
        self.assertEqual(aval["window_size"], cl.CFG["window"])
        pol = cl.politica(aval, "teste")
        self.assertEqual(pol["policytype_id"], "1")
        self.assertEqual(pol["lab_context"]["decision_id"], aval["decision_id"])
        acao = cl.pedido_de_acao(pol)
        self.assertEqual(acao["action"], "rate_limit")
        self.assertEqual(acao["target"]["direction"], "uplink")
        self.assertEqual(acao["policy_id"], pol["policy_id"])

    def test_effect_report_offline_nunca_e_causal(self):
        d = dados()
        rep = cl.efeito(d, "stress", "recovery", offline=True)
        self.assertIs(rep["causal"], False)
        self.assertIn("nao e efeito", rep["note"])
        thp = "DRB.UEThpUl"
        b, a = rep["before"][thp]["mean"], rep["after"][thp]["mean"]
        self.assertAlmostEqual(rep["relative_delta_mean_pct"][thp], 100 * (a - b) / b)
        prb = "RRU.PrbTotUl"
        self.assertAlmostEqual(rep["delta_pp_mean"][prb], rep["after"][prb]["mean"] - rep["before"][prb]["mean"])

    def test_numeros_da_aula_batem_com_os_slides(self):
        t, p = cl.AULA["thp"], cl.AULA["prb"]
        # o slide arredonda as medias; o artefato usa as medias sem arredondar
        self.assertAlmostEqual(cl.rel(t["antes_media"], t["depois_media"]), cl.AULA["artefato"]["thp_rel"], delta=0.1)
        self.assertAlmostEqual(cl.rel(p["antes_media"], p["depois_media"]), cl.AULA["artefato"]["prb_rel"], delta=0.1)
        self.assertAlmostEqual(p["depois_media"] - p["antes_media"], cl.AULA["artefato"]["prb_pp"], delta=0.1)

    def test_recuperacao(self):
        self.assertAlmostEqual(cl.recuperacao(100, 10, 100), 1.0)
        self.assertAlmostEqual(cl.recuperacao(100, 10, 55), 0.5)
        self.assertIsNone(cl.recuperacao(10, 10, 10))


class Fluxo(unittest.TestCase):
    def _arquivo(self, linhas):
        fh = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
        for ln in linhas:
            fh.write(json.dumps(ln) + "\n")
        fh.close()
        self.addCleanup(os.unlink, fh.name)
        return fh.name

    def _amostras(self, fase, n, thp, delay, prb):
        return [{"phase": fase, "sample_index": i,
                 "metrics": {"DRB.UEThpUl": thp, "DRB.RlcSduDelayDl": delay, "RRU.PrbTotUl": prb}} for i in range(n)]

    def test_cadeia_completa_grava_os_artefatos(self):
        with tempfile.TemporaryDirectory() as out:
            rc, saida = roda(["--file", AMOSTRA, "--out", out])
            self.assertEqual(rc, 0)
            for nome in ["model.json", "decision.json", "policy.json", "action_request.json",
                         "effect_report.json", "actuator_events.jsonl"]:
                self.assertTrue(os.path.exists(os.path.join(out, nome)), nome)
            with open(os.path.join(out, "actuator_events.jsonl"), encoding="utf-8") as fh:
                eventos = [json.loads(l)["event"] for l in fh]
            self.assertEqual(eventos, ["decision", "a1_dry_run", "emulate_dry_run", "effect_report", "rollback_dry_run"])
            self.assertIn("NAO E EFEITO DA ATUACAO", saida)
            self.assertIn("Veredito:", saida)
            for passo in range(1, 9):
                self.assertIn(f"{passo}. ", saida)

    def test_sem_carga_nao_nasce_politica(self):
        calmo = self._amostras("baseline", 20, 3.7, 0.0, 2.0) + self._amostras("stress", 20, 3.7, 0.0, 2.0)
        with tempfile.TemporaryDirectory() as out:
            rc, saida = roda(["--file", self._arquivo(calmo), "--out", out])
            self.assertEqual(rc, 0)
            self.assertIn("decision observe", saida)
            self.assertFalse(os.path.exists(os.path.join(out, "policy.json")))
            self.assertFalse(os.path.exists(os.path.join(out, "action_request.json")))

    def test_sem_fase_depois_nao_ha_effect_report(self):
        duas = self._amostras("baseline", 20, 3.7, 0.0, 2.0) + self._amostras("stress", 20, 80000.0, 150.0, 99.0)
        with tempfile.TemporaryDirectory() as out:
            rc, saida = roda(["--file", self._arquivo(duas), "--out", out])
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.exists(os.path.join(out, "action_request.json")))
            self.assertFalse(os.path.exists(os.path.join(out, "effect_report.json")))
            self.assertIn("sem janela 'depois'", saida)


class Seguranca(unittest.TestCase):
    def test_offline_nao_tem_como_executar_comando(self):
        with open(cl.__file__, encoding="utf-8") as fh:
            fonte = fh.read()
        for proibido in ("import subprocess", "os.system", "os.popen", "Popen("):
            self.assertNotIn(proibido, fonte)


if __name__ == "__main__":
    unittest.main(verbosity=2)
