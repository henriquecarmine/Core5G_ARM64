# Política de custos da plataforma

> Atende o **ponto 8 do checklist do Prof. Jonas** (2026-07-02): *"tomar muito
> cuidado com os custos de manutenção da plataforma para não comprometer o
> orçamento"*. Este documento é a referência única de quanto custa, quais são
> as regras de operação e como decidir upgrades. Contexto: o servidor é
> custeado do bolso do mantenedor (ver README §6).

## 1. O que custa hoje (2026-07-03)

| Item | Valor | Custo aproximado* |
|---|---|---|
| Instância EC2 **t4g.medium** (2 vCPU Graviton2, 4 GB) — `us-east-2` | ligada 24/7 | ~US$ 25/mês |
| Volume EBS 30 GB (gp3) | sempre | ~US$ 2,5/mês |
| Tráfego de saída | poucos GB/mês (painel + deploys) | ~US$ 0–2/mês |
| DuckDNS (DNS dinâmico) | — | grátis |
| **Total típico** | | **~US$ 28–30/mês** |

*Valores de referência on-demand `us-east-2`; conferir na fatura. Instância
**parada** (stop) paga só o EBS (~US$ 2,5/mês) — o dado persiste.

## 2. Regras de operação (para não estourar o orçamento)

1. **Desligar fora de aula quando possível.** `stop` na instância preserva
   tudo (disco, imagens, dados); ao religar, o cron do DuckDNS re-aponta o
   domínio em ≤5 min. Uma instância que roda só em aulas + preparação
   (~40 h/mês) custa ~1/5 do 24/7.
2. **Teste `p2-test-e2-kpm-traffic` roda 1× destacado, nunca em série.**
   Ele satura o box de 2 vCPU (load ~30, derruba SSH) — além do risco, CPU
   burstable queima créditos (ver §4).
3. **Higiene de disco é recorrente.** Em 2026-07-03 o disco chegou a 8% livre;
   a limpeza recuperou 5,5 GB (3,1 GB → 8,6 GB livres). Causas e prevenções:
   - **Volumes MySQL anônimos órfãos** (197 MB por religada do core P2):
     corrigido na raiz com volume nomeado `mysql-data` no compose do
     `oai-cn5g-v2`. Se voltar a acumular: `docker volume prune -f` (remove só
     anônimos; os nomeados — MongoDB dos alunos — ficam).
   - **Imagens não usadas**: só remover com aval (as OAI arm64 custom e o
     `oai-upf-vpp` portado NÃO são re-puxáveis; as oficiais v1.5.1/mysql:8.0
     legadas foram removidas com aval em 2026-07-03).
   - Journal/apt: `journalctl --vacuum-size=100M` + `apt-get clean`.
   - **Binários grandes nunca entram no git** (política do `.gitignore`).
4. **Alerta prático:** abaixo de ~15% de disco livre ou load sustentado > 4,
   investigar antes de rodar labs pesados.

## 3. Upgrade de CPU — laboratório de RIC (Near-RT/Non-RT) com IA

O lab de IA (xApps com scikit-learn no Near-RT + rApps de treino no Non-RT)
**não cabe na t4g.medium**. Isso já era verdade ANTES da IA: o relatório
completo de KPM com throughput real depende de 4 vCPU (bible §10 — forçar os
2 cores congelou o box 2×). A IA soma inferência no loop de segundos, treino
batch e ~200–300 MB de RAM por processo Python (numpy/scipy/sklearn — wheels
aarch64 já vendorados em `server/panel/vendor/`).

| Cenário | vCPU/RAM | Custo 24/7* | Observação |
|---|---|---|---|
| t4g.medium (atual) | 2 / 4 GB | ~US$ 25/mês | P1 e demos leves; **insuficiente p/ IA e KPM real** |
| **t4g.xlarge** | 4 / 16 GB | ~US$ 97/mês | Resolve; mas é *burstable* — load sustentado consome créditos de CPU (modo `unlimited` cobra o excedente) |
| **c7g/c8g.xlarge** | 4 / 8 GB | ~US$ 100–110/mês | Compute-optimized, sem créditos: o perfil certo para lab com carga sustentada |

### Recomendação: híbrido (resize sob demanda)

O resize é **reversível em ~3 minutos** e preserva tudo:

```text
1. stop na instância (console AWS ou aws-cli)
2. Actions → Instance settings → Change instance type → t4g.xlarge (ou c8g.xlarge)
3. start — o disco/EBS é o mesmo; o DuckDNS re-aponta o IP novo sozinho (cron)
4. (voltar para t4g.medium pelo mesmo caminho após o lab)
```

Mantendo a medium no dia a dia e subindo para xlarge **só nos dias do lab de
IA** (~40 h/mês), o custo extra fica em **~US$ 5–8/mês** — em vez de
quadruplicar a fatura permanente.

Atenção pós-resize: os symlinks do FlexRIC (`/usr/local/lib/flexric`)
sobrevivem ao resize (mesmo disco), mas **se perdem ao trocar de instância**
(nova AMI) — pendência da bible §10.

## 4. Decisões em aberto

- [ ] Aval do professor para o cronograma de resize (quais aulas usam 4 vCPU).
- [ ] Fonte de custeio do delta (~US$ 5–8/mês no cenário híbrido; ~US$ 75/mês
      se 4 vCPU permanente).
- [ ] Automatizar o resize (script `aws ec2 modify-instance-attribute` +
      stop/start) quando a rotina do lab de IA estiver definida.
