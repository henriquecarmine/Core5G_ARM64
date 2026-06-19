# Tarefa pendente — subir imagens OAI arm64 compiladas

## Contexto

As 6 imagens OAI 5G Core (amf, smf, nrf, udr, udm, ausf) já foram compiladas
para arm64 no Mac. O `.gitignore` que excluía `artifacts/oai-images/*.tar`
foi removido (commit `5188431f`) para permitir versionar esses arquivos no
repo. Falta apenas commitar e enviar os `.tar` de dentro do Mac, onde eles
existem.

## O que falta fazer (rodar no Mac, dentro da pasta do projeto)

```bash
git pull
git add -f artifacts/oai-images/*.tar
git status        # confirme que os 6 .tar aparecem como "Changes to be committed"
git commit -m "feat: imagens OAI arm64 compiladas (.tar)"
git push
```

Depois, validar do lado do servidor/outra máquina com `git pull` que os 6
arquivos chegaram corretamente.

## Prazo

Apresentação em 2026-06-20, 08:00–11:00 (Aula 06) — esse bloqueio é urgente.
