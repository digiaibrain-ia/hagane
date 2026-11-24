#!/usr/bin/env python3
"""Gera dashboard/src/baggio_monitor_v0.4.html a partir da v0.3 (arquivada).

v0.4:
  * NOME: o sistema e "Baggio - Sistema de filtragem"; "Hagane" e a FABRICA que o usa.
    Tudo que era hagane_* passa a baggio_* (rotas /baggio, chaves do navegador, arquivos).
  * FONTE DOS DADOS no cabecalho: CPU (Node-RED) ou SIMULACAO embutida no proprio HTML. A tela funciona
    sem Node-RED e sem PLC (abre ate com dois cliques no arquivo). Selo DEMO sempre visivel na simulacao.
  * NIVEL DOS TANQUES pelos sensores de nivel (I6.x), com movimento da agua: ondas na superficie e fluxo
    nos tubos das bombas. Botao "Animacao" liga/desliga (lembrado; comeca desligado se o sistema pede menos movimento).
  * TEXTOS: 6 colisoes medidas (tests/colisao_textos.js) corrigidas nos dois visuais.
Uso: python3 -B -I dashboard/gerador/gerar_monitor_v0.4.py   (aborta se o destino existir ou a v0.3 mudou)
"""
import importlib.util, json, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ORIG = RAIZ / "dashboard/arquivo/hagane_monitor_v0.3.html"
DEST = RAIZ / "dashboard/src/baggio_monitor_v0.4.html"
if DEST.exists() and "--forcar" not in sys.argv:
    sys.exit(f"ABORTA: {DEST.name} ja existe (versao nova, nunca sobrescrever)")
s = ORIG.read_text(encoding="utf-8")

def troca(velho, novo, n=1):
    global s
    if s.count(velho) != n:
        sys.exit(f"ABORTA: trecho da v0.3 mudou ({s.count(velho)}x): {velho[:80]!r}")
    s = s.replace(velho, novo)

def troca_entre(ini, fim, novo):
    global s
    a = s.find(ini); b = s.find(fim, a + 1)
    if a < 0 or b < 0:
        sys.exit(f"ABORTA: marcador nao encontrado: {ini[:50]!r} / {fim[:50]!r}")
    s = s[:a] + novo + s[b:]

# contrato monitorado (mesmo do fluxo) e nucleo do simulador, embutidos no HTML
spec = importlib.util.spec_from_file_location("gf", RAIZ / "nodered/gerador/gerar_fluxos_v0.4.py")
gf = importlib.util.module_from_spec(spec); _argv = sys.argv; sys.argv = ["x"]; spec.loader.exec_module(gf); sys.argv = _argv
CONTRATO = json.dumps(gf.contrato_monitorado(), ensure_ascii=False)
SIM = gf.nucleo_simulador()

# ---------- 0. renomeia o projeto: hagane -> baggio (a fabrica "Hagane" e reintroduzida abaixo, de proposito) ----------
s = s.replace("hagane", "baggio").replace("Hagane", "Baggio").replace("HAGANE", "BAGGIO")

# ---------- 1. versao / titulo ----------
troca('<meta name="app-version" content="0.3">', '<meta name="app-version" content="0.4">')
troca('  BAGGIO MONITOR v0.3  (SOMENTE LEITURA)', '  BAGGIO MONITOR v0.4  (SOMENTE LEITURA)')
troca('    v0.3  Dois visuais', '    v0.4  Nome Baggio (Hagane = fabrica); fonte CPU/Simulacao no proprio HTML; nivel dos tanques pelos sensores com\n'
      '          animacao da agua (liga/desliga); 6 colisoes de texto corrigidas.\n    v0.3  Dois visuais')
troca('const VERSAO = "0.3";', 'const VERSAO = "0.4";\n/* contrato monitorado embutido (para a SIMULACAO funcionar sem Node-RED) */\nconst CONTRATO_EMB = __CONTRATO__;\n/* simulador puro (o mesmo codigo do fluxo demo do Node-RED) */\n__SIM__')
troca('<title>Baggio — Sistema de Filtragem</title>', '<title>Baggio — Sistema de filtragem (Hagane)</title>')

# ---------- 2. cabecalho: marca/fabrica, fonte dos dados ----------
troca('<h1>Baggio<small id="site">Baggio, sistema de água</small></h1>',
      '<h1><span class="h-marca">Baggio</span><span class="h-fab">Hagane</span><small id="site">Sistema de filtragem, Hagane</small></h1>')
troca('  <div class="vis" role="group" aria-label="Visual da tela">',
      '  <div class="vis" id="fonteSel" role="group" aria-label="Fonte dos dados">\n'
      '    <button data-fonte="cpu" aria-pressed="false" title="Dados da CPU, lidos pelo Node-RED">CPU</button>\n'
      '    <button data-fonte="sim" aria-pressed="false" title="Simulação embutida: não precisa de Node-RED nem de PLC">Simulação</button>\n'
      '  </div>\n  <div class="vis" role="group" aria-label="Visual da tela">')
troca('BAGGIO - SISTEMA DE ÁGUA - OVERVIEW', 'BAGGIO - SISTEMA DE FILTRAGEM - OVERVIEW')
troca('aria-label="Overview do sistema de água (filtragem)"', 'aria-label="Overview do sistema de filtragem"')
troca('    <button class="info-btn info-flut"', '    <label class="anim-sw" title="Liga ou desliga o movimento da água (ondas e fluxo nos tubos)"><input type="checkbox" id="animChk"> Animação</label>\n    <button class="info-btn info-flut"')

# ---------- 3. dados: fonte CPU ou simulacao ----------
troca('''  async ler(){
    try {
      if (!this.contrato) await this.carregarContrato();
      const e = await this.buscar("/baggio/api/estado");''', '''  fonte: "cpu", simUltimo: null,
  /* SIMULACAO: gera o estado no proprio navegador (mesmo codigo do fluxo demo). Nada de rede. */
  lerSim(){
    if (!this.contrato) { this.contrato = CONTRATO_EMB; this.tagsPorEnd = {}; CONTRATO_EMB.tags.forEach(t=>this.tagsPorEnd[t.endereco]=t); }
    const B = simularBytes(CONTRATO_EMB, Date.now());
    if (B) { const bits = {}; CONTRATO_EMB.tags.forEach(t=>{ const v=B[t.byte]; if (typeof v==="number") bits[t.endereco]=((v>>t.nbit)&1)===1; }); this.simUltimo = {ts:Date.now(), bits}; }
    const u = this.simUltimo, idade = u ? Date.now()-u.ts : null, ok = !!u && idade <= Cfg.velhoMs;
    this.falhas = 0;
    this.estado = {versao:VERSAO, origem:"demo", agora:Date.now(), ts:u&&u.ts, idade_ms:idade, comunicacao: ok?"ok":"sem_comunicacao", motivo: ok?"":"simulador em silêncio (teste de queda)", bits: u?u.bits:{}};
    this.definirCom(!ok, ok ? "" : this.estado.motivo);
    if (ok) this.ultimoOk = Date.now();
  },
  /* troca de fonte em funcionamento: zera o que veio da fonte anterior */
  trocarFonte(f){
    this.fonte = f; this.contrato = null; this.estado = null; this.tagsPorEnd = {}; this.simUltimo = null;
    this.falhas = 0; this.semCom = true; this.motivo = "aguardando 1ª leitura"; this.semDesde = Date.now();
    Alarmes.defs = []; Alarmes.estado = {}; Alarmes.iniciado = false; TelaES.montadoAnalog = false;
    gravarStorage("baggio_fonte", f);
    $$("#fonteSel button").forEach(b=>b.setAttribute("aria-pressed", b.dataset.fonte===f));
    this.ler();
  },
  async ler(){
    if (this.fonte === "sim") { this.lerSim(); this.ouvintes.forEach(f=>{ try{ f(); }catch(e){ console.error(e); } }); return; }
    try {
      if (!this.contrato) await this.carregarContrato();
      const e = await this.buscar("/baggio/api/estado");''')

# ---------- 4. inicio: fonte, animacao ----------
troca('''  let base = qs.get("api") || "";
  if (!base && location.protocol==="file:") base = lerStorage("baggio_api") || "";
  if (!base && location.protocol==="file:") {''', '''  let base = qs.get("api") || "";
  if (!base && location.protocol==="file:") base = lerStorage("baggio_api") || "";
  // fonte: ?fonte= na URL > ultima escolha > (arquivo aberto direto = simulacao; servido pelo Node-RED = CPU)
  const fonte = qs.get("fonte") || lerStorage("baggio_fonte") || (location.protocol==="file:" ? "sim" : "cpu");
  Dados.fonte = fonte==="sim" ? "sim" : "cpu";
  $$("#fonteSel button").forEach(b=>{ b.setAttribute("aria-pressed", b.dataset.fonte===Dados.fonte); b.addEventListener("click",()=>Dados.trocarFonte(b.dataset.fonte)); });
  if (!base && location.protocol==="file:" && Dados.fonte==="cpu") {''')
troca('  Tema.iniciar();\n', '  Tema.iniciar(); Anim.iniciar();\n')
troca('  if (Dados.base || location.protocol!=="file:") Dados.iniciar();', '  if (Dados.base || location.protocol!=="file:" || Dados.fonte==="sim") Dados.iniciar();')
troca('window.Baggio = {Dados, Mapa, Alarmes, VERSAO};', 'window.Baggio = {Dados, Mapa, Alarmes, Overview, Anim, VERSAO};')
troca('/* visual: "mod" (moderno)', '''/* animacao da agua: ligada/desligada. Padrao: ligada, exceto se o sistema pede menos movimento. */
const Anim = {
  aplicar(on){ document.body.classList.toggle("anim", on); $("#animChk").checked = on; gravarStorage("baggio_anim", on?"1":"0"); },
  iniciar(){
    const salvo = lerStorage("baggio_anim");
    const reduz = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
    this.aplicar(salvo==null ? !reduz : salvo==="1");
    $("#animChk").addEventListener("change", e=>this.aplicar(e.target.checked));
  }
};
/* visual: "mod" (moderno)''')

# ---------- 5. mapa: lampadas do funil dentro da borda, para o rotulo ficar fora ----------
troca('{id:"transp",   nome:"Transportador do filtro (dragante)",x:168, y:127, eq:"dragante"}', '{id:"transp",   nome:"Transportador do filtro (dragante)",x:164, y:127, eq:"dragante"}')
troca('{id:"extrator", nome:"Extrator de lodo",                 x:198, y:162, eq:"extrator"}', '{id:"extrator", nome:"Extrator de lodo",                 x:164, y:162, eq:"extrator"}')

# ---------- 6. desenho: rotulos (colisoes medidas), liquidos, fluxo ----------
troca('[66,102,"VÁLVULA SOPRO"]', '[68,99,"VÁLVULA"],[68,111,"SOPRO"]')
troca('[155,131,"TRANSP. FILTRO","end"]', '[144,131,"TRANSP. FILTRO","end"]')
troca('[186,166,"EXTRATOR LODO","end"]', '[144,162,"EXTRATOR","end"],[144,174,"LODO","end"]')
troca('[180,229,"VÁLVULA"],[180,241,"QUEBRA VÁCUO"]', '[134,231,"VÁLVULA","end"],[134,243,"QUEBRA VÁCUO","end"]')
troca('[650,58,"ALIMENTAÇÃO"]', '[690,42,"ALIMENTAÇÃO","middle"]')
troca('  tubo(d,cls){ return `<path class="tb-o ${cls||""}" d="${d}"/><path class="tb-i ${cls||""}" d="${d}"/>`; },',
      '''  /* tubo: contorno + miolo; com "flux" ganha o traco de fluxo (so aparece com Animacao ligada e equipamento ativo) */
  tubo(d,cls,flux,rev){ return `<path class="tb-o ${cls||""}" d="${d}"/><path class="tb-i ${cls||""}" d="${d}"/>`+(flux?`<path class="tb-f${rev?" rev":""}" data-flux="${flux}" d="${d}"/>`:""); },
  /* superficie da agua: onda que se repete a cada "per"; o grupo anda 1 periodo em loop (CSS) */
  onda(x0,larg,per,amp,fundo){
    let d = `M${x0-per} 0`; const n = Math.ceil((larg+2*per)/per);
    d += ` Q${x0-per+per/4} ${-amp} ${x0-per+per/2} 0`; for (let i=1;i<n*2-0;i++) d += ` T${x0-per+per/2*(i+1)} 0`;
    return d + ` V${fundo} H${x0-per} Z`;
  },
  /* nivel (0..1) a partir dos sensores; sensor ativo = coberto (suposicao P-10, a validar) */
  nivelSujo(){ const b=a=>Dados.bit(a)===true; if (Dados.semCom) return null;
    return b("I6.0")?0.95 : b("I6.3")?0.72 : b("I6.2")?0.45 : b("I6.1")?0.18 : 0.05; },
  nivelLimpo(){ const b=a=>Dados.bit(a)===true; if (Dados.semCom) return null;
    return b("I6.4")?0.92 : b("I6.5")?0.55 : 0.08; },''')
troca('''        <linearGradient id="gMotor" x1="0" y1="0" x2="0" y2="1">''', '''        <clipPath id="cSujo"><polygon points="232,228 918,228 918,360 268,360"/></clipPath>
        <clipPath id="cLimpo"><rect x="312" y="73" width="216" height="154"/></clipPath>
        <linearGradient id="gMotor" x1="0" y1="0" x2="0" y2="1">''')
troca('''      <polygon class="liq" fill="#ecea00" points="248,287 918,287 918,360 268,360"/>''',
      '''      <g clip-path="url(#cSujo)"><g id="liqS" class="liqg"><g class="ondas"><path class="liq" d="${this.onda(232,690,46,3.2,200)}"/></g><g class="ondas ondas2"><path class="liq liq2" d="${this.onda(232,690,70,2.2,200)}"/></g></g></g>''')
troca('''      <rect class="eqp" x="312" y="73" width="216" height="154"/>''',
      '''      <rect class="eqp" x="312" y="73" width="216" height="154"/>
      <g clip-path="url(#cLimpo)"><g id="liqL" class="liqg"><g class="ondas ondasL"><path class="liqL" d="${this.onda(312,216,40,2.6,200)}"/></g></g></g>''')
troca('${this.tubo("M55 62 V198 Q55 213 70 213 H140","ar")}', '${this.tubo("M55 62 V198 Q55 213 70 213 H140","ar","ar")}')
troca('${this.tubo("M265 520 V216 Q265 208 273 208 H690")}', '${this.tubo("M265 520 V216 Q265 208 273 208 H690","","b1")}')
troca('${this.tubo("M275 530 H327 Q335 530 335 522 V390")}', '${this.tubo("M275 530 H327 Q335 530 335 522 V390","","b1",true)}')
troca('${this.tubo("M450 520 V208")}', '${this.tubo("M450 520 V208","","b2")}')
troca('${this.tubo("M363 390 V598 Q363 606 371 606 H463 Q471 606 471 598 V538 Q471 530 463 530 H444")}', '${this.tubo("M363 390 V598 Q363 606 371 606 H463 Q471 606 471 598 V538 Q471 530 463 530 H444","","b2")}')
troca('${this.tubo("M690 52 V260 Q690 268 698 268 H857 Q865 268 865 260 V240")}', '${this.tubo("M690 52 V260 Q690 268 698 268 H857 Q865 268 865 260 V240","","lav")}')

# ---------- 7. atualizar: nivel dos tanques e fluxo ----------
troca('''    $$("#svg [data-lp],#svg [data-vl]").forEach(g=>{''', '''    // nivel da agua pelos sensores (translateY do grupo; a transicao so existe com Animacao ligada)
    const aplicaNivel = (id, L, yBase, altura) => { const g = $(id); if (!g) return;
      if (L==null) { g.style.visibility = "hidden"; return; }
      g.style.visibility = "visible"; g.style.transform = `translateY(${(yBase - altura*L).toFixed(1)}px)`; };
    aplicaNivel("#liqS", this.nivelSujo(), 360, 132);
    aplicaNivel("#liqL", this.nivelLimpo(), 227, 154);
    // fluxo nos tubos: so onde o equipamento esta ativo
    const ativo = {b1:()=>this.estadoEq("bomba1").k==="run", b2:()=>this.estadoEq("bomba2").k==="run",
                   ar:()=>Dados.bit("Q14.3")===true, lav:()=>Dados.bit("Q15.6")===true};
    $$("#svg .tb-f").forEach(p=>p.classList.toggle("vivo", !Dados.semCom && !!(ativo[p.dataset.flux]&&ativo[p.dataset.flux]())));
    $$("#svg [data-lp],#svg [data-vl]").forEach(g=>{''')

# ---------- 8. ajuda ----------
troca('+"<li>Líquido amarelo e tubos são desenho fixo. Frequência das bombas ainda não é lida (P-03).</li></ul>"],',
      '+"<li><b>Nível dos tanques</b> vem dos sensores de nível (sensor ativo = coberto, a validar na máquina, P-10). Ondas e fluxo nos tubos são ilustrativos; o botão <b>Animação</b> liga e desliga.</li>"\n'
      '    +"<li><b>Fonte</b> (cabeçalho): <b>CPU</b> lê pelo Node-RED; <b>Simulação</b> roda dentro da página, sem Node-RED nem PLC, com selo DEMO.</li>"\n'
      '    +"<li>Frequência das bombas ainda não é lida (P-03).</li></ul>"],')

# ---------- 9. CSS ----------
troca('</style>', r'''
/* ============ v0.4 · marca/fabrica, animacao, liquidos ============ */
body.tema-mod .h-fab{display:none}
body.tema-ori .h-marca{display:none}
.anim-sw{position:absolute;top:6px;right:12px;z-index:2;display:inline-flex;align-items:center;gap:6px;font-weight:600;font-size:12.5px;color:#fff;cursor:pointer}
body.tema-mod .anim-sw{right:46px;top:9px;color:var(--ink)}
.anim-sw input{width:16px;height:16px;accent-color:var(--acento,#ec7000)}
.liqg{transition:none}
.liq{fill:#ecea00}                                  /* Original: amarelo do WinCC */
.liqL{fill:#7ec8e8;opacity:.8}
.liq2{opacity:.55;fill:#fff3a0}
body.tema-mod .liq2{fill:#ffe9a0}
body.tema-mod .liqL{fill:#6fb3dc;opacity:.85}
.tb-f{fill:none;stroke:#fff;stroke-opacity:.9;stroke-width:2.4;stroke-linecap:round;stroke-dasharray:1 13;display:none}
body.anim .tb-f.vivo{display:inline}
body.anim .tb-f.vivo{animation:fluxo .9s linear infinite}
body.anim .tb-f.vivo.rev{animation-direction:reverse}
@keyframes fluxo{to{stroke-dashoffset:-14}}
body.anim .liqg{transition:transform 1.8s ease-in-out}
body.anim .ondas{animation:onda 5s linear infinite}
body.anim .ondas2{animation-duration:8s;animation-direction:reverse}
@keyframes onda{to{transform:translateX(-46px)}}
body.anim .ondas2{animation-name:onda2}
@keyframes onda2{to{transform:translateX(-70px)}}
body.anim .ondasL{animation-name:ondaL;animation-duration:4s}
@keyframes ondaL{to{transform:translateX(-40px)}}
@media (max-width:900px){ .anim-sw{top:6px} }
@media (prefers-color-scheme:dark){ body.tema-mod .anim-sw{color:var(--ink)} body.tema-mod .liqL{fill:#4f9ccf} }
</style>''')

s = s.replace("__CONTRATO__", CONTRATO).replace("__SIM__", SIM)
DEST.write_text(s, encoding="utf-8")
print("ok", DEST.relative_to(RAIZ), len(s)//1024, "KB")
