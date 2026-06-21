# Guia do sistema de relatórios didáticos

> Para colaboradores que vão **entender, manter ou criar** os testes/relatórios
> do painel. Aqui está, minuciosamente, *como* um relatório vira aquela saída
> colorida com "Por quê" e "Resumo" que o professor mostra em aula — e como
> adicionar o seu sem quebrar nada.

Pré-requisitos: leia antes o [`CONTRIBUTING.md`](../CONTRIBUTING.md) (regras de
ouro, fluxo de PR) e o [README §1](../README.md) (subir o lab). Este documento é
o aprofundamento técnico do que o CONTRIBUTING §4 cita de passagem.

---

## 1. Os dois tipos de relatório

O painel tem **duas vias** de relatório, com mecânicas diferentes:

| Via | Onde aparece | Como o script fala com a UI | Exemplos |
|---|---|---|---|
| **Testes do menu** | console principal (`#output`) | stdout cru → ANSI vira cor no navegador | todos os `test_*.sh` (P1 e P2) |
| **Demonstração E2E** | modal dedicado (passos + console) | linhas estruturadas `STEP\|`/`DONE\|`/`PHASE\|` | `demo_e2e.sh` |

Ambas terminam com um **bloco "Resumo"** (o que fez + veredito). A diferença é só
o canal e a riqueza visual: a Demo E2E tem um rail de passos à direita; os testes
do menu são lineares no console.

---

## 2. Via A — testes do menu (`lib/testlog.sh`)

### 2.1 Como o fluxo funciona

1. Um botão no `index.html` tem `data-cmd="<chave>"`
   (ex.: `data-cmd="test-ng-setup"`). Ao clicar, o JS chama
   `fetch('/api/run/<chave>')` ([index.html:1335](../server/panel/static/index.html#L1335)).
2. O backend resolve a chave no dicionário **`COMMANDS`**
   ([server.py:331](../server/panel/server.py#L331)) → roda o `.sh` correspondente
   e faz *stream* da stdout linha a linha para o console (via `tee_to_live`, que
   também espelha pros Alunos e persiste em "Resultados salvos").
3. O script imprime cor com **códigos ANSI**; o painel **não é um terminal**, mas
   converte ANSI → cor no navegador (lib de colorimetria do front).

> O painel **não interpreta** a saída dos testes do menu — ele só renderiza. Toda
> a didática (seções, ✓/✗, Resumo) vem do **próprio script**, via a lib.

### 2.2 A lib `lib/testlog.sh` (a API)

Fonte: [`server/scripts/lib/testlog.sh`](../server/scripts/lib/testlog.sh).
Sempre comece o script com:

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"
# shellcheck source=lib/testlog.sh
source "$SCRIPT_DIR/lib/testlog.sh"
```

Funções disponíveis (todas já emitem ANSI):

| Função | Uso | Render |
|---|---|---|
| `section "Título"` | abre um bloco | `── Título ──` ciano/negrito |
| `ok "msg"` | checagem passou | `✓ msg` verde |
| `warn "msg"` | ressalva não-crítica | `! msg` amarelo |
| `err "msg"` | falha | `✗ msg` vermelho |
| `info "msg"` | nota neutra | `• msg` azul |
| `step "msg"` | passo/explicação | `→ msg` ciano |
| `kv "Rótulo" "valor"` | par chave-valor alinhado | `  Rótulo   valor` |
| `summary "o que fez" "veredito" ok\|warn\|err` | **bloco final** | bloco "Resumo" colorido |

### 2.3 O padrão didático (siga à risca)

1. **Uma `section` por etapa lógica**, numerada quando houver ordem
   (`1/6 · ...`).
2. **Uma linha `step "Por quê: ..."`** logo após a section, explicando *o que
   aquela etapa prova* — é o que transforma um teste em material de aula.
3. **Uma checagem colorida por verificação** (`ok`/`warn`/`err`), com o dado real
   embutido (RTT, IP, contagem) — não só "passou".
4. **Guardas de pré-condição** (container no ar? UE com IP?) emitem `err` +
   `summary ... err` e **saem com `exit 0`** (não `exit 1` — veja §5).
5. **Veredito honesto**: conte falhas/ressalvas e escolha o status do `summary`
   (`err` se quebrou algo crítico, `warn` se há ressalva, `ok` se tudo passou).
   **Nunca** termine sempre em `ok`.

Esqueleto mínimo:

```bash
fails=0; warns=0
section "Meu teste — o que ele valida"

# pré-condição
if ! docker inspect -f '{{.State.Status}}' ueransim 2>/dev/null | grep -q running; then
    err "RAN não está no ar — suba o Projeto 1."
    summary "tentou validar X" "abortado: RAN fora do ar" err
    exit 0
fi
ok "RAN em execução."

section "1/2 · Primeira verificação"
step "Por quê: prova que ..."
if <condição>; then ok "passou (dado=$x)."; else warn "ressalva."; warns=$((warns+1)); fi

# veredito honesto
if   [ "$fails" -gt 0 ]; then summary "fez ..." "FALHOU: ..." err
elif [ "$warns" -gt 0 ]; then summary "fez ..." "ok com ressalvas: ..." warn
else                         summary "fez ..." "tudo passou (✓)" ok
fi
```

---

## 3. Via B — Demonstração E2E (protocolo do modal)

Fonte: [`server/scripts/demo_e2e.sh`](../server/scripts/demo_e2e.sh) ·
render no [index.html](../server/panel/static/index.html) (função `runOperation`).

O modal tem **dois painéis**: o rail de passos (direita) e o console de logs
(esquerda). O script controla os dois com linhas estruturadas:

| Linha emitida | Efeito na UI |
|---|---|
| `PHASE\|<texto>` | atualiza o título do *spinner* (passo em andamento) |
| `STEP\|<ok\|fail\|info>\|<título>\|<detalhe>` | adiciona um passo colorido no rail |
| `DONE\|<ok\|fail>` | fecha com o veredito (verde/vermelho) |
| `$ <comando>` | linha **azul** no console (eco do comando) |
| qualquer outra linha | linha normal no console (saída real) |

O padrão didático da Demo E2E (que os outros relatórios devem espelhar no
espírito):

- antes de cada passo, **ecoe o comando real** com `$ docker exec ...` e **a
  saída real** logo abaixo (indentada). O aluno vê *exatamente* o que rodou;
- inclua uma linha **"Por quê:"** explicando o que aquele passo comprova;
- emita o `STEP|ok|...` correspondente para o rail.

Helpers já prontos no `demo_e2e.sh` (`say`, `cmd`, `out`, `rule`, `emit`,
`phase`) — copie o padrão de lá ao criar uma nova demonstração.

---

## 4. Como adicionar um relatório novo (passo a passo)

### 4.1 Teste do menu (o caso comum)

1. **Crie** `server/scripts/test_minha_coisa.sh` seguindo o esqueleto do §2.3
   (`source` da lib + sections + `summary` honesto). `chmod +x`.
2. **Registre** a chave no dicionário `COMMANDS`
   ([server.py:331](../server/panel/server.py#L331)):
   ```python
   "test-minha-coisa": {"cmd": ["./scripts/test_minha_coisa.sh"], "cwd": SERVER_DIR},
   ```
   (Para P2, `cwd` aponta para `SERVER_DIR / "oai-cn-gnb-e2"`.)
3. **Adicione o botão** no `index.html`, dentro do bloco do projeto certo
   (`data-tools="p1"` ou `"p2"`):
   ```html
   <button class="test-p1" data-cmd="test-minha-coisa">Minha coisa</button>
   ```
   (ou uma `<option>` no `<select id="diag-test-select">` para P1.)
4. **Valide** (`bash -n`) e **teste ao vivo** (§6) — sempre.

### 4.2 Nova demonstração (modal)

1. Crie o `.sh` emitindo `PHASE|`/`STEP|`/`DONE|` + `$ comando`/saída (§3).
2. Adicione um endpoint `@app.post("/api/minha-demo")` que faz
   `tee_to_live(stream_command([...]), "Título", by)` — espelhe o `demo_e2e`
   ([server.py:1103](../server/panel/server.py#L1103)).
3. No front, ligue um botão com `openOperation({ endpoint: '/api/minha-demo', ... })`.

---

## 5. Gotchas (erros reais que já mordemos)

Estes não são teóricos — cada um quebrou um relatório de verdade e foi corrigido.
Veja o [CHANGELOG](../CHANGELOG.md) 0.25.0–0.25.2.

1. **Nome de container ≠ nome de serviço compose.** No Open5GS, o *serviço*
   compose é `amf`, mas o *container* se chama `open5gs-amf-containerized`.
   - `docker compose logs amf` → usa o **serviço** ✅
   - `docker inspect <x>` / `docker exec <x>` / `docker logs <x>` → exigem o
     **nome do container** ✅
   Misturar dá **falso-negativo** ("AMF não está rodando" com o AMF no ar). Foi
   exatamente o bug do `test_ng_setup`/`test_registration`. Os nomes reais estão
   na lista `SERVICES` em [server.py](../server/panel/server.py#L1117).

2. **`exit 1` em pré-condição = relatório feio.** Sair não-zero faz o painel
   mostrar falha "dura". Prefira `err` + `summary ... err` + **`exit 0`**: o
   relatório renderiza limpo, explicando *por que* não rodou.

3. **Veredito sempre "ok" engana.** Conte `fails`/`warns` e reflita no `summary`.
   Um teste que diz "ok" com 3 checagens vermelhas é pior que não ter teste.

4. **`bash -n` não pega bug semântico.** Ex.: `wget http://ifconfig.me` devolve
   **HTML**, e o relatório exibia `IP público <!DOCTYPE html>`. Só **rodar ao
   vivo** (§6) pega isso. Regra: relatório novo ou alterado **roda ao vivo** antes
   do PR.

5. **`p2-test-e2-kpm-traffic` nunca em série.** Satura o box de 2 vCPU (load ~30,
   derruba SSH). Rode 1× destacado. (Regra de ouro do CONTRIBUTING §2.)

6. **Saída de comando pode colidir com o protocolo.** Numa Demo E2E, evite que a
   saída crua comece com `STEP|`/`DONE|`/`PHASE|`/`$ ` sem querer (ping/iperf/`ip`
   não fazem isso, mas fique atento ao parsear logs de terceiros).

---

## 6. Como verificar ao vivo

O painel renderiza ANSI, mas pra checar no terminal é útil **remover** os códigos.
Padrão usado nesta sessão (P1 no ar):

```bash
# do seu .env: AWS_SERVER_USER, AWS_SERVER_HOST, AWS_SSH_KEY_PATH
ssh -i "$AWS_SSH_KEY_PATH" "$AWS_SERVER_USER@$AWS_SERVER_HOST" \
  "cd ~/server && bash ./scripts/test_ue_connection.sh" \
  | sed -E 's/\x1b\[[0-9;]*m//g'      # tira o ANSI pra ler no terminal
```

- **Sincronizar só um script** (sem o `deploy.sh sync`, que exige `server/.env`):
  ```bash
  rsync -az -e "ssh -i $AWS_SSH_KEY_PATH" \
    server/scripts/test_minha_coisa.sh \
    "$AWS_SERVER_USER@$AWS_SERVER_HOST:~/server/scripts/"
  ```
- **Subir/baixar o lab** sem o sync que falha no `.env`:
  ```bash
  ssh ... "cd ~/server && ./scripts/up.sh && ./scripts/up_ran.sh"   # P1
  ssh ... "cd ~/server && ./scripts/switch_project.sh p2"           # → P2
  ssh ... "cd ~/server && ./scripts/switch_project.sh off"          # desliga tudo
  ```
- **Lembre de desligar** depois (`switch_project.sh off`) — o box custa por hora.

---

## 7. Inventário dos relatórios atuais

### Projeto 1 (Open5GS + UERANSIM) — menu "Testes · Projeto 1"

| Chave (`data-cmd`) | Script | O que prova |
|---|---|---|
| `status` | `healthcheck.sh` | saúde geral do stack |
| `test-system-status` | `test-system-status.sh` | containers, versão UERANSIM, IP do UE, célula servidora, erros conhecidos |
| `test-ng-setup` | `test_ng_setup.sh` | N2: NGSetupResponse no gNB + NGAP no AMF |
| `test-registration` | `test_registration.sh` | registro N1/NAS: Registration accept, estado REGISTERED, sessão PDU |
| `test-config-coherence` | `test_config_coherence.sh` | PLMN/slice/APN coerentes entre `gnb.yaml` e `ue.yaml` |
| `test-ue-connection` | `test_ue_connection.sh` | conectividade fim-a-fim (ping/DNS/HTTP/rota/UPFs/N2/PFCP/NAS) |
| `test-upf-failover` | `test_upf_failover.sh` | derruba um UPF e mede se a sessão sobrevive (failover) |
| *(Demo E2E)* | `demo_e2e.sh` | UE → IP → internet → IP público → throughput pelo túnel 5G |

### Projeto 2 (OAI + FlexRIC) — menu "Testes · Projeto 2"

| Chave (`data-cmd`) | Script (em `oai-cn-gnb-e2/`) | O que prova |
|---|---|---|
| `p2-test-e2-sm` | `test_e2_sm.sh all` | cadeia O-RAN: gNB → E2 → RIC → xApps (KPM/RC/MAC/RLC/PDCP/GTP) |
| `p2-test-e2-kpm` | `test_e2_kpm.sh` | assinatura E2SM-KPM (métricas de desempenho do RAN) |
| `p2-test-e2-kpm-traffic` | `KPM_TRAFFIC=1 test_e2_kpm.sh` | idem com tráfego (⚠ **nunca em série** — satura o box) |
| `p2-test-e2-rc` | `test_e2_rc_attach.sh` | E2SM-RC: captura eventos de controle/RRC (attach) via E2 |

> `test_distance.sh` e `test_interference.sh` são **utilitários de CLI legados**,
> **não acionáveis pelo painel** — o painel usa `test_channel.sh` para canal de
> rádio. Não são relatórios.

---

Dúvidas sobre este sistema? Abra uma **Discussion** ou fale com o mantenedor
(CONTRIBUTING §7).
