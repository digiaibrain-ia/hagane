#!/usr/bin/env python3
"""Gera dashboard/src/baggio_monitor_v0.9.html a partir da v0.8 (arquivada).

v0.9:
  * CORRECAO DE RAIZ: o simulador embutido no HTML estava DESATUALIZADO desde a v0.4 (cada HTML era gerado a partir do
    anterior e o simulador novo so chegava aos fluxos do Node-RED). Por isso a "falha de comunicacao" e os alarmes
    antigos continuavam aparecendo. Agora o gerador REEMBUTE o nucleo atual (nodered/gerador/js/50_simulador_core.js)
    e um teste compara o texto embutido com o arquivo-fonte.
  * CENARIO FIXO na simulacao: sempre 1 Falha (F-PRS-001) e 1 Alerta (A-DSJ-006) ativos, com a logica real do PLC.
    Os alarmes "DEM" fictícios da v0.8 foram retirados.  Aviso "Dados simulados" na tela de alertas.
  * CABECALHO limpo, em uma linha so e SEM BORDAS: marca, abas, estado, origem dos dados (chip que diz CLARAMENTE quem esta
    ativo: "Dados simulados" / "PLC ao vivo" / "PLC sem comunicacao"), relogio e engrenagem. Origem dos dados, visual,
    animacao e tela cheia ficam no painel de opcoes (botoes de escolha com "em uso").
  * PROPORCAO: overview ganha a altura que o cabecalho economiza e textos maiores; alertas e E/S ficam menores em telas
    de ate 1500 px (1366x768).
  * Sem os digitos 1/0 nos enderecos; rotulo "TRANSP. DRAGANTE"; a tela se atualiza ao voltar de outra aba do navegador.
Uso: python3 -B -I dashboard/gerador/gerar_monitor_v0.9.py   (aborta se o destino existir ou se a v0.8 mudou)
"""
import importlib.util, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ORIG = RAIZ / "dashboard/arquivo/baggio_monitor_v0.8.html"
DEST = RAIZ / "dashboard/src/baggio_monitor_v0.9.html"
if DEST.exists() and "--forcar" not in sys.argv:
    sys.exit(f"ABORTA: {DEST.name} ja existe (versao nova, nunca sobrescrever)")
s = ORIG.read_text(encoding="utf-8")

spec = importlib.util.spec_from_file_location("gf", RAIZ / "nodered/gerador/gerar_fluxos_v0.9.py")
gf = importlib.util.module_from_spec(spec); _argv = sys.argv; sys.argv = ["x"]; spec.loader.exec_module(gf); sys.argv = _argv

def troca(velho, novo, n=1):
    global s
    if s.count(velho) != n:
        sys.exit(f"ABORTA: trecho da v0.8 mudou ({s.count(velho)}x): {velho[:90]!r}")
    s = s.replace(velho, novo)

def troca_entre(ini, fim, novo):
    global s
    a = s.find(ini); b = s.find(fim, a + 1)
    if a < 0 or b < 0:
        sys.exit(f"ABORTA: marcador nao encontrado: {ini[:60]!r} / {fim[:60]!r}")
    s = s[:a] + novo + s[b:]

# ------------------------------------------------------------------ versao
troca('<meta name="app-version" content="0.8">', '<meta name="app-version" content="0.9">')
troca('  BAGGIO MONITOR v0.8  (SOMENTE LEITURA)', '  BAGGIO MONITOR v0.9  (SOMENTE LEITURA)')
troca('    v0.8  T da alimentacao', '    v0.9  Simulador do HTML reembutido (estava velho desde a v0.4); cenario fixo (1 falha + 1 alerta); cabecalho limpo sem bordas;\n          origem dos dados clara; proporcao das telas; sem 1/0; TRANSP. DRAGANTE.\n    v0.8  T da alimentacao')
troca('const VERSAO = "0.8";', 'const VERSAO = "0.9";')

# ------------------------------------------------------------------ 1. CAUSA-RAIZ: reembute o simulador atual
i = s.find("// [F] SIMULADOR PURO (DEMO)"); fim = "  return B;\n}\n"; j = s.find(fim, i)
if i < 0 or j < 0:
    sys.exit("ABORTA: simulador embutido nao encontrado")
s = s[:i] + gf.nucleo_simulador().rstrip() + "\n" + s[j + len(fim):]

# ------------------------------------------------------------------ 2. cabecalho (uma linha, sem bordas) + painel de opcoes
troca_entre('<header>', '<div id="aviso"', r'''<header>
  <h1><span class="h-marca">Baggio</span><small id="site">Sistema de filtragem</small></h1>
  <nav role="tablist" aria-label="Telas">
    <button role="tab" id="aba-ov" aria-selected="true" data-v="ov">Overview</button>
    <button role="tab" id="aba-al" aria-selected="false" data-v="al">Alertas e falhas<span class="cnt" id="cntAl">0</span></button>
    <button role="tab" id="aba-es" aria-selected="false" data-v="es">Entradas e saídas</button>
  </nav>
  <span class="esp"></span>
  <span id="pEstado" class="chip-h st-nd" aria-live="polite">—</span>
  <button id="pDados" class="chip-h dd-nd" aria-haspopup="dialog" aria-expanded="false" aria-controls="opc" title="Origem dos dados. Clique para trocar.">—</button>
  <span id="relogio"></span>
  <button id="btnOpc" class="btn-h" aria-haspopup="dialog" aria-expanded="false" aria-controls="opc" aria-label="Opções" title="Opções">⚙</button>
</header>
<div id="opc" class="opc" role="dialog" aria-label="Opções" hidden>
  <fieldset><legend>Origem dos dados</legend>
    <label class="rad"><input type="radio" name="fonte" value="cpu"><span><b>PLC real</b><small>Mostra os dados do PLC, lidos pelo Node-RED.</small></span></label>
    <label class="rad"><input type="radio" name="fonte" value="sim"><span><b>Dados simulados</b><small>Para teste e demonstração. Não precisa de PLC nem de Node-RED.</small></span></label>
  </fieldset>
  <fieldset><legend>Visual</legend>
    <label class="rad"><input type="radio" name="tema" value="mod"><span><b>Moderno</b></span></label>
    <label class="rad"><input type="radio" name="tema" value="ori"><span><b>Original</b><small>Igual à tela do WinCC.</small></span></label>
  </fieldset>
  <label class="tg"><input type="checkbox" id="animChk"> Animação da água</label>
  <button class="btn" id="btnTela" type="button">Tela cheia</button>
</div>
''')
troca('    <label class="anim-sw" title="Liga ou desliga o movimento da água (ondas e fluxo nos tubos)"><input type="checkbox" id="animChk"> Animação</label>\n', '')

# ------------------------------------------------------------------ 3. Cab: chip claro da origem dos dados
troca_entre('    const o = Dados.estado ? Dados.estado.origem : null;', '    document.body.classList.toggle("sem-com"', r'''    // ORIGEM DOS DADOS: um unico chip que diz CLARAMENTE quem esta ativo (e a saude da leitura)
    const dd = $("#pDados"); let cl, tx, tt;
    if (Dados.fonte==="sim") { cl="dd-sim"; tx="● Dados simulados"; tt="Os dados desta tela são de teste, gerados na própria página. Clique para trocar para o PLC."; }
    else if (!Dados.contrato || !Dados.estado) { cl="dd-nd"; tx = Dados.falhas>=Cfg.falhasParaCair ? "● PLC sem Node-RED" : "● Conectando ao PLC…"; tt="Aguardando a primeira leitura. Clique para trocar a origem dos dados."; }
    else if (Dados.semCom) { cl="dd-bad"; tx="● PLC sem comunicação"; tt="Não há leitura atual do PLC. Clique para trocar a origem dos dados."; }
    else { cl="dd-ok"; tx="● PLC ao vivo"; tt="Dados reais do PLC. Clique para trocar para dados simulados."; }
    dd.className = "chip-h "+cl; dd.textContent = tx; dd.title = tt;
''')
troca('pe.className = "pill st-"+e.k;', 'pe.className = "chip-h st-"+e.k;')

# ------------------------------------------------------------------ 4. opcoes: escolhas, tela cheia; Dados/Tema sem os botoes antigos
troca('    $$("#fonteSel button").forEach(b=>b.setAttribute("aria-pressed", b.dataset.fonte===f));\n', '    Opc.sincronizar();\n')
troca('    $$(".vis button").forEach(b=>b.setAttribute("aria-pressed", b.dataset.tema===t));\n', '    if (typeof Opc !== "undefined") Opc.sincronizar();\n')
troca('    $$(".vis button").forEach(b=>b.addEventListener("click",()=>{ this.aplicar(b.dataset.tema); renderTudo(); }));\n', '')
troca('  $$("#fonteSel button").forEach(b=>{ b.setAttribute("aria-pressed", b.dataset.fonte===Dados.fonte); b.addEventListener("click",()=>Dados.trocarFonte(b.dataset.fonte)); });\n', '')
troca('function abrirInfo(chave,btn){', r'''/* painel de opcoes: origem dos dados, visual, animacao, tela cheia. Aberto pela engrenagem ou pelo chip de origem. */
const Opc = {
  iniciar(){
    const pop = $("#opc"), b1 = $("#btnOpc"), b2 = $("#pDados");
    const abrir = alvo => { pop.hidden = false; [b1,b2].forEach(b=>b.setAttribute("aria-expanded","true"));
      const r = alvo.getBoundingClientRect(); pop.style.top = (r.bottom+6)+"px"; pop.style.right = Math.max(8, innerWidth-r.right)+"px";
      const f = pop.querySelector("input:checked") || pop.querySelector("input"); if (f) f.focus(); };
    const fechar = () => { pop.hidden = true; [b1,b2].forEach(b=>b.setAttribute("aria-expanded","false")); };
    [b1,b2].forEach(b=>b.addEventListener("click", e=>{ e.stopPropagation(); if (pop.hidden) abrir(b); else fechar(); }));
    document.addEventListener("click", e=>{ if (!pop.hidden && !e.target.closest("#opc")) fechar(); });
    document.addEventListener("keydown", e=>{ if (e.key==="Escape" && !pop.hidden) { fechar(); b1.focus(); } });
    $$('#opc input[name="fonte"]').forEach(r=>r.addEventListener("change",()=>Dados.trocarFonte(r.value)));
    $$('#opc input[name="tema"]').forEach(r=>r.addEventListener("change",()=>{ Tema.aplicar(r.value); renderTudo(); }));
    $("#btnTela").addEventListener("click", ()=>{ try { if (document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen(); } catch(e){} fechar(); });
    this.sincronizar();
  },
  sincronizar(){
    $$('#opc input[name="fonte"]').forEach(r=>{ r.checked = r.value===Dados.fonte; });
    $$('#opc input[name="tema"]').forEach(r=>{ r.checked = r.value===(document.body.classList.contains("tema-ori")?"ori":"mod"); });
  }
};
function abrirInfo(chave,btn){''')
troca('  Tema.iniciar(); Anim.iniciar();\n', '  Tema.iniciar(); Anim.iniciar(); Opc.iniciar();\n  document.addEventListener("visibilitychange", ()=>{ if (!document.hidden) Dados.ler(); });   // ao voltar de outra aba do navegador\n')
troca('window.Baggio = {Dados, Mapa, Alarmes, Overview, Anim, VERSAO};', 'window.Baggio = {Dados, Mapa, Alarmes, Overview, Anim, Opc, CAT_ALARMES, CONTRATO_EMB, VERSAO};')

# ------------------------------------------------------------------ 5. alertas: sem os DEM; aviso de dados simulados
troca_entre('const ALARMES_DEMO = ', ';   /* fictícios', 'const ALARMES_DEMO = []')
troca('  <div class="barra">\n    <h2>Alertas e falhas</h2>', '  <p class="sim-aviso" id="alSimAviso" hidden><b>Dados simulados.</b> Os alarmes abaixo são exemplos para demonstração e não vêm do PLC.</p>\n  <div class="barra">\n    <h2>Alertas e falhas</h2>')
troca('    if (!Alarmes.defs.length) { $("#alLista").innerHTML = ', '    $("#alSimAviso").hidden = !Alarmes.demoLigado();\n    if (!Alarmes.defs.length) { $("#alLista").innerHTML = ')
troca_entre('    +"<p><b>DEMO:</b>', '    +"<p>Os alarmes que o PLC retém', '    +"<p><b>Dados simulados:</b> com a origem em <b>Dados simulados</b> a tela mostra sempre uma falha e um alerta de exemplo, para demonstração. Eles não vêm do PLC.</p>"\n')

# ------------------------------------------------------------------ 6. sem os digitos 1/0
troca('<span class="tp tp-F">Falha</span> <b></b></button>', '<span class="tp tp-F">Falha</span> <b></b></button>')   # (contagem do filtro: continua)
troca('chip(e){ return `<span class="chip" data-end="${esc(e)}">${esc(e)} <b></b></span>`; },', 'chip(e){ return `<span class="chip" data-end="${esc(e)}">${esc(e)}</span>`; },')
troca('      $("b",c).textContent = v===undefined ? "—" : v ? "1" : "0"; });', '      c.title = v===undefined ? "sem dado" : v ? "ligado" : "desligado"; });')
troca('          <span class="e">${v===undefined?"—":v?"1":"0"}</span></div>`;}).join("");', '          <span class="sr-only">${v===undefined?"sem dado":v?"ligado":"desligado"}</span></div>`;}).join("");')

# ------------------------------------------------------------------ 7. rotulo, lampada, tamanhos
troca('[144,131,"TRANSP. FILTRO","end"]', '[144,127,"TRANSP.","end"],[144,139,"DRAGANTE","end"]')
troca('<circle r="8"/><text class="lpx" y="4" text-anchor="middle"></text>', '<circle r="9"/><text class="lpx" y="4" text-anchor="middle"></text>')

# ------------------------------------------------------------------ 7b. geometria para o texto maior (colisoes medidas)
troca('{id:"aspirador",nome:"Aspirador",                        x:230, y:128, eq:"aspirador"}', '{id:"aspirador",nome:"Aspirador",                        x:216, y:128, eq:"aspirador"}')
troca('[241,132,"ASPIRADOR"]', '[228,132,"ASPIRADOR"]')
troca('<rect class="eqp2" x="108" y="200" width="96" height="76"/>', '<rect class="eqp2" x="96" y="200" width="108" height="76"/>')
troca('180,276 108,276 108,200 150,200', '180,276 96,276 96,200 150,200')
troca('M55 62 V198 Q55 213 70 213 H108', 'M55 62 V198 Q55 213 70 213 H96')
troca('[78,338,"ROTAÇÃO BANDA"],[78,350,"FILTRANTE"]', '[64,338,"ROTAÇÃO BANDA"],[64,350,"FILTRANTE"]')
troca('[176,505,"BOMBA 1"],[176,517,"DE FILTRAGEM"]', '[156,505,"BOMBA 1"],[156,517,"DE FILTRAGEM"]')
troca('x:158, y:505, eq:"bomba1"}', 'x:140, y:505, eq:"bomba1"}')
troca('x:559, y:505, eq:"bomba2"}', 'x:624, y:505, eq:"bomba2"}')
troca('<rect class="seg" x="105" y="440" width="447" height="196"', '<rect class="seg" x="105" y="440" width="500" height="196"')

# ------------------------------------------------------------------ 8. CSS
troca('</style>', r'''
/* ============ v0.9 · cabecalho de uma linha, sem bordas ============ */
header{padding:0 12px;gap:10px;flex-wrap:nowrap;min-height:44px}
header h1{flex:0 0 auto;font-size:16px;letter-spacing:.01em;margin-right:6px}
header h1 small{display:none}
@media (min-width:1560px){ header h1 small{display:inline} }
header nav{background:none;border:0;padding:0;gap:2px;overflow:visible;flex:0 1 auto}
header nav button{color:rgba(255,255,255,.74);border-bottom:3px solid transparent;padding:13px 12px 10px;font-weight:600;font-size:13.5px}
header nav button:hover{color:#fff}
header nav button[aria-selected="true"]{color:#fff;border-bottom-color:var(--acento,#fff)}
body header nav button[aria-selected="true"],body.tema-mod header nav button[aria-selected="true"]{color:#fff}   /* vence a regra antiga "body.tema-mod nav button" (texto azul sobre azul) */
.barra[hidden],.al-selbar[hidden],.sim-aviso[hidden]{display:none}   /* hidden nao pode perder para display:flex */
body.tema-ori header nav button[aria-selected="true"]{border-bottom-color:#fff}
header nav .cnt{background:rgba(255,255,255,.22);color:#fff}
header nav .cnt.ativo{background:var(--bad);color:#fff}
header nav .cnt.aviso{background:var(--warn);color:#fff}
.esp{flex:1 1 0}
.chip-h{display:inline-flex;align-items:center;border:0;border-radius:999px;padding:4px 12px;font-weight:650;font-size:12.5px;white-space:nowrap;background:rgba(255,255,255,.14);color:#fff}
button.chip-h{cursor:pointer}
button.chip-h:hover{filter:brightness(1.12)}
#pEstado{width:122px;justify-content:center}               /* largura fixa: o texto muda, o cabecalho nao se mexe */
#pDados{width:192px;justify-content:center}
.chip-h.st-run{background:#dff2e8;color:#1c7f55}
.chip-h.st-warn{background:#fff1cc;color:#8a5a00}
.chip-h.st-bad{background:var(--bad);color:#fff}
.chip-h.st-off,.chip-h.st-nd{background:rgba(255,255,255,.14);color:#fff}
.chip-h.dd-sim{background:#ffd23f;color:#3b2f00}
.chip-h.dd-ok{background:rgba(255,255,255,.14);color:#9ff0c0}
.chip-h.dd-bad{background:var(--bad);color:#fff}
.chip-h.dd-nd{background:rgba(255,255,255,.14);color:#fff}
.btn-h{border:0;background:rgba(255,255,255,.14);color:#fff;border-radius:8px;width:34px;height:30px;font-size:17px;line-height:1}
.btn-h:hover{background:rgba(255,255,255,.26)}
#relogio{opacity:.85;font-size:12.5px}
/* painel de opcoes */
.opc{position:fixed;z-index:40;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:10px;box-shadow:0 10px 30px rgba(0,0,0,.3);padding:10px 14px 12px;width:min(330px,94vw)}
.opc[hidden]{display:none}
.opc fieldset{border:0;margin:0 0 8px;padding:0}
.opc legend{font-weight:700;padding:0;margin-bottom:4px}
.rad{display:flex;gap:9px;padding:6px 8px;border-radius:8px;cursor:pointer;align-items:flex-start}
.rad:hover{background:var(--off-bg)}
.rad input{margin-top:3px;accent-color:var(--head);width:16px;height:16px}
.rad b{display:block}
.rad small{display:block;color:var(--muted);font-size:12px}
.rad:has(input:checked){background:var(--off-bg);box-shadow:inset 3px 0 0 var(--head)}
.rad input:checked + span b::after{content:"  · em uso";color:var(--run);font-weight:700}
.tg{display:flex;gap:9px;align-items:center;margin:4px 8px 10px;font-weight:600;cursor:pointer}
.tg input{width:16px;height:16px;accent-color:var(--head)}
.opc .btn{margin-left:8px}
.sim-aviso{background:var(--warn-bg);border-left:4px solid var(--warn);padding:6px 12px;border-radius:4px;margin:0 0 8px;color:var(--ink)}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
/* ============ v0.9 · proporcao ============ */
main{padding:8px 12px 0}
#v-al,#v-es{padding-bottom:44px}
body{--alt-svg:96px}                      /* original: cabecalho 44 + barra do titulo 31 + folgas */
body.tema-mod{--alt-svg:62px}
.rt{font-size:12px}
.rt2{font-size:13.5px}
.rt3{font-size:15px}
body.tema-mod .rt{font-size:12px}
th,td{padding:6px 10px}
.al-tab td{padding:4px 10px;line-height:1.25}
@media (max-width:1500px){ #v-al,#v-es{zoom:.88} }
@media (max-width:1000px){
  header{flex-wrap:wrap;padding:6px 10px;gap:6px}
  header nav{order:9;flex:1 0 100%;overflow-x:auto}
  .esp,#relogio{display:none}
  #pEstado{width:auto;min-width:0}
  #pDados{width:auto;min-width:0;flex:1 1 auto}
  .opc{left:8px;right:8px!important;width:auto}
}
@media (prefers-color-scheme:dark){ body.tema-mod .opc{background:var(--panel)} }
</style>''')

DEST.write_text(s, encoding="utf-8")
print("ok", DEST.relative_to(RAIZ), len(s)//1024, "KB")
