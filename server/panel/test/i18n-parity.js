#!/usr/bin/env node
/*
 * Paridade dos dicionários i18n do painel (static/i18n.js) e dos Estudos
 * por cadeira (static/lab/lab-i18n.js).
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
];

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
