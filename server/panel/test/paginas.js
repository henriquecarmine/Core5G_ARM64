#!/usr/bin/env node
/*
 * Conferência estática de TODA página HTML servida pelo painel.
 *
 * 1) <meta charset> dentro do PRIMEIRO KILOBYTE. O navegador só olha os
 *    primeiros 1024 bytes; fora dali ele adivinha, e em português adivinhar
 *    errado vira "RegressÃ£o". Isto já quebrou duas vezes:
 *      - três páginas do lab não tinham a etiqueta nenhuma;
 *      - sete tinham a PALAVRA "charset" enterrada num script, e um
 *        `grep -L charset` deu falso-negativo nelas.
 *    Por isso aqui se mede a POSIÇÃO da etiqueta, não a presença da palavra.
 *
 * 2) Toda página com cor própria carrega a folha de identidade — senão volta
 *    a existir paleta paralela.
 *
 * Uso: node paginas.js   (ou via npm run test:paginas)
 */
const fs = require('fs');
const path = require('path');

const STATIC = path.resolve(__dirname, '..', 'static');
const LIMITE = 1024;

function html(dir, achados = []) {
  for (const nome of fs.readdirSync(dir)) {
    const p = path.join(dir, nome);
    const st = fs.statSync(p);
    if (st.isDirectory()) html(p, achados);
    else if (nome.endsWith('.html')) achados.push(p);
  }
  return achados;
}

const erros = [];
const paginas = html(STATIC).sort();

for (const arq of paginas) {
  const rel = path.relative(STATIC, arq);
  const buf = fs.readFileSync(arq);
  const texto = buf.toString('utf8');

  // 1) charset no primeiro kilobyte
  const m = /<meta[^>]+charset/i.exec(texto);
  if (!m) {
    erros.push(`${rel}: sem <meta charset>`);
  } else {
    const bytes = Buffer.byteLength(texto.slice(0, m.index), 'utf8');
    if (bytes > LIMITE) erros.push(`${rel}: <meta charset> no byte ${bytes} (o navegador só lê os primeiros ${LIMITE})`);
  }

  // 2) ícone da aba: sem ele o navegador pede /favicon.ico e leva 404 em toda
  //    visita, e a aba fica com o ícone genérico do navegador.
  if (!/rel="icon"/.test(texto)) erros.push(`${rel}: sem <link rel="icon">`);

  // 3) quem pinta, carrega a identidade
  const pinta = /<style[\s>]/.test(texto);
  const temIdentidade = /href="\/static\/tokens\.css/.test(texto);
  if (pinta && !temIdentidade) erros.push(`${rel}: tem <style> mas não carrega /static/tokens.css`);
}

if (erros.length) {
  console.error(`✗ PÁGINAS REPROVADAS (${erros.length}):`);
  erros.forEach((e) => console.error('  -', e));
  process.exit(1);
}
console.log(`✅ ${paginas.length} páginas OK — <meta charset> no primeiro kilobyte, ícone da aba e identidade carregada em todas que pintam`);
