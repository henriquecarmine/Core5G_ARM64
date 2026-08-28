/*
 * Servidor estático mínimo para os testes de fumaça, com raiz em
 * `server/panel/` — para que os caminhos absolutos das páginas resolvam.
 *
 * POR QUE isto existe: os testes carregavam as páginas por `file://`, e
 * `<link href="/static/tokens.css">` aponta para a RAIZ DO DISCO ali. O painel
 * era renderizado sem a folha de identidade e os testes passavam mesmo assim —
 * verde falso, cego para uma classe inteira de quebra. Servindo por HTTP, o que
 * o teste vê é o que o navegador vê.
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const RAIZ = path.resolve(__dirname, '..');

const TIPOS = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
};

/** Sobe o servidor numa porta livre. Devolve { url, fechar }. */
function subir() {
  return new Promise((resolve, reject) => {
    const srv = http.createServer((req, res) => {
      const rel = decodeURIComponent(req.url.split('?')[0]);
      const arq = path.join(RAIZ, path.normalize(rel).replace(/^(\.\.[/\\])+/, ''));
      if (!arq.startsWith(RAIZ)) { res.writeHead(403).end(); return; }
      fs.readFile(arq, (err, buf) => {
        if (err) { res.writeHead(404, { 'Content-Type': 'text/plain' }).end('404 ' + rel); return; }
        res.writeHead(200, { 'Content-Type': TIPOS[path.extname(arq).toLowerCase()] || 'application/octet-stream' });
        res.end(buf);
      });
    });
    srv.on('error', reject);
    srv.listen(0, '127.0.0.1', () => {
      const { port } = srv.address();
      resolve({
        url: (rel) => `http://127.0.0.1:${port}${rel}`,
        fechar: () => new Promise((r) => srv.close(r)),
      });
    });
  });
}

module.exports = { subir };
