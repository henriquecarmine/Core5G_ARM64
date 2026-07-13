/* Lab de IA — modo passo a passo (guiado)
   Transforma cada aula (seções .card empilhadas) num percurso de UM passo
   por vez: barra "Passo X de Y", dica do que fazer em cada etapa, botões
   Voltar/Próximo e a etapa final explicando quando clicar "Entendi".
   Motivo: aluno leigo testou a página inteira e se perdeu — não sabia onde
   nem quando clicar. Progressive disclosure resolve.
   Uso: <script src="/static/lab-stepper.js"></script> no fim da aula.
   - Reordena didaticamente: conceito (📖) vem antes da base de dados (🗂️).
   - Guarda o passo atual por aula (localStorage) e retoma de onde parou.
   - "ver a aula inteira" desliga o modo guiado (preferência global).
   - i18n via LABI18N (chaves step.*) com fallback PT embutido. */
(function () {
  "use strict";
  const wrap = document.querySelector(".wrap");
  if (!wrap) return;
  const cards = Array.from(wrap.querySelectorAll(":scope > section.card"));
  const comp = wrap.querySelector(":scope > .comp");
  if (cards.length < 2 || !comp) return;

  const lesson = (location.pathname.split("/").filter(Boolean).pop() || "aula").replace(/[^a-z0-9-]/gi, "");
  const SKEY = "c5g-lab-step-" + lesson;
  const MKEY = "c5g-lab-mode"; // "guiado" | "inteira"

  /* ---- fallback PT (páginas fora do painel, sem LABI18N) ---- */
  const PT = {
    "step.of": "Passo {n} de {t}",
    "step.next": "Próximo passo ▸",
    "step.back": "◂ Voltar",
    "step.all": "ver a aula inteira",
    "step.guided": "◂ voltar ao passo a passo",
    "step.do": "👉 O que fazer aqui:",
    "step.final.t": "Concluir a aula",
    "step.hint.concept": "Só leitura: entenda a ideia com calma. Nada para clicar — quando terminar, toque em “Próximo passo”.",
    "step.hint.base": "Escolha uma base de dados clicando num dos cartões (pode ficar na primeira, que é a do professor). Depois avance.",
    "step.hint.oran": "Só leitura: veja ONDE isso roda numa rede real, seguindo o fluxo. Depois avance.",
    "step.hint.mexe": "Agora é com você: mexa nos controles e veja o resultado mudar na hora. Não tem como quebrar nada — brinque à vontade.",
    "step.hint.models": "Compare os modelos: menor erro = melhor. Repare em quem vence NESTA base. Só leitura.",
    "step.hint.multi": "Só leitura: o mesmo modelo atendendo vários de uma vez, como num RIC de verdade.",
    "step.hint.report": "Opcional: gere o relatório (PDF/Word/.py) com o que você rodou. Não precisa agora? Só avance.",
    "step.hint.extra": "Leia com calma e avance quando terminar.",
    "step.hint.final": "Última etapa! A aula fez sentido? Clique “✅ Entendi” — ela fica marcada como concluída e a próxima abre. Algo ficou confuso? Clique “🤔 Não entendi”, escreva a dúvida e envie: ela vai direto ao professor."
  };
  const T = (k, p) => {
    let s = window.LABI18N ? LABI18N.t(k, p) : null;
    if (!s || s === k) { s = PT[k] || k; if (p) for (const q in p) s = s.replace(new RegExp("{" + q + "}", "g"), p[q]); }
    return s;
  };

  /* ---- classifica cada seção pelo ícone do título ---- */
  const tipoDe = el => {
    const t = (el.querySelector("h2") || {}).textContent || "";
    if (t.indexOf("🗂") > -1) return "base";
    if (t.indexOf("🛰") > -1) return "oran";
    if (t.indexOf("🎛") > -1 || t.indexOf("🎨") > -1 || t.indexOf("🚨") > -1) return "mexe";
    if (t.indexOf("📊") > -1 || t.indexOf("📋") > -1) return "models";
    if (t.indexOf("👥") > -1) return "multi";
    if (t.indexOf("📄") > -1) return "report";
    if (t.indexOf("📖") > -1) return "concept";
    return "extra";
  };
  let steps = cards.map(el => ({ el, tp: tipoDe(el) }));
  // didática: o conceito (📖) vem ANTES da escolha de base (🗂️)
  const ci = steps.findIndex(s => s.tp === "concept");
  const bi = steps.findIndex(s => s.tp === "base");
  if (ci > -1 && bi > -1 && bi < ci) { const c = steps.splice(ci, 1)[0]; steps.splice(bi, 0, c); }
  steps.push({ el: comp, tp: "final" });
  const total = steps.length;

  /* ---- estado ---- */
  const lsGet = (k, d) => { try { return localStorage.getItem(k) || d; } catch (e) { return d; } };
  const lsSet = (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} };
  let mode = lsGet(MKEY, "guiado");
  let idx = Math.min(Math.max(parseInt(lsGet(SKEY, "0"), 10) || 0, 0), total - 1);

  /* ---- CSS ---- */
  const css = document.createElement("style");
  css.textContent = `
  .stpbar{position:sticky;top:0;z-index:60;display:flex;align-items:center;gap:12px;flex-wrap:wrap;
    margin:0 0 14px;padding:10px 14px;border:1px solid var(--line);border-radius:12px;
    background:var(--bg);box-shadow:0 4px 14px rgba(0,0,0,.06)}
  .stpbar .stpof{font-size:.78rem;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:var(--accent);white-space:nowrap}
  .stpbar .stpt{font-size:.9rem;font-weight:700;color:var(--ink);flex:1;min-width:120px}
  .stpdots{display:flex;gap:6px;align-items:center}
  .stpdots button{width:12px;height:12px;border-radius:50%;border:1.5px solid var(--line);background:transparent;cursor:pointer;padding:0}
  .stpdots button.done{background:var(--accent);border-color:var(--accent);opacity:.45}
  .stpdots button.on{background:var(--accent);border-color:var(--accent);transform:scale(1.25)}
  .stpbar .stpmode{font-size:.76rem;color:var(--ink-3);background:none;border:none;cursor:pointer;text-decoration:underline;white-space:nowrap}
  .stphint{display:flex;gap:10px;align-items:flex-start;margin:12px 0 2px;padding:10px 12px;border-radius:10px;
    background:color-mix(in srgb,var(--accent) 9%,transparent);border:1px dashed color-mix(in srgb,var(--accent) 45%,transparent);
    font-size:.9rem;line-height:1.5;color:var(--ink-2)}
  .stphint b{color:var(--ink);white-space:nowrap}
  .stpnav{display:flex;justify-content:space-between;gap:10px;margin-top:18px;padding-top:14px;border-top:1px dashed var(--line)}
  .stpnav button{font:inherit;font-size:.92rem;font-weight:700;padding:10px 18px;border-radius:10px;cursor:pointer}
  .stpnav .stpnext{background:var(--accent);color:var(--accent-ink,#fff);border:1px solid var(--accent)}
  .stpnav .stpnext:hover{filter:brightness(1.08)}
  .stpnav .stpback{background:transparent;color:var(--ink-2);border:1px solid var(--line)}
  .stpnav .stpback[disabled]{opacity:.35;cursor:default}
  .stp-hide{display:none!important}
  html.embed .stpbar{top:6px}
  @media (max-width:640px){.stpbar{gap:8px}.stpdots{order:3;width:100%;justify-content:center}}`;
  document.head.appendChild(css);

  /* ---- barra de progresso (entra logo após o cabeçalho .top) ---- */
  const bar = document.createElement("div");
  bar.className = "stpbar";
  bar.innerHTML = `<span class="stpof"></span><span class="stpt"></span>
    <span class="stpdots"></span><button class="stpmode"></button>`;
  const top = wrap.querySelector(":scope > .top");
  (top || wrap.firstElementChild).insertAdjacentElement("afterend", bar);
  const elOf = bar.querySelector(".stpof"), elT = bar.querySelector(".stpt"),
        elDots = bar.querySelector(".stpdots"), elMode = bar.querySelector(".stpmode");

  /* ---- dica + navegação (realocados a cada passo) ---- */
  const hint = document.createElement("div");
  hint.className = "stphint";
  const nav = document.createElement("div");
  nav.className = "stpnav";
  nav.innerHTML = `<button class="stpback"></button><button class="stpnext"></button>`;
  const btBack = nav.querySelector(".stpback"), btNext = nav.querySelector(".stpnext");
  btBack.addEventListener("click", () => go(idx - 1));
  btNext.addEventListener("click", () => go(idx + 1));

  function tituloDe(s) {
    if (s.tp === "final") return T("step.final.t");
    const h = s.el.querySelector("h2");
    return h ? h.textContent.trim() : "";
  }

  function render() {
    const guiado = mode === "guiado";
    elMode.textContent = guiado ? T("step.all") : T("step.guided");
    elOf.textContent = guiado ? T("step.of", { n: idx + 1, t: total }) : "";
    elT.textContent = guiado ? tituloDe(steps[idx]) : "";
    elDots.innerHTML = guiado ? steps.map((s, i) =>
      `<button data-i="${i}" class="${i < idx ? "done" : i === idx ? "on" : ""}" title="${T("step.of", { n: i + 1, t: total })}"></button>`).join("") : "";
    elDots.querySelectorAll("button").forEach(b => b.addEventListener("click", () => go(+b.dataset.i)));

    steps.forEach((s, i) => s.el.classList.toggle("stp-hide", guiado && i !== idx));
    hint.remove(); nav.remove();
    if (!guiado) return;

    const s = steps[idx];
    hint.innerHTML = `<b>${T("step.do")}</b><span>${T("step.hint." + s.tp)}</span>`;
    const h2 = s.el.querySelector("h2");
    if (h2) h2.insertAdjacentElement("afterend", hint);
    else s.el.insertAdjacentElement("afterbegin", hint);

    btBack.textContent = T("step.back");
    btBack.disabled = idx === 0;
    btNext.textContent = T("step.next");
    if (s.tp !== "final") s.el.appendChild(nav);         // no final, quem manda são os botões Entendi/Não entendi
    else { nav.innerHTML = ""; }
  }

  function go(i) {
    idx = Math.min(Math.max(i, 0), total - 1);
    lsSet(SKEY, String(idx));
    render();
    try { (top || bar).scrollIntoView({ block: "start" }); window.scrollTo(0, 0); } catch (e) {}
  }

  elMode.addEventListener("click", () => { mode = mode === "guiado" ? "inteira" : "guiado"; lsSet(MKEY, mode); render(); });

  // setas do teclado (fora de campos de texto)
  document.addEventListener("keydown", e => {
    if (mode !== "guiado") return;
    const tag = (e.target && e.target.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea" || tag === "select" || e.target.isContentEditable) return;
    if (e.key === "ArrowRight" && idx < total - 1 && steps[idx].tp !== "final") go(idx + 1);
    if (e.key === "ArrowLeft") go(idx - 1);
  });

  // concluiu a aula → próxima visita recomeça do passo 1
  const ok = document.getElementById("compOk");
  if (ok) ok.addEventListener("click", () => { try { localStorage.removeItem(SKEY); } catch (e) {} });

  if (window.LABI18N) LABI18N.onChange(render);
  render();
})();
