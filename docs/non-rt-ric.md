# Non-RT RIC — o que falta na pilha e como instalar

> **Status (25/07/2026):** o Non-RT RIC **não existe** nesta pilha. O que roda é
> só o Near-RT (FlexRIC sobre E2). Este documento registra a lacuna, corrige uma
> afirmação errada da bíblia, e traz um caminho de instalação **testado** — que
> não roda no servidor ARM.
>
> **Atualização (08/08/2026):** o bloqueio ARM64 do §3 foi contornado
> **construindo as imagens da fonte, nativamente** (os serviços são Java/Python —
> o amd64-only era só o CI do O-RAN SC). Par mínimo A1 (PMS 2.9.0 + A1
> Simulator 2.8.0) pronto em [`server/nonrt-ric/`](../server/nonrt-ric/),
> espelhando a Fase 1 do lab do Prof. Kunzler. Runbook completo:
> [instalacao-nonrt-arm64.md](instalacao-nonrt-arm64.md). Os §§4–5 abaixo
> (caminho x86 local e limites do FlexRIC sem A1) permanecem válidos.

## 1. Por que isto importa

As técnicas de ML do lab (`/lab`) — previsão de throughput por UE (UE-TP),
otimização de energia, traffic steering — são, pela própria arquitetura O-RAN,
**funções de Non-RT RIC**:

| Camada | Horizonte de controle | O que roda ali |
|---|---|---|
| **Non-RT RIC** (dentro do SMO) | **> 1 s** | rApps, treino de modelo, políticas A1 |
| **Near-RT RIC** | 10 ms – 1 s | xApps, E2SM-KPM / E2SM-RC |

Ou seja: **as aulas de regressão já fazem a função Non-RT** (treinar sobre KPIs
coletados e inferir em horizonte longo). O que falta não é a função — é o
invólucro: a plataforma, o empacotamento como rApp e o caminho A1 para descer a
política ao Near-RT RIC.

## 2. O que existe e o que não existe

**Existe (Near-RT, real e rodando):**

- FlexRIC como Near-RT RIC, falando **E2** com o gNB da OAI
- xApps: E2SM-KPM (métricas), E2SM-RC (controle), monitores
- Testes no painel (Projeto 2): `p2-e2lab`, `p2-test-e2-kpm`, `p2-test-e2-rc`,
  `p2-test-e2-sm`, `p2-kpm-analytics`, `p2-kpm-real`

**Não existe:**

- Nenhuma plataforma Non-RT RIC / SMO
- Nenhum caminho A1
- Nenhum rApp (o `xapp_ue_tp_moni.c` é um **xApp**, no lado Near-RT)

### 2.1 Correção: o FlexRIC **não** fala A1

A bíblia afirmava, na tabela "Onde cada container Docker está no modelo O-RAN",
que o `flexric` expõe `E2, A1`. **Está errado** — corrigido em 25/07/2026.

Evidência, na árvore em `server/oai-cn-gnb-e2/openairinterface5g/openair2/E2AP/flexric/`:

- `src/` contém apenas `agent`, `lib`, `ric`, `sm`, `util`, `xApp` — sem A1, sem rApp
- `examples/` só tem `xApp/` — não existe `examples/rApp/`
- Busca ampla por `A1` no código retorna **só falso-positivo**: strings hex do
  `sqlite3.c`, arquivos ASN.1 do RRC e XMLs de encoder do E2AP

Consequência prática: mesmo empacotando a regressão como rApp, **não há por onde
entregá-la** ao Near-RT RIC desta pilha.

### 2.2 O "UE-TP-rApp" é um xApp com EWMA

O arquivo é
`openairinterface5g/openair2/E2AP/flexric/examples/xApp/c/monitor/xapp_ue_tp_moni.c`.
Ele está na camada Near-RT, amostra a **1 s**, e prevê com **EWMA (alpha = 0,3)** —
não com modelo treinado. O próprio comentário do código reconhece: *"um rApp real
ajustaria alpha por UE/cenário"*.

O nome "UE-TP-rApp" refere-se ao **caso de uso** do artigo (Ngo et al. §6.1), não a
um componente Non-RT implantado. Vale dizer isso em aula antes que um aluno pergunte.

## 3. O bloqueio: nenhuma imagem do Non-RT RIC tem build ARM64

Este é o achado que decide onde o Non-RT RIC pode rodar. Medido com
`docker manifest inspect --verbose` a partir do próprio servidor `aarch64`
(25/07/2026), sobre as imagens do **Release K** do O-RAN SC:

| Imagem (`nexus3.o-ran-sc.org:10002/o-ran-sc/…`) | Tag | Arquitetura |
|---|---|---|
| `nonrtric-plt-a1policymanagementservice` | 2.9.0 | `amd64` |
| `nonrtric-plt-informationcoordinatorservice` | 1.6.1 | `amd64` |
| `nonrtric-controlpanel` | 2.5.0 | `amd64` |
| `nonrtric-gateway` | 1.2.0 | `amd64` |
| `a1-simulator` | 2.8.0 | `amd64` |
| `nonrtric-plt-rappmanager` | 0.2.0 | `amd64` |
| `nonrtric-plt-rappcatalogue` | 1.2.0 | `amd64` |

**Sete de sete em `amd64` puro.** Não são manifest lists multi-arch — são
manifestos v2 de arquitetura única. É o mesmo padrão já documentado para o
`gradiant/open5gs` 2.7.3+.

O servidor (t4g.xlarge, Graviton) **não tem handler binfmt/QEMU registrado**, então
nem emulação está disponível sem instalar `qemu-user-static` e configurar binfmt —
o que, para serviços Spring Boot/JVM, sairia caro em CPU num box que já é
compartilhado com o lab E2.

## 4. Caminho validado: rodar local, em x86_64, com podman

A máquina de trabalho (Fedora, `x86_64`, podman 5.8.4) roda essas imagens
**nativamente**. Testado ponta a ponta em 25/07/2026 com o A1 Policy Management
Service 2.9.0.

### 4.1 Os dois obstáculos (e as soluções)

**Obstáculo 1 — UID fora da faixa de subuid.** A imagem usa UID `120957` para
`/home/nonrtric`; a faixa rootless padrão do usuário é `524288:65536`. O pull falha com:

```
potentially insufficient UIDs or GIDs available in user namespace
(requested 120957:120957 for /home/nonrtric)
```

Solução sem root — um `storage.conf` com `ignore_chown_errors`:

```toml
[storage]
driver = "overlay"
[storage.options.overlay]
ignore_chown_errors = "true"
```

E aponte `CONTAINERS_STORAGE_CONF` para ele (assim não se altera a configuração
permanente da máquina).

**Obstáculo 2 — `crun: setgroups: Invalid argument` no `run`.** Mesma raiz: o
usuário `nonrtric` da imagem não é mapeável. Solução: `--user 0` (dentro do
container é root; no host, com podman rootless, continua sendo o seu usuário).

### 4.2 Receita mínima, testada

```bash
export CONTAINERS_STORAGE_CONF=/caminho/para/storage.conf

cat > application_configuration.json <<'EOF'
{
  "config": {
    "ric": [
      { "name": "ric1", "baseUrl": "http://a1-sim:8085/", "managedElementIds": ["gnb_core5g_1"] }
    ]
  }
}
EOF

podman pull nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-plt-a1policymanagementservice:2.9.0

podman run -d --name a1pms --user 0 -p 18081:8081 \
  -v "$PWD/application_configuration.json:/opt/app/policy-agent/data/application_configuration.json:Z,ro" \
  nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-plt-a1policymanagementservice:2.9.0
```

**Resultado medido:** Spring Boot 3.4.0 sobre Java 17.0.2, `Started Application in
10.128 seconds`. Endpoints respondendo:

| Endpoint | Código | Corpo |
|---|---|---|
| `/actuator/health` | 200 | `{"status":"UP"}` |
| `/a1-policy/v2/status` | 200 | `{"status":"success"}` |
| `/a1-policy/v2/rics` | 200 | `{"rics":[{"ric_id":"ric1","managed_element_ids":["gnb_core5g_1"],"state":"UNAVAILABLE",…}]}` |

O `state: UNAVAILABLE` é **esperado e correto**: não há nada atrás do A1. Para o
serviço sair de `UNAVAILABLE` é preciso subir o `a1-simulator:2.8.0` no
`baseUrl` configurado.

### 4.3 Stack completo

O projeto oficial traz docker-compose pronto:

```bash
git clone "https://gerrit.o-ran-sc.org/r/nonrtric"
cd nonrtric/docker-compose/
```

Há variantes com e sem o controlador A1 do SDNC. O `README.md` daquela pasta
descreve cada uma. Todos os containers se ligam por uma rede própria:

```bash
docker network create nonrtric-docker-net
```

## 5. O que isto **não** resolve

Instalar o Non-RT RIC dá a plataforma, mas **não integra com o RAN deste
laboratório**, porque o FlexRIC não tem A1 (§2.1). O que se obtém é:

- Non-RT RIC completo, conversando com o **A1 Simulator** — demonstra a camada,
  as políticas A1 e o ciclo do rApp, de forma autocontida
- **Não** demonstra Non-RT → A1 → Near-RT → E2 → gNB real

Fechar essa ponta exigiria um Near-RT RIC com terminação A1 (o RIC da própria
O-RAN SC, por exemplo), substituindo ou acompanhando o FlexRIC. É componente
novo, não ajuste.

## 6. Alternativa intermediária: o rApp como sidecar Python

Sem plataforma Non-RT e sem A1, o passo de menor custo com sentido arquitetural
(item 4 do [plano do lab](plano-lab-ric-ia.md)) é um **sidecar Python** que:

1. lê o CSV do `kpm_analytics.sh` (KPM real do lab E2)
2. roda a regressão treinada em horizonte > 1 s
3. emite a previsão como política

Isso não cria um Non-RT RIC, mas coloca a regressão **na camada arquitetural
certa**, em vez do EWMA que hoje roda dentro de um xApp. Recomendado como sidecar,
não como porta do sklearn para C.

## 7. Versões registradas

| Item | Versão | Observação |
|---|---|---|
| O-RAN SC Non-RT RIC | Release K | todas as imagens `amd64` |
| A1 Policy Management Service | 2.9.0 | Spring Boot 3.4.0, Java 17.0.2 |
| podman (máquina local) | 5.8.4 | Fedora, `x86_64` |
| Docker (servidor) | 29.6.0 | `aarch64`, sem binfmt |
| Faixa subuid local | `524288:65536` | insuficiente p/ o UID 120957 da imagem |

## Fontes

- [Deploy NONRTRIC with Docker — O-RAN SC](https://lf-o-ran-sc.atlassian.net/wiki/spaces/RICNR/pages/15073738/Deploy+NONRTRIC+with+Docker)
- [Release K — Run in Docker](https://lf-o-ran-sc.atlassian.net/wiki/spaces/RICNR/pages/86802677/Release+K+-+Run+in+Docker)
- [Release K — Docker Images](https://lf-o-ran-sc.atlassian.net/wiki/spaces/RICNR/pages/86802720)
- [nonrtric — repositório Gerrit](https://gerrit.o-ran-sc.org/r/nonrtric) · [espelho no GitHub](https://github.com/o-ran-sc/nonrtric)
- [Installation Guide — nonrtric docs](https://docs.o-ran-sc.org/projects/o-ran-sc-nonrtric/en/dawn/installation-guide.html)
