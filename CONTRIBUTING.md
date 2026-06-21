# Como colaborar — Core5G ARM64

Bem-vindo! Este guia explica, em linguagem simples, **como contribuir** com o
laboratório (mesmo que você nunca tenha colaborado num projeto no GitHub) e quais
são as **regras de ouro** para não quebrar o lab que roda ao vivo.

> Resumo de 10 segundos: edite **sempre na sua máquina**, valide, abra um
> **Pull Request** descrevendo *o que mudou e por quê*. Segredos nunca entram no
> git. Dúvidas → abra uma **Issue** ou fale comigo (contato no fim).

---

## 1. Os três jeitos de colaborar (do mais leve ao mais envolvido)

O GitHub oferece três "espaços". Você não precisa de permissão especial para os
dois primeiros — qualquer pessoa com conta GitHub pode usar:

| Espaço | Para quê | Como |
|---|---|---|
| **Issues** | Relatar um bug, propor uma ideia, tirar dúvida | Aba **Issues** do repositório → *New issue* → escolha o modelo |
| **Discussions** | Conversar, perguntar "como funciona X", trocar ideia sem ser um bug | Aba **Discussions** do repositório |
| **Pull Request (PR)** | Enviar uma mudança de código/documentação | *Fork* → branch → commit → abrir PR (passo a passo no §3) |

Não sabe qual usar? **Na dúvida, abra uma Issue** — a gente conversa por lá.

**Quer ser adicionado como colaborador** (acesso direto de escrita) **ou pegar as
imagens OAI arm64** (que não ficam no git)? Me mande um e-mail (§7).

---

## 2. Regras de ouro (o que NÃO fazer)

1. **Nunca edite arquivos direto no servidor por SSH.** Tudo é local → `deploy.sh`.
   O que você editar no servidor some no próximo deploy.
2. **Segredos nunca entram no git.** `.env` e as chaves (`ssl/*.pem`) estão no
   `.gitignore` — mantenha assim. Dado novo e sensível vai como variável no `.env`.
3. **Dados pessoais de aluno** (e-mail do roster, `panel_results/`) ficam **só no
   servidor**, nunca no repositório.
4. **Não rode o teste `p2-test-e2-kpm-traffic` em série.** Ele satura o box de
   2 vCPU (load ~30, derruba o SSH). Rode 1× destacado, nunca repetido.
5. **Projeto 1 e Projeto 2 são mutuamente exclusivos** — um liga, o outro desliga.

---

## 3. Fluxo de Pull Request (passo a passo)

```bash
# 1. Fork no GitHub (botão "Fork") e clone o SEU fork
git clone https://github.com/<voce>/Core5G_ARM64.git
cd Core5G_ARM64
cp .env.example .env        # preencha (veja README §1.2)

# 2. Crie uma branch a partir da main (nunca trabalhe direto na main)
git checkout -b feat/minha-melhoria

# 3. Edite, valide (§4) e faça commits pequenos e descritivos (§5)
git add <arquivos>
git commit -m "feat(painel): descrição curta do que mudou"

# 4. Envie e abra o PR pelo link que o git imprime
git push -u origin feat/minha-melhoria
```

No PR, descreva **o que mudou e por quê** (mesmo espírito do CHANGELOG) e diga
**como você validou**. O modelo de PR já te lembra desses pontos.

---

## 4. Como validar antes de abrir PR

Não precisa de servidor para a maior parte das mudanças do painel — dá para
validar localmente:

- **Backend (Python):** `python3 -c "import ast; ast.parse(open('server/panel/server.py').read())"`
  (checa sintaxe sem precisar do FastAPI instalado).
- **Frontend (JS embutido no HTML):** extraia os `<script>` e rode `new Function(...)`
  para checar sintaxe — veja exemplos em `server/panel/test/`.
- **Visual headless:** o projeto usa `puppeteer-core` + Chrome do sistema para
  tirar *screenshots* e checar estados sem subir o servidor (mock das rotas
  `/api/*`). Há exemplos de smoke test em `server/panel/test/`.
- **Lab de verdade:** `./deploy.sh status` (Projeto 1) e
  `./scripts/test_e2_sm.sh all` (Projeto 2) devem passar.

Se a sua mudança toca o servidor, descreva no PR o teste ao vivo que você fez.

---

## 5. Convenção de commit

Mensagens no formato `tipo(escopo): assunto`, em português, focadas em
**o que mudou e por quê** (igual ao CHANGELOG):

```
feat(painel): link "ver logs" no fim dos testes que geram logs
fix(p2): corrige ativar/desligar (scripts v1 → v2)
perf(painel): coletor único de telemetria (escala p/ turma)
docs: onboarding de colaboradores + CONTRIBUTING
```

Tipos comuns: `feat`, `fix`, `perf`, `docs`, `refactor`, `chore`.

---

## 6. Versionamento (SemVer)

A versão vive em [`server/panel/VERSION`](server/panel/VERSION) no formato
`MAJOR.MINOR.PATCH`:

- **MAJOR** — o painel muda de forma visível para o professor/apresentação.
- **MINOR** — um novo bloco de funcionalidade.
- **PATCH** — correção pontual.

A cada release:

1. Atualize `server/panel/VERSION`.
2. Registre no [`CHANGELOG.md`](CHANGELOG.md) (tabela + seção detalhada).
3. Faça o deploy e confira a versão ao vivo: `GET /api/version`.
4. (Mantenedor) crie a **tag git** anotada: `git tag -a vX.Y.Z -m "..."` e
   `git push origin vX.Y.Z`. As tags marcam cada release no histórico.

---

## 7. Contato

Dúvidas, acesso de colaborador, ou as imagens OAI arm64 do Drive do grupo:

- **Henrique Carmine** — [henriquecarmine@gmail.com](mailto:henriquecarmine@gmail.com) ·
  [@henriquecarmine](https://github.com/henriquecarmine)

Obrigado por contribuir! 🚀
