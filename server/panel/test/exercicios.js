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
 *   - associar: alvos e itens válidos, e nenhum item que aceite tudo;
 *   - TODO item do catálogo tem arquivo e pontos (desde a 0.87 não há mais
 *     exercício fora: a plataforma do professor saiu do ar);
 *   - a cadeira que usa exercícios de outra (`cruzada`) aponta para itens que
 *     existem, com os mesmos pontos;
 *   - o gabarito não se entrega sozinho: a certa não pode ser a alternativa mais
 *     longa em mais de um terço das perguntas, nem ficar concentrada numa posição;
 *   - nenhum arquivo do painel cita o domínio da plataforma antiga.
 *
 * Uso: node exercicios.js   (ou via npm run test:exercicios)
 */
const fs = require('fs');
const path = require('path');

const EST = path.resolve(__dirname, '..', 'static', 'lab', 'estudos');
const cat = JSON.parse(fs.readFileSync(path.join(EST, 'index.json'), 'utf8'));

// A média para passar é DADO do catálogo, não número espalhado pelas telas.
if (typeof cat.media !== 'number' || cat.media <= 0 || cat.media > 100)
  console.error("✗ o catálogo precisa de `media` (a nota de passagem, em %)") || process.exit(1);

const itens = {};
const cruzados = [];
for (const e of cat.estudos) {
  const A = e.atividades || {};
  for (const i of A.itens || []) {
    if (A.cruzada) cruzados.push({ e: e.id, i });   // usa os exercícios de outra cadeira
    else itens[i.h] = i;
  }
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

  let soma = 0, escolhas = 0, certaMaisLonga = 0;
  const posicoes = [0, 0, 0, 0];
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
      } else if (b.tipo === 'associar') {
        const alvos = q.alvos || [], it = q.itens || [];
        if (alvos.length < 2) erros.push(`${onde}: associar com ${alvos.length} alvo(s)`);
        if (new Set(alvos).size !== alvos.length) erros.push(`${onde}: alvos repetidos`);
        if (it.length < 3) erros.push(`${onde}: associar com ${it.length} item(ns)`);
        if (new Set(it.map((x) => x.t)).size !== it.length) erros.push(`${onde}: itens repetidos`);
        for (const x of it) {
          const ok = Array.isArray(x.ok) ? x.ok : [];
          if (!ok.length || !ok.every((a) => Number.isInteger(a) && a >= 0 && a < alvos.length))
            erros.push(`${onde}: o item "${String(x.t).slice(0, 30)}" não aponta para um alvo que existe`);
        }
        // Se todo item aceitasse todo alvo, qualquer resposta pontuaria.
        if (it.length && it.every((x) => (x.ok || []).length === alvos.length))
          erros.push(`${onde}: todo item aceita todo alvo — não há o que acertar`);
      } else if (b.tipo !== 'escolha') {
        erros.push(`${rel} · ${b.nome}: tipo de bloco '${b.tipo}' desconhecido (escolha, ordem ou associar)`);
      } else {
        const alt = q.alt || [];
        if (alt.length < 3) erros.push(`${onde}: só ${alt.length} alternativa(s)`);
        if (new Set(alt).size !== alt.length) erros.push(`${onde}: alternativas repetidas`);
        if (!(Number.isInteger(q.ok) && q.ok >= 0 && q.ok < alt.length))
          erros.push(`${onde}: 'ok'=${q.ok} não aponta para uma alternativa`);
        escolhas++;
        if (q.ok >= 0 && q.ok < 4) posicoes[q.ok]++;
        const tam = alt.map((a) => String(a).length), max = Math.max(...tam);
        if (tam[q.ok] === max && tam.filter((t) => t === max).length === 1) certaMaisLonga++;
      }
    }
  }
  if (soma !== ex.pts)
    erros.push(`${rel}: as perguntas somam ${soma} e o exercício vale ${ex.pts} — o aluno tiraria nota errada`);
  // Quem chuta "a mais comprida" ou "sempre a segunda" não pode passar sem estudar.
  // Os exercícios antigos tinham a certa como a mais longa em 9 de 9 perguntas.
  if (escolhas >= 6 && certaMaisLonga > Math.floor(escolhas / 3))
    erros.push(`${rel}: a certa é a alternativa mais longa em ${certaMaisLonga} de ${escolhas} perguntas — o tamanho entrega o gabarito`);
  if (escolhas >= 6 && Math.max(...posicoes) > 0.6 * escolhas)
    erros.push(`${rel}: ${Math.max(...posicoes)} de ${escolhas} respostas certas na mesma posição — a posição entrega o gabarito`);
}

// o contrário: item do catálogo sem arquivo daria 404 — não há mais "fora" para onde mandar
for (const [h, i] of Object.entries(itens)) {
  if (!arquivos.includes(slug(h) + '.json'))
    erros.push(`catálogo: '${h}' não tem ex/${slug(h)}.json — o link daria 404`);
  if (!(Number.isInteger(i.pts) && i.pts > 0))
    erros.push(`catálogo: '${h}' sem 'pts' — o total da nota tem de vir do catálogo`);
}
for (const { e, i } of cruzados) {
  const orig = itens[i.h];
  if (!orig) erros.push(`catálogo: ${e} usa '${i.h}', que não existe em nenhuma cadeira`);
  else if (orig.pts !== i.pts) erros.push(`catálogo: ${e} diz que '${i.h}' vale ${i.pts}, a origem diz ${orig.pts}`);
}

// A plataforma do professor saiu do ar: nenhum link para ela pode sobrar no painel.
const RAIZ = path.resolve(__dirname, '..');
const PROIBIDO = /cesar-activities-|activities-api-/;
(function varre(d) {
  for (const n of fs.readdirSync(d, { withFileTypes: true })) {
    if (['node_modules', 'test', '.git', '__pycache__'].includes(n.name)) continue;
    const c = path.join(d, n.name);
    if (n.isDirectory()) varre(c);
    else if (/\.(html|js|css|json|py|md)$/.test(n.name) && PROIBIDO.test(fs.readFileSync(c, 'utf8')))
      erros.push(`${path.relative(RAIZ, c)}: cita o domínio da plataforma antiga, que saiu do ar`);
  }
})(RAIZ);

if (erros.length) {
  console.error(`✗ EXERCÍCIOS REPROVADOS (${erros.length}):`);
  erros.slice(0, 20).forEach((e) => console.error('  -', e));
  process.exit(1);
}
const total = Object.keys(itens).length;
console.log(`✅ ${total} exercícios, todos no painel — ${totalQs} perguntas, pontos batendo com o `
  + `catálogo, toda pergunta com 'porque', nenhum gabarito entregue pelo tamanho ou pela posição`);
