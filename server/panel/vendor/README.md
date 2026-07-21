# vendor/ — dependências vendorizadas (offline)

Wheels do **scikit-learn 1.9.0** e dependências (numpy, scipy, joblib, threadpoolctl,
narwhals) para a plataforma do servidor: **aarch64, Python 3.12 (Ubuntu 24.04)**.

Baixados no próprio servidor ARM64 em 2026-07-02, então batem exatamente com o
venv do painel. Total ~57 MB.

## Propósito

O scikit-learn roda os **testes de ML por caso de uso** do painel — `p2-ml-uetp`,
`p2-ml-localizacao`, `p2-ml-pm` (v0.47.0): cada um executa o experimento
`../../oai-cn-gnb-e2/scripts/ml/*_experiment.py` (numpy-only) sobre os dados reais
do walk test SUTD e streama a tabela de métricas no console. É também a base dos
componentes de inteligência do RAN (O-RAN):

- **Near-RT RIC** — xApps com ML sobre as métricas E2SM-KPM (pipeline KPM).
- **Non-RT RIC** — rApps/análise offline sobre séries históricas de KPIs (A1).

**Instalado automaticamente** no venv pelo `infra/server-bootstrap.sh` (a partir da
v0.47.0), com o mesmo comando offline abaixo. Os experimentos usam só **numpy +
scikit-learn** — pandas/matplotlib **não** estão vendorizados (por isso os
experimentos do servidor são numpy-only).

## Instalar no venv do painel (no servidor)

```bash
~/server/panel/.venv/bin/pip install --no-index \
    --find-links ~/server/panel/vendor/wheels scikit-learn
```

`--no-index` garante instalação 100% offline, só a partir desta pasta.
O `./deploy.sh panel` já sincroniza `server/panel/` inteiro, incluindo esta pasta.

## Usar

Depois de instalado no venv, é um import normal:

```python
from sklearn.cluster import KMeans
```

## Atualizar os wheels

No servidor (para garantir a plataforma correta):

```bash
~/server/panel/.venv/bin/pip download scikit-learn -d ~/sklearn-wheels
rsync ~/sklearn-wheels/ -> server/panel/vendor/wheels/ (local)
```

Atenção: estes wheels são **aarch64** — não instalam em máquina de
desenvolvimento x86_64.
