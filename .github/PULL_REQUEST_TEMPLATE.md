<!-- Obrigado por contribuir! Leia o CONTRIBUTING.md se for sua primeira vez. -->

## O que mudou e por quê
Descreva a mudança no mesmo espírito do CHANGELOG (o que muda para quem usa).

## Como validei
- [ ] Sintaxe backend: `python3 -c "import ast; ast.parse(open('server/panel/server.py').read())"`
- [ ] Sintaxe frontend (JS embutido) checada
- [ ] Smoke headless / screenshot (se mexeu na UI)
- [ ] Ao vivo: `./deploy.sh status` (P1) e/ou `./scripts/test_e2_sm.sh all` (P2)
- [ ] Outro: ...

## Checklist
- [ ] Editei **local** (nada direto no servidor por SSH)
- [ ] **Nenhum segredo** no diff (`.env`, `ssl/*.pem`, e-mails de aluno)
- [ ] Atualizei o `CHANGELOG.md` e o `server/panel/VERSION` (se for release)
- [ ] Não rodei `p2-test-e2-kpm-traffic` em série (satura o box de 2 vCPU)

## Issue relacionada
Closes #
