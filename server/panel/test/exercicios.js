#!/usr/bin/env node
/*
 * Os exercícios NOSSOS — conferência do que o navegador não denuncia.
 *
 * A nota do aluno vem daqui: o servidor grava `acertos` contra o `pts` do
 * CATÁLOGO. Se a soma das perguntas de um exercício não der o `pts` do
 * catálogo, o aluno tira uma nota que não existe — e nada quebra na tela.
 * Este teste existe para isso.
 *
 * Confere, em cada arquivo de static/lab/estudos/ex/:
 *   - o `h` e o `pts` batem com o catálogo;
 *   - a soma dos pontos das perguntas dá o `pts`;
 *   - toda pergunta tem `porque` (um exercício que só diz "errou" não ensina);
 *   - escolha: `ok` aponta para uma alternativa que existe, e há ao menos 3;
 *   - ordem: ao menos 3 itens, sem repetidos;
 *   - todo item marcado `"nosso": true` no catálogo TEM arquivo, e vice-versa.
 *
 * Uso: node exercicios.js   (ou via npm run test:exercicios)
 */
const fs = require('fs');
const path = require('path');

const EST = path.resolve(__dirname, '..', 'static', 'lab', 'estudos');
const cat = JSON.parse(fs.readFileSync(path.join(EST, 'index.json'), 'utf8'));

const itens = {};
for (const e of cat.estudos) {
  const A = e.atividades || {};
  if (A.cruzada) continue;                 // aponta para os de outra cadeira
  for (const i of A.itens || []) itens[i.h] = i;
}
const slug = (h) => h.replace('#', '').replace('/', '-');
const erros = [];
let totalQs = 0;

const dir = path.join(EST, 'ex');
const arquivos = fs.existsSync(dir) ? fs.readdirSync(dir).filter((f) => f.endsWith('.json')) : [];

for (const f of arquivos) {
  const rel = `ex/${f}`;
  let ex;
  try { ex = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')); }
  catch (e) { erros.push(`${rel}: JSON inválido — ${e.message}`); continue; }

  const cat_i = itens[ex.h];
  if (!cat_i) { erros.push(`${rel}: hash '${ex.h}' não existe no catálogo`); continue; }
  if (slug(ex.h) + '.json' !== f) erros.push(`${rel}: o nome do arquivo não corresponde a '${ex.h}'`);
  if (cat_i.pts != null && ex.pts !== cat_i.pts)
    erros.push(`${rel}: pts=${ex.pts} mas o catálogo diz ${cat_i.pts}`);
  if (!cat_i.nosso) erros.push(`${rel}: existe, mas o catálogo não marcou "nosso": true — o aluno continua indo para fora`);

  let soma = 0;
  for (const b of ex.blocos || []) {
    for (const q of b.qs || []) {
      totalQs++;
      soma += q.pts || 0;
      const onde = `${rel} · ${b.nome} · "${String(q.q).slice(0, 40)}…"`;
      if (!q.porque || !String(q.porque).trim()) erros.push(`${onde}: sem 'porque' — não ensina nada a quem errou`);
      if (!q.pts) erros.push(`${onde}: sem pontos`);
      if (b.tipo === 'ordem') {
        const it = q.itens || [];
        if (it.length < 3) erros.push(`${onde}: ordenar com ${it.length} item(ns)`);
        if (new Set(it).size !== it.length) erros.push(`${onde}: itens repetidos na ordenação`);
      } else {
        const alt = q.alt || [];
        if (alt.length < 3) erros.push(`${onde}: só ${alt.length} alternativa(s)`);
        if (new Set(alt).size !== alt.length) erros.push(`${onde}: alternativas repetidas`);
        if (!(Number.isInteger(q.ok) && q.ok >= 0 && q.ok < alt.length))
          erros.push(`${onde}: 'ok'=${q.ok} não aponta para uma alternativa`);
      }
    }
  }
  if (soma !== ex.pts)
    erros.push(`${rel}: as perguntas somam ${soma} e o exercício vale ${ex.pts} — o aluno tiraria nota errada`);
}

// o contrário: catálogo promete o nosso e o arquivo não existe
for (const [h, i] of Object.entries(itens)) {
  if (i.nosso && !arquivos.includes(slug(h) + '.json'))
    erros.push(`catálogo: '${h}' está marcado "nosso" mas não há ex/${slug(h)}.json — o link daria 404`);
}

if (erros.length) {
  console.error(`✗ EXERCÍCIOS REPROVADOS (${erros.length}):`);
  erros.slice(0, 20).forEach((e) => console.error('  -', e));
  process.exit(1);
}
const total = Object.keys(itens).length;
console.log(`✅ ${arquivos.length} de ${total} exercícios já são nossos — ${totalQs} perguntas, `
  + `pontos batendo com o catálogo, toda pergunta com 'porque'`);
