# scripts/ml/ — experimentos scikit-learn dos casos RIC-IA (numpy-only)

Reproduzem os 3 casos de uso do artigo de referência (Ngo et al., *"RAN
Intelligent Controller (RIC): From open-source implementation to real-world
validation"*, ICT Express 10(3), 2024, DOI 10.1016/j.icte.2024.02.001), no
**recorte Instance**, sobre os dados reais do walk test do SUTD
([`FCCLab/sutd_5g_dataset_2023`](https://github.com/FCCLab/sutd_5g_dataset_2023)).

Rodam **no servidor**, disparados pelos testes do painel (`p2-ml-*` →
`scripts/p2_ml_*.sh`), e **streamam a tabela de métricas** ao vivo no console.

| Experimento | Caso | Tarefa | Métricas | Tabela do artigo |
|---|---|---|---|---|
| `uetp_experiment.py` | UE-TP | prever throughput DL (regressão) | RMSE · MAE · R² | Tabela 4 |
| `localization_experiment.py` | Localization | andar do UE (4/5/6) | Acc · Prec · Rec · F1 | Tabela 3 |
| `pm_experiment.py` | Predictive Maintenance | RRUs ativas (2 × 1) | Acc · Prec · Rec · F1 | Tabela 7 |

## Por que numpy-only

O venv do painel no servidor tem apenas **numpy + scipy + scikit-learn + joblib**
(wheels aarch64 em `server/panel/vendor/`); **não tem pandas nem matplotlib**. Por
isso estes scripts leem os CSVs com `numpy.genfromtxt` e **não geram figuras** — a
saída é só a tabela de métricas, streamada linha a linha (`print(..., flush=True)`).
As versões completas com pandas/figuras vivem em `pdfs/02-ric-ai/casos-artigo/`.

## Convenções (recorte Instance, honesto)

- **7 KPMs** do artigo como features (throughput em Mbps no UE-TP); rótulos de
  vazamento (`Corridor_tag`, `lab_*`, `Label`) e identificadores ficam de fora.
- **Split temporal 70:30** por trilha (a 2 Hz o split aleatório vaza vizinhança).
- `GradientBoosting` ≈ XGBoost (mesma família); o `MLP` reproduz a DNN do artigo.

## Uso

```bash
# via painel: botão "IA · ..." no console (Projeto 2), ou direto:
PANEL_PY=~/server/panel/.venv/bin/python3 ./scripts/p2_ml_localizacao.sh
# ou o experimento sozinho:
~/server/panel/.venv/bin/python3 -u scripts/ml/localization_experiment.py --data data/sutd
```

Requer o scikit-learn instalado no venv (o `infra/server-bootstrap.sh` faz isso
offline a partir das wheels vendorizadas). Dados em `../data/sutd/`.
