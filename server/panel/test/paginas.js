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
 * 3) Quem tem botão de tema LEMBRA o tema. As 12 páginas do lab tinham o
 *    botão, mas nenhuma gravava a escolha: o professor punha o tema claro no
 *    painel para o projetor, clicava numa aula e voltava tudo escuro. Como o
 *    botão funcionava, ninguém via defeito nenhum — só um incômodo repetido.
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

  // 3) o cache-buster é UM só, resolvido ao servir (`?v=%VER%`).
  //    Havia nove números escritos à mão espalhados, e eles se separaram: o
  //    painel pedia o tokens.css da 0.75.0 quando o projeto já ia na 0.80.3.
  //    Como /static é cacheado pelo navegador, a tela do professor não mudava
  //    depois do deploy — e não havia como perceber olhando.
  const fixos = [...texto.matchAll(/\?v=([0-9][0-9.]*)/g)].map((m) => m[1]);
  if (fixos.length) erros.push(`${rel}: ?v= com número escrito à mão (${[...new Set(fixos)].join(', ')}) — use ?v=%VER%`);

  //    ...e TODO asset de /static precisa carregar o cache-buster. Faltando ele,
  //    o arquivo é servido pelo StaticFiles com cache normal e fica velho no
  //    navegador depois do deploy — a mesma quebra da 0.80.4, agora sem número
  //    errado para denunciar, só ausência. Eram 28 referências assim no lab.
  const semV = [...texto.matchAll(/(?:src|href)="(\/static\/[^"]+\.(?:js|css))"/g)].map((m) => m[1]);
  if (semV.length) erros.push(`${rel}: ${semV.length} asset(s) de /static sem ?v=%VER% (${semV.slice(0, 3).join(', ')})`);

  // 5) botão de tema ⇒ tema lembrado. Ler ANTES de pintar (script no <head>)
  //    e gravar no clique, na mesma chave do painel: `c5g-theme`.
  const temBotao = /id="theme-?[bB]tn"|id="theme-btn"/.test(texto);
  if (temBotao) {
    if (!/localStorage\.getItem\("c5g-theme"\)|localStorage\.getItem\('c5g-theme'\)/.test(texto))
      erros.push(`${rel}: tem botão de tema mas não LÊ c5g-theme (o tema não atravessa a navegação)`);
    if (!/localStorage\.setItem\(["']c5g-theme["']/.test(texto))
      erros.push(`${rel}: tem botão de tema mas não GRAVA c5g-theme (a escolha morre ao sair da página)`);
  }

  // 4) quem pinta, carrega a identidade
  const pinta = /<style[\s>]/.test(texto);
  const temIdentidade = /href="\/static\/tokens\.css/.test(texto);
  if (pinta && !temIdentidade) erros.push(`${rel}: tem <style> mas não carrega /static/tokens.css`);
}

if (erros.length) {
  console.error(`✗ PÁGINAS REPROVADAS (${erros.length}):`);
  erros.forEach((e) => console.error('  -', e));
  process.exit(1);
}
console.log(`✅ ${paginas.length} páginas OK — <meta charset> no primeiro kilobyte, ícone da aba, identidade carregada em todas que pintam e tema lembrado em todas que têm o botão`);
