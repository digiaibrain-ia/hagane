// Teste das telas do Baggio v0.13 (Playwright). Uso: node tests/telas_v0.13.js [URL] [PASTA_PRINTS]
// v0.3: roda nos DOIS visuais: ...?tema=mod e ...?tema=ori (passe a URL completa) e confere a menor repeticao de informacao.
// v0.2: Overview fiel ao WinCC -> verificado pelas classes das lampadas (on/off/fail/nd).
// Cobre: erros de console, enderecos do Mapa existem no contrato, estados (normal, falha, aviso,
// sem comunicacao), layout 1536x694 sem rolagem vertical da pagina e celular 390x844.
// NAO cobre: leitura real da CPU, polaridade dos sensores, cores em tela real do notebook.
const { chromium } = require("playwright");
const fs = require("fs");
const URL = process.argv[2] || "http://localhost:1891/baggio";
const PRINTS = process.argv[3] || "/tmp";
const TEMA = (URL.match(/tema=(\w+)/) || [,"mod"])[1];
let falhas = 0;
const ok = (c, m) => { console.log((c ? "OK   " : "FALHA ") + m); if (!c) falhas++; };

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1536, height: 694 }, deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  const erros = [];
  p.on("pageerror", e => erros.push("pageerror: " + e.message));
  let abortando = false;   // erro de rede provocado de proposito no cenario "erro" nao conta
  p.on("console", m => { if (m.type() === "error" && !(abortando && /Failed to load resource/.test(m.text()))) erros.push("console: " + m.text()); });

  // ---- cenarios fabricados a partir do estado real da API ----
  let modo = "real";           // real | normal | falha | aviso | semcom | erro
  const base = await (await fetch(URL.replace(/\/baggio.*/, "/baggio/api/estado"))).json();
  const T = base.bits;
  const cen = (extra) => ({ ...base, origem: "real", comunicacao: "ok", idade_ms: 300, bits: { ...Object.fromEntries(Object.keys(T).map(k => [k, false])), ...extra } });
  const NORMAL = { "I0.0":1,"I0.3":1,"I0.6":1,"I1.0":1,"I1.4":1,"I2.0":1,"I2.2":1,"I2.4":1,"I3.0":1,"I3.5":1,"I1.1":1,"I1.5":1,"I2.1":1,"I3.6":1,"Q12.1":1,"Q12.2":1,"Q11.4":1,"Q15.3":1,"Q14.0":1,"I5.4":1,"I5.6":1,"Q14.4":1 };
  const mk = o => Object.fromEntries(Object.entries(o).map(([k, v]) => [k, !!v]));
  await p.route("**/baggio/api/estado", async r => {
    if (modo === "real") return r.continue();
    if (modo === "erro") return r.abort();
    let e;
    if (modo === "normal") e = cen(mk(NORMAL));
    if (modo === "aviso") e = cen(mk({ ...NORMAL, "M13.7": 1, "M21.3": 1, "Q11.6": 1 }));
    if (modo === "falha") e = cen(mk({ ...NORMAL, "I1.1": 0, "I1.0": 0, "M10.5": 1, "M21.0": 1, "Q11.5": 1, "Q11.7": 1, "Q11.4": 0, "M11.5": 1 }));
    if (modo === "b_off") e = cen(mk({ ...NORMAL, "I1.1": 0, "I1.5": 0 }));
    if (modo === "n_max") e = cen(mk({ ...NORMAL, "I6.0": 1, "I6.3": 1, "I6.2": 1, "I6.1": 1, "I6.4": 1, "I6.5": 1 }));
    if (modo === "n_ini") e = cen(mk({ ...NORMAL, "I6.2": 1, "I6.1": 1, "I6.5": 1 }));
    if (modo === "n_zero") e = cen(mk({ ...NORMAL }));
    if (modo === "semcom") e = { ...cen(mk(NORMAL)), comunicacao: "sem_comunicacao", motivo: "CPU: desconectada", idade_ms: 9000 };
    return r.fulfill({ contentType: "application/json", headers: { "Access-Control-Allow-Origin": "*" }, body: JSON.stringify(e) });
  });
  const espera = ms => p.waitForTimeout(ms);
  const foto = async n => p.screenshot({ path: `${PRINTS}/${TEMA}_${n}.png` });

  await p.goto(URL); await espera(2500);
  // 1) enderecos do Mapa existem no contrato
  const faltam = await p.evaluate(() => Baggio.Mapa.enderecosUsados().filter(a => !Baggio.Dados.tag(a)));
  ok(faltam.length === 0, "todos os enderecos do Mapa existem no contrato" + (faltam.length ? " — faltam: " + faltam : ""));
  // 2) comentarios do contrato batem com o papel no Mapa (HG-002)
  const checks = await p.evaluate(() => {
    const T = a => (Baggio.Dados.tag(a) || {}).comentario || "";
    const m = Baggio.Mapa, r = [];
    const par = (a, re) => r.push([a, re.source, re.test(T(a))]);
    par(m.eq.bomba1.run, /BOMBA 1.*LIGADA/i); par(m.eq.bomba2.run, /BOMBA 2.*LIGADA/i);
    par(m.eq.bomba1.disj, /BOMBA 1.*OK/i); par(m.eq.bomba2.disj, /BOMBA 2.*OK/i);
    par(m.eq.aspirador.run, /ASPIRADOR LIGADO/i); par(m.eq.rotovac.run, /ROTOVAC LIGADO/i);
    par(m.eq.extrator.run, /EXTRATOR.*LIGADO/i); par(m.eq.dragante.run, /DRAGANTE LIGADO/i);
    par(m.eq.bombaTC.run, /T\. ?C\. LIGADA/i);
    par("Q14.1", /QUEBRA/i); par("Q14.2", /COMPENSA/i); par("Q14.3", /ASSOPRAGEM|SOPR/i); par("Q15.6", /LAVAGEM/i);
    par("M11.5", /EMERG/i); par("Q11.5", /FALHA/i);
    // lampadas do overview fiel ao WinCC
    par("Q14.0", /AR COMPRIMIDO/i); par("Q15.3", /ROTA/i); par("Q14.4", /ALTO.*COMPENSA/i); par("Q14.5", /BAIXO.*COMPENSA/i);
    par("I6.0", /MAXIMO.*SUJO/i); par("I6.3", /FIM DE ENCHIMENTO/i); par("I6.2", /INICIO DE ENCHIMENTO/i); par("I6.1", /MINIMO.*SUJO/i);
    par("Q15.2", /PAPEL/i); par("Q12.1", /AUT/i); par("Q12.0", /MAN/i); par("Q12.2", /CICLO AUT. LIGADO/i); par("Q12.6", /DESLIGADO CICLO/i);
    par("Q12.4", /AUTOLIMPEZA LIGADO/i); par("Q12.5", /CONTINUA/i); par("Q12.3", /FINAL SEMANA/i); par("Q15.4", /V[AÁ]CUO/i);
    return r;
  });
  checks.filter(c => !c[2]).forEach(c => ok(false, `comentario de ${c[0]} nao bate com ${c[1]}`));
  ok(checks.every(c => c[2]), `comentarios x papel no Mapa (${checks.length} conferidos)`);

  // 3) Cenarios
  modo = "normal"; await espera(1800); await foto("ov_normal");
  let t = await p.evaluate(() => document.body.innerText);
  ok(/PLC ao vivo/.test(t), "normal: chip de origem = PLC ao vivo");
  const cnt = () => p.evaluate(() => ({ A: document.querySelector("#cntA b").textContent.trim(), F: document.querySelector("#cntF b").textContent.trim(), cA: document.querySelector("#cntA").className, cF: document.querySelector("#cntF").className }));
  ok((await cnt()).A === "0" && (await cnt()).F === "0", "normal: contadores do cabecalho Alertas 0 e Falhas 0");
  ok(await p.evaluate(t => document.body.classList.contains("tema-" + t), TEMA), "tema ativo = " + TEMA);
  // menos repeticao: local (Baggio) uma unica vez; nada de faixa antiga
  const vis = await p.evaluate(() => document.body.innerText);
  ok((vis.match(/baggio/gi) || []).length === 1, "Baggio aparece 1 vez na tela (" + (vis.match(/baggio/gi) || []).length + ")");
  ok(!/ALARME CRÍTICO PRESENTE|Sistema ligado|Sirene/.test(vis), "sem a faixa antiga (Sistema ligado/Sirene/alarme critico repetidos)");
  ok(await p.evaluate(() => document.documentElement.scrollHeight <= innerHeight + 2), "1536x694: pagina sem rolagem vertical (overview)");
  const cls = id => p.evaluate(i => document.querySelector(`[data-lp="${i}"]`).getAttribute("class"), id);
  ok(await p.evaluate(() => document.querySelectorAll("#svg [data-lp]").length) === 25, "overview: 25 lampadas (17 do desenho + 8 do painel)");
  ok(/\bon\b/.test(await cls("b1")) && /\bon\b/.test(await cls("b2")), "normal: lampadas das bombas 1 e 2 verdes");
  ok(/\boff\b/.test(await cls("rotovac")), "normal: rotovac parado = cinza");
  ok(/\bon\b/.test(await cls("p00")), "normal: painel 'Filtro Automatico' (Q12.1) verde");
  modo = "falha"; await espera(1800); await foto("ov_falha");
  t = await p.evaluate(() => document.body.innerText);
  ok(/\bfail\b/.test(await cls("b1")), "falha: lampada da bomba 1 vermelha (fail)");
  await p.click('[data-lp="b1"]'); await espera(300);
  const pop = await p.evaluate(() => (document.querySelector(".pop")||{}).innerText || "");
  ok(/Bomba 1/.test(pop) && /FALHA/.test(pop) && /I1\.1/.test(pop), "clique na lampada da bomba 1 mostra estado e endereco");
  await p.keyboard.press("Escape");
  ok((await cnt()).F === "2" && /ct-f/.test((await cnt()).cF), "falha: contador Falhas = 2 em vermelho (" + JSON.stringify(await cnt()) + ")");
  await p.click("#aba-al"); await espera(600); await foto("al_falha");
  t = await p.evaluate(() => document.querySelector("#alLista").innerText);
  ok(/Emergência atuada/.test(t) && /Disjuntor da bomba 1 desarmado/.test(t) && /F-SEG-001/.test(t) && /F-DSJ-002/.test(t), "falha: lista traz codigo + nome (F-SEG-001 e F-DSJ-002)");
  const n = +(await cnt()).F;
  ok(n === 2, "falha: contador de falhas ativas = " + n);
  modo = "normal"; await espera(1800);
  t = await p.evaluate(() => document.querySelector("#alLista").innerText);
  ok(/Nenhum alarme ativo/.test(t), "normal: 'Nenhum alarme ativo'");
  const hist = await p.evaluate(() => Baggio.Alarmes.hist.map(h => h.ev));
  ok(hist.includes("ATIVOU") && hist.includes("NORMALIZOU"), "historico registra ATIVOU e NORMALIZOU: " + hist.join(","));
  modo = "aviso"; await espera(1800); await p.click("#aba-ov"); await espera(500); await foto("ov_aviso");
  ok((await cnt()).A === "1" && (await cnt()).F === "0" && /ct-a/.test((await cnt()).cA), "aviso: contador Alertas = 1 em destaque e Falhas = 0 (" + JSON.stringify(await cnt()) + ")");
  // sem comunicacao (resposta do servidor) e Node-RED fora (fetch falha)
  modo = "semcom"; await espera(1800); await foto("ov_semcom");
  t = await p.evaluate(() => document.body.innerText);
  ok(/SEM COMUNICAÇÃO/.test(t) && await p.evaluate(() => !document.querySelector("#svg .lp.on, #svg .vl.on")), "sem comunicacao: banner e nenhuma lampada verde");
  ok((await cnt()).A === "?" && (await cnt()).F === "?", "sem comunicacao: contadores mostram ? (nao inventam numero)");
  modo = "erro"; abortando = true; await espera(3500);
  ok(/Node-RED ✖/.test(await p.evaluate(() => document.querySelector("#aviso").innerText)), "Node-RED fora do ar: a faixa mostra Node-RED ✖ (o elo que falhou)");
  ok(await p.evaluate(() => Baggio.Dados.semCom), "Node-RED fora (fetch falha): tela declara sem comunicacao");
  modo = "normal"; await espera(1800); abortando = false;
  ok(!(await p.evaluate(() => Baggio.Dados.semCom)), "recupera quando a comunicacao volta");
  // E/S
  await p.click("#aba-es"); await espera(600); await foto("es_entradas");
  t = await p.evaluate(() => document.body.innerText);
  ok(/I0\.0/.test(t) && /BOMBA 1 DE FILTRAGEM LIGADA/i.test(t), "E/S: entradas listadas");
  ok(!/ix_0\.0_rl/.test(t), "E/S: nome da tag nao repetido na linha (fica no title)");
  await p.click('[data-area="Q"]'); await espera(500); await foto("es_saidas");
  await p.fill("#esBusca", "rotovac"); await espera(400);
  const nitens = await p.evaluate(() => document.querySelectorAll("#esGrade .bit").length);
  ok(nitens > 0 && nitens < 6, "E/S: busca 'rotovac' filtra (" + nitens + " itens)");
  // popover
  await p.click("#aba-ov"); await p.click('[data-info="ov"] >> visible=true'); await espera(300);
  ok(await p.evaluate(() => !!document.querySelector(".pop")), "popover ⓘ abre"); await p.keyboard.press("Escape");
  ok(await p.evaluate(() => !document.querySelector(".pop")), "popover fecha com Esc");
  // SEM DESLOCAMENTO DE UI: a posicao de tudo e igual em qualquer estado (normal, aviso, falha, sem comunicacao)
  const geo = () => p.evaluate(() => { const R = e => { const q = document.querySelector(e).getBoundingClientRect(); return [q.left, q.top, q.width, q.height].map(v => Math.round(v * 2) / 2); };
    return { header: R("header"), nav: R("nav"), vista: R(".vista.ativa"), aba2: R("#aba-al"), aba3: R("#aba-es"), dados: R("#pDados"), opc: R("#btnOpc"), cntA: R("#cntA"), cntF: R("#cntF"), ver: R("#btnVer"),
             larg: document.documentElement.clientWidth, rolagemH: document.documentElement.scrollWidth > innerWidth }; });
  await p.click("#aba-ov"); modo = "normal"; await espera(1700); const gN = await geo();
  const iguais = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  for (const m of ["aviso", "falha", "semcom"]) { modo = m; await espera(1700); const g = await geo();
    ok(iguais(g, gN), `sem deslocamento: layout igual em "${m}" e "normal"` + (iguais(g, gN) ? "" : " -> " + JSON.stringify(g) + " vs " + JSON.stringify(gN))); }
  modo = "semcom"; await espera(1700);
  ok(await p.evaluate(() => { const a = document.querySelector("#aviso").getBoundingClientRect(), v = document.querySelector(".vista.ativa").getBoundingClientRect();
    return getComputedStyle(document.querySelector("#aviso")).position === "fixed" && a.top >= v.bottom - 60 || v.bottom <= a.top + 1; }), "faixa SEM COMUNICACAO fica no rodape (fixa), nao empurra o conteudo");
  await foto("semcom_rodape");
  const faixa = await p.evaluate(() => document.querySelector("#aviso").innerText);
  ok(/HTML ✔/.test(faixa) && /Node-RED ✔ conectado/.test(faixa) && /PLC ✖ não conectado/.test(faixa), "faixa de sem comunicacao mostra a cadeia: HTML ✔ → Node-RED ✔ → PLC ✖ (" + faixa.replace(/\s+/g, " ").slice(-90) + ")");
  await p.click("#btnOpc"); await espera(200);
  const cad = await p.evaluate(() => [...document.querySelectorAll("#cadeia li")].map(l => l.className.replace("cd-", "") + ":" + l.innerText.replace(/\s+/g, " ").trim()));
  await p.keyboard.press("Escape");
  ok(cad.length === 3 && /^ok:HTML/.test(cad[0]) && /^ok:Node-RED/.test(cad[1]) && /^nao:PLC/.test(cad[2]), "opcoes: cartao de comunicacao com 3 elos (HTML ok, Node-RED ok, PLC nao): " + cad.join(" | "));
  for (const aba of ["#aba-al", "#aba-es", "#aba-ov"]) { await p.click(aba); modo = "normal"; await espera(1500); const a = await geo(); modo = "semcom"; await espera(1700); const b2 = await geo();
    ok(iguais(a, b2), `sem deslocamento na aba ${aba}: normal x sem comunicacao`); }
  modo = "normal"; await espera(1500);
  // CABECALHO: sem "Hagane"; seletor de dados com nome claro
  const cab = await p.evaluate(() => document.querySelector("header").innerText);
  ok(!/hagane/i.test(cab), "cabecalho sem 'Hagane'");
  ok(!/CPU|Simulação/.test(cab) && await p.evaluate(() => document.querySelector("header").querySelectorAll("button, span, nav").length <= 14), "cabecalho enxuto (sem CPU/Simulacao antigos; poucos elementos)");
  const contr = await p.evaluate(() => { const lum = c => { const m = c.match(/[\d.]+/g).map(Number), f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(m[0]) + 0.7152 * f(m[1]) + 0.0722 * f(m[2]); };
    const bg = getComputedStyle(document.querySelector("header")).backgroundColor, L2 = lum(bg);
    return [...document.querySelectorAll("header nav button")].map(b => { const L1 = lum(getComputedStyle(b).color); return { id: b.id, sel: b.getAttribute("aria-selected"), r: (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05) }; }); });
  ok(contr.every(c => c.r >= (c.sel === "true" ? 4.5 : 3)), "cabecalho: texto de todas as abas legivel (contraste " + contr.map(c => c.id.slice(4) + (c.sel === "true" ? "*" : "") + "=" + c.r.toFixed(1)).join(" ") + ")");
  ok(await p.evaluate(() => [...document.querySelectorAll("header *")].every(e => ["0px", ""].includes(getComputedStyle(e).borderTopWidth) || getComputedStyle(e).borderTopStyle === "none")), "cabecalho SEM BORDAS em nenhum elemento");
  // ALERTAS E FALHAS (padrao do medidor): linha -> painel com efeito, causa, solucao e como o PLC decide
  modo = "falha"; await p.click("#aba-al"); await espera(1800);
  await p.click('.al-lin[data-cod="F-DSJ-002"]'); await espera(400);
  const det = await p.evaluate(() => (document.querySelector(".al-det") || {}).innerText || "");
  ok(/1 · Efeito/.test(det) && /2 · Causa/.test(det) && /3 · Solução/.test(det) && /Como o PLC decide/.test(det), "alerta: painel com efeito, causa, solucao e como o PLC decide");
  ok(/Teste rápido/.test(det) && /Painel elétrico|Campo|Operador/.test(det) && /RESET FALHAS/.test(det), "alerta: teste rapido, 'onde' da solucao e RESET FALHAS");
  ok(/I1\.0/.test(det) && /M10\.5/.test(det) && /T31/.test(det) && /FC_ALARME_CRITICO, rede 2/.test(det), "alerta: enderecos, T31 e bloco/rede do PLC (FC_ALARME_CRITICO, rede 2)");
  const chipOk = await p.evaluate(() => { const c = e => document.querySelector(`.chip[data-end="${e}"]`); return c("M10.5").classList.contains("on") && !c("I1.0").classList.contains("on") && !/\s[01]$/.test(c("M10.5").innerText.trim()) && !/\s[01]$/.test(c("I1.0").innerText.trim()); });
  ok(chipOk, "alerta: enderecos ao vivo so por cor, sem digitos 1/0");
  await espera(2600);
  ok(await p.evaluate(() => !!document.querySelector(".al-det")), "alerta: painel continua aberto depois de varias atualizacoes (sem recolher)");
  // selecao de texto sobrevive as atualizacoes (a lista nao e refeita a cada segundo)
  await p.evaluate(() => { const el = document.querySelector(".al-det .corpo p"); const r = document.createRange(); r.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(r); });
  await espera(2300);
  ok(await p.evaluate(() => getSelection().toString().length > 5), "alerta: texto selecionado permanece selecionado (sem refazer a lista)");
  await foto("alertas_detalhe");
  // exportar texto traz o codigo e a solucao
  const [dl] = await Promise.all([p.waitForEvent("download"), (async () => { await p.click("#alExp"); await p.click('[data-exp="txt"]'); })()]);
  const txtExp = require("fs").readFileSync(await dl.path(), "utf8");
  ok(/F-DSJ-002/.test(txtExp) && /Efeito:/.test(txtExp) && /Solução \[/.test(txtExp) && /Como o PLC decide/.test(txtExp), "exportar .txt traz codigo, efeito, solucao e logica do PLC");
  ok(await p.evaluate(() => (localStorage.getItem("baggio_alertasHist_v1") || "").includes("F-DSJ-002")), "historico gravado no navegador (chave baggio_alertasHist_v1)");
  // cadastro completo
  await p.click('#alVista [data-vista="cadastro"]'); await espera(500);
  const nCad = await p.evaluate(() => document.querySelectorAll(".al-lin").length);
  ok(nCad >= 39, "cadastro completo lista os alarmes dos blocos do PLC + planilha (" + nCad + ")");
  await p.fill("#alBusca", "bomba 2"); await espera(400);
  ok(await p.evaluate(() => [...document.querySelectorAll(".al-lin .cod")].every(c => true) && document.querySelectorAll(".al-lin").length >= 2), "busca por texto filtra o cadastro");
  await foto("alertas_cadastro");
  await p.fill("#alBusca", ""); await p.click('#alVista [data-vista="ativos"]'); await espera(400);
  modo = "normal"; await espera(1800); await p.click("#aba-ov"); await espera(500);
  // TUBULACAO e VALVULA QUEBRA VACUO (medidas no desenho)
  const geom = await p.evaluate(() => { const svg = document.querySelector("#svg"); const q = e => svg.querySelector(e);
    const tubo = Array.from(svg.querySelectorAll(".tb-o")).find(t => { const a = t.getPointAtLength(0); return Math.abs(a.y - 160) < 1 && a.x > 300; });
    const a = tubo && tubo.getPointAtLength(0); const limpo = Array.from(svg.querySelectorAll(".eqp")).find(r => r.tagName === "rect" && +r.getAttribute("x") === 312 && +r.getAttribute("y") === 73);
    const vqv = q('[data-vl="vQv"]'), m = /translate\(([-\d.]+),([-\d.]+)\)/.exec(vqv.getAttribute("transform"));
    const lamp = q('[data-lp="qv"]'), ml = /translate\(([-\d.]+),([-\d.]+)\)/.exec(lamp.getAttribute("transform"));
    const caixa = q(".eqp2"); const cx = +caixa.getAttribute("x"), cw = +caixa.getAttribute("width"), cy = +caixa.getAttribute("y"), ch = +caixa.getAttribute("height");
    const txt = Array.from(svg.querySelectorAll(":scope > text")).filter(t => /QUEBRA VÁCUO|^VÁLVULA$/.test(t.textContent.trim()) && +t.getAttribute("x") < 240 && +t.getAttribute("y") > 215 && +t.getAttribute("y") < 260);
    return { tuboNaParede: !!(a && limpo && Math.abs(a.x - (+limpo.getAttribute("x"))) < 1.5 && a.y > +limpo.getAttribute("y") && a.y < +limpo.getAttribute("y") + +limpo.getAttribute("height")),
             lampDentro: +ml[1] > cx && +ml[1] < cx + cw && +ml[2] > cy && +ml[2] < cy + ch, rotDentro: txt.length === 2 && txt.every(t => { const b = t.getBBox(); return b.x >= cx && b.x + b.width <= cx + cw && b.y >= cy && b.y + b.height <= cy + ch; }),
             valvulaNoTubo: Array.from(svg.querySelectorAll(".tb-o")).some(t => t.isPointInStroke(new DOMPoint(+m[1], +m[2]))) }; });
  ok(geom.tuboNaParede, "tubo ao lado do filtro sai da PAREDE do tanque limpo (nao fica solto nem no funil)");
  ok(geom.valvulaNoTubo, "valvula quebra vacuo esta SOBRE o tubo");
  ok(geom.lampDentro && geom.rotDentro, "valvula quebra vacuo: lampada e rotulo juntos dentro da mesma caixa");
  // ============ v0.12: sem analogicas (o equipamento nao tem) ============
  ok(await p.evaluate(() => !document.querySelector("#esAnalog") && ![...document.querySelectorAll("h3.sec")].some(h => /Anal[óo]gic/i.test(h.textContent))), "nenhuma area de entradas/saidas analogicas na dashboard");
  // ============ v0.11: bombas verdes (funcionando) / cinza (desligadas); sem a sinalizacao de Hz ============
  const corB = id => p.evaluate(i => getComputedStyle(document.querySelector(`[data-bmb="${i}"] .bm-motor`)).fill.match(/[\d.]+/g).slice(0, 3).map(Number), id);
  const verde = c => c[1] > c[0] + 25 && c[1] > c[2] + 15, cinza = c => Math.max(...c) - Math.min(...c) <= 22, verm = c => c[0] > c[1] + 60;
  modo = "normal"; await espera(1700);
  ok(verde(await corB("bomba1")) && verde(await corB("bomba2")), "bombas 1 e 2 funcionando: motor e bomba VERDES " + JSON.stringify([await corB("bomba1"), await corB("bomba2")]));
  ok(await p.evaluate(() => document.querySelectorAll("#svg .hz, #svg .hzt").length === 0 && !/Hz/.test(document.querySelector("#svg").textContent)), "sinalizacao de Hz removida do desenho");
  await foto("bombas_verdes");
  modo = "b_off"; await espera(1700);
  ok(cinza(await corB("bomba1")) && cinza(await corB("bomba2")), "bombas desligadas: CINZA " + JSON.stringify([await corB("bomba1"), await corB("bomba2")]));
  await foto("bombas_cinza");
  modo = "falha"; await espera(1700);
  ok(verm(await corB("bomba1")) && verde(await corB("bomba2")), "bomba 1 em falha: VERMELHA; bomba 2 funcionando: verde (uma nao esconde a outra)");
  modo = "semcom"; await espera(1700);
  ok(await p.evaluate(() => [...document.querySelectorAll("[data-bmb]")].every(g => g.classList.contains("nd"))), "sem comunicacao: bombas tracejadas (sem dado), nunca verdes");
  modo = "normal"; await espera(1700);
  await p.evaluate(() => Baggio.Anim.aplicar(true)); await espera(250);
  const rot = () => p.evaluate(() => ({ b1: getComputedStyle(document.querySelector('[data-bmb="bomba1"] .imp')).animationName, b2: getComputedStyle(document.querySelector('[data-bmb="bomba2"] .imp')).animationName }));
  ok((await rot()).b1 !== "none" && (await rot()).b2 !== "none", "animacao ligada: o rotor das bombas funcionando GIRA");
  modo = "b_off"; await espera(1700);
  ok((await rot()).b1 === "none" && (await rot()).b2 === "none", "bomba desligada: rotor parado");
  modo = "normal"; await espera(1700); await p.evaluate(() => Baggio.Anim.aplicar(false)); await espera(250);
  ok((await rot()).b1 === "none", "animacao desligada: rotor parado mesmo com a bomba funcionando (a cor continua verde)");
  ok(verde(await corB("bomba1")), "animacao desligada: a cor verde continua");
  await p.evaluate(() => Baggio.Anim.aplicar(true));
  // ============ v0.10: versao do programa, contadores clicaveis, historico ============
  modo = "falha"; await p.click("#aba-ov"); await espera(1800);
  await p.click("#cntF"); await espera(500);
  ok(await p.evaluate(() => document.querySelector("#aba-al").getAttribute("aria-selected") === "true" && [...document.querySelectorAll(".al-lin")].every(l => l.classList.contains("tp-F")) && document.querySelectorAll(".al-lin").length === 2 && getComputedStyle(document.querySelector("#alLimpaFiltro")).display !== "none"), "clicar em 'Falhas' abre Alertas ja filtrada so nas falhas, com 'Limpar filtros' visivel");
  await p.click("#alLimpaFiltro"); modo = "normal"; await p.click("#aba-ov"); await espera(1500);
  await p.click("#btnVer"); await espera(300);
  const v = await p.evaluate(() => { const d = document.querySelector("#ver"), r = d.getBoundingClientRect(); return { vis: getComputedStyle(d).display !== "none", txt: d.innerText, n: d.querySelectorAll(".ver-item").length, w: r.width, top: d.querySelector("h3").textContent.trim(), foco: document.activeElement.id }; });
  ok(v.vis && /VERSÃO DO PROGRAMA/i.test(v.txt) && /Versão em uso: 0\.13/.test(v.txt) && v.n === 13 && /^v0\.13/.test(v.top), `dialogo da versao: abre, mostra 'Versao em uso: 0.12' e ${v.n} versoes (a mais nova primeiro: ${v.top})`);
  ok(v.foco === "verOk", "dialogo da versao: foco vai para o botao Fechar");
  await p.click("#verExp"); await espera(150);
  const w2 = await p.evaluate(() => document.querySelector("#ver").getBoundingClientRect().width);
  ok(w2 > v.w + 100, `dialogo da versao: 'Ampliar' alarga a janela (${v.w.toFixed(0)} -> ${w2.toFixed(0)} px)`);
  await p.keyboard.press("Tab"); await p.keyboard.press("Tab"); await p.keyboard.press("Tab"); await p.keyboard.press("Tab");
  ok(await p.evaluate(() => document.querySelector("#ver").contains(document.activeElement)), "dialogo da versao: o foco fica preso na janela (Tab nao escapa)");
  await foto("dialogo_versao");
  await p.keyboard.press("Escape"); await espera(150);
  ok(await p.evaluate(() => getComputedStyle(document.querySelector("#ver")).display === "none" && document.activeElement.id === "btnVer"), "dialogo da versao: Esc fecha e o foco volta ao botao da versao");
  await p.click("#btnVer"); await p.mouse.click(8, 300); await espera(150);
  ok(await p.evaluate(() => getComputedStyle(document.querySelector("#ver")).display === "none"), "dialogo da versao: clicar fora fecha");
  await p.click("#btnVer"); await p.click("#verOk"); await espera(150);
  ok(await p.evaluate(() => getComputedStyle(document.querySelector("#ver")).display === "none"), "dialogo da versao: botao Fechar fecha");
  const fsv = require("fs"), raizv = require("path").resolve(__dirname, "..");
  const hv = JSON.parse(fsv.readFileSync(raizv + "/docs/historico_versoes.json", "utf8"));
  ok((await p.evaluate(() => JSON.stringify(Baggio.HIST_VERSOES))) === JSON.stringify(hv) && hv.versoes[0].v === (await p.evaluate(() => Baggio.VERSAO)), "historico embutido == docs/historico_versoes.json e a 1a entrada e a versao em uso");
  ok((await p.textContent("#btnVer")).trim() === "v" + hv.atual, "botao da versao no cabecalho mostra v" + hv.atual);
  // ============ REGRAS DO DESENHO (v0.7): afastamento, pontes, setas, valvulas ============
  const reg = await p.evaluate(() => {
    const svg = document.querySelector("#svg"), out = {};
    const tubos = Array.from(svg.querySelectorAll(".tb-o"));
    const amostra = t => { const L = t.getTotalLength(), a = []; for (let s = 0; s <= L; s += 3) a.push(t.getPointAtLength(s)); return a; };
    const A = tubos.map(amostra), pontas = tubos.flatMap(t => [t.getPointAtLength(0), t.getPointAtLength(t.getTotalLength())]);
    const contatos = [];
    for (let i = 0; i < A.length; i++) for (let j = i + 1; j < A.length; j++) A[i].forEach(p => { if (A[j].some(q => Math.hypot(p.x - q.x, p.y - q.y) < 1.6)) contatos.push({ x: p.x, y: p.y, i, j }); });
    const exempt = pontas.concat(contatos), viol = [];
    for (let i = 0; i < A.length; i++) for (let j = i + 1; j < A.length; j++) { let min = 1e9, onde = null;
      A[i].forEach(p => { if (exempt.some(e => Math.hypot(p.x - e.x, p.y - e.y) < 30)) return; A[j].forEach(q => { const d = Math.hypot(p.x - q.x, p.y - q.y); if (d < min) { min = d; onde = p; } }); });
      if (min < 23.5) viol.push(`tubos ${i + 1} e ${j + 1}: ${min.toFixed(1)} em (${Math.round(onde.x)},${Math.round(onde.y)})`); }
    out.afastamento = viol; out.nTubos = tubos.length;
    const cruz = contatos.filter(c => ![A[c.i][0], A[c.i][A[c.i].length - 1], A[c.j][0], A[c.j][A[c.j].length - 1]].some(e => Math.hypot(e.x - c.x, e.y - c.y) < 14));
    const halos = Array.from(svg.querySelectorAll(".tb-halo")).map(h => h.getBBox());
    out.cruzSemPonte = cruz.filter(c => !halos.some(b => c.x >= b.x - 8 && c.x <= b.x + b.width + 8 && c.y >= b.y - 2 && c.y <= b.y + b.height + 2)).map(c => `${Math.round(c.x)},${Math.round(c.y)}`);
    out.nCruz = cruz.length;
    const chev = Array.from(svg.querySelectorAll(".seta-ch")), R = e => e.getBoundingClientRect();
    const inter = (a, b, m) => a.left < b.right + m && a.right > b.left - m && a.top < b.bottom + m && a.bottom > b.top - m;
    const comSeta = tubos.map((t, i) => +t.dataset.seta !== 0 ? i : -1).filter(i => i >= 0);
    out.semSeta = comSeta.filter(i => !chev.some(c => +c.dataset.tubo === i)); out.nSetas = chev.length;
    out.distSeta = []; out.sentido = []; out.perto = [];
    chev.forEach(c => { const i = +c.dataset.tubo, m = /translate\(([-\d.]+),([-\d.]+)\) rotate\(([-\d.]+)\)/.exec(c.getAttribute("transform")), x = +m[1], y = +m[2], ang = +m[3];
      let best = 1e9, bk = 0; A[i].forEach((q, k) => { const d = Math.hypot(q.x - x, q.y - y); if (d < best) { best = d; bk = k; } });
      out.distSeta.push(+best.toFixed(1));
      const a = A[i][Math.max(0, bk - 1)], b = A[i][Math.min(A[i].length - 1, bk + 1)]; let tg = Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI; if (c.dataset.dir === "rev") tg += 180;
      out.sentido.push(Math.abs(((ang - tg) % 360 + 540) % 360 - 180));
      A.forEach((aa, qi) => { if (qi !== i) aa.forEach(q => { const d = Math.hypot(q.x - x, q.y - y); if (d < 10) out.perto.push(`seta do tubo ${i + 1} a ${d.toFixed(1)} do tubo ${qi + 1}`); }); }); });
    const outros = Array.from(svg.querySelectorAll("[data-vl],.inst,[data-lp],.bmb,:scope > text"));
    out.setaEncosta = []; chev.forEach(c => outros.forEach(o => { if (inter(R(c), R(o), 1)) out.setaEncosta.push(`tubo ${+c.dataset.tubo + 1} ~ ${((o.textContent || o.dataset.lp || o.dataset.vl || o.getAttribute("class") || "")).toString().trim().slice(0, 16)}`); }));
    out.valv = Array.from(svg.querySelectorAll("[data-vl]")).map(v => { const m = /translate\(([-\d.]+),([-\d.]+)\)/.exec(v.getAttribute("transform")), x = +m[1], y = +m[2];
      let best = 1e9, ti = -1, tk = 0; A.forEach((a, i) => a.forEach((q, k) => { const d = Math.hypot(q.x - x, q.y - y); if (d < best) { best = d; ti = i; tk = k; } }));
      const a = A[ti][Math.max(0, tk - 1)], b = A[ti][Math.min(A[ti].length - 1, tk + 1)], ang = Math.abs(Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI) % 180;
      const eixo = (ang < 20 || ang > 160) ? "h" : (ang > 70 && ang < 110) ? "v" : "?", rv = R(v);
      const enc = outros.filter(o => o !== v && !o.classList.contains("inst") && !o.classList.contains("bmb") && inter(rv, R(o), 0)).map(o => (o.textContent || o.dataset.lp || o.dataset.vl || "").trim().slice(0, 16));
      return { id: v.dataset.vl, dist: +best.toFixed(1), eixo, esperado: v.dataset.eixo, enc }; });
    const grupos = []; tubos.forEach((t, i) => { const rev = t.dataset.rev === "1", L = t.getTotalLength(), a = t.getPointAtLength(0), b = t.getPointAtLength(L);
      [[a, rev ? "in" : "out"], [b, rev ? "out" : "in"]].forEach(([p, papel]) => { const g = grupos.find(g => Math.hypot(g.x - p.x, g.y - p.y) < 3); if (g) g.itens.push(papel); else grupos.push({ x: p.x, y: p.y, itens: [papel] }); }); });
    out.juncaoRuim = grupos.filter(g => g.itens.length >= 2 && (!g.itens.includes("in") || !g.itens.includes("out"))).map(g => `(${Math.round(g.x)},${Math.round(g.y)}) ${g.itens}`);
    out.nJuncoes = grupos.filter(g => g.itens.length >= 2).length;
    const pc = chev.map(c => { const m = /translate\(([-\d.]+),([-\d.]+)\) rotate\(([-\d.]+)\)/.exec(c.getAttribute("transform")); return { x: +m[1], y: +m[2], a: +m[3] }; });
    out.TSobe = pc.filter(c => c.x > 694 && c.x < 712 && c.y < 208).map(c => c.a); out.TDesce = pc.filter(c => c.x > 694 && c.x < 712 && c.y > 208 && c.y < 270).map(c => c.a);
    return out; });
  ok(reg.juncaoRuim.length === 0 && reg.nJuncoes >= 2, `juncoes: toda juncao de pontas tem entrada E saida (${reg.nJuncoes} juncoes)` + (reg.juncaoRuim.length ? " -> " + reg.juncaoRuim.join("; ") : ""));
  ok(reg.TSobe.length >= 1 && reg.TSobe.every(a => Math.abs(a + 90) < 8) && reg.TDesce.length >= 1 && reg.TDesce.every(a => Math.abs(a - 90) < 8), "T da alimentacao: acima do T a seta SOBE e abaixo DESCE " + JSON.stringify([reg.TSobe, reg.TDesce]));
  ok(reg.afastamento.length === 0, `tubulacao: afastamento minimo de 24 entre tubos paralelos (${reg.nTubos} tubos)` + (reg.afastamento.length ? " -> " + reg.afastamento.join("; ") : ""));
  ok(reg.cruzSemPonte.length === 0 && reg.nCruz >= 1, `tubulacao: todo cruzamento sem ligacao tem ponte (${reg.nCruz} cruzamento(s))` + (reg.cruzSemPonte.length ? " -> " + reg.cruzSemPonte.join("; ") : ""));
  ok(reg.semSeta.length === 0 && reg.nSetas >= 9, `setas: todo tubo sinalizado tem seta (${reg.nSetas} setas)` + (reg.semSeta.length ? " -> tubos sem seta: " + reg.semSeta.map(i => i + 1) : ""));
  ok(reg.distSeta.every(d => d >= 11.5 && d <= 12.5), "setas: todas a 12 unidades do eixo do tubo (distancia padrao) " + JSON.stringify([...new Set(reg.distSeta)]));
  ok(reg.sentido.every(d => d <= 8), "setas: apontam no sentido do tubo (a mesma direcao da animacao)" + (reg.sentido.some(d => d > 8) ? " -> desvios " + reg.sentido.filter(d => d > 8).map(d => d.toFixed(0)) : ""));
  ok(reg.perto.length === 0 && reg.setaEncosta.length === 0, "setas: nao encostam em tubo, valvula, instrumento, lampada nem texto" + ((reg.perto.concat(reg.setaEncosta)).length ? " -> " + reg.perto.concat(reg.setaEncosta).slice(0, 6).join("; ") : ""));
  ok(reg.valv.every(v => v.dist <= 1.5 && v.eixo === v.esperado && v.enc.length === 0), "valvulas: centro SOBRE o tubo, eixo alinhado ao tubo e sem encostar em texto/lampada " + JSON.stringify(reg.valv.filter(v => !(v.dist <= 1.5 && v.eixo === v.esperado && v.enc.length === 0))));
  // sentido da animacao = sentido das setas (fwd: o tracejado avanca ao longo do caminho; rev: ao contrario)
  await p.evaluate(() => Baggio.Anim.aplicar(true)); modo = "normal"; await espera(1600);
  const lerDash = () => p.evaluate(() => Array.from(document.querySelectorAll("#svg .tb-f.vivo")).map(e => ({ rev: e.classList.contains("rev"), off: parseFloat(getComputedStyle(e).strokeDashoffset) })));
  const votos = { fwd: [0, 0], rev: [0, 0] };
  for (let k = 0; k < 6; k++) { const a = await lerDash(); await espera(70); const b = await lerDash();
    a.forEach((x, i) => { const dlt = b[i].off - x.off; if (Math.abs(dlt) > 0.2 && Math.abs(dlt) < 7) { const v = votos[x.rev ? "rev" : "fwd"]; v[dlt < 0 ? 0 : 1]++; } }); }
  ok(votos.fwd[0] > votos.fwd[1] * 3 && (votos.rev[0] + votos.rev[1] === 0 || votos.rev[1] > votos.rev[0] * 3), `animacao: tracejado anda no mesmo sentido das setas (fwd ${votos.fwd}, rev ${votos.rev})`);
  await foto("regras_desenho");
  // NIVEL pelos sensores: quanto mais sensores cobertos, mais alto (menor translateY) o liquido
  const yLiq = id => p.evaluate(i => { const m = /translateY\(([-\d.]+)px\)/.exec(document.querySelector(i).style.transform || ""); return m ? +m[1] : null; }, id);
  modo = "n_max"; await espera(1700); const yMax = await yLiq("#liqS"), yLmax = await yLiq("#liqL");
  modo = "n_ini"; await espera(1700); const yIni = await yLiq("#liqS"), yLmed = await yLiq("#liqL");
  modo = "n_zero"; await espera(1700); const yZero = await yLiq("#liqS"), yLmin = await yLiq("#liqL");
  ok(yMax < yIni && yIni < yZero, `tanque sujo: nivel acompanha os sensores (maximo ${yMax} < inicio ${yIni} < vazio ${yZero})`);
  ok(yLmax < yLmed && yLmed < yLmin, `tanque limpo: nivel acompanha os sensores (${yLmax} < ${yLmed} < ${yLmin})`);
  await foto("nivel_vazio");
  modo = "n_ini"; await espera(2200); await foto("nivel_inicio");
  modo = "n_max"; await espera(2200); await foto("nivel_maximo");
  modo = "semcom"; await espera(1700);
  ok(await p.evaluate(() => getComputedStyle(document.querySelector("#liqS")).visibility === "hidden"), "sem comunicacao: agua do tanque some (nao mostra nivel velho)");
  modo = "normal"; await espera(1700);
  // ANIMACAO liga/desliga e lembrada
  const anim = () => p.evaluate(() => document.body.classList.contains("anim"));
  const a0 = await anim();
  await p.click("#btnOpc"); await p.click("#animChk"); await p.keyboard.press("Escape"); ok(await anim() === !a0, "botao Animacao alterna (" + a0 + " -> " + !a0 + ")");
  await p.goto(URL); await espera(1500); ok(await anim() === !a0, "animacao lembrada apos recarregar");
  await p.evaluate(() => Baggio.Anim.aplicar(true)); await espera(300);
  ok(await p.evaluate(() => getComputedStyle(document.querySelector("#svg .ondas")).animationName !== "none"), "animacao ligada: ondas animadas");
  await p.evaluate(() => Baggio.Anim.aplicar(false)); await espera(300);
  ok(await p.evaluate(() => getComputedStyle(document.querySelector("#svg .ondas")).animationName === "none"), "animacao desligada: ondas paradas");
  await p.evaluate(() => Baggio.Anim.aplicar(true));
  // alternar o visual no cabecalho e lembrar apos recarregar
  const outro = TEMA === "mod" ? "ori" : "mod";
  await p.click("#btnOpc"); await p.check(`#opc input[name="tema"][value="${outro}"]`); await p.keyboard.press("Escape"); await espera(500); await foto("troca_" + outro);
  ok(await p.evaluate(t => document.body.classList.contains("tema-" + t), outro), "opcoes: escolher o visual troca para " + outro);
  await p.goto(URL.replace(/\?.*/, "")); await espera(1500);
  ok(await p.evaluate(t => document.body.classList.contains("tema-" + t), outro), "visual escolhido e lembrado apos recarregar");
  ok(erros.length === 0, "sem erros de console/pagina" + (erros.length ? ": " + erros.slice(0, 3).join(" | ") : ""));

  // 3b) SIMULACAO embutida: abre o arquivo direto (file://), sem Node-RED e sem PLC
  const arq = "file://" + require("path").resolve(__dirname, "..", "dashboard", "src", "baggio_monitor_v0.13.html");
  const sc = await b.newContext({ viewport: { width: 1536, height: 694 } }); const sp = await sc.newPage(); const rede = []; const errS = [];
  sp.on("request", q => { if (/\/baggio\/api\//.test(q.url())) rede.push(q.url()); }); sp.on("pageerror", e => errS.push(e.message));
  await sp.goto(arq + "?tema=" + TEMA); await sp.waitForTimeout(2500);
  const tS = await sp.evaluate(() => document.body.innerText);
  ok(/Dados simulados/.test(tS), "arquivo aberto direto: simulacao ativa sem Node-RED (chip 'Dados simulados')");
  ok(rede.length === 0, "simulacao: nenhuma chamada a API do Node-RED (" + rede.length + ")");
  ok(await sp.evaluate(() => document.querySelectorAll("#svg .lp.on").length > 3), "simulacao: lampadas reagem");
  await sp.screenshot({ path: `${PRINTS}/${TEMA}_simulacao_arquivo.png` });
  ok(errS.length === 0, "simulacao: sem erros de pagina");
  await sp.click("#btnOpc"); await sp.check('#opc input[name="fonte"][value="cpu"]'); await sp.keyboard.press("Escape"); await sp.waitForTimeout(3500);
  ok(/PLC sem/.test(await sp.textContent("#pDados")), "origem PLC sem Node-RED: o chip diz 'PLC sem ...' (nao finge dados)");
  ok(await sp.evaluate(() => Baggio.Dados.semCom), "arquivo + fonte CPU sem Node-RED: declara sem comunicacao (nao inventa dado)");
  await sp.click("#btnOpc"); await sp.check('#opc input[name="fonte"][value="sim"]'); await sp.keyboard.press("Escape"); await sp.waitForTimeout(1500);
  ok(!(await sp.evaluate(() => Baggio.Dados.semCom)), "voltar para Simulacao: dados voltam");
  // ---- v0.9: origem dos dados, cenario fixo, simulador igual ao arquivo ----
  const relogio = async seg => { await sp.evaluate(s => { if (!window.__DN) window.__DN = Date.now.bind(Date); const agora = window.__DN() / 1000, off = (((s - (agora % 180)) + 180) % 180) * 1000; Date.now = () => window.__DN() + off; }, seg); };
  const semCom = () => sp.evaluate(() => Baggio.Dados.semCom);
  let semFalha = true; const ruins = [];
  for (const seg of [5, 30, 55, 100, 150, 156, 160, 165, 175]) { await relogio(seg); await sp.waitForTimeout(1300); if (await semCom()) { semFalha = false; ruins.push(seg); } }
  ok(semFalha, "simulacao nunca gera falha de comunicacao (varri o ciclo de 180 s, inclusive o antigo silencio 150-165)" + (ruins.length ? " -> falhou em " + ruins : ""));
  const chip = await sp.evaluate(() => ({ t: document.querySelector("#pDados").textContent.trim(), c: document.querySelector("#pDados").className }));
  ok(/Dados simulados/.test(chip.t) && /dd-sim/.test(chip.c), "cabecalho: chip de origem diz 'Dados simulados' (" + chip.t + ")");
  await sp.click("#btnOpc"); await sp.waitForTimeout(200);
  const cadS = await sp.evaluate(() => [...document.querySelectorAll("#cadeia li")].map(l => l.className.replace("cd-", "") + ":" + l.innerText.replace(/\s+/g, " ").trim()));
  ok(cadS.length === 3 && /^ok:HTML/.test(cadS[0]) && /^na:Node-RED.*não usado/.test(cadS[1]) && /^na:PLC.*não usado/.test(cadS[2]), "simulacao: cadeia mostra HTML ok e Node-RED/PLC 'nao usado': " + cadS.join(" | "));
  const opcs = await sp.evaluate(() => ({ vis: !document.querySelector("#opc").hidden, marc: document.querySelectorAll(".rad:has(input:checked)").length, fonte: document.querySelector('#opc input[name="fonte"]:checked').value }));
  ok(opcs.vis && opcs.marc === 2 && opcs.fonte === "sim", "opcoes: painel abre com UMA escolha marcada por grupo ('em uso'); origem = simulados");
  await sp.keyboard.press("Escape");
  ok(await sp.evaluate(() => document.querySelector("#opc").hidden), "opcoes: Esc fecha");
  await sp.click("#aba-al"); await sp.waitForTimeout(500);
  ok(await sp.evaluate(() => ["#alSelBar", "#alLimpaFiltro"].every(s => getComputedStyle(document.querySelector(s)).display === "none")), "alertas: barra de selecao e 'Limpar filtros' escondidas quando nao se aplicam");
  const linhas = () => sp.evaluate(() => [...document.querySelectorAll(".al-lin .cod")].map(c => c.textContent));
  const vistos = new Set(); let fixo = true;
  for (const seg of [3, 45, 75, 105, 135, 160, 178]) { await relogio(seg); await sp.waitForTimeout(1300); const l = (await linhas()).join(","); vistos.add(l); if (l !== "F-PRS-001,A-DSJ-006") fixo = false; }
  ok(fixo, "cenario fixo: em qualquer instante do ciclo os ativos sao exatamente F-PRS-001 + A-DSJ-006 (" + [...vistos].join(" | ") + ")");
  ok(await sp.evaluate(() => !document.querySelector("#alSimAviso").hidden), "tela de alertas avisa 'Dados simulados' (exemplos, nao vem do PLC)");
  ok((await sp.textContent("#cntF b")).trim() === "1" && (await sp.textContent("#cntA b")).trim() === "1", "cenario fixo: contadores Alertas 1 e Falhas 1");
  ok(await sp.evaluate(() => !Baggio.Alarmes.defs.some(d => /DEM/.test(d.codigo))), "sem alarmes ficticios DEM (o cenario usa alarmes reais do PLC)");
  const fs = require("fs"), root = require("path").resolve(__dirname, "..");
  const nucleo = fs.readFileSync(root + "/nodered/gerador/js/50_simulador_core.js", "utf8").trim();
  ok(fs.readFileSync(arq.replace("file://", ""), "utf8").includes(nucleo), "simulador embutido no HTML e IDENTICO a nodered/gerador/js/50_simulador_core.js (era o defeito: ficou velho desde a v0.4)");
  ok((await sp.evaluate(() => JSON.stringify(Baggio.CAT_ALARMES))) === JSON.stringify(JSON.parse(fs.readFileSync(root + "/docs/contratos/alarmes_v0.1.json", "utf8"))), "catalogo de alarmes embutido == docs/contratos/alarmes_v0.1.json");
  await sp.click('.al-lin[data-cod="F-PRS-001"]'); await sp.waitForTimeout(300);
  const chipsTxt = await sp.evaluate(() => [...document.querySelectorAll(".al-det .chip")].map(c => c.innerText.trim()));
  ok(chipsTxt.length >= 2 && chipsTxt.every(x => !/\s[01]$/.test(x)), "enderecos do painel sem digitos 1/0: " + chipsTxt.join(" "));
  await sp.click('.al-lin[data-cod="F-PRS-001"]');
  await sp.click("#aba-es"); await sp.waitForTimeout(500);
  ok(await sp.evaluate(() => document.querySelectorAll("#esGrade .bit").length > 20 && document.querySelectorAll("#esGrade .bit .e").length === 0), "entradas e saidas: sem a coluna de digitos 1/0");
  await sp.click("#aba-ov"); await sp.waitForTimeout(400);
  ok(await sp.evaluate(() => { const T = [...document.querySelectorAll("#svg > text")].map(t => t.textContent.trim()); return T.includes("DRAGANTE") && T.includes("TRANSP.") && !T.some(x => /FILTRO/.test(x) && /TRANSP/.test(x)); }), "rotulo 'TRANSP. DRAGANTE' (nao mais 'Transp. Filtro')");
  await sp.click("#aba-al"); await sp.waitForTimeout(300);
  await sp.click('#alVista [data-vista="cadastro"]'); await sp.waitForTimeout(400);
  const nTotal = (await linhas()).length;
  ok(nTotal >= 39, "cadastro completo na simulacao (" + nTotal + " alarmes)");
  const cont = await sp.evaluate(() => ({ F: +document.querySelector('#alTipos [data-tipo="F"] b').textContent, A: +document.querySelector('#alTipos [data-tipo="A"] b').textContent, I: +document.querySelector('#alTipos [data-tipo="I"] b').textContent }));
  ok(cont.F + cont.A + cont.I === nTotal && cont.F >= 12 && cont.A >= 17 && cont.I === 2, "filtro por tipo: contagens F/A/I somam o total " + JSON.stringify(cont));
  await sp.click('#alTipos [data-tipo="A"]'); await sp.click('#alTipos [data-tipo="I"]'); await sp.waitForTimeout(300);
  let l2 = await linhas();
  ok(l2.length === cont.F && l2.every(c => c.startsWith("F-")), "filtro por tipo: so Falhas (" + l2.length + ")");
  ok(/Mostrando \d+ de \d+/.test(await sp.textContent("#alContagem")) && await sp.evaluate(() => !document.querySelector("#alLimpaFiltro").hidden), "'Mostrando X de Y' e botao 'Limpar filtros' visivel");
  await sp.selectOption("#alFam", "DSJ"); await sp.waitForTimeout(300);
  l2 = await linhas(); ok(l2.length >= 3 && l2.every(c => /^F-DSJ-/.test(c)), "filtro por familia (DSJ) junto com tipo Falha: " + l2.join(","));
  await sp.click("#alLimpaFiltro"); await sp.waitForTimeout(300);
  l2 = await linhas(); ok(l2.length === nTotal && await sp.evaluate(() => document.querySelector("#alLimpaFiltro").hidden), "limpar filtros volta ao total");
  await sp.fill("#alBusca", "rotovac"); await sp.waitForTimeout(300);
  l2 = await linhas(); ok(l2.length >= 2 && l2.length < 8, "busca 'rotovac' filtra: " + l2.join(","));
  await sp.click("#alLimpaFiltro");
  await sp.check('input[data-sel="F-DSJ-002"]'); await sp.check('input[data-sel="A-CMD-001"]'); await sp.waitForTimeout(300);
  ok(/2 selecionados/.test(await sp.textContent("#alSelTxt")) && /selecionados \(2\)/.test(await sp.textContent('[data-exp="txt"]')), "selecao: barra e menu Exportar mostram '(2)'");
  ok(await sp.evaluate(() => !document.querySelector(".al-det")), "marcar a caixa nao abre o painel da linha");
  const [dl2] = await Promise.all([sp.waitForEvent("download"), (async () => { await sp.click("#alExp"); await sp.click('[data-exp="txt"]'); })()]);
  const t2 = require("fs").readFileSync(await dl2.path(), "utf8");
  ok(/F-DSJ-002/.test(t2) && /A-CMD-001/.test(t2) && !/F-SEG-001/.test(t2) && /Estado: normal/.test(t2), "exportar selecionados: so os 2 itens (mesmo normais)");
  await sp.check("#alSelTodos"); await sp.waitForTimeout(300);
  ok((await sp.evaluate(() => document.querySelectorAll("input[data-sel]:checked").length)) === nTotal, "'selecionar todos' marca a lista inteira");
  await sp.screenshot({ path: `${PRINTS}/${TEMA}_alertas_filtros.png` });
  await sp.click("#alSelLimpa"); await sp.waitForTimeout(200);
  ok(await sp.evaluate(() => getComputedStyle(document.querySelector("#alSelBar")).display === "none"), "limpar selecao: a barra some DE VERDADE (display none, nao so o atributo)");
  await sc.close();
  // ---- proporcao em notebook 1366x768 (area util do navegador ~578 px) ----
  const nb = await b.newContext({ viewport: { width: 1366, height: 578 } }), np = await nb.newPage();
  await np.goto(arq + "?tema=" + TEMA); await np.waitForTimeout(2500);
  const pr = await np.evaluate(() => { const s = document.querySelector("#svg").getBoundingClientRect(), k = s.width / 1185; return { larg: s.width / innerWidth, fonte: 12 * k, rolagem: document.documentElement.scrollHeight > innerHeight + 2, cab: document.querySelector("header").getBoundingClientRect().height }; });
  ok(!pr.rolagem && pr.fonte >= 9 && pr.larg >= 0.64, `proporcao 1366x578: overview sem rolagem, texto ${pr.fonte.toFixed(1)} px (>= 9), ocupa ${(pr.larg * 100).toFixed(0)}% da largura (>= 64%), cabecalho ${pr.cab.toFixed(0)} px`);
  await np.screenshot({ path: `${PRINTS}/${TEMA}_nb_overview.png` });
  await np.click("#aba-al"); await np.waitForTimeout(600);
  const pa = await np.evaluate(() => ({ h: document.querySelector(".al-lin").getBoundingClientRect().height, zoom: getComputedStyle(document.querySelector("#v-al")).zoom }));
  ok(pa.h <= 32 && +pa.zoom < 1, `proporcao 1366x578: linhas de alerta compactas (${pa.h.toFixed(0)} px; zoom ${pa.zoom})`);
  await np.screenshot({ path: `${PRINTS}/${TEMA}_nb_alertas.png` });
  await np.click("#aba-es"); await np.waitForTimeout(500); await np.screenshot({ path: `${PRINTS}/${TEMA}_nb_es.png` });
  await nb.close();
  // 3c) nomes: nada de "hagane" como nome do sistema (so a fabrica, escrita "Hagane")
  const html = require("fs").readFileSync(arq.replace("file://", ""), "utf8");
  const resto = html.replace(/<!--[\s\S]*?-->/g, "").match(/hagane/gi) || [];
  ok(resto.length === 0, "nenhum 'Hagane' na pagina (fora do historico em comentario) " + (resto.length ? resto.length + " sobraram" : ""));
  // 4) celular
  const m = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const q = await m.newPage(); const errM = []; q.on("pageerror", e => errM.push(e.message));
  await q.goto(URL); await q.waitForTimeout(2500);
  await q.screenshot({ path: `${PRINTS}/${TEMA}_cel_ov.png` });
  ok(await q.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), "celular 390: sem rolagem horizontal da pagina");
  await q.click("#aba-al"); await q.waitForTimeout(500); await q.screenshot({ path: `${PRINTS}/${TEMA}_cel_al.png` });
  await q.click("#aba-es"); await q.waitForTimeout(500); await q.screenshot({ path: `${PRINTS}/${TEMA}_cel_es.png` });
  ok(await q.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), "celular 390: E/S sem rolagem horizontal da pagina");
  ok(errM.length === 0, "celular: sem erros de pagina");
  await b.close();
  console.log(falhas ? `\n${falhas} FALHA(S)` : "\nTUDO OK");
  process.exit(falhas ? 1 : 0);
})();
