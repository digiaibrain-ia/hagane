#!/usr/bin/env python3
"""Gera dashboard/src/hagane_monitor_v0.3.html a partir da v0.2 (arquivada).

Mudancas da v0.3:
  * DOIS VISUAIS no mesmo HTML: "Moderno" (identidade do medidor: tinta #1a4a78, acento #ec7000,
    modo escuro automatico) e "Original" (= v0.2, fiel ao WinCC). Escolha no cabecalho; lembrada no navegador;
    ?tema=ori|mod na URL forca um deles. Mesma geometria e mesmos dados nos dois.
  * MENOS REPETICAO: titulo do local aparece uma vez por visual; estado da maquina vira um unico selo
    no cabecalho (some a faixa Sistema ligado/Aviso/Falha/Sirene/"alarme critico"); na E/S o nome da tag
    sai da linha (fica no title).
Uso: python3 -I dashboard/gerador/gerar_monitor_v0.3.py   (aborta se o destino existir ou a v0.2 mudou)
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ORIG = RAIZ / "dashboard/arquivo/hagane_monitor_v0.2.html"
DEST = RAIZ / "dashboard/src/hagane_monitor_v0.3.html"
if DEST.exists() and "--forcar" not in sys.argv:
    sys.exit(f"ABORTA: {DEST.name} ja existe (versao nova, nunca sobrescrever)")
s = ORIG.read_text(encoding="utf-8")

def troca(velho, novo, n=1):
    global s
    if s.count(velho) != n:
        sys.exit(f"ABORTA: trecho da v0.2 mudou ({s.count(velho)}x): {velho[:70]!r}")
    s = s.replace(velho, novo)

def troca_entre(ini, fim, novo):
    global s
    a = s.find(ini); b = s.find(fim, a + 1)
    if a < 0 or b < 0:
        sys.exit(f"ABORTA: marcador nao encontrado: {ini[:50]!r} / {fim[:50]!r}")
    s = s[:a] + novo + s[b:]

# ---------- versao ----------
troca('<meta name="app-version" content="0.2">', '<meta name="app-version" content="0.3">')
troca('  HAGANE MONITOR v0.2  (SOMENTE LEITURA)', '  HAGANE MONITOR v0.3  (SOMENTE LEITURA)')
troca('    v0.2  Overview fiel', '    v0.3  Dois visuais (Moderno = identidade do medidor; Original = WinCC); menos informacao repetida.\n    v0.2  Overview fiel')
troca('const VERSAO = "0.2";', 'const VERSAO = "0.3";')
troca('<body>', '<body class="tema-mod">')

# ---------- cabecalho: marca + selo de estado + origem + comunicacao + visual + relogio ----------
troca_entre('<header>', '<nav role="tablist"', '''<header>
  <h1>Hagane<small id="site">Baggio, sistema de água</small></h1>
  <span id="pEstado" class="pill st-nd" aria-live="polite">—</span>
  <span id="pOrigem" class="pill com-nd">—</span>
  <span id="pCom" class="pill com-nd">sem leitura</span>
  <div class="vis" role="group" aria-label="Visual da tela">
    <button data-tema="mod" aria-pressed="true" title="Visual moderno (identidade do medidor)">Moderno</button>
    <button data-tema="ori" aria-pressed="false" title="Visual original (tela do WinCC)">Original</button>
  </div>
  <span id="relogio"></span>
</header>
''')
troca('<div id="faixa" aria-live="polite"></div>\n', '')

# ---------- overview: ⓘ flutuante (o visual moderno nao tem barra de titulo) ----------
troca('<div class="tela-tit">BAGGIO - SISTEMA DE ÁGUA - OVERVIEW <button class="info-btn" data-info="ov" aria-label="Sobre esta tela">i</button></div>',
      '<div class="tela-tit">BAGGIO - SISTEMA DE ÁGUA - OVERVIEW <button class="info-btn" data-info="ov" aria-label="Sobre esta tela">i</button></div>\n'
      '    <button class="info-btn info-flut" data-info="ov" aria-label="Sobre esta tela">i</button>')

# ---------- desenho: classes para o tema poder pintar ----------
troca('<rect x="0" y="20" width="1185" height="625" fill="#d5d9dc"/><rect x="0" y="20" width="1185" height="625" fill="url(#pts)"/>',
      '<rect class="cv" x="0" y="20" width="1185" height="625" fill="#d5d9dc"/><rect class="cvp" x="0" y="20" width="1185" height="625" fill="url(#pts)"/>')
troca('<polygon fill="#ecea00" points=', '<polygon class="liq" fill="#ecea00" points=')
troca('<rect x="105" y="416" width="447" height="220" fill="none" stroke="#e3cf00"', '<rect class="seg" x="105" y="416" width="447" height="220" fill="none" stroke="#e3cf00"')
troca('max-height:calc(100vh - 202px);margin:0 auto}', 'max-height:calc(100vh - var(--alt-svg,170px));margin:0 auto}')

# ---------- E/S: nome da tag sai da linha (fica no title) ----------
troca('<span class="d">${esc(desc)}${alerta}<small>${esc(t.nome)}</small></span>', '<span class="d" title="${esc(t.nome)}">${esc(desc)}${alerta}</span>')

# ---------- lampada "ligada" com marca de verificacao no visual moderno (cor nunca e o unico sinal) ----------
troca('if (x) x.textContent = d.c==="fail"?"!": d.c==="nd"?"?":"";',
      'if (x) x.textContent = d.c==="fail"?"!": d.c==="nd"?"?": (d.c==="on" && g.dataset.lp && document.body.classList.contains("tema-mod") ? "✓" : "");')

# ---------- Cab: faixa vira UM selo de estado ----------
troca_entre('    // faixa\n', '    // contador\n', '''    // estado da maquina: um unico selo (antes eram 4 luzes + "alarme critico")
    const e = Cab.estado(), pe = $("#pEstado");
    pe.className = "pill st-"+e.k; pe.textContent = e.t; pe.title = e.dica;
''')
troca('const Cab = {\n', '''const Cab = {
  /* prioridade: sem dado > falha > aviso > em operacao > parada */
  estado(){
    const f = Mapa.faixa, b = a=>Dados.bit(a);
    if (!Dados.contrato || !Dados.estado || Dados.semCom) return {k:"nd", t:"Sem dado", dica:"Sem leitura atual da CPU"};
    const sirene = b(f.sirene)===true ? " Sirene ligada." : "";
    const grave = Alarmes.ativos().some(d=>d.sev==="emergencia"||d.sev==="critico");
    if (b(f.vermelha)===true || grave) return {k:"bad", t:"■ Falha", dica:"Coluna vermelha / alarme crítico ativo."+sirene};
    if (b(f.amarela)===true || b(f.permissivel)===true) return {k:"warn", t:"▲ Aviso", dica:"Coluna amarela / alarme permissível ativo."+sirene};
    if (b(f.verde)===true) return {k:"run", t:"● Em operação", dica:"Coluna verde: sistema de filtragem ligado."+sirene};
    return {k:"off", t:"○ Parada", dica:"Nenhuma coluna acesa."+sirene};
  },
''')

# ---------- texto de ajuda ----------
troca_entre('  ov:["Overview"', '  al:["Alertas', '''  ov:["Overview","<p>Mesma disposição da tela do WinCC. <b>Somente leitura</b>: nada aqui envia comando.</p><ul>"
    +"<li>Lâmpada <b>verde</b> = ativo/em operação (no visual moderno com ✓); <b>cinza</b> = inativo/parado; <b>vermelha com !</b> = falha (alarme ou disjuntor do equipamento); <b>tracejada com ?</b> = sem dado.</li>"
    +"<li><b>Toque/clique numa lâmpada ou válvula</b> para ver o estado e o endereço no PLC.</li>"
    +"<li>O selo no topo resume a máquina: Em operação, Aviso, Falha ou Parada.</li>"
    +"<li>Visual <b>Original</b> = tela do WinCC; <b>Moderno</b> = identidade do medidor. Os dados são os mesmos.</li>"
    +"<li>Líquido amarelo e tubos são desenho fixo. Frequência das bombas ainda não é lida (P-03).</li></ul>"],
''')

# ---------- inicio: tema ----------
troca('  Dados.aoAtualizar(renderTudo);\n', '''  Tema.iniciar();
  Dados.aoAtualizar(renderTudo);
''')
troca('function abrirInfo(chave,btn){', '''/* visual: "mod" (moderno) ou "ori" (original/WinCC). ?tema= na URL tem prioridade; senao o ultimo escolhido; senao moderno. */
const Tema = {
  aplicar(t){
    if (t!=="ori" && t!=="mod") t = "mod";
    document.body.classList.remove("tema-mod","tema-ori"); document.body.classList.add("tema-"+t);
    $$(".vis button").forEach(b=>b.setAttribute("aria-pressed", b.dataset.tema===t));
    gravarStorage("hagane_tema", t);
  },
  iniciar(){
    const q = new URLSearchParams(location.search).get("tema");
    this.aplicar(q || lerStorage("hagane_tema") || "mod");
    $$(".vis button").forEach(b=>b.addEventListener("click",()=>{ this.aplicar(b.dataset.tema); renderTudo(); }));
  }
};
function abrirInfo(chave,btn){''')

# ---------- CSS ----------
troca('</style>', r'''
/* ============ v0.3 · cabecalho: selo de estado e chave de visual ============ */
.pill.st-run{background:var(--run-bg);color:var(--run)}
.pill.st-warn{background:var(--warn-bg);color:var(--warn);border-color:var(--warn)}
.pill.st-bad{background:var(--bad);color:#fff}
.pill.st-off,.pill.st-nd{background:var(--off-bg);color:var(--muted)}
.vis{display:inline-flex;border:1.5px solid rgba(255,255,255,.55);border-radius:7px;overflow:hidden}
.vis button{border:0;background:transparent;color:#fff;padding:3px 11px;font-weight:600;font-size:12.5px}
.vis button[aria-pressed="true"]{background:#fff;color:var(--head)}
.tela{position:relative}
.info-flut{display:none;position:absolute;top:8px;right:8px;z-index:2}
body.tema-ori #site{display:none}               /* no Original o local ja aparece na barra do WinCC */

/* ============ v0.3 · visual MODERNO (identidade do medidor) ============ */
body.tema-mod{
  --bg:#f3f5f8; --panel:#ffffff; --ink:#141414; --muted:#5b6b7e; --line:#dde2e8;
  --head:#1a4a78; --acento:#ec7000;
  --run:#1f7a4d; --run-bg:#e3f3ea; --warn:#b45f00; --warn-bg:#fff0dc;
  --bad:#c62828; --bad-bg:#fde8e8; --off:#8a98a8; --off-bg:#eef1f5; --focus:#1a4a78;
  --font:system-ui,"Segoe UI",Roboto,Arial,sans-serif;
  --alt-svg:140px;
}
body.tema-mod nav button[aria-selected="true"]{color:var(--head);border-bottom-color:var(--acento)}
body.tema-mod .tela-tit{display:none}
body.tema-mod .info-flut{display:inline-block}
body.tema-mod .tela{background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden}
body.tema-mod #svg text{font-family:var(--font)}
body.tema-mod .cv{fill:var(--panel)}
body.tema-mod .cvp{display:none}
body.tema-mod .eqp{fill:#eef1f5;stroke:#8a98a8;stroke-width:1.5}
body.tema-mod .eqp2{fill:#dfe5ec;stroke:#8a98a8;stroke-width:1.5}
body.tema-mod .pnl{fill:#f3f5f8;stroke:var(--line)}
body.tema-mod .tb-i{display:none}
body.tema-mod .tb-o{stroke:#3d86b8;stroke-width:4.5}
body.tema-mod .tb-o.ar{stroke:#1a4a78}
body.tema-mod .tb-ponta{fill:#3d86b8;stroke:none}
body.tema-mod .liq{fill:#f2c94c;opacity:.9}
body.tema-mod .seg{stroke:var(--acento);stroke-width:1.2;stroke-dasharray:4 4}
body.tema-mod .rt,body.tema-mod .rt2,body.tema-mod .rt3,body.tema-mod .seta{fill:var(--ink)}
body.tema-mod .rt{font-size:10.5px;font-weight:600}
body.tema-mod .lp circle{fill:#d3dae2;stroke:#8a98a8;stroke-width:1.5}
body.tema-mod .lp.on circle{fill:var(--run);stroke:var(--run)}
body.tema-mod .lp.fail circle{fill:var(--bad);stroke:var(--bad)}
body.tema-mod .lp.nd circle{fill:var(--panel);stroke:var(--off)}
body.tema-mod .vl path{fill:var(--panel);stroke:var(--muted);stroke-width:1.5}
body.tema-mod .vl.on path{fill:var(--run);stroke:var(--run)}
body.tema-mod .hz{fill:var(--panel);stroke:var(--line)}
body.tema-mod .hzt{fill:var(--muted)}

/* ============ v0.3 · MODERNO no escuro (como o medidor: segue o sistema) ============ */
@media (prefers-color-scheme:dark){
  body.tema-mod{
    --bg:#10161d; --panel:#18212b; --ink:#e8edf2; --muted:#93a3b5; --line:#2a3744; --head:#0f2e4d;
    --run:#4cc38a; --run-bg:#143025; --warn:#f2a54a; --warn-bg:#352612;
    --bad:#cf4242; --bad-bg:#3a1a1a; --off:#6c7c8e; --off-bg:#1f2933; --focus:#7fb4ea;
  }
  body.tema-mod nav,body.tema-mod table,body.tema-mod .pop,body.tema-mod .byte,body.tema-mod .painel{background:var(--panel)}
  body.tema-mod th{background:#1f2933}
  body.tema-mod .btn,body.tema-mod .info-btn,body.tema-mod input[type=search],body.tema-mod .sub button,body.tema-mod #conf input{background:var(--panel);color:var(--ink)}
  body.tema-mod .sub button[aria-pressed="true"]{background:#2a5d94;color:#fff}
  body.tema-mod .pill.real{background:#e8edf2;color:#0f2e4d}
  body.tema-mod nav button[aria-selected="true"]{color:#fff}
  body.tema-mod .eqp{fill:#222e3a;stroke:#6c7c8e}
  body.tema-mod .eqp2{fill:#2a3745;stroke:#6c7c8e}
  body.tema-mod .pnl{fill:#1f2933}
  body.tema-mod .tb-o{stroke:#4f9ccf}
  body.tema-mod .tb-o.ar{stroke:#7fb4ea}
  body.tema-mod .tb-ponta{fill:#4f9ccf}
  body.tema-mod .liq{fill:#b8932a}
  body.tema-mod .lp circle{fill:#3a4756;stroke:#6c7c8e}
  body.tema-mod .lp.on circle{stroke:var(--run)}
  body.tema-mod .vl path{fill:#18212b}
  body.tema-mod tr.ativo td{color:var(--ink)}
}
</style>''')

DEST.write_text(s, encoding="utf-8")
print("ok", DEST.relative_to(RAIZ), len(s)//1024, "KB")
