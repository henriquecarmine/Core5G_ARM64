#!/usr/bin/env node
/*
 * Variável CSS usada e NUNCA definida.
 *
 * Em CSS isso falha em silêncio: `fill-opacity: var(--nao-existe)` deixa a
 * propriedade inválida e o navegador aplica o VALOR INICIAL — sem erro, sem
 * aviso, sem nada no console. Foi assim que as bandas da topologia viraram
 * blocos sólidos de cor quando `--band-fill` desapareceu junto com o bloco de
 * paleta antigo: as bandas passaram de véu (7% de opacidade) a preenchimento
 * cheio, e o nome do grupo, que é da mesma cor, sumiu dentro delas.
 *
 * `var(--x, reserva)` não é problema: tem plano B declarado.
 *
 * LIMITE CONHECIDO: a conferência é por ARQUIVO, não por escopo. Uma variável
 * definida só no bloco de um tema passa aqui e mesmo assim falta no outro. Para
 * pegar isso seria preciso resolver a cascata — o que o navegador faz, e é por
 * isso que o teste visual 0.c mede CONTRASTE de verdade em cada tema.
 *
 * Uso: node variaveis.js   (ou via npm run test:vars)
 */
const fs = require('fs');
const path = require('path');

const STATIC = path.resolve(__dirname, '..', 'static');
const lerTudo = (dir, achados = []) => {
  for (const nome of fs.readdirSync(dir)) {
    const p = path.join(dir, nome);
    if (fs.statSync(p).isDirectory()) lerTudo(p, achados);
    else if (/\.(html|css|js)$/.test(nome)) achados.push(p);
  }
  return achados;
};

const defs = (txt) => new Set([...txt.matchAll(/(--[a-z0-9-]+)\s*:/g)].map((m) => m[1]));
const tokens = defs(fs.readFileSync(path.join(STATIC, 'tokens.css'), 'utf8'));
const ponteLab = defs(fs.readFileSync(path.join(STATIC, 'lab', 'lab-ponte.css'), 'utf8'));

const erros = [];
for (const arq of lerTudo(STATIC).sort()) {
  if (arq.endsWith('tokens.css')) continue;
  const rel = path.relative(STATIC, arq);
  const t = fs.readFileSync(arq, 'utf8');

  const definidas = new Set([...defs(t), ...tokens, ...(rel.startsWith('lab/') ? ponteLab : [])]);
  const usadas = new Set([...t.matchAll(/var\(\s*(--[a-z0-9-]+)/g)].map((m) => m[1]));
  const comReserva = new Set([...t.matchAll(/var\(\s*(--[a-z0-9-]+)\s*,/g)].map((m) => m[1]));
  // nome montado em tempo de execução (`var(--c-${camada})`) não dá para conferir aqui
  const dinamicas = new Set([...t.matchAll(/var\(\s*(--[a-z0-9-]*)\$\{/g)].map((m) => m[1]));

  for (const v of [...usadas].sort()) {
    if (definidas.has(v) || comReserva.has(v) || dinamicas.has(v)) continue;
    erros.push(`${rel}: usa ${v} e ninguém define`);
  }
}

if (erros.length) {
  console.error(`✗ VARIÁVEIS ÓRFÃS (${erros.length}) — em CSS isso falha calado:`);
  erros.forEach((e) => console.error('  -', e));
  process.exit(1);
}
console.log('✅ nenhuma variável CSS usada sem definição (nem sem reserva declarada)');
