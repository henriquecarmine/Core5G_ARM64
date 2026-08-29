#!/usr/bin/env node
/*
 * Paridade dos dicionários i18n do painel (static/i18n.js), dos Estudos por
 * cadeira (static/lab/lab-i18n.js) e do glossário 5G/O-RAN
 * (static/ops/glossario.js).
 *
 * Garante que TODA chave existe nos 4 idiomas (pt/en/es/fr) — o fallback
 * mascara chave faltante na tela, então só o teste pega. Também falha se um
 * idioma tiver chave órfã (que não existe no pt canônico) ou valor vazio.
 *
 * Uso: node i18n-parity.js   (ou via npm run test:i18n)
 */
const fs = require('fs');
const path = require('path');

const LANGS = ['pt', 'en', 'es', 'fr'];
const errors = [];

// O painel guarda o dicionário em I18N_DICTS; o lab-i18n.js roda dentro de uma
// IIFE e o expõe em window.LABI18N.dicts — daí o `window` de mentira.
const carrega = (rel, extrai) => {
  const src = fs.readFileSync(path.resolve(__dirname, '..', ...rel), 'utf8');
  return extrai(src);
};
const ALVOS = [
  { nome: 'static/i18n.js',
    dicts: carrega(['static', 'i18n.js'], src => new Function(`${src}; return I18N_DICTS;`)()) },
  { nome: 'static/lab/lab-i18n.js',
    dicts: carrega(['static', 'lab', 'lab-i18n.js'], src => {
      const win = {};
      const doc = { cookie: '', readyState: 'complete',
        getElementById: () => null, querySelectorAll: () => [], addEventListener: () => {} };
      new Function('window', 'document', 'navigator', 'localStorage',
        `${src}; return window.LABI18N;`)(
        win, doc, { language: 'pt' }, { getItem: () => null, setItem: () => {} });
      return win.LABI18N.dicts;
    }) },
  { nome: 'static/ops/glossario.js',
    dicts: carrega(['static', 'ops', 'glossario.js'], src => {
      const win = {};
      new Function('window', `${src}; return window.GLOSSARIO;`)(win);
      return win.GLOSSARIO.dicts;
    }) },
];

// O glossário tem uma segunda amarração, própria dele: cada TERMO precisa das
// duas explicações (`.o` = o que é · `.p` = para que serve) e cada explicação
// precisa de um termo. Sem esta conferência, um termo entra na lista, aparece
// sublinhado na legenda, e o balão abre VAZIO — falha calada, do mesmo tipo da
// variável CSS órfã.
const glossario = (() => {
  const src = fs.readFileSync(path.resolve(__dirname, '..', 'static', 'ops', 'glossario.js'), 'utf8');
  const win = {};
  new Function('window', `${src}; return window.GLOSSARIO;`)(win);
  return win.GLOSSARIO;
})();
{
  const termos = Object.keys(glossario.termos);
  const esperadas = new Set(['ui.o', 'ui.p']);
  for (const t of termos) { esperadas.add(t + '.o'); esperadas.add(t + '.p'); }
  const pt = glossario.dicts.pt || {};
  for (const k of esperadas) if (!pt[k]) errors.push(`glossário: termo sem explicação — falta '${k}'`);
  for (const k of Object.keys(pt)) if (!esperadas.has(k)) errors.push(`glossário: explicação sem termo — '${k}' não está em TERMOS`);
  if (!termos.length) errors.push('glossário: lista de termos vazia');
  // apelido (grafia alternativa) tem de apontar para um verbete que existe —
  // senão o termo sai sublinhado na tela e o balão abre vazio
  for (const [a, canon] of Object.entries(glossario.alias || {})) {
    if (!Object.prototype.hasOwnProperty.call(glossario.termos, canon))
      errors.push(`glossário: apelido '${a}' aponta para '${canon}', que não existe em TERMOS`);
    if (Object.prototype.hasOwnProperty.call(glossario.termos, a))
      errors.push(`glossário: '${a}' é apelido E verbete ao mesmo tempo — escolha um`);
  }
}

let totalChaves = 0;
for (const alvo of ALVOS) {
  const { nome, dicts } = alvo;
  for (const l of LANGS) {
    if (!dicts[l]) errors.push(`${nome}: idioma ausente: ${l}`);
  }
  const ptKeys = new Set(Object.keys(dicts.pt || {}));
  if (!ptKeys.size) errors.push(`${nome}: dicionário pt (canônico) vazio`);
  totalChaves += ptKeys.size;

  for (const l of LANGS) {
    const keys = new Set(Object.keys(dicts[l] || {}));
    for (const k of ptKeys) if (!keys.has(k)) errors.push(`${nome} ${l}: falta a chave '${k}'`);
    for (const k of keys) if (!ptKeys.has(k)) errors.push(`${nome} ${l}: chave órfã '${k}' (não existe no pt canônico)`);
    for (const k of keys) {
      const v = dicts[l][k];
      if (typeof v !== 'string' || !v.trim()) errors.push(`${nome} ${l}: valor vazio em '${k}'`);
      // Placeholders {x} precisam bater com o canônico (tradução não pode perdê-los)
      const ph = s => (s.match(/\{\w+\}/g) || []).sort().join(',');
      if (ptKeys.has(k) && ph(v) !== ph(dicts.pt[k])) errors.push(`${nome} ${l}: placeholders divergem em '${k}'`);
    }
  }
}

if (errors.length) {
  console.error(`✗ PARIDADE i18n FALHOU (${errors.length} problema(s)):`);
  errors.slice(0, 40).forEach(e => console.error('  -', e));
  process.exit(1);
}
console.log(`✅ i18n OK — ${totalChaves} chaves × ${LANGS.length} idiomas (pt/en/es/fr) em ${ALVOS.length} dicionários (${ALVOS.map(a => a.nome).join(', ')}), sem órfãs, placeholders consistentes`);
console.log(`✅ glossário OK — ${Object.keys(glossario.termos).length} termos (+${Object.keys(glossario.alias || {}).length} grafias alternativas), cada um com "o que é" e "para que serve" nos 4 idiomas`);
