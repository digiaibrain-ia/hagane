#!/usr/bin/env python3
"""Gera dashboard/src/baggio_monitor_v0.10.html a partir da v0.9 (arquivada).

v0.10 (aproveitando o projeto do medidor):
  * DIALOGO "VERSAO DO PROGRAMA": botao da versao no cabecalho abre o historico resumido (fonte unica:
    docs/historico_versoes.json). O gerador ABORTA se a primeira entrada do historico nao for a versao gerada.
  * CONTADORES "Alertas" e "Falhas" no cabecalho (como no medidor). Clicar abre a tela de alertas ja filtrada.
    O selo de estado e a bolinha da aba sairam (cabecalho mais limpo).
  * DIAGNOSTICO DA CADEIA HTML -> Node-RED -> PLC (cartao "Modo" do medidor): nas opcoes e na faixa de "sem comunicacao",
    mostra qual elo esta conectado.
Uso: python3 -B -I dashboard/gerador/gerar_monitor_v0.10.py   (aborta se o destino existir ou se a v0.9 mudou)
"""
import json, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
VERSAO = "0.10"
ORIG = RAIZ / "dashboard/arquivo/baggio_monitor_v0.9.html"
DEST = RAIZ / f"dashboard/src/baggio_monitor_v{VERSAO}.html"
if DEST.exists() and "--forcar" not in sys.argv:
    sys.exit(f"ABORTA: {DEST.name} ja existe (versao nova, nunca sobrescrever)")
HIST = json.loads((RAIZ / "docs/historico_versoes.json").read_text(encoding="utf-8"))
if HIST["atual"] != VERSAO or HIST["versoes"][0]["v"] != VERSAO:
    sys.exit(f"ABORTA: docs/historico_versoes.json nao esta atualizado para a v{VERSAO} (atual={HIST['atual']}, 1a entrada={HIST['versoes'][0]['v']})")
s = ORIG.read_text(encoding="utf-8")

def troca(velho, novo, n=1):
    global s
    if s.count(velho) != n:
        sys.exit(f"ABORTA: trecho da v0.9 mudou ({s.count(velho)}x): {velho[:90]!r}")
    s = s.replace(velho, novo)

def troca_entre(ini, fim, novo):
    global s
    a = s.find(ini); b = s.find(fim, a + 1)
    if a < 0 or b < 0:
        sys.exit(f"ABORTA: marcador nao encontrado: {ini[:60]!r} / {fim[:60]!r}")
    s = s[:a] + novo + s[b:]

# ------------------------------------------------------------------ versao
troca('<meta name="app-version" content="0.9">', f'<meta name="app-version" content="{VERSAO}">')
troca('  BAGGIO MONITOR v0.9  (SOMENTE LEITURA)', f'  BAGGIO MONITOR v{VERSAO}  (SOMENTE LEITURA)')
troca('    v0.9  Simulador do HTML reembutido', f'    v{VERSAO} Dialogo "Versao do programa" (historico), contadores Alertas/Falhas no cabecalho, diagnostico da cadeia HTML-Node-RED-PLC.\n    v0.9  Simulador do HTML reembutido')
troca('const VERSAO = "0.9";', f'const VERSAO = "{VERSAO}";\n/* historico resumido das versoes (fonte: docs/historico_versoes.json) */\nconst HIST_VERSOES = ' + json.dumps(HIST, ensure_ascii=False) + ';')

# ------------------------------------------------------------------ 1. cabecalho: contadores e botao de versao
troca('Alertas e falhas<span class="cnt" id="cntAl">0</span></button>', 'Alertas e falhas</button>')
troca('  <span id="pEstado" class="chip-h st-nd" aria-live="polite">—</span>\n',
      '  <button id="cntA" class="chip-h ct" type="button" title="Alertas ativos. Clique para ver só os alertas.">▲ Alertas <b>0</b></button>\n'
      '  <button id="cntF" class="chip-h ct" type="button" title="Falhas ativas. Clique para ver só as falhas.">■ Falhas <b>0</b></button>\n')
troca('  <span id="relogio"></span>\n  <button id="btnOpc"',
      '  <span id="relogio"></span>\n  <button id="btnVer" class="chip-h ver" type="button" aria-haspopup="dialog" aria-expanded="false" title="Versão do programa e histórico">v0.10</button>\n  <button id="btnOpc"')

# ------------------------------------------------------------------ 2. painel de opcoes: cadeia de comunicacao; dialogo de versao
troca('<div id="opc" class="opc" role="dialog" aria-label="Opções" hidden>\n',
      '<div id="opc" class="opc" role="dialog" aria-label="Opções" hidden>\n  <fieldset><legend>Comunicação</legend><ul class="cadeia" id="cadeia"></ul></fieldset>\n')
troca('<div id="aviso" role="alert"></div>', '''<div id="verFundo" class="fundo" hidden></div>
<div id="ver" class="dlg" role="dialog" aria-modal="true" aria-labelledby="verTit" hidden>
  <div class="dlg-cab"><h2 id="verTit">Versão do programa</h2>
    <button class="dlg-b" id="verExp" type="button" aria-label="Ampliar" title="Ampliar">⤢</button>
    <button class="dlg-b" id="verFec" type="button" aria-label="Fechar" title="Fechar">✕</button></div>
  <div class="dlg-corpo" id="verCorpo"></div>
  <div class="dlg-rod"><button class="btn" id="verOk" type="button">Fechar</button></div>
</div>
<div id="aviso" role="alert"></div>''')

# ------------------------------------------------------------------ 3. cadeia HTML -> Node-RED -> PLC
troca('  /* troca de fonte em funcionamento: zera o que veio da fonte anterior */',
      r'''  /* cadeia de comunicacao (cartao "Modo" do medidor): HTML -> Node-RED -> PLC. cada elo: ok / nao / na (nao usado) / espera */
  cadeia(){
    if (this.fonte==="sim") return [["HTML","ok","ativo"],["Node-RED","na","não usado (dados simulados)"],["PLC","na","não usado (dados simulados)"]];
    const nrOk = !!this.contrato && this.falhas<Cfg.falhasParaCair, nrNao = this.falhas>=Cfg.falhasParaCair;
    const nr = nrOk ? ["Node-RED","ok","conectado"] : nrNao ? ["Node-RED","nao","não conectado"] : ["Node-RED","espera","conectando…"];
    let plc;
    if (!nrOk) plc = ["PLC","espera","sem informação (Node-RED não respondeu)"];
    else if (!this.estado) plc = ["PLC","espera","aguardando a primeira leitura"];
    else if (this.semCom) plc = ["PLC","nao","não conectado"+(this.motivo?" ("+this.motivo+")":"")];
    else plc = ["PLC","ok","conectado"];
    return [["HTML","ok","ativo"], nr, plc];
  },
  /* troca de fonte em funcionamento: zera o que veio da fonte anterior */''')
troca('    av.innerHTML = "SEM COMUNICAÇÃO — valores apagados"+(Dados.semDesde?" desde "+hhmmss(Dados.semDesde):"")+"<small>"+esc(Dados.motivo||"")+"</small>";',
      '    av.innerHTML = "SEM COMUNICAÇÃO — valores apagados"+(Dados.semDesde?" desde "+hhmmss(Dados.semDesde):"")+"<small>"+esc(Dados.motivo||"")+"</small><small>"+Cab.cadeiaTxt()+"</small>";\n'
      '    $("#cadeia").innerHTML = Dados.cadeia().map(c=>`<li class="cd-${c[1]}"><span class="cd-pt" aria-hidden="true"></span><b>${esc(c[0])}</b><span class="mut">${esc(c[2])}</span></li>`).join("");')
troca('const Cab = {', '''const Cab = {
  /* texto curto da cadeia para a faixa de "sem comunicacao": HTML ✔ -> Node-RED ✔ -> PLC ✖ */
  cadeiaTxt(){ const s = {ok:"✔",nao:"✖",na:"–",espera:"…"}; return Dados.cadeia().map(c=>esc(c[0])+" "+s[c[1]]+" "+esc(c[2])).join("  →  "); },''')

# ------------------------------------------------------------------ 4. contadores (substituem o selo de estado e a bolinha da aba)
troca_entre('    // estado da maquina: um unico selo', '  }\n};', r'''    // contadores de alarmes (como no medidor): Alertas e Falhas; clique abre a tela de alertas ja filtrada
    const at = Alarmes.ativos(), nA = at.filter(d=>d.tipo==="A").length, nF = at.filter(d=>d.tipo==="F").length;
    [["#cntA", nA, "ct-a"], ["#cntF", nF, "ct-f"]].forEach(([id, n, cl])=>{ const b = $(id);
      b.className = "chip-h ct"+(!Dados.semCom && n ? " "+cl : ""); $("b", b).textContent = Dados.semCom ? "?" : n; });
''')
troca('  /* universo da lista atual, ANTES dos filtros', '''  /* abre a lista de ativos so com um tipo (usado pelos contadores do cabecalho) */
  soTipo(t){
    this.vista = "ativos"; $$("#alVista button").forEach(x=>x.setAttribute("aria-pressed", String(x.dataset.vista==="ativos")));
    this.tipos = {F:t==="F", A:t==="A", I:false}; $$("#alTipos button").forEach(b=>b.setAttribute("aria-pressed", String(this.tipos[b.dataset.tipo])));
    this.assin = ""; renderTudo();
  },
  /* universo da lista atual, ANTES dos filtros''')

# ------------------------------------------------------------------ 5. dialogo da versao + ligacoes
troca('function abrirInfo(chave,btn){', r'''/* dialogo "Versao do programa": historico resumido; ampliar, fechar, Esc, clique fora; foco preso no dialogo */
const Ver = {
  iniciar(){
    $("#btnVer").textContent = "v"+VERSAO;
    $("#verCorpo").innerHTML = `<p class="ver-atual">Versão em uso: <b>${esc(HIST_VERSOES.atual)}</b> · ${esc(HIST_VERSOES.data)}</p>`+
      HIST_VERSOES.versoes.map(v=>`<section class="ver-item"><h3>v${esc(v.v)} <span class="mut">· ${esc(v.data)}</span></h3><ul>${v.itens.map(i=>`<li>${esc(i)}</li>`).join("")}</ul></section>`).join("");
    const dlg = $("#ver"), fundo = $("#verFundo"), btn = $("#btnVer");
    const abrir = ()=>{ dlg.hidden = false; fundo.hidden = false; btn.setAttribute("aria-expanded","true"); $("#verOk").focus(); };
    const fechar = ()=>{ dlg.hidden = true; fundo.hidden = true; btn.setAttribute("aria-expanded","false"); btn.focus(); };
    btn.addEventListener("click", e=>{ e.stopPropagation(); abrir(); });
    ["verFec","verOk"].forEach(id=>$("#"+id).addEventListener("click", fechar));
    fundo.addEventListener("click", fechar);
    $("#verExp").addEventListener("click", ()=>dlg.classList.toggle("grande"));
    document.addEventListener("keydown", e=>{ if (e.key==="Escape" && !dlg.hidden) { e.stopPropagation(); fechar(); } }, true);
    dlg.addEventListener("keydown", e=>{ if (e.key!=="Tab") return; const f = $$("button", dlg), i = f.indexOf(document.activeElement);
      if (e.shiftKey && i<=0) { e.preventDefault(); f[f.length-1].focus(); } else if (!e.shiftKey && i===f.length-1) { e.preventDefault(); f[0].focus(); } });
  }
};
function abrirInfo(chave,btn){''')
troca('  Tema.iniciar(); Anim.iniciar(); Opc.iniciar();\n', '  Tema.iniciar(); Anim.iniciar(); Opc.iniciar(); Ver.iniciar();\n  ["cntA","cntF"].forEach(id=>$("#"+id).addEventListener("click", ()=>{ mostrar("al"); TelaAlertas.soTipo(id==="cntA" ? "A" : "F"); }));\n')
troca('window.Baggio = {Dados, Mapa, Alarmes, Overview, Anim, Opc, CAT_ALARMES, CONTRATO_EMB, VERSAO};', 'window.Baggio = {Dados, Mapa, Alarmes, Overview, Anim, Opc, Ver, CAT_ALARMES, CONTRATO_EMB, HIST_VERSOES, VERSAO};')

# ------------------------------------------------------------------ 6. CSS
troca('</style>', r'''
/* ============ v0.10 · contadores, versao, cadeia, dialogo ============ */
.chip-h.ct{width:112px;justify-content:center;cursor:pointer;background:rgba(255,255,255,.14);color:#fff}
.chip-h.ct b{margin-left:7px;min-width:12px;text-align:left;font-variant-numeric:tabular-nums}
.chip-h.ct-a{background:#ffe0a8;color:#6b3d00}
.chip-h.ct-f{background:var(--bad);color:#fff}
.chip-h.ver{background:transparent;color:rgba(255,255,255,.82);padding:4px 8px;font-weight:600}
.chip-h.ver:hover{background:rgba(255,255,255,.14);color:#fff}
.cadeia{list-style:none;margin:0;padding:0}
.cadeia li{display:flex;gap:8px;align-items:center;padding:3px 8px}
.cadeia .mut{font-size:12px}
.cd-pt{width:11px;height:11px;border-radius:50%;border:2px solid var(--off);flex:none}
.cd-ok .cd-pt{background:var(--run);border-color:var(--run)}
.cd-nao .cd-pt{background:var(--bad);border-color:var(--bad)}
.cd-na .cd-pt{border-style:dashed}
.cd-espera .cd-pt{border-color:var(--warn)}
#aviso small+small{opacity:.95}
.fundo{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:45}
.fundo[hidden],.dlg[hidden]{display:none}
.dlg{position:fixed;z-index:50;left:50%;top:50%;transform:translate(-50%,-50%);width:min(560px,94vw);max-height:84vh;display:flex;flex-direction:column;background:var(--panel);color:var(--ink);border-radius:10px;box-shadow:0 16px 48px rgba(0,0,0,.4)}
.dlg.grande{width:min(980px,96vw);max-height:94vh}
.dlg-cab{display:flex;align-items:center;gap:6px;padding:11px 14px 11px 18px;background:var(--head);color:#fff;border-radius:10px 10px 0 0}
.dlg-cab h2{flex:1;margin:0;font-size:14px;letter-spacing:.05em;text-transform:uppercase}
.dlg-b{border:0;background:rgba(255,255,255,.14);color:#fff;width:30px;height:28px;border-radius:6px;font-size:15px}
.dlg-b:hover{background:rgba(255,255,255,.28)}
.dlg-corpo{padding:10px 20px 14px;overflow:auto;flex:1}
.ver-atual{margin:4px 0 6px}
.ver-item h3{margin:16px 0 4px;font-size:14px}
.ver-item ul{margin:0;padding-left:20px}
.ver-item li{margin:3px 0}
.dlg-rod{padding:10px 16px;border-top:1px solid var(--line);text-align:center}
</style>''')

DEST.write_text(s, encoding="utf-8")
print("ok", DEST.relative_to(RAIZ), len(s)//1024, "KB")
