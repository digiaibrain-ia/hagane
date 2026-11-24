// Mede colisoes dos rotulos do desenho do Overview: texto x tubo, texto x contorno de equipamento,
// texto x lampada/valvula e texto x texto. Uso: node tests/colisao_textos.js URL_OU_ARQUIVO [mod|ori]
// Saida: lista de colisoes (vazia = ok). Sai com codigo 1 se houver alguma.
const { chromium } = require("playwright");
(async () => {
  const url = process.argv[2], tema = process.argv[3] || "mod";
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1536, height: 694 } });
  await p.goto(url + (url.includes("?") ? "&" : "?") + "tema=" + tema); await p.waitForTimeout(2500);
  const r = await p.evaluate(() => {
    const svg = document.querySelector("#svg"), out = [];
    const txt = Array.from(svg.querySelectorAll(":scope > text")).filter(t => t.textContent.trim() && !t.classList.contains("hzt") && !t.classList.contains("seta"));
    const caixa = t => { const q = t.getBBox(); return { x: q.x, y: q.y + q.height * 0.18, w: q.width, h: q.height * 0.64 }; };   // miolo da linha
    const pt = (x, y) => { const q = svg.createSVGPoint(); q.x = x; q.y = y; return q; };
    const tubos = Array.from(svg.querySelectorAll(".tb-o")), cont = Array.from(svg.querySelectorAll(".eqp,.eqp2,.pnl"));
    const marcas = Array.from(svg.querySelectorAll("[data-lp],[data-vl]")).map(g => {
      const m = /translate\(([-\d.]+),([-\d.]+)\)/.exec(g.getAttribute("transform")); return { id: g.dataset.lp || g.dataset.vl, x: +m[1], y: +m[2], r: g.dataset.lp ? 9 : 10 }; });
    const rotulo = t => t.textContent.trim().slice(0, 28);
    const bx = txt.map(caixa);
    txt.forEach((t, i) => {
      const c = bx[i];
      // texto x tubo e texto x contorno
      for (let x = c.x; x <= c.x + c.w; x += 3) for (let y = c.y; y <= c.y + c.h; y += 3) {
        const P = pt(x, y);
        const tb = tubos.find(e => e.isPointInStroke(P)); if (tb) { out.push(`"${rotulo(t)}" cruza TUBO`); x = 1e9; break; }
      }
      for (let x = c.x; x <= c.x + c.w; x += 3) { let achou = false;
        for (let y = c.y; y <= c.y + c.h; y += 3) { const P = pt(x, y); if (cont.some(e => e.isPointInStroke(P))) { out.push(`"${rotulo(t)}" cruza CONTORNO de equipamento`); achou = true; break; } }
        if (achou) break; }
      // texto x lampada/valvula
      marcas.forEach(m => { if (m.x + m.r > c.x && m.x - m.r < c.x + c.w && m.y + m.r > c.y && m.y - m.r < c.y + c.h) out.push(`"${rotulo(t)}" encosta em ${m.id}`); });
      // texto x texto
      txt.forEach((u, j) => { if (j <= i) return; const d = bx[j];
        if (c.x < d.x + d.w && c.x + c.w > d.x && c.y < d.y + d.h && c.y + c.h > d.y) out.push(`"${rotulo(t)}" sobrepoe "${rotulo(u)}"`); });
    });
    return Array.from(new Set(out));
  });
  console.log(`tema ${tema}: ${r.length} colisoes`); r.forEach(x => console.log("  - " + x));
  await b.close(); process.exit(r.length ? 1 : 0);
})();
