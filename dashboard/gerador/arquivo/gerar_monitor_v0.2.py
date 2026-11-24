#!/usr/bin/env python3
"""Gera dashboard/src/hagane_monitor_v0.2.html a partir da v0.1.

Mudanca da v0.2: Overview redesenhado FIEL a tela "BAGGIO - SISTEMA DE AGUA - OVERVIEW"
do WinCC (mesma disposicao de tanques, filtro, tubos, bombas, lampadas e painel lateral).
Lampadas dinamicas; clique numa lampada mostra nome, estado e endereco (ajuda no teste com PLCSIM).
Alertas e E/S nao mudam.
Uso: python3 -I dashboard/gerador/gerar_monitor_v0.2.py   (aborta se o destino existir ou se a v0.1 mudou)
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ORIG = RAIZ / "dashboard/arquivo/hagane_monitor_v0.1.html"   # base: versao anterior (arquivada)
DEST = RAIZ / "dashboard/arquivo/hagane_monitor_v0.2.html"
if DEST.exists() and "--forcar" not in sys.argv:
    sys.exit(f"ABORTA: {DEST.name} ja existe (versao nova, nunca sobrescrever)")
s = ORIG.read_text(encoding="utf-8")

def troca(velho, novo, n=1):
    global s
    if s.count(velho) != n:
        sys.exit(f"ABORTA: trecho da v0.1 mudou ({s.count(velho)}x): {velho[:70]!r}")
    s = s.replace(velho, novo)

def troca_entre(ini, fim, novo):
    global s
    a = s.find(ini); b = s.find(fim, a + 1)
    if a < 0 or b < 0:
        sys.exit(f"ABORTA: marcador nao encontrado: {ini[:50]!r} / {fim[:50]!r}")
    s = s[:a] + novo + s[b:]

# ---------- cabecalho / versao ----------
troca('<meta name="app-version" content="0.1">', '<meta name="app-version" content="0.2">')
troca('  HAGANE MONITOR v0.1  (SOMENTE LEITURA)', '  HAGANE MONITOR v0.2  (SOMENTE LEITURA)')
troca('    v0.1  Primeira versao: Overview, Alertas e falhas, Entradas e saidas.',
      '    v0.2  Overview fiel a tela do WinCC (Baggio - Sistema de agua); clique na lampada = detalhe.\n'
      '    v0.1  Primeira versao: Overview, Alertas e falhas, Entradas e saidas.')
troca('const VERSAO = "0.1";', 'const VERSAO = "0.2";')

# ---------- CSS da tela fiel ----------
troca('/* ---- alertas ---- */', '''/* ---- overview fiel ao WinCC (v0.2) ---- */
.tela{background:#d5d9dc;border:1px solid #9aa3a8}
.tela-tit{background:#0d4a5e;color:#fff;font:700 15px Tahoma,Arial,sans-serif;padding:6px 14px;display:flex;align-items:center;gap:10px;letter-spacing:.02em}
.tela-tit .info-btn{background:transparent;color:#fff;border-color:#fff}
.tela .svgwrap{border:0;border-radius:0;background:transparent}
#svg text{font-family:Tahoma,Arial,sans-serif}
.rt{font-size:10px;font-weight:700;fill:#1b2a33}
.rt2{font-size:12px;fill:#1b2a33}
.rt3{font-size:13.5px;fill:#1b2a33}
.seta{font-size:14px;fill:#1b2a33}
.eqp{fill:#cfd3d6;stroke:#6f7a80;stroke-width:1.5}
.eqp2{fill:#b3b9bd;stroke:#6f7a80;stroke-width:1.5}
.pnl{fill:#c3c8cc;stroke:#9aa3a8}
.tb-o{fill:none;stroke:#2b9a43;stroke-width:9;stroke-linejoin:round;stroke-linecap:round}
.tb-i{fill:none;stroke:#7be884;stroke-width:5;stroke-linejoin:round;stroke-linecap:round}
.tb-o.ar{stroke:#2c5cb5}.tb-i.ar{stroke:#7aa6f2}
.tb-ponta{fill:#7be884;stroke:#2b9a43;stroke-width:2.5}
.lp{cursor:pointer}
.lp circle{fill:url(#gOff);stroke:#59646a;stroke-width:1}
.lp.on circle{fill:url(#gOn);stroke:#0f6a2c}
.lp.fail circle{fill:url(#gFail);stroke:#7d120c}
.lp.nd circle{fill:#e4e7e9;stroke-dasharray:2 2}
.lpx{font:700 11px Arial,sans-serif;fill:#fff;pointer-events:none}
.lp.nd .lpx{fill:#59646a}
.vl{cursor:pointer}
.vl path{fill:#eef0f1;stroke:#59646a;stroke-width:1.3}
.vl.on path{fill:#35c75a;stroke:#0f6a2c}
.vl.nd path{stroke-dasharray:2 2}
.hz{fill:#fff;stroke:#8d969c}
.hzt{font-size:12px;fill:#1b2a33}
@media (max-width:900px){ #svg{min-width:900px} }

/* ---- alertas ---- */''')
troca('#svg{display:block;width:100%;height:auto;min-width:760px;max-height:calc(100vh - 205px);margin:0 auto}',
      '#svg{display:block;width:100%;height:auto;max-height:calc(100vh - 202px);margin:0 auto}')

# ---------- HTML da secao Overview ----------
troca_entre('<section class="vista ativa" id="v-ov"', '<!-- ================= ALERTAS', '''<section class="vista ativa" id="v-ov" aria-labelledby="aba-ov">
  <div class="tela dados">
    <div class="tela-tit">BAGGIO - SISTEMA DE ÁGUA - OVERVIEW <button class="info-btn" data-info="ov" aria-label="Sobre esta tela">i</button></div>
    <div class="svgwrap"><svg id="svg" viewBox="0 20 1185 625" role="img" aria-label="Overview do sistema de água (filtragem)"></svg></div>
  </div>
</section>

''')

# ---------- Mapa: painel lateral e lampadas do overview ----------
troca_entre('  /* painel lateral:', '  faixa:{', '''  /* Overview fiel ao WinCC: posicao (x,y) em coordenadas do desenho; bit = endereco, eq = equipamento */
  ov:{
    lampadas:[
      {id:"ar",       nome:"Ar comprimido",                    x:57,  y:45,  bit:"Q14.0"},
      {id:"rotovac",  nome:"Rotovac",                          x:198, y:92,  eq:"rotovac"},
      {id:"transp",   nome:"Transportador do filtro (dragante)",x:168, y:127, eq:"dragante"},
      {id:"aspirador",nome:"Aspirador",                        x:230, y:128, eq:"aspirador"},
      {id:"extrator", nome:"Extrator de lodo",                 x:198, y:162, eq:"extrator"},
      {id:"qv",       nome:"Válvula quebra vácuo aberta",      x:165, y:232, bit:"Q14.1"},
      {id:"banda",    nome:"Rotação da banda filtrante",       x:200, y:340, bit:"Q15.3"},
      {id:"lAlto",    nome:"Tanque limpo - nível alto",        x:325, y:130, bit:"Q14.4"},
      {id:"lMin",     nome:"Tanque limpo - nível mínimo",      x:325, y:186, bit:"Q14.5"},
      {id:"comp",     nome:"Válvula de compensação aberta",    x:492, y:155, bit:"Q14.2"},
      {id:"sMax",     nome:"Nível máximo tanque sujo",         x:483, y:256, bit:"I6.0"},
      {id:"sFim",     nome:"Nível fim de enchimento",          x:483, y:282, bit:"I6.3"},
      {id:"sIni",     nome:"Nível início de enchimento",       x:483, y:310, bit:"I6.2"},
      {id:"sMin",     nome:"Nível mínimo tanque sujo",         x:483, y:337, bit:"I6.1"},
      {id:"papel",    nome:"Rolo de papel (controle de papel)",x:863, y:160, bit:"Q15.2"},
      {id:"b1",       nome:"Bomba 1 de filtragem",             x:158, y:505, eq:"bomba1"},
      {id:"b2",       nome:"Bomba 2 de filtragem",             x:559, y:505, eq:"bomba2"}
    ],
    painel:[   /* dois grupos, como no WinCC */
      [["Filtro Automático","Q12.1"],["Filtro Manual","Q12.0"],["Ciclo Automático Ligado","Q12.2"],["Ciclo Automático Desligado","Q12.6"]],
      [["Auto Limpeza","Q12.4"],["Auto Limpeza Contínua","Q12.5"],["Ciclo Final de Semana","Q12.3"],["Vácuo no Filtro","Q15.4"]]
    ],
    valvulas:[
      {id:"vSopro", nome:"Válvula sopro",          x:55,  y:95,  vert:true,  bit:"Q14.3"},
      {id:"vQv",    nome:"Válvula quebra vácuo",   x:231, y:262, vert:true,  bit:"Q14.1"},
      {id:"vComp",  nome:"Válvula de compensação", x:469, y:155, vert:true,  bit:"Q14.2"},
      {id:"vLav",   nome:"Válvula de lavagem",     x:828, y:268, vert:false, bit:"Q15.6"}
    ]
  },
''')
troca('    this.modos.forEach(m=>s.add(m[1]));',
      '    this.ov.lampadas.forEach(l=>l.bit&&s.add(l.bit)); this.ov.valvulas.forEach(v=>s.add(v.bit));\n'
      '    this.ov.painel.flat().forEach(p=>s.add(p[1]));')
troca('    Object.values(this.valvulas).forEach(v=>s.add(v.end));\n    this.nivSujo.concat(this.nivLimpo).forEach(n=>s.add(n[1]));\n', '')

# ---------- Overview (JS) ----------
troca_entre('const Overview = {', '/* ============================================================\n   6. ALERTAS', r'''const Overview = {
  montado:false,
  /* estado de um equipamento: run / stop / fail / nd (sem dado) */
  estadoEq(id){
    const e = Mapa.eq[id];
    if (Dados.semCom) return {k:"nd", t:"SEM DADO"};
    const run = Dados.bit(e.run), disj = e.disj?Dados.bit(e.disj):true;
    const falhas = (e.falha||[]).filter(a=>Dados.bit(a)===true);
    if (falhas.length) { const tg = Dados.tag(falhas[0]); return {k:"fail", t:"FALHA", d: tg ? tg.comentario||tg.nome : falhas[0], end:falhas[0]}; }
    if (disj===false) return {k:"fail", t:"FALHA", d:"Disjuntor não OK", end:e.disj};
    if (run===undefined) return {k:"nd", t:"SEM DADO"};
    return run ? {k:"run", t:"EM OPERAÇÃO"} : {k:"stop", t:"PARADO"};
  },
  /* estado de uma lampada do desenho -> classe on / off / fail / nd + texto */
  estadoLampada(l){
    if (Dados.semCom) return {c:"nd", t:"sem dado", end:l.bit||Mapa.eq[l.eq].run};
    if (l.eq) {
      const r = this.estadoEq(l.eq), e = Mapa.eq[l.eq];
      return {c:{run:"on",stop:"off",fail:"fail",nd:"nd"}[r.k], t:r.t+(r.d?": "+r.d:""),
              end:"retorno "+e.run+(r.end?" · falha "+r.end:"")};
    }
    const v = Dados.bit(l.bit);
    return {c: v===undefined?"nd": v?"on":"off", t: v===undefined?"sem dado": v?"ATIVO (1)":"inativo (0)", end:l.bit};
  },
  lampada(id,x,y){ return `<g class="lp nd" data-lp="${id}" transform="translate(${x},${y})"><title></title><circle r="8"/><text class="lpx" y="4" text-anchor="middle"></text></g>`; },
  valvula(v){
    const d = v.vert ? "M-7 -9 L7 -9 L-7 9 L7 9 Z" : "M-9 -7 L-9 7 L9 -7 L9 7 Z";
    return `<g class="vl nd" data-vl="${v.id}" transform="translate(${v.x},${v.y})"><title></title><path d="${d}"/></g>`;
  },
  tubo(d,cls){ return `<path class="tb-o ${cls||""}" d="${d}"/><path class="tb-i ${cls||""}" d="${d}"/>`; },
  texto(x,y,t,cls,ancora){ return `<text class="${cls||"rt"}" x="${x}" y="${y}"${ancora?` text-anchor="${ancora}"`:""}>${esc(t)}</text>`; },
  /* bomba centrifuga desenhada como no WinCC: motor com aletas + voluta a direita */
  bomba(x,y){
    return `<g transform="translate(${x},${y})">
      <rect x="-34" y="-10" width="40" height="20" rx="4" fill="url(#gMotor)" stroke="#6f7a80"/>
      ${[-27,-20,-13,-6].map(a=>`<line x1="${a}" y1="-9" x2="${a}" y2="9" stroke="#8d969c" stroke-width="1"/>`).join("")}
      <rect x="4" y="-6" width="5" height="12" fill="#9aa3a8" stroke="#6f7a80"/>
      <circle cx="20" cy="0" r="12" fill="url(#gMotor)" stroke="#6f7a80"/><circle cx="20" cy="0" r="4" fill="#8d969c"/>
      <rect x="-30" y="10" width="56" height="4" fill="#8d969c"/></g>`;
  },
  /* valvula de retencao / instrumento (decorativo, como no WinCC) */
  retencao(x,y){ return `<g transform="translate(${x},${y})"><rect x="-5" y="-9" width="10" height="18" fill="#c3c8cc" stroke="#59646a"/><rect x="8" y="-6" width="3" height="18" fill="#e0731b"/></g>`; },
  montar(){
    const O = Mapa.ov;
    const setas = [[218,195,"↓"],[218,380,"↓"],[277,255,"↑"],[676,92,"↑"],[676,182,"↑"],[676,258,"↑"],[733,128,"↓"],[733,212,"↓"],
                   [254,478,"↑"],[326,473,"↓"],[374,473,"↓"],[436,478,"↑"],[600,192,"⇢"],[790,262,"⇢"]];
    const rot = [[73,43,"AR"],[73,55,"COMPRIMIDO"],[66,102,"VÁLVULA SOPRO"],[212,97,"ROTOVAC"],[155,131,"TRANSP. FILTRO","end"],
                 [241,132,"ASPIRADOR"],[186,166,"EXTRATOR LODO","end"],[180,229,"VÁLVULA"],[180,241,"QUEBRA VÁCUO"],
                 [100,338,"ROTAÇÃO BANDA"],[100,350,"FILTRANTE"],[338,134,"NÍVEL ALTO"],[338,190,"NÍVEL MÍNIMO"],
                 [506,152,"VÁLVULA DE"],[506,164,"COMPENSAÇÃO"],[650,58,"ALIMENTAÇÃO"],[722,96,"RETORNO"],[838,103,"ROLO DE PAPEL"],
                 [806,290,"VÁLVULA DE"],[806,302,"LAVAGEM"],[176,505,"BOMBA 1"],[176,517,"DE FILTRAGEM"],[469,505,"BOMBA 2"],[469,517,"DE FILTRAGEM"]];
    const niveis = [[500,260,"Nível Máximo Tanque Sujo"],[500,286,"Nível Fim de Enchimento"],[500,314,"Nível Início de Enchimento"],[500,341,"Nível Mínimo Tanque Sujo"]];
    const yPainel = [[47,74,101,128],[187,214,241,268]];
    let painel = "";
    O.painel.forEach((g,gi)=>g.forEach((p,i)=>{ painel += this.lampada("p"+gi+i, 976, yPainel[gi][i]) + this.texto(992, yPainel[gi][i]+4, p[0], "rt2"); }));
    $("#svg").innerHTML = `
      <defs>
        <pattern id="pts" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="0.9" fill="#8e979d"/></pattern>
        <radialGradient id="gOn" cx="35%" cy="35%" r="70%"><stop offset="0" stop-color="#c8f7d1"/><stop offset=".45" stop-color="#35c75a"/><stop offset="1" stop-color="#0f6a2c"/></radialGradient>
        <radialGradient id="gOff" cx="35%" cy="35%" r="70%"><stop offset="0" stop-color="#f4f5f6"/><stop offset=".5" stop-color="#b8bfc4"/><stop offset="1" stop-color="#6f7a80"/></radialGradient>
        <radialGradient id="gFail" cx="35%" cy="35%" r="70%"><stop offset="0" stop-color="#ffd0cb"/><stop offset=".45" stop-color="#e0352b"/><stop offset="1" stop-color="#7d120c"/></radialGradient>
        <linearGradient id="gMotor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f5f6"/><stop offset=".5" stop-color="#c3c8cc"/><stop offset="1" stop-color="#8a9298"/></linearGradient>
      </defs>
      <rect x="0" y="20" width="1185" height="625" fill="#d5d9dc"/><rect x="0" y="20" width="1185" height="625" fill="url(#pts)"/>
      <rect x="105" y="416" width="447" height="220" fill="none" stroke="#e3cf00" stroke-width="1.5" stroke-dasharray="3 3"/>
      <!-- tanque sujo e liquido (amarelo fixo, como no WinCC) -->
      <polygon class="eqp" points="232,228 918,228 918,360 268,360"/>
      <polygon fill="#ecea00" points="248,287 918,287 918,360 268,360"/>
      <!-- filtro (funil) e bloco da valvula quebra vacuo -->
      <polygon class="eqp" points="150,95 195,95 268,360 245,360 180,276 140,276 140,200 150,200"/>
      <rect class="eqp2" x="140" y="200" width="40" height="76"/>
      <!-- tanque limpo, rolo de papel, caixa de saida -->
      <rect class="eqp" x="312" y="73" width="216" height="154"/>
      <rect class="eqp" x="841" y="115" width="45" height="112"/>
      <rect class="eqp2" x="300" y="360" width="76" height="30"/>
      <!-- tubulacao -->
      ${this.tubo("M55 62 V198 Q55 213 70 213 H140","ar")}
      ${this.tubo("M248 172 H239 Q231 172 231 180 V412 Q231 420 239 420 H313 V390")}
      ${this.tubo("M265 520 V216 Q265 208 273 208 H690")}
      ${this.tubo("M275 530 H327 Q335 530 335 522 V390")}
      ${this.tubo("M450 520 V208")}
      ${this.tubo("M363 390 V598 Q363 606 371 606 H463 Q471 606 471 598 V538 Q471 530 463 530 H444")}
      ${this.tubo("M469 118 V208")}
      ${this.tubo("M690 52 V260 Q690 268 698 268 H857 Q865 268 865 260 V240")}
      ${this.tubo("M745 105 V228")}
      <circle class="tb-ponta" cx="469" cy="118" r="7"/><circle class="tb-ponta" cx="865" cy="240" r="7"/>
      ${this.retencao(265,467)}${this.retencao(450,467)}${this.retencao(745,140)}
      ${this.bomba(241,530)}${this.bomba(424,530)}
      <rect class="hz" x="209" y="553" width="68" height="22" rx="3"/><text class="hzt" x="243" y="568" text-anchor="middle"><title>Frequência não lida na v0.1/v0.2 (pendência P-03)</title>-- Hz</text>
      <rect class="hz" x="391" y="553" width="68" height="22" rx="3"/><text class="hzt" x="425" y="568" text-anchor="middle"><title>Frequência não lida na v0.1/v0.2 (pendência P-03)</title>-- Hz</text>
      ${O.valvulas.map(v=>this.valvula(v)).join("")}
      ${setas.map(a=>`<text class="seta" x="${a[0]}" y="${a[1]}">${a[2]}</text>`).join("")}
      ${rot.map(r=>this.texto(r[0],r[1],r[2],"rt",r[3])).join("")}
      <text class="rt3" x="348" y="101">TANQUE LIMPO</text>
      ${niveis.map(n=>this.texto(n[0],n[1],n[2],"rt2")).join("")}
      <rect class="pnl" x="958" y="30" width="213" height="117" rx="2"/>
      <rect class="pnl" x="958" y="170" width="213" height="117" rx="2"/>
      ${painel}
      ${O.lampadas.map(l=>this.lampada(l.id,l.x,l.y)).join("")}`;
    // clique/toque numa lampada ou valvula: mostra nome, estado e endereco (ajuda no teste)
    $("#svg").addEventListener("click", e=>{
      const g = e.target.closest("[data-lp],[data-vl]"); if (!g) return;
      e.stopPropagation();
      const d = this.detalhe(g);
      abrirPop(d.nome, `<p><b>${esc(d.t)}</b></p><p class="rot">Endereço: ${esc(d.end)}</p>`, g.getBoundingClientRect());
    });
    this.montado = true;
  },
  /* acha a definicao de uma lampada/valvula pelo elemento do desenho */
  defDe(g){
    if (g.dataset.vl) { const v = Mapa.ov.valvulas.find(x=>x.id===g.dataset.vl); return {nome:v.nome, bit:v.bit}; }
    const id = g.dataset.lp;
    if (id[0]==="p" && /^p\d\d$/.test(id)) { const p = Mapa.ov.painel[+id[1]][+id[2]]; return {nome:p[0], bit:p[1]}; }
    return Mapa.ov.lampadas.find(x=>x.id===id);
  },
  detalhe(g){
    const l = this.defDe(g), r = this.estadoLampada(l);
    const t = g.dataset.vl ? (r.c==="on"?"ABERTA (1)": r.c==="off"?"fechada (0)": r.t) : r.t;
    return {nome:l.nome, t:t, end:r.end, c:r.c};
  },
  atualizar(){
    if (!Dados.contrato) return;
    if (!this.montado) this.montar();
    $$("#svg [data-lp],#svg [data-vl]").forEach(g=>{
      const d = this.detalhe(g);
      g.setAttribute("class", (g.dataset.vl?"vl ":"lp ")+d.c);
      g.querySelector("title").textContent = d.nome+" — "+d.t+" ["+d.end+"]";
      const x = g.querySelector(".lpx"); if (x) x.textContent = d.c==="fail"?"!": d.c==="nd"?"?":"";
    });
  }
};

''')

# ---------- popover generico (usado pelo ⓘ e pelas lampadas) ----------
troca('''function abrirInfo(chave,btn){
  fecharInfo();
  const t = Textos[chave]; const p = document.createElement("div");
  p.className="pop"; p.id="pop"; p.setAttribute("role","dialog"); p.setAttribute("aria-label",t[0]);
  p.innerHTML = `<button class="fechar" aria-label="Fechar">✕</button><h3>${esc(t[0])}</h3>${t[1]}`;
  document.body.appendChild(p);
  const r = btn.getBoundingClientRect();''', '''function abrirInfo(chave,btn){ const t = Textos[chave]; abrirPop(t[0], t[1], btn.getBoundingClientRect()); }
function abrirPop(titulo, html, r){
  fecharInfo();
  const p = document.createElement("div");
  p.className="pop"; p.id="pop"; p.setAttribute("role","dialog"); p.setAttribute("aria-label",titulo);
  p.innerHTML = `<button class="fechar" aria-label="Fechar">✕</button><h3>${esc(titulo)}</h3>${html}`;
  document.body.appendChild(p);''')

troca(s[s.index('  ov:["Overview"'):s.index('"],\n', s.index('  ov:["Overview"'))+3],
      '  ov:["Overview","<p>Mesma disposição da tela do WinCC. <b>Somente leitura</b>: nada aqui envia comando.</p><ul>'
      '<li>Lâmpada <b>verde</b> = ativo/em operação; <b>cinza</b> = inativo/parado; <b>vermelha com !</b> = falha (alarme ou disjuntor do equipamento); <b>tracejada com ?</b> = sem dado.</li>'
      '<li><b>Toque/clique numa lâmpada ou válvula</b> para ver o estado e o endereço no PLC (útil no teste com PLCSIM).</li>'
      '<li>Líquido amarelo e tubos são desenho fixo, como no WinCC. Frequência das bombas ainda não é lida (P-03).</li></ul>"],\n')

DEST.write_text(s, encoding="utf-8")
print("ok", DEST.relative_to(RAIZ), len(s)//1024, "KB")
