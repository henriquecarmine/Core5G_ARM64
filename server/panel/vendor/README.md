# vendor/ — dependências vendorizadas (offline)

Wheels do **scikit-learn 1.9.0** e dependências (numpy, scipy, joblib, threadpoolctl,
narwhals) para a plataforma do servidor: **aarch64, Python 3.12 (Ubuntu 24.04)**.

Baixados no próprio servidor ARM64 em 2026-07-02, então batem exatamente com o
venv do painel. Total ~57 MB.

## Propósito

O scikit-learn será usado nos componentes de inteligência do RAN (O-RAN):

- **Near-RT RIC** — xApps com ML sobre as métricas E2SM-KPM (pipeline de dados
  KPM da v0.31.0), ex.: detecção de anomalia e classificação de carga em
  escala de segundos.
- **Non-RT RIC** — rApps/análise offline sobre séries históricas de KPIs para
  políticas de otimização (A1) em escala de minutos/horas.

Ainda não está instalado no venv do painel nem referenciado no
`requirements.txt` — por ora apenas vendorizado nesta pasta.

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
