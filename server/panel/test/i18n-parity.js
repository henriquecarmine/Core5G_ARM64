#!/usr/bin/env node
/*
 * Paridade dos dicionários i18n do painel (static/i18n.js).
 *
 * Garante que TODA chave existe nos 4 idiomas (pt/en/es/fr) — o fallback
 * mascara chave faltante na tela, então só o teste pega. Também falha se um
 * idioma tiver chave órfã (que não existe no pt canônico) ou valor vazio.
 *
 * Uso: node i18n-parity.js   (ou via npm run test:i18n)
 */
const fs = require('fs');
const path = require('path');

const src = fs.readFileSync(path.resolve(__dirname, '..', 'static', 'i18n.js'), 'utf8');
// Executa o arquivo num sandbox sem DOM (o i18n.js é guardado p/ isso) e
// extrai o objeto de dicionários.
const dicts = new Function(`${src}; return I18N_DICTS;`)();

const LANGS = ['pt', 'en', 'es', 'fr'];
const errors = [];

for (const l of LANGS) {
  if (!dicts[l]) errors.push(`idioma ausente: ${l}`);
}
const ptKeys = new Set(Object.keys(dicts.pt || {}));
if (!ptKeys.size) errors.push('dicionário pt (canônico) vazio');

for (const l of LANGS) {
  const keys = new Set(Object.keys(dicts[l] || {}));
  for (const k of ptKeys) if (!keys.has(k)) errors.push(`${l}: falta a chave '${k}'`);
  for (const k of keys) if (!ptKeys.has(k)) errors.push(`${l}: chave órfã '${k}' (não existe no pt canônico)`);
  for (const k of keys) {
    const v = dicts[l][k];
    if (typeof v !== 'string' || !v.trim()) errors.push(`${l}: valor vazio em '${k}'`);
    // Placeholders {x} precisam bater com o canônico (tradução não pode perdê-los)
    const ph = s => (s.match(/\{\w+\}/g) || []).sort().join(',');
    if (ptKeys.has(k) && ph(v) !== ph(dicts.pt[k])) errors.push(`${l}: placeholders divergem em '${k}'`);
  }
}

if (errors.length) {
  console.error(`✗ PARIDADE i18n FALHOU (${errors.length} problema(s)):`);
  errors.slice(0, 40).forEach(e => console.error('  -', e));
  process.exit(1);
}
console.log(`✅ i18n OK — ${ptKeys.size} chaves × ${LANGS.length} idiomas (pt/en/es/fr), sem órfãs, placeholders consistentes`);
