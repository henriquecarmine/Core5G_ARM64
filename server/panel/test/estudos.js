#!/usr/bin/env node
/*
 * Estudos por cadeira: o catálogo e as aulas batem entre si, nos 4 idiomas.
 *
 * Confere, para cada cadeira de static/lab/estudos/index*.json:
 *  - os 4 índices têm as mesmas cadeiras, com as mesmas aulas e os mesmos exercícios;
 *  - a bancada e todo comando citado têm rótulo no catálogo de cada idioma;
 *  - cada aula existe em pt, en, es e fr com o mesmo id, número, slide, cena e
 *    comandos, e com a mesma quantidade de objetivos, conceitos, fórmulas e quiz;
 *  - a cena de `onde` existe no minimapa (static/ops/mini-map.js);
 *  - todo quiz tem pergunta e resposta;
 *  - o número da aula não se repete dentro da cadeira.
 *
 * Existe porque a lista de aulas linkava pelo número do professor e a rota abre
 * pela posição: com a Aula 0 da cadeira 5, "Aula 1" abriria a Aula 0, e nada
 * disso aparecia enquanto todas as cadeiras começavam na Aula 1.
 */
const fs = require('fs');
const path = require('path');

const EST = path.resolve(__dirname, '..', 'static', 'lab', 'estudos');
const LANGS = ['', '.en', '.es', '.fr'];
const erros = [];

function ler(f) {
  try { return JSON.parse(fs.readFileSync(path.join(EST, f), 'utf8')); }
  catch (e) { erros.push(`${f}: ${e.code === 'ENOENT' ? 'não existe' : 'JSON inválido — ' + e.message}`); return null; }
}

// As cenas são as chaves do objeto MMAP do minimapa (uma por linha, 4 espaços).
function cenasDoMinimapa() {
  const src = fs.readFileSync(path.resolve(__dirname, '..', 'static', 'ops', 'mini-map.js'), 'utf8');
  const a = src.indexOf('{', src.indexOf('var MMAP = {'));
  let d = 0, fim = -1;
  for (let i = a; i < src.length; i++) {
    if (src[i] === '{') d++;
    else if (src[i] === '}' && --d === 0) { fim = i; break; }
  }
  return new Set([...src.slice(a, fim + 1).matchAll(/^\s{4}([a-z0-9]+)\s*:\s*\{/gm)].map((m) => m[1]));
}

const cenas = cenasDoMinimapa();
const idx = Object.fromEntries(LANGS.map((l) => [l, ler(`index${l}.json`)]));
if (!idx['']) { erros.forEach((m) => console.error('✗ ' + m)); process.exit(1); }

let nAulas = 0, nQuiz = 0;
for (const e of idx[''].estudos) {
  for (const l of LANGS) {
    const cat = idx[l];
    if (!cat) continue;
    const el = cat.estudos.find((x) => x.id === e.id);
    const nome = `index${l}.json · ${e.id}`;
    if (!el) { erros.push(`${nome}: cadeira ausente`); continue; }
    if (JSON.stringify(el.aulas || []) !== JSON.stringify(e.aulas || [])) erros.push(`${nome}: aulas diferentes do índice pt`);
    if (JSON.stringify(el.exercicios) !== JSON.stringify(e.exercicios)) erros.push(`${nome}: exercícios diferentes do índice pt`);
    if (!cat.bancadas[el.bancada]) erros.push(`${nome}: bancada '${el.bancada}' sem rótulo`);
    for (const c of el.exercicios || []) if (!cat.comandos[c]) erros.push(`${nome}: comando '${c}' sem rótulo`);
  }

  const numeros = new Set();
  for (const id of e.aulas || []) {
    const pt = ler(`${id}.json`);
    if (!pt) continue;
    nAulas++;
    nQuiz += (pt.quiz || []).length;
    if (pt.id !== id) erros.push(`${id}.json: id interno '${pt.id}'`);
    if (numeros.has(pt.n)) erros.push(`${id}.json: aula ${pt.n} repetida na cadeira ${e.id}`);
    numeros.add(pt.n);
    const cena = (pt.onde || {}).scene;
    if (!cenas.has(cena)) erros.push(`${id}.json: cena '${cena}' não existe no minimapa`);

    for (const l of LANGS) {
      const a = l ? ler(`${id}${l}.json`) : pt;
      if (!a) continue;
      const f = `${id}${l}.json`;
      for (const k of ['id', 'n', 'slide']) if (a[k] !== pt[k]) erros.push(`${f}: '${k}' difere do pt`);
      if ((a.onde || {}).scene !== cena) erros.push(`${f}: cena difere do pt`);
      if (JSON.stringify(a.exercicios) !== JSON.stringify(pt.exercicios)) erros.push(`${f}: exercícios diferem do pt`);
      for (const k of ['objetivos', 'conceitos', 'formulas', 'quiz']) {
        const n = Array.isArray(a[k]) ? a[k].length : null;
        if (n !== (pt[k] || []).length) erros.push(`${f}: '${k}' com ${n ?? 'nenhum'} item(ns), o pt tem ${(pt[k] || []).length}`);
      }
      if (!a.titulo || !a.resumo) erros.push(`${f}: sem título ou resumo`);
      for (const c of a.exercicios || []) if (idx[l] && !idx[l].comandos[c]) erros.push(`${f}: comando '${c}' sem rótulo em index${l}.json`);
      (a.quiz || []).forEach((q, i) => { if (!q.q || !q.a) erros.push(`${f}: quiz ${i + 1} sem pergunta ou resposta`); });
    }
  }
}

if (erros.length) {
  erros.forEach((m) => console.error('✗ ' + m));
  console.error(`\n❌ ESTUDOS: ${erros.length} problema(s)`);
  process.exit(1);
}
console.log(`✅ estudos OK — ${idx[''].estudos.length} cadeiras, ${nAulas} aulas × 4 idiomas, ${nQuiz} perguntas de quiz; cenas do minimapa, comandos e rótulos conferidos`);
