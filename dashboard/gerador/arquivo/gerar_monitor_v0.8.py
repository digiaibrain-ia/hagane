#!/usr/bin/env python3
"""Gera dashboard/src/baggio_monitor_v0.8.html a partir da v0.7 (arquivada).

v0.8:
  * T DA ALIMENTACAO conforme o WinCC: o tubo horizontal chega ao T e SE DIVIDE: um ramo SOBE (alimentacao) e o outro
    DESCE (lavagem). Na v0.7 o tubo inteiro subia, inclusive abaixo do T. A animacao e as setas seguem o mesmo sentido.
    Teste novo: em toda juncao de pontas tem de haver entrada e saida (conservacao do fluxo).
  * SIMULACAO NUNCA GERA FALHA DE COMUNICACAO: o estado simulado e sempre "ok" (antes, o ramo de silencio ainda existia).
  * ALERTAS E FALHAS DE DEMONSTRACAO: com dados simulados ha SEMPRE uma Falha e um Alerta ficticios, autoexplicativos
    (F-DEM-001 / A-DEM-001). Nao existem no PLC, nao entram no historico e nao mudam o selo de estado.
  * FILTROS na tela de alertas: tipo (Falha / Alerta / Informacao, com contagem), familia (lista), busca; "Limpar filtros";
    "Mostrando X de Y".  CAIXAS DE SELECAO por linha + "selecionar todos"; Exportar usa os selecionados.
Uso: python3 -B -I dashboard/gerador/gerar_monitor_v0.8.py   (aborta se o destino existir ou se a v0.7 mudou)
"""
import json, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ORIG = RAIZ / "dashboard/arquivo/baggio_monitor_v0.7.html"
DEST = RAIZ / "dashboard/src/baggio_monitor_v0.8.html"
if DEST.exists() and "--forcar" not in sys.argv:
    sys.exit(f"ABORTA: {DEST.name} ja existe (versao nova, nunca sobrescrever)")
s = ORIG.read_text(encoding="utf-8")

def troca(velho, novo, n=1):
    global s
    if s.count(velho) != n:
        sys.exit(f"ABORTA: trecho da v0.7 mudou ({s.count(velho)}x): {velho[:90]!r}")
    s = s.replace(velho, novo)

def troca_entre(ini, fim, novo):
    global s
    a = s.find(ini); b = s.find(fim, a + 1)
    if a < 0 or b < 0:
        sys.exit(f"ABORTA: marcador nao encontrado: {ini[:60]!r} / {fim[:60]!r}")
    s = s[:a] + novo + s[b:]

# ------------------------------------------------------------------ versao
troca('<meta name="app-version" content="0.7">', '<meta name="app-version" content="0.8">')
troca('  BAGGIO MONITOR v0.7  (SOMENTE LEITURA)', '  BAGGIO MONITOR v0.8  (SOMENTE LEITURA)')
troca('    v0.7  Setas geradas do tubo', '    v0.8  T da alimentacao (um ramo sobe, o outro desce); simulacao sem falha de comunicacao; Falha e Alerta de demonstracao\n          sempre ativos na simulacao; filtros e caixas de selecao em Alertas e falhas.\n    v0.7  Setas geradas do tubo')
troca('const VERSAO = "0.7";', 'const VERSAO = "0.8";')

# ------------------------------------------------------------------ 1. T da alimentacao
troca('${this.tubo("M690 256 V52","","ali",false,-1)}', '${this.tubo("M690 208 V52","","ali",false,1)}')
troca('${this.tubo("M690 256 H853 Q861 256 861 248 V240","","lav",false,-1)}',
      '${this.tubo("M690 208 V268","bt","lav",false,-1)}\n      ${this.tubo("M690 268 Q690 280 702 280 H849 Q861 280 861 268 V240","bt","lav",false,-1)}')
troca('x:800, y:256, vert:false, bit:"Q15.6"}', 'x:800, y:280, vert:false, bit:"Q15.6"}')
troca('[800,282,"VÁLVULA DE","middle"],[800,294,"LAVAGEM","middle"]', '[800,306,"VÁLVULA DE","middle"],[800,318,"LAVAGEM","middle"]')

# ------------------------------------------------------------------ 2. simulacao nunca falha
troca_entre('    const u = this.simUltimo, idade', '  /* troca de fonte em funcionamento', '''    const u = this.simUltimo;
    this.falhas = 0;
    this.estado = {versao:VERSAO, origem:"demo", agora:Date.now(), ts:u.ts, idade_ms:0, comunicacao:"ok", motivo:"", bits:u.bits};   // simulacao: SEMPRE ok
    this.definirCom(false, "");
    this.ultimoOk = Date.now();
  },
''')

# ------------------------------------------------------------------ 3. alarmes de demonstracao
DEMO = [
    {"bit": "DEMO", "codigo": "F-DEM-001", "tipo": "F", "familia": "DEM", "familia_nome": "Demonstração (fictício)", "demo": True,
     "prioridade": "critico", "bloco": None, "rede": None, "rede_titulo": None, "retentivo": None, "reset": None, "porta_t31": None,
     "atraso_s": None, "timers": [], "operandos": [], "nome": "DEMONSTRAÇÃO: falha de exemplo (fictícia)",
     "gatilho": "Fictício: fica sempre ativo enquanto os dados forem simulados. Não existe no PLC.",
     "efeito": "Esta é uma falha de exemplo, criada só para mostrar a tela. Uma FALHA (código começando com F) é um alarme crítico do PLC: algo que deveria funcionar e não funciona.",
     "causas": [
         {"t": "Exemplo de causa: o que provavelmente originou o alarme (a raiz do problema).",
          "teste": "Exemplo de teste rápido: uma verificação simples que confirma a causa, como olhar um sinal na tela Entradas e saídas.",
          "sol": [["Exemplo de passo feito pelo operador, no botão ou na tela.", "operador"], ["Exemplo de passo feito no painel elétrico.", "painel"], ["Exemplo de passo feito na máquina.", "campo"]]},
         {"t": "Segunda causa possível. A tela lista todas as causas, da mais provável para a menos provável.",
          "teste": "Cada causa tem o seu próprio teste rápido: faça o teste antes de mexer em qualquer coisa.",
          "sol": [["Exemplo de correção no programa do PLC (feita pela engenharia).", "programa"]]}],
     "obs": "Alarme de demonstração: aparece só quando os dados são simulados e não muda o selo de estado do cabeçalho.",
     "comentario_tag": "", "evidencia": {"logica": "demonstração", "texto": "fictício"}},
    {"bit": "DEMO", "codigo": "A-DEM-001", "tipo": "A", "familia": "DEM", "familia_nome": "Demonstração (fictício)", "demo": True,
     "prioridade": "permissivel", "bloco": None, "rede": None, "rede_titulo": None, "retentivo": None, "reset": None, "porta_t31": None,
     "atraso_s": None, "timers": [], "operandos": [], "nome": "DEMONSTRAÇÃO: alerta de exemplo (fictício)",
     "gatilho": "Fictício: fica sempre ativo enquanto os dados forem simulados. Não existe no PLC.",
     "efeito": "Este é um alerta de exemplo, criado só para mostrar a tela. Um ALERTA (código começando com A) é um alarme permissível: pede atenção, mas a máquina pode continuar funcionando.",
     "causas": [
         {"t": "Exemplo de causa de um alerta: uma condição que ainda não parou a máquina, mas pode piorar.",
          "teste": "Exemplo de teste rápido: confira o valor ou o estado indicado no 'Como o PLC decide'.",
          "sol": [["Exemplo de passo feito pelo operador.", "operador"], ["Exemplo de passo feito na máquina.", "campo"]]}],
     "obs": "Alarme de demonstração: aparece só quando os dados são simulados e não muda o selo de estado do cabeçalho.",
     "comentario_tag": "", "evidencia": {"logica": "demonstração", "texto": "fictício"}},
]
troca('const CHAVE_HIST = "baggio_alertasHist_v1";', 'const ALARMES_DEMO = ' + json.dumps(DEMO, ensure_ascii=False) + ';   /* fictícios: só existem com dados simulados */\nconst CHAVE_HIST = "baggio_alertasHist_v1";')
troca('this.defs = CAT_ALARMES.alarmes.filter(a=>Dados.tag(a.bit));          // so o que existe no contrato lido',
      'this.defs = CAT_ALARMES.alarmes.filter(a=>Dados.tag(a.bit)).concat(ALARMES_DEMO);   // do PLC: so o que existe no contrato lido; + os de demonstracao')
troca('  ativo(d){ const v = Dados.bit(d.bit); return v===undefined ? undefined : v===true; },',
      '''  demoLigado(){ return !Dados.semCom && !!Dados.estado && Dados.estado.origem==="demo"; },
  visivel(d){ return !d.demo || this.demoLigado(); },                    // demonstracao so aparece com dados simulados
  ativo(d){ if (d.demo) return this.demoLigado();
            const v = Dados.bit(d.bit); return v===undefined ? undefined : v===true; },''')
troca('  ativos(){ return this.defs.filter(d=>d.tipo!=="I" && this.ativo(d)===true); },', '  ativos(){ return this.defs.filter(d=>d.tipo!=="I" && this.visivel(d) && this.ativo(d)===true); },')
troca('if (d.tipo!=="I") {', 'if (d.tipo!=="I" && !d.demo) {', 2)        # demonstracao nao entra no historico
troca('Alarmes.ativos().some(d=>d.tipo==="F")', 'Alarmes.ativos().some(d=>d.tipo==="F" && !d.demo)', 2)   # nem no selo de estado

# ------------------------------------------------------------------ 4. HTML da tela de alertas (filtros, selecao)
troca_entre('  <div class="barra">\n    <h2>Alertas e falhas</h2>', '  <div class="dados" id="alLista"></div>', r'''  <div class="barra">
    <h2>Alertas e falhas</h2><button class="info-btn" data-info="al" aria-label="Sobre esta tela">i</button>
    <div class="sub" id="alVista" role="group" aria-label="Lista">
      <button data-vista="ativos" aria-pressed="true">Ativos agora</button>
      <button data-vista="cadastro" aria-pressed="false">Cadastro completo</button>
    </div>
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
  <div class="barra al-filtros" role="group" aria-label="Filtros">
    <span class="fl-rot">Filtrar por</span>
    <div class="chips-f" id="alTipos" role="group" aria-label="Tipo">
      <button data-tipo="F" aria-pressed="true" title="Falha: alarme crítico do PLC"><span class="tp tp-F">Falha</span> <b></b></button>
      <button data-tipo="A" aria-pressed="true" title="Alerta: alarme permissível, pede atenção"><span class="tp tp-A">Alerta</span> <b></b></button>
      <button data-tipo="I" aria-pressed="true" title="Informação: só um estado, não conta como alarme"><span class="tp tp-I">Informação</span> <b></b></button>
    </div>
    <label class="fl-sel">Família
      <select id="alFam" aria-label="Filtrar por família"><option value="">Todas</option></select></label>
    <input type="search" id="alBusca" placeholder="Buscar por código, texto ou endereço" aria-label="Buscar alarme">
    <button class="btn" id="alLimpaFiltro" hidden>Limpar filtros</button>
    <span id="alContagem" class="fl-cont"></span>
  </div>
  <p class="dica">Toque numa linha para abrir o painel (efeito, causa e solução). Marque a caixa à esquerda para selecionar; o botão Exportar usa os selecionados.</p>
  <div class="barra al-selbar" id="alSelBar" hidden><span id="alSelTxt"></span> <button class="btn" id="alSelLimpa">Limpar seleção</button></div>
''')

# ------------------------------------------------------------------ 5. JS da tela de alertas (filtros, selecao, demo)
troca_entre('const TelaAlertas = {', '/* ============================================================\n   7. ENTRADAS', r'''const TelaAlertas = {
  vista:"ativos", busca:"", tipos:{F:true,A:true,I:true}, familia:"", abertos:new Set(), sel:new Set(), assin:"", famAssin:"", todosAbertos:false,
  ORD:{F:0,A:1,I:2}, NOME:{F:"Falha",A:"Alerta",I:"Informação"},
  iniciar(){
    const alvo = $("#alLista");
    alvo.addEventListener("click", e=>{ if (e.target.closest(".sel-c")) return;                 // caixa de selecao: tratada no "change"
      const tr = e.target.closest(".al-lin"); if (tr) this.alternar(tr.dataset.cod); });
    alvo.addEventListener("change", e=>{ const t = e.target;
      if (t.matches("input[data-sel]")) { if (t.checked) this.sel.add(t.dataset.sel); else this.sel.delete(t.dataset.sel); this.assin=""; renderTudo(); }
      else if (t.id==="alSelTodos") { const L = this.lista(); L.forEach(d=>{ if (t.checked) this.sel.add(d.codigo); else this.sel.delete(d.codigo); }); this.assin=""; renderTudo(); } });
    alvo.addEventListener("keydown", e=>{ if (e.target.matches && e.target.matches("input")) return;
      const tr = e.target.closest && e.target.closest(".al-lin");
      if (tr && (e.key==="Enter" || e.key===" ")) { e.preventDefault(); this.alternar(tr.dataset.cod); } });
    $$("#alVista button").forEach(b=>b.addEventListener("click",()=>{ this.vista = b.dataset.vista; $$("#alVista button").forEach(x=>x.setAttribute("aria-pressed", x===b)); this.assin=""; renderTudo(); }));
    $$("#alTipos button").forEach(b=>b.addEventListener("click",()=>{ const t = b.dataset.tipo; this.tipos[t] = !this.tipos[t]; b.setAttribute("aria-pressed", String(this.tipos[t])); this.assin=""; renderTudo(); }));
    $("#alFam").addEventListener("change", e=>{ this.familia = e.target.value; this.assin=""; renderTudo(); });
    $("#alBusca").addEventListener("input", e=>{ this.busca = e.target.value; this.assin=""; renderTudo(); });
    $("#alLimpaFiltro").addEventListener("click", ()=>this.limparFiltros());
    $("#alSelLimpa").addEventListener("click", ()=>{ this.sel.clear(); this.assin=""; renderTudo(); });
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
  filtrado(){ return !!(this.busca.trim() || this.familia || !(this.tipos.F && this.tipos.A && this.tipos.I)); },
  limparFiltros(){
    this.busca = ""; $("#alBusca").value = ""; this.familia = ""; $("#alFam").value = ""; this.tipos = {F:true,A:true,I:true};
    $$("#alTipos button").forEach(b=>b.setAttribute("aria-pressed","true")); this.assin=""; renderTudo();
  },
  /* universo da lista atual, ANTES dos filtros (so a vista: ativos agora ou cadastro completo) */
  base(){ return Alarmes.defs.filter(d=>Alarmes.visivel(d) && (this.vista==="cadastro" || Alarmes.ativo(d)===true)); },
  lista(){
    const q = this.busca.trim().toLowerCase();
    return this.base().filter(d=>this.tipos[d.tipo] && (!this.familia || d.familia===this.familia) &&
        (!q || (d.codigo+" "+d.nome+" "+d.bit+" "+d.gatilho).toLowerCase().includes(q)))
      .sort((a,b)=>{ const aa = Alarmes.ativo(a)===true, bb = Alarmes.ativo(b)===true;
        return (bb-aa) || this.ORD[a.tipo]-this.ORD[b.tipo] || a.codigo.localeCompare(b.codigo); });
  },
  chip(e){ return `<span class="chip" data-end="${esc(e)}">${esc(e)} <b></b></span>`; },
  /* painel de uma ocorrencia: Efeito -> Causa (teste rapido) -> Solucao (onde) + como o PLC decide */
  det(d){
    const causas = d.causas.map(c=>`<li>${esc(c.t)}<br><span class="mut">Teste rápido: ${esc(c.teste)}</span></li>`).join("");
    const sol = d.causas.map((c,i)=>c.sol.length ? `<p class="mut">Se for a causa ${i+1}:</p><ul class="sol">${c.sol.map(x=>`<li><span class="onde">${esc(CAT_ALARMES.onde[x[1]]||x[1])}</span> ${esc(x[0])}</li>`).join("")}</ul>` : "").join("") || '<p class="mut">Sem passos cadastrados.</p>';
    const ret = d.retentivo===true ? "Sim: fica ligado até apertar <b>RESET FALHAS (I0.2)</b> com a causa já resolvida."
              : d.retentivo===false ? "Não: acompanha a condição, sem reter." : d.demo ? "Não se aplica (alarme fictício)." : "Não informado (lógica fora dos blocos fornecidos).";
    const atr = d.atraso_s ? `${d.atraso_s>=60 ? (d.atraso_s/60)+" min" : d.atraso_s+" s"}${d.timers&&d.timers.length?" ("+d.timers.join(", ")+")":""}` : "sem atraso próprio";
    const ond = d.bloco ? `${esc(d.bloco)}, rede ${d.rede}${d.rede_titulo?" ("+esc(d.rede_titulo)+")":""}` : d.demo ? "não existe no PLC" : "fora dos blocos fornecidos";
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
        ${d.demo?"":`<dt>Endereços</dt><dd class="chips">${this.chip(d.bit)} ${(d.operandos||[]).filter(x=>x!==d.bit).map(x=>this.chip(x)).join(" ")}</dd>`}</dl>
        ${d.obs?`<p class="obs"><b>Observação${d.demo?"":" do programa"}:</b> ${esc(d.obs)}</p>`:""}
        <p class="mut peq">${d.demo?"Texto de demonstração, escrito para explicar a tela.":"Os fatos acima vêm do código do PLC. Efeito, causa, teste e solução são texto proposto e precisam da validação de quem opera a máquina."}</p>
      </div></div>`;
  },
  desenha(L){
    const box = $("#alLista");
    if (!L.length) {
      box.innerHTML = Dados.semCom ? '<div class="vazio" style="color:var(--muted)">Sem dado atual</div>'
        : this.filtrado() ? '<div class="vazio" style="color:var(--muted)">Nenhum alarme com estes filtros</div>' : '<div class="vazio">✔ Nenhum alarme ativo</div>';
      return;
    }
    const mostraEst = this.vista==="cadastro", ncol = (mostraEst?8:7);
    box.innerHTML = `<table class="al-tab"><thead><tr><th class="sel-c"><input type="checkbox" id="alSelTodos" aria-label="Selecionar todos os alarmes desta lista"></th><th></th><th>Código</th><th>Tipo</th><th>Alarme</th>${mostraEst?"<th>Estado</th>":""}<th>Início</th><th>Duração</th></tr></thead><tbody>`+
      L.map(d=>{
        const a = Alarmes.ativo(d), ab = this.aberto(d), marc = this.sel.has(d.codigo);
        const est = a===undefined ? "sem dado" : a ? "● ativo" : "○ normal";
        return `<tr class="al-lin ${a?"ativo":"inativo"} tp-${d.tipo}${marc?" marcado":""}" data-cod="${esc(d.codigo)}" tabindex="0" role="button" aria-expanded="${ab}">
          <td class="sel-c"><input type="checkbox" data-sel="${esc(d.codigo)}" ${marc?"checked":""} aria-label="Selecionar ${esc(d.codigo)}"></td>
          <td class="seta-c">${ab?"▾":"▸"}</td><td><span class="cod">${esc(d.codigo)}</span></td>
          <td><span class="tp tp-${d.tipo}">${this.NOME[d.tipo]}</span></td><td>${esc(d.nome)}${d.demo?' <span class="demo-tag">DEMO</span>':""}</td>${mostraEst?`<td>${est}</td>`:""}
          <td class="num" data-ini="${esc(d.codigo)}"></td><td class="num" data-dur="${esc(d.codigo)}"></td></tr>`+
          (ab?`<tr class="al-det"><td colspan="${ncol}">${this.det(d)}</td></tr>`:"");
      }).join("")+"</tbody></table>";
    const todos = $("#alSelTodos"), n = L.filter(d=>this.sel.has(d.codigo)).length;
    todos.checked = n===L.length; todos.indeterminate = n>0 && n<L.length;
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
  /* contagens dos tipos, lista de familias, "mostrando X de Y", barra de selecao e rotulos do menu */
  controles(L){
    const B = this.base();
    ["F","A","I"].forEach(t=>{ $(`#alTipos [data-tipo="${t}"] b`).textContent = B.filter(d=>d.tipo===t).length; });
    const fams = Array.from(new Map(Alarmes.defs.filter(d=>Alarmes.visivel(d)).map(d=>[d.familia, d.familia_nome])).entries()).sort((a,b)=>a[0].localeCompare(b[0]));
    const fa = fams.map(f=>f[0]).join(",");
    if (fa !== this.famAssin) { this.famAssin = fa; const sel = $("#alFam"); const atual = this.familia;
      sel.innerHTML = '<option value="">Todas</option>'+fams.map(f=>`<option value="${esc(f[0])}">${esc(f[0])} · ${esc(f[1])}</option>`).join("");
      if (!fams.some(f=>f[0]===atual)) { this.familia = ""; } sel.value = this.familia; }
    $("#alContagem").textContent = `Mostrando ${L.length} de ${B.length}`;
    $("#alLimpaFiltro").hidden = !this.filtrado();
    const n = Array.from(this.sel).filter(c=>Alarmes.defs.some(d=>d.codigo===c && Alarmes.visivel(d))).length;
    $("#alSelBar").hidden = n===0; $("#alSelTxt").textContent = `${n} selecionado${n===1?"":"s"}. O botão Exportar usa só os selecionados.`;
    $('[data-exp="txt"]').textContent = n ? `Texto (.txt): selecionados (${n})` : "Texto (.txt): ativos agora";
    $('[data-exp="md"]').textContent = n ? `Markdown (.md): selecionados (${n})` : "Markdown (.md): ativos agora";
    $('[data-exp="pdf"]').textContent = n ? `PDF (imprimir): selecionados (${n})` : "PDF (imprimir): ativos agora";
  },
  atualizar(){
    if (!Alarmes.defs.length) { $("#alLista").innerHTML = '<div class="vazio" style="color:var(--muted)">Carregando…</div>'; this.assin=""; }
    else {
      const L = this.lista();
      const sig = [this.vista, this.busca, this.familia, JSON.stringify(this.tipos), Dados.semCom?1:0, Array.from(this.abertos).sort().join(","), Array.from(this.sel).sort().join(","), this.todosAbertos?1:0,
                   L.map(d=>d.codigo+(Alarmes.ativo(d)===true?"+":Alarmes.ativo(d)===undefined?"?":"-")).join(",")].join("|");
      this.controles(L);
      if (sig !== this.assin) { this.assin = sig; this.desenha(L); }
      this.vivo();
    }
    $("#alHist tbody").innerHTML = Alarmes.hist.slice().reverse().slice(0,100).map(x=>`<tr><td class="num">${new Date(x.t).toLocaleString("pt-BR",{hour12:false})}</td><td><b>${esc(x.ev)}</b></td><td><span class="cod">${esc(x.cod||"")}</span></td><td>${esc(x.txt)}</td><td>${esc(x.dados||"")}</td><td class="num">${esc(x.dur)}</td></tr>`).join("")
      || '<tr><td colspan="6" style="color:var(--muted)">Sem eventos registrados.</td></tr>';
  },
  /* ---------- exportar: os SELECIONADOS (se houver) ou os ativos agora ---------- */
  alvo(){
    const sel = Alarmes.defs.filter(d=>this.sel.has(d.codigo) && Alarmes.visivel(d));
    const l = sel.length ? sel : Alarmes.ativos();
    return {itens:l.slice().sort((a,b)=>this.ORD[a.tipo]-this.ORD[b.tipo]||a.codigo.localeCompare(b.codigo)), selecionados:sel.length>0};
  },
  relatorio(md){
    const {itens, selecionados} = this.alvo();
    const origem = Dados.estado && Dados.estado.origem==="demo" ? "DADOS SIMULADOS" : "PLC";
    const L = []; const h = (t,n)=>md ? "#".repeat(n)+" "+t : t.toUpperCase();
    L.push(h("Baggio — Alertas e falhas "+(selecionados?"selecionados":"ativos"),1)); L.push("Gerado em "+new Date().toLocaleString("pt-BR",{hour12:false})+" · dados: "+origem); L.push("");
    if (!itens.length) L.push("Nenhum alarme ativo.");
    itens.forEach(d=>{ const e = Alarmes.estado[d.codigo], a = Alarmes.ativo(d)===true;
      L.push(h(d.codigo+" · "+this.NOME[d.tipo]+" · "+d.nome,2)); L.push((a ? "Ativo desde "+(e?hhmmss(e.desde):"?") : "Estado: normal (não ativo agora)")+(d.demo?"":" · endereço "+d.bit));
      L.push((md?"- ":"")+"Efeito: "+d.efeito); L.push((md?"- ":"")+"Como o PLC decide: "+d.gatilho);
      if (d.obs) L.push((md?"- ":"")+"Observação: "+d.obs);
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

# ------------------------------------------------------------------ 6. ajuda
troca('+"<p>Os alarmes que o PLC retém só apagam com <b>RESET FALHAS</b>',
      '+"<p><b>Filtrar:</b> use os botões <b>Falha / Alerta / Informação</b> (mostram a contagem), a lista de <b>Família</b> e a busca; <b>Limpar filtros</b> volta ao normal. <b>Selecionar:</b> marque a caixa de cada linha (ou a do cabeçalho para todas) e use Exportar para levar só os selecionados.</p>"\n'
      '    +"<p><b>DEMO:</b> com dados simulados há sempre uma falha e um alerta fictícios (códigos DEM) para mostrar como a tela funciona. Eles não existem no PLC e não mudam o selo de estado.</p>"\n'
      '    +"<p>Os alarmes que o PLC retém só apagam com <b>RESET FALHAS</b>')

# ------------------------------------------------------------------ 7. CSS
troca('</style>', r'''
/* ============ v0.8 · filtros, selecao e demonstracao ============ */
.al-filtros{gap:10px;align-items:center;margin-bottom:4px}
.fl-rot{font-weight:600;color:var(--muted)}
.tb-o.bt,.tb-i.bt{stroke-linecap:butt}                      /* tubos emendados (T da alimentacao): sem bolha na juncao */
.chips-f{display:inline-flex;gap:6px;flex-wrap:wrap}
.chips-f button{display:inline-flex;align-items:center;gap:6px;border:1.5px solid var(--line);background:var(--panel);border-radius:7px;padding:3px 9px;font-weight:600}
.chips-f button b{min-width:18px;text-align:center;color:var(--muted)}
.chips-f button[aria-pressed="false"]{opacity:.5;background:var(--off-bg)}
.chips-f button[aria-pressed="false"] .tp{filter:grayscale(1)}
.fl-sel{display:inline-flex;align-items:center;gap:6px;font-weight:600;color:var(--muted)}
.fl-sel select{font:inherit;padding:5px 8px;border:1.5px solid var(--line);border-radius:6px;background:var(--panel);color:var(--ink);max-width:240px}
#alBusca{min-width:280px;flex:1 1 280px;max-width:440px}
.fl-cont{margin-left:auto;color:var(--muted);font-variant-numeric:tabular-nums}
.dica{margin:2px 0 8px;color:var(--muted);font-size:13px}
.al-selbar{background:var(--warn-bg);border:1px solid var(--warn);border-radius:6px;padding:4px 10px;margin:0 0 8px}
.al-selbar .btn{padding:2px 10px}
.al-tab .sel-c{width:38px;text-align:center}
.al-tab .sel-c input{width:17px;height:17px;accent-color:var(--head);cursor:pointer}
tr.marcado td{box-shadow:inset 3px 0 0 var(--head)}
.demo-tag{display:inline-block;margin-left:6px;padding:0 6px;border:1.5px dashed var(--warn);border-radius:4px;color:var(--warn);font-size:11px;font-weight:700;vertical-align:1px}
@media (prefers-color-scheme:dark){ body.tema-mod .chips-f button,body.tema-mod .fl-sel select{background:var(--panel);color:var(--ink)} }
</style>''')

DEST.write_text(s, encoding="utf-8")
print("ok", DEST.relative_to(RAIZ), len(s)//1024, "KB")
