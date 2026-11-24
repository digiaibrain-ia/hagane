#!/usr/bin/env python3
"""Gera dashboard/src/baggio_monitor_v0.6.html a partir da v0.5 (arquivada).

v0.6:
  * "Hagane" some da tela (cabecalho e titulo).
  * Origem dos dados com nome claro: "Dados: PLC | Simulados" (antes "CPU | Simulacao"); selo "PLC real".
  * TUBULACAO conferida com o WinCC: o tubo que desce ao lado do filtro sai da PAREDE DO TANQUE LIMPO (na v0.5 eu
    o tinha ligado ao funil, errado). VALVULA QUEBRA VACUO: rotulo, lampada e valvula juntos na caixa (como no WinCC),
    com atuador desenhado na valvula.
  * ALERTAS E FALHAS no padrao do medidor, adaptado ao Baggio e alimentado pelos blocos do PLC
    (FC_ALARME_CRITICO / FC_ALARME_PERMISSIVEL): codigo T-AAA-NNN, efeito -> causa (teste rapido) -> solucao (onde),
    "como o PLC decide" (gatilho, atraso, retencao, enderecos ao vivo), historico persistente, Exportar.
    Catalogo: docs/contratos/alarmes_v0.1.json (gerado por plc/variaveis/gerar_alarmes_v0.1.py).
  * Alarmes deduzidos de entradas foram REMOVIDOS: o PLC e a unica fonte (a leitura "I1.3 = 1 e falha" estava errada).
Uso: python3 -B -I dashboard/gerador/gerar_monitor_v0.6.py   (aborta se o destino existir ou se a v0.5 mudou)
"""
import json, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ORIG = RAIZ / "dashboard/arquivo/baggio_monitor_v0.5.html"
DEST = RAIZ / "dashboard/src/baggio_monitor_v0.6.html"
if DEST.exists() and "--forcar" not in sys.argv:
    sys.exit(f"ABORTA: {DEST.name} ja existe (versao nova, nunca sobrescrever)")
s = ORIG.read_text(encoding="utf-8")
CAT = (RAIZ / "docs/contratos/alarmes_v0.1.json").read_text(encoding="utf-8")
json.loads(CAT)   # valida

def troca(velho, novo, n=1):
    global s
    if s.count(velho) != n:
        sys.exit(f"ABORTA: trecho da v0.5 mudou ({s.count(velho)}x): {velho[:80]!r}")
    s = s.replace(velho, novo)

def troca_entre(ini, fim, novo):
    global s
    a = s.find(ini); b = s.find(fim, a + 1)
    if a < 0 or b < 0:
        sys.exit(f"ABORTA: marcador nao encontrado: {ini[:60]!r} / {fim[:60]!r}")
    s = s[:a] + novo + s[b:]

# ------------------------------------------------------------ 1. versao, titulo, cabecalho
troca('<meta name="app-version" content="0.5">', '<meta name="app-version" content="0.6">')
troca('  BAGGIO MONITOR v0.5  (SOMENTE LEITURA)', '  BAGGIO MONITOR v0.6  (SOMENTE LEITURA)')
troca('    v0.5  Sem deslocamento', '    v0.6  Sem "Hagane" na tela; Dados: PLC | Simulados; tubo ligado ao tanque limpo; valvula quebra vacuo; Alertas e falhas\n          no padrao do medidor (codigo, efeito, causa, solucao, como o PLC decide) a partir dos blocos do PLC.\n    v0.5  Sem deslocamento')
troca('const VERSAO = "0.5";', 'const VERSAO = "0.6";')
troca('<title>Baggio — Sistema de filtragem (Hagane)</title>', '<title>Baggio — Sistema de filtragem</title>')
troca('<h1><span class="h-marca">Baggio</span><span class="h-fab">Hagane</span><small id="site">Sistema de filtragem, Hagane</small></h1>',
      '<h1><span class="h-marca">Baggio</span><small id="site">Sistema de filtragem</small></h1>')
troca('''  <div class="vis" id="fonteSel" role="group" aria-label="Fonte dos dados">
    <button data-fonte="cpu" aria-pressed="false" title="Dados da CPU, lidos pelo Node-RED">CPU</button>
    <button data-fonte="sim" aria-pressed="false" title="Simulação embutida: não precisa de Node-RED nem de PLC">Simulação</button>
  </div>''', '''  <span class="vis-rot">Dados:</span>
  <div class="vis" id="fonteSel" role="group" aria-label="Origem dos dados">
    <button data-fonte="cpu" aria-pressed="false" title="Mostra os dados reais do PLC, lidos pelo Node-RED">PLC</button>
    <button data-fonte="sim" aria-pressed="false" title="Mostra dados de teste gerados na própria página. Não precisa de PLC nem de Node-RED.">Simulados</button>
  </div>''')
troca('"CPU REAL"', '"PLC real"')
troca('<li><b>Fonte</b> (cabeçalho): <b>CPU</b> lê pelo Node-RED; <b>Simulação</b> roda dentro da página, sem Node-RED nem PLC, com selo DEMO.</li>',
      '<li><b>Dados</b> (cabeçalho): <b>PLC</b> mostra os dados reais, lidos pelo Node-RED; <b>Simulados</b> mostra dados de teste gerados na própria página, sem PLC nem Node-RED, com selo DEMO.</li>')

# ------------------------------------------------------------ 2. desenho: tubulacao e valvula quebra vacuo
troca('M214 172 H223 Q231 172 231 180 V412 Q231 420 239 420 H313 V390', 'M312 172 H239 Q231 172 231 180 V412 Q231 420 239 420 H313 V390')
troca('M55 62 V198 Q55 213 70 213 H140', 'M55 62 V198 Q55 213 70 213 H132')
troca('<rect class="eqp2" x="140" y="200" width="40" height="76"/>', '<rect class="eqp2" x="132" y="200" width="94" height="76"/>')
troca('[134,231,"VÁLVULA","end"],[134,243,"QUEBRA VÁCUO","end"]', '[222,234,"VÁLVULA","end"],[222,246,"QUEBRA VÁCUO","end"]')
troca('{id:"qv",       nome:"Válvula quebra vácuo aberta",      x:165, y:232, bit:"Q14.1"}', '{id:"qv",       nome:"Válvula quebra vácuo aberta",      x:150, y:263, bit:"Q14.1"}')
troca('''    return `<g class="vl nd" data-vl="${v.id}" transform="translate(${v.x},${v.y})"><title></title><path d="${d}"/></g>`;''',
      '''    return `<g class="vl nd" data-vl="${v.id}" transform="translate(${v.x},${v.y})"><title></title><path d="${d}"/><rect class="vl-at" x="-3" y="${v.vert?-17:-16}" width="6" height="8"/></g>`;''')
# funil: a borda inferior-esquerda coincide com a caixa alargada (sem linha escondida atras dela)
troca('points="150,95 195,95 268,360 245,360 180,276 140,276 140,200 150,200"', 'points="150,95 195,95 268,360 245,360 180,276 132,276 132,200 150,200"')
# falhas das bombas: so o que o PLC informa (I1.3/I1.7 nao sao "falha = 1": ver P-14)
troca('falha:["M10.1","M10.5","M12.2","M122.2","M61.0","I1.3"]', 'falha:["M10.1","M10.5","M12.2","M122.2","M61.0"]')
troca('"M61.1","I1.7"]', '"M61.1"]')

# ------------------------------------------------------------ 3. mapa: fim dos alarmes deduzidos
troca_entre('  /* alarmes derivados de entradas', '  enderecosUsados(){', '')
troca('    this.derivados.forEach(d=>s.add(d.end));\n', '')

# ------------------------------------------------------------ 4. HTML da tela de alertas
troca_entre('<section class="vista" id="v-al"', '<!-- ================= E/S', r'''<section class="vista" id="v-al" aria-labelledby="aba-al">
  <div class="barra">
    <h2>Alertas e falhas</h2><button class="info-btn" data-info="al" aria-label="Sobre esta tela">i</button>
    <div class="sub" id="alVista" role="group" aria-label="Lista">
      <button data-vista="ativos" aria-pressed="true">Ativos agora</button>
      <button data-vista="cadastro" aria-pressed="false">Cadastro completo</button>
    </div>
    <input type="search" id="alBusca" placeholder="Código, texto ou endereço" aria-label="Buscar alarme">
    <div class="menu-wrap">
      <button class="btn" id="alExp" aria-haspopup="true" aria-expanded="false">Exportar ▾</button>
      <div class="menu" id="alExpMenu" hidden>
        <button data-exp="txt">Texto (.txt): ativos agora</button>
        <button data-exp="md">Markdown (.md): ativos agora</button>
        <button data-exp="csv">Planilha (.csv): histórico</button>
        <button data-exp="pdf">PDF (imprimir): ativos agora</button>
      </div>
    </div>
  </div>
  <div class="dados" id="alLista"></div>
  <div class="barra al-hist-bar"><h3 class="sec">Histórico</h3>
    <button class="btn" id="alLimpar">Limpar histórico</button></div>
  <div class="tw"><table id="alHist"><thead><tr><th>Hora</th><th>Evento</th><th>Código</th><th>Alarme</th><th>Dados</th><th>Duração</th></tr></thead><tbody></tbody></table></div>
</section>

''')
troca('  $("#alTodos").addEventListener("change",renderTudo); $("#alCsv").addEventListener("click",()=>TelaAlertas.csv());', '  TelaAlertas.iniciar();')

# ------------------------------------------------------------ 5. JS: alarmes (catalogo do PLC) e tela
troca_entre('const Alarmes = {', '/* ============================================================\n   5. OVERVIEW', r'''/* Catalogo gerado do codigo do PLC (docs/contratos/alarmes_v0.1.json). Fatos = PLC; textos de efeito/causa/solucao = propostos. */
const CAT_ALARMES = __ALARMES__;
const CHAVE_HIST = "baggio_alertasHist_v1";
const Alarmes = {
  defs: [], estado: {}, hist: [], iniciado: false,
  montar(){
    this.defs = CAT_ALARMES.alarmes.filter(a=>Dados.tag(a.bit));          // so o que existe no contrato lido
    const salvo = lerStorage(CHAVE_HIST);
    if (salvo) { try { this.hist = JSON.parse(salvo)||[]; } catch(e){} }
  },
  ativo(d){ const v = Dados.bit(d.bit); return v===undefined ? undefined : v===true; },
  ativos(){ return this.defs.filter(d=>d.tipo!=="I" && this.ativo(d)===true); },   // informacoes (I) nao contam como alarme
  atualizar(){
    if (!Dados.contrato) return;
    if (!this.defs.length) this.montar();
    if (Dados.semCom) return;                       // sem dado atual: nao registra transicoes
    const agora = Date.now(); let mudou = false;
    const origem = Dados.estado && Dados.estado.origem==="demo" ? "simulados" : "PLC";
    this.defs.forEach(d=>{
      const a = this.ativo(d); if (a===undefined) return;
      const e = this.estado[d.codigo];
      if (a && (!e || !e.ativo)) {
        this.estado[d.codigo] = {ativo:true, desde:agora, aoAbrir:!this.iniciado};
        if (d.tipo!=="I") { this.hist.push({t:agora, ev:this.iniciado?"ATIVOU":"JÁ ATIVO AO ABRIR", cod:d.codigo, end:d.bit, txt:d.nome, dados:origem, dur:""}); mudou = true; }
      } else if (!a && e && e.ativo) {
        if (d.tipo!=="I") { this.hist.push({t:agora, ev:"NORMALIZOU", cod:d.codigo, end:d.bit, txt:d.nome, dados:origem, dur:dur(agora-e.desde)}); mudou = true; }
        this.estado[d.codigo] = {ativo:false, desde:agora};
      } else if (!e) this.estado[d.codigo] = {ativo:false, desde:agora};
    });
    this.iniciado = true;
    if (mudou) { if (this.hist.length > 500) this.hist = this.hist.slice(-500); gravarStorage(CHAVE_HIST, JSON.stringify(this.hist)); }
  }
};

''')
troca_entre('const TelaAlertas = {', '/* ============================================================\n   7. ENTRADAS', r'''const TelaAlertas = {
  vista:"ativos", busca:"", abertos:new Set(), assin:"", todosAbertos:false,
  ORD:{F:0,A:1,I:2}, NOME:{F:"Falha",A:"Alerta",I:"Informação"},
  iniciar(){
    const alvo = $("#alLista");
    alvo.addEventListener("click", e=>{ const tr = e.target.closest(".al-lin"); if (tr) this.alternar(tr.dataset.cod); });
    alvo.addEventListener("keydown", e=>{ const tr = e.target.closest && e.target.closest(".al-lin");
      if (tr && (e.key==="Enter" || e.key===" ")) { e.preventDefault(); this.alternar(tr.dataset.cod); } });
    $$("#alVista button").forEach(b=>b.addEventListener("click",()=>{ this.vista = b.dataset.vista; $$("#alVista button").forEach(x=>x.setAttribute("aria-pressed", x===b)); this.assin=""; renderTudo(); }));
    $("#alBusca").addEventListener("input", e=>{ this.busca = e.target.value; this.assin=""; renderTudo(); });
    const btn = $("#alExp"), menu = $("#alExpMenu");
    btn.addEventListener("click", e=>{ e.stopPropagation(); menu.hidden = !menu.hidden; btn.setAttribute("aria-expanded", String(!menu.hidden)); });
    document.addEventListener("click", ()=>{ menu.hidden = true; btn.setAttribute("aria-expanded","false"); });
    document.addEventListener("keydown", e=>{ if (e.key==="Escape") { menu.hidden = true; btn.setAttribute("aria-expanded","false"); } });
    menu.addEventListener("click", e=>{ const b = e.target.closest("[data-exp]"); if (b) { menu.hidden = true; this.exportar(b.dataset.exp); } });
    $("#alLimpar").addEventListener("click", ()=>{ if (confirm("Apagar o histórico de alertas e falhas deste navegador?")) { Alarmes.hist = []; gravarStorage(CHAVE_HIST,"[]"); renderTudo(); } });
    window.addEventListener("afterprint", ()=>{ if (this.todosAbertos) { this.todosAbertos = false; this.assin=""; renderTudo(); } });
  },
  alternar(cod){ if (this.abertos.has(cod)) this.abertos.delete(cod); else this.abertos.add(cod); this.assin=""; renderTudo(); },
  aberto(d){ return this.abertos.has(d.codigo) || (this.todosAbertos && Alarmes.ativo(d)===true); },
  lista(){
    const q = this.busca.trim().toLowerCase();
    let L = this.vista==="ativos" ? Alarmes.defs.filter(d=>Alarmes.ativo(d)===true) : Alarmes.defs.slice();
    if (q) L = L.filter(d=>(d.codigo+" "+d.nome+" "+d.bit+" "+d.gatilho).toLowerCase().includes(q));
    return L.sort((a,b)=>{ const aa = Alarmes.ativo(a)===true, bb = Alarmes.ativo(b)===true;
      return (bb-aa) || this.ORD[a.tipo]-this.ORD[b.tipo] || a.codigo.localeCompare(b.codigo); });
  },
  chip(e){ return `<span class="chip" data-end="${esc(e)}">${esc(e)} <b></b></span>`; },
  /* painel de uma ocorrencia: Efeito -> Causa (teste rapido) -> Solucao (onde) + como o PLC decide */
  det(d){
    const causas = d.causas.map(c=>`<li>${esc(c.t)}<br><span class="mut">Teste rápido: ${esc(c.teste)}</span></li>`).join("");
    const sol = d.causas.map((c,i)=>c.sol.length ? `<p class="mut">Se for a causa ${i+1}:</p><ul class="sol">${c.sol.map(x=>`<li><span class="onde">${esc(CAT_ALARMES.onde[x[1]]||x[1])}</span> ${esc(x[0])}</li>`).join("")}</ul>` : "").join("") || '<p class="mut">Sem passos cadastrados.</p>';
    const ret = d.retentivo===true ? "Sim: fica ligado até apertar <b>RESET FALHAS (I0.2)</b> com a causa já resolvida."
              : d.retentivo===false ? "Não: acompanha a condição, sem reter." : "Não informado (lógica fora dos blocos fornecidos).";
    const atr = d.atraso_s ? `${d.atraso_s>=60 ? (d.atraso_s/60)+" min" : d.atraso_s+" s"}${d.timers&&d.timers.length?" ("+d.timers.join(", ")+")":""}` : "sem atraso próprio";
    const ond = d.bloco ? `${esc(d.bloco)}, rede ${d.rede}${d.rede_titulo?" ("+esc(d.rede_titulo)+")":""}` : "fora dos blocos fornecidos";
    return `<div class="corpo">
      <div><h4>1 · Efeito</h4><p>${esc(d.efeito)}</p></div>
      <div><h4>2 · Causa</h4><ol>${causas}</ol></div>
      <div><h4>3 · Solução</h4>${sol}</div>
      <div class="plc"><h4>Como o PLC decide</h4>
        <dl><dt>Gatilho</dt><dd>${esc(d.gatilho)}</dd>
        <dt>Atraso</dt><dd>${atr}</dd>
        <dt>Retém</dt><dd>${ret}</dd>
        ${d.porta_t31?'<dt>Condição</dt><dd>Só avalia com a máquina em trabalho há 3 s (T31).</dd>':""}
        <dt>Onde</dt><dd>${ond}</dd>
        <dt>Endereços</dt><dd class="chips">${this.chip(d.bit)} ${(d.operandos||[]).filter(x=>x!==d.bit).map(x=>this.chip(x)).join(" ")}</dd></dl>
        ${d.obs?`<p class="obs"><b>Observação do programa:</b> ${esc(d.obs)}</p>`:""}
        <p class="mut peq">Os fatos acima vêm do código do PLC. Efeito, causa, teste e solução são texto proposto e precisam da validação de quem opera a máquina.</p>
      </div></div>`;
  },
  desenha(L){
    const box = $("#alLista");
    if (!L.length) {
      box.innerHTML = Dados.semCom ? '<div class="vazio" style="color:var(--muted)">Sem dado atual</div>'
        : this.busca ? '<div class="vazio" style="color:var(--muted)">Nenhum alarme encontrado</div>' : '<div class="vazio">✔ Nenhum alarme ativo</div>';
      return;
    }
    const mostraEst = this.vista==="cadastro";
    box.innerHTML = `<table class="al-tab"><thead><tr><th></th><th>Código</th><th>Tipo</th><th>Alarme</th>${mostraEst?"<th>Estado</th>":""}<th>Início</th><th>Duração</th></tr></thead><tbody>`+
      L.map(d=>{
        const a = Alarmes.ativo(d), ab = this.aberto(d);
        const est = a===undefined ? "sem dado" : a ? "● ativo" : "○ normal";
        return `<tr class="al-lin ${a?"ativo":"inativo"} tp-${d.tipo}" data-cod="${esc(d.codigo)}" tabindex="0" role="button" aria-expanded="${ab}">
          <td class="seta-c">${ab?"▾":"▸"}</td><td><span class="cod">${esc(d.codigo)}</span></td>
          <td><span class="tp tp-${d.tipo}">${this.NOME[d.tipo]}</span></td><td>${esc(d.nome)}</td>${mostraEst?`<td>${est}</td>`:""}
          <td class="num" data-ini="${esc(d.codigo)}"></td><td class="num" data-dur="${esc(d.codigo)}"></td></tr>`+
          (ab?`<tr class="al-det"><td colspan="${mostraEst?7:6}">${this.det(d)}</td></tr>`:"");
      }).join("")+"</tbody></table>";
  },
  /* partes que mudam a cada segundo sem refazer a lista (mantem selecao de texto e painel aberto) */
  vivo(){
    const agora = Date.now();
    $$("#alLista [data-ini]").forEach(td=>{ const e = Alarmes.estado[td.dataset.ini], d = Alarmes.defs.find(x=>x.codigo===td.dataset.ini);
      const a = d && Alarmes.ativo(d)===true; td.textContent = a&&e ? hhmmss(e.desde)+(e.aoAbrir?" (ao abrir)":"") : "—"; });
    $$("#alLista [data-dur]").forEach(td=>{ const e = Alarmes.estado[td.dataset.dur], d = Alarmes.defs.find(x=>x.codigo===td.dataset.dur);
      const a = d && Alarmes.ativo(d)===true; td.textContent = a&&e ? dur(agora-e.desde) : "—"; });
    $$("#alLista .chip").forEach(c=>{ const v = Dados.bit(c.dataset.end); c.classList.toggle("on", v===true); c.classList.toggle("nd", v===undefined);
      $("b",c).textContent = v===undefined ? "—" : v ? "1" : "0"; });
  },
  atualizar(){
    if (!Alarmes.defs.length) { $("#alLista").innerHTML = '<div class="vazio" style="color:var(--muted)">Carregando…</div>'; this.assin=""; }
    else {
      const L = this.lista();
      const sig = [this.vista, this.busca, Dados.semCom?1:0, Array.from(this.abertos).sort().join(","), this.todosAbertos?1:0,
                   L.map(d=>d.codigo+(Alarmes.ativo(d)===true?"+":Alarmes.ativo(d)===undefined?"?":"-")).join(",")].join("|");
      if (sig !== this.assin) { this.assin = sig; this.desenha(L); }
      this.vivo();
    }
    const n = Alarmes.hist.length;
    $("#alHist tbody").innerHTML = Alarmes.hist.slice().reverse().slice(0,100).map(x=>`<tr><td class="num">${new Date(x.t).toLocaleString("pt-BR",{hour12:false})}</td><td><b>${esc(x.ev)}</b></td><td><span class="cod">${esc(x.cod||"")}</span></td><td>${esc(x.txt)}</td><td>${esc(x.dados||"")}</td><td class="num">${esc(x.dur)}</td></tr>`).join("")
      || '<tr><td colspan="6" style="color:var(--muted)">Sem eventos registrados.</td></tr>';
  },
  /* ---------- exportar ---------- */
  relatorio(md){
    const ativos = Alarmes.ativos().sort((a,b)=>this.ORD[a.tipo]-this.ORD[b.tipo]||a.codigo.localeCompare(b.codigo));
    const origem = Dados.estado && Dados.estado.origem==="demo" ? "DADOS SIMULADOS" : "PLC";
    const L = []; const h = (t,n)=>md ? "#".repeat(n)+" "+t : t.toUpperCase();
    L.push(h("Baggio — Alertas e falhas ativos",1)); L.push("Gerado em "+new Date().toLocaleString("pt-BR",{hour12:false})+" · dados: "+origem); L.push("");
    if (!ativos.length) L.push("Nenhum alarme ativo.");
    ativos.forEach(d=>{ const e = Alarmes.estado[d.codigo];
      L.push(h(d.codigo+" · "+this.NOME[d.tipo]+" · "+d.nome,2)); L.push("Ativo desde "+(e?hhmmss(e.desde):"?")+" · endereço "+d.bit);
      L.push((md?"- ":"")+"Efeito: "+d.efeito); L.push((md?"- ":"")+"Como o PLC decide: "+d.gatilho);
      if (d.obs) L.push((md?"- ":"")+"Observação do programa: "+d.obs);
      d.causas.forEach((c,i)=>{ L.push((md?"- ":"")+"Causa "+(i+1)+": "+c.t); L.push("    Teste rápido: "+c.teste);
        c.sol.forEach(x=>L.push("    Solução ["+(CAT_ALARMES.onde[x[1]]||x[1])+"]: "+x[0])); });
      L.push(""); });
    L.push("Efeito, causa, teste e solução são texto proposto, a validar com quem opera a máquina.");
    return L.join("\n");
  },
  baixar(nome, txt, tipo){
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([txt],{type:tipo+";charset=utf-8"})); a.download = nome;
    document.body.appendChild(a); a.click(); a.remove();
  },
  exportar(f){
    const carimbo = new Date().toISOString().slice(0,19).replace(/[:T]/g,"-");
    if (f==="txt") this.baixar("baggio_alertas_"+carimbo+".txt", "﻿"+this.relatorio(false), "text/plain");
    else if (f==="md") this.baixar("baggio_alertas_"+carimbo+".md", "﻿"+this.relatorio(true), "text/markdown");
    else if (f==="csv") { const linhas = [["hora","evento","codigo","alarme","endereco","dados","duracao"]].concat(Alarmes.hist.map(x=>[new Date(x.t).toLocaleString("pt-BR",{hour12:false}),x.ev,x.cod||"",x.txt,x.end||"",x.dados||"",x.dur]));
      this.baixar("baggio_historico_"+carimbo+".csv", "﻿"+linhas.map(l=>l.map(c=>'"'+String(c).replace(/"/g,'""')+'"').join(";")).join("\r\n"), "text/csv"); }
    else if (f==="pdf") { this.todosAbertos = true; this.assin=""; renderTudo(); setTimeout(()=>window.print(), 60); }
  }
};

''')
s = s.replace("__ALARMES__", CAT)

# ------------------------------------------------------------ 6. cabecalho: selo e contador usam o tipo do catalogo
troca('const grave = Alarmes.ativos().some(d=>d.sev==="emergencia"||d.sev==="critico");', 'const grave = Alarmes.ativos().some(d=>d.tipo==="F");')
troca('c.className = "cnt"+(!Dados.semCom && n ? (Alarmes.ativos().some(d=>d.sev==="emergencia"||d.sev==="critico")?" ativo":" aviso"):"");',
      'c.className = "cnt"+(!Dados.semCom && n ? (Alarmes.ativos().some(d=>d.tipo==="F")?" ativo":" aviso"):"");')

# ------------------------------------------------------------ 7. ajuda da tela de alertas
troca_entre('  al:["Alertas e falhas"', '  es:["Entradas e saídas"', r'''  al:["Alertas e falhas","<p>Lista dos alarmes do PLC. <b>Toque numa linha</b> para ver: <b>1 · Efeito</b> (o sintoma), <b>2 · Causa</b> (com teste rápido) e <b>3 · Solução</b> (e onde se resolve), mais <b>Como o PLC decide</b>, com os endereços ao vivo.</p>"
    +"<p><b>Código</b> <code>T-AAA-NNN</code>: T = <b>F</b> falha (alarme crítico do PLC), <b>A</b> alerta (alarme permissível) ou <b>I</b> informação (só estado, não conta como alarme); AAA = família (DSJ disjuntor, CMD comando sem retorno, NIV nível, PRS ar, SEG emergência, FLT filtro, PRT partida das bombas, BND banda). O número nunca é reutilizado.</p>"
    +"<p>Os alarmes que o PLC retém só apagam com <b>RESET FALHAS</b> depois que a causa foi resolvida. As horas são as do navegador. O histórico fica neste navegador (últimos 500 eventos).</p>"
    +"<p><b>Texto proposto:</b> efeito, causa, teste e solução foram escritos a partir da lógica do PLC e precisam da validação de quem opera a máquina. Alarmes marcados OUT vêm da planilha de tags e a lógica deles não está nos blocos fornecidos.</p>"],
  ''')

# ------------------------------------------------------------ 8. CSS
troca('</style>', r'''
/* ============ v0.6 · cabecalho e valvula ============ */
.vis-rot{color:#fff;font-size:12.5px;font-weight:600;opacity:.9}
.vl-at{fill:#c3c8cc;stroke:#59646a;stroke-width:1}
body.tema-mod .vl-at{fill:var(--off-bg);stroke:var(--muted)}
body.tema-mod .vl.on .vl-at{fill:#bfe6cf}

/* ============ v0.6 · alertas e falhas (padrao do medidor: efeito -> causa -> solucao) ============ */
.menu-wrap{position:relative;margin-left:auto}
.menu{position:absolute;right:0;top:calc(100% + 4px);z-index:30;min-width:270px;background:var(--panel);border:1px solid var(--line);border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.25);padding:4px}
.menu[hidden]{display:none}
.menu button{display:block;width:100%;text-align:left;border:0;background:none;padding:8px 12px;border-radius:6px;font-weight:600}
.menu button:hover,.menu button:focus-visible{background:var(--off-bg)}
.al-hist-bar{margin-top:6px}
.al-hist-bar .sec{margin:12px 0 0}
.al-hist-bar .btn{margin-top:12px}
.al-tab .al-lin{cursor:pointer}
.al-tab .al-lin:hover td{filter:brightness(.97)}
.al-tab .seta-c{width:26px;color:var(--muted);text-align:center}
.cod{font-family:ui-monospace,Consolas,monospace;font-weight:700;white-space:nowrap}
.tp{display:inline-block;padding:1px 9px;border-radius:4px;font-size:12px;font-weight:700;white-space:nowrap}
.tp-F.tp{background:var(--bad);color:#fff}
.tp-A.tp{border:1.5px solid var(--warn);color:var(--warn)}
.tp-I.tp{border:1.5px solid var(--off);color:var(--muted)}
tr.ativo.tp-F td{background:var(--bad-bg)}
tr.ativo.tp-A td{background:var(--warn-bg)}
tr.ativo.tp-I td{background:var(--off-bg)}
tr.al-det td{padding:0;background:var(--panel);border-bottom:2px solid var(--line)}
.corpo{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px 22px;padding:14px 18px 16px;max-width:1400px}
.corpo h4{margin:0 0 6px;font-size:14px}
.corpo p,.corpo ol,.corpo ul{margin:.3em 0}
.corpo ol{padding-left:20px}
.corpo ul.sol{list-style:none;padding:0}
.corpo ul.sol li{margin:6px 0}
.onde{display:inline-block;font-size:11.5px;font-weight:700;border:1.5px solid var(--line);border-radius:4px;padding:0 6px;margin-right:6px;color:var(--muted);white-space:nowrap}
.corpo .plc{grid-column:1/-1;border-top:1px dashed var(--line);padding-top:10px;margin-top:6px}
.plc dl{display:grid;grid-template-columns:110px minmax(0,1fr);gap:4px 12px;margin:6px 0}
.plc dt{color:var(--muted);font-weight:600}
.plc dd{margin:0}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{display:inline-flex;gap:6px;align-items:center;border:1.5px solid var(--line);border-radius:6px;padding:0 8px;font-family:ui-monospace,Consolas,monospace;font-size:12.5px}
.chip.on{border-color:var(--run);color:var(--run);background:var(--run-bg)}
.chip.nd{border-style:dashed;color:var(--muted)}
.obs{background:var(--warn-bg);border-left:4px solid var(--warn);padding:6px 10px;border-radius:4px}
.peq{font-size:12px}
@media (max-width:1000px){ .corpo{grid-template-columns:1fr} .plc dl{grid-template-columns:90px minmax(0,1fr)} }
@media print{
  body *{visibility:hidden}
  #v-al,#v-al *{visibility:visible}
  #v-al{position:absolute;left:0;top:0;width:100%}
  .barra,.al-hist-bar,#alHist,.tw{display:none!important}
  #aviso{display:none!important}
}
</style>''')

DEST.write_text(s, encoding="utf-8")
print("ok", DEST.relative_to(RAIZ), len(s)//1024, "KB")
