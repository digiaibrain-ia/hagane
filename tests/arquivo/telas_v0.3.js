// Teste das telas do Hagane v0.3 (Playwright). Uso: node tests/telas_v0.3.js [URL] [PASTA_PRINTS]
// v0.3: roda nos DOIS visuais: ...?tema=mod e ...?tema=ori (passe a URL completa) e confere a menor repeticao de informacao.
// v0.2: Overview fiel ao WinCC -> verificado pelas classes das lampadas (on/off/fail/nd).
// Cobre: erros de console, enderecos do Mapa existem no contrato, estados (normal, falha, aviso,
// sem comunicacao), layout 1536x694 sem rolagem vertical da pagina e celular 390x844.
// NAO cobre: leitura real da CPU, polaridade dos sensores, cores em tela real do notebook.
const { chromium } = require("playwright");
const fs = require("fs");
const URL = process.argv[2] || "http://localhost:1891/hagane";
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
  const base = await (await fetch(URL.replace(/\/hagane.*/, "/hagane/api/estado"))).json();
  const T = base.bits;
  const cen = (extra) => ({ ...base, comunicacao: "ok", idade_ms: 300, bits: { ...Object.fromEntries(Object.keys(T).map(k => [k, false])), ...extra } });
  const NORMAL = { "I0.0":1,"I0.3":1,"I0.6":1,"I1.0":1,"I1.4":1,"I2.0":1,"I2.2":1,"I2.4":1,"I3.0":1,"I3.5":1,"I1.1":1,"I1.5":1,"I2.1":1,"I3.6":1,"Q12.1":1,"Q12.2":1,"Q11.4":1,"Q15.3":1,"Q14.0":1,"I5.4":1,"I5.6":1,"Q14.4":1 };
  const mk = o => Object.fromEntries(Object.entries(o).map(([k, v]) => [k, !!v]));
  await p.route("**/hagane/api/estado", async r => {
    if (modo === "real") return r.continue();
    if (modo === "erro") return r.abort();
    let e;
    if (modo === "normal") e = cen(mk(NORMAL));
    if (modo === "aviso") e = cen(mk({ ...NORMAL, "M13.7": 1, "M21.3": 1, "Q11.6": 1 }));
    if (modo === "falha") e = cen(mk({ ...NORMAL, "I1.1": 0, "M12.2": 1, "M21.0": 1, "Q11.5": 1, "Q11.7": 1, "Q11.4": 0, "I0.1": 1, "M11.5": 1 }));
    if (modo === "semcom") e = { ...cen(mk(NORMAL)), comunicacao: "sem_comunicacao", motivo: "CPU: desconectada", idade_ms: 9000 };
    return r.fulfill({ contentType: "application/json", headers: { "Access-Control-Allow-Origin": "*" }, body: JSON.stringify(e) });
  });
  const espera = ms => p.waitForTimeout(ms);
  const foto = async n => p.screenshot({ path: `${PRINTS}/${TEMA}_${n}.png` });

  await p.goto(URL); await espera(2500);
  // 1) enderecos do Mapa existem no contrato
  const faltam = await p.evaluate(() => Hagane.Mapa.enderecosUsados().filter(a => !Hagane.Dados.tag(a)));
  ok(faltam.length === 0, "todos os enderecos do Mapa existem no contrato" + (faltam.length ? " — faltam: " + faltam : ""));
  // 2) comentarios do contrato batem com o papel no Mapa (HG-002)
  const checks = await p.evaluate(() => {
    const T = a => (Hagane.Dados.tag(a) || {}).comentario || "";
    const m = Hagane.Mapa, r = [];
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
  ok(/comunicação OK/.test(t), "normal: comunicacao OK");
  const estado = () => p.evaluate(() => document.querySelector("#pEstado").textContent.trim());
  ok(/Em operação/.test(await estado()), "normal: selo de estado = Em operacao (" + await estado() + ")");
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
  ok(/Falha/.test(await estado()), "falha: selo de estado = Falha (" + await estado() + ")");
  await p.click("#aba-al"); await espera(600); await foto("al_falha");
  t = await p.evaluate(() => document.querySelector("#alLista").innerText);
  ok(/EMERGÊNCIA/.test(t) && /ALARME BOMBA 1/i.test(t), "falha: lista tem emergencia e ALARME BOMBA 1");
  const n = await p.evaluate(() => +document.querySelector("#cntAl").textContent);
  ok(n >= 3, "falha: contador de alarmes ativos = " + n);
  modo = "normal"; await espera(1800);
  t = await p.evaluate(() => document.querySelector("#alLista").innerText);
  ok(/Nenhum alarme ativo/.test(t), "normal: 'Nenhum alarme ativo'");
  const hist = await p.evaluate(() => Hagane.Alarmes.hist.map(h => h.ev));
  ok(hist.includes("ATIVOU") && hist.includes("NORMALIZOU"), "historico registra ATIVOU e NORMALIZOU: " + hist.join(","));
  await p.check("#alTodos"); await espera(500); await foto("al_todos"); await p.uncheck("#alTodos");
  modo = "aviso"; await espera(1800); await p.click("#aba-ov"); await espera(500); await foto("ov_aviso");
  ok(/Aviso/.test(await estado()), "aviso: selo de estado = Aviso (" + await estado() + ")");
  // sem comunicacao (resposta do servidor) e Node-RED fora (fetch falha)
  modo = "semcom"; await espera(1800); await foto("ov_semcom");
  t = await p.evaluate(() => document.body.innerText);
  ok(/SEM COMUNICAÇÃO/.test(t) && await p.evaluate(() => !document.querySelector("#svg .lp.on, #svg .vl.on")), "sem comunicacao: banner e nenhuma lampada verde");
  ok(/Sem dado/.test(await estado()), "sem comunicacao: selo = Sem dado");
  modo = "erro"; abortando = true; await espera(3500);
  ok(await p.evaluate(() => Hagane.Dados.semCom), "Node-RED fora (fetch falha): tela declara sem comunicacao");
  modo = "normal"; await espera(1800); abortando = false;
  ok(!(await p.evaluate(() => Hagane.Dados.semCom)), "recupera quando a comunicacao volta");
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
  // alternar o visual no cabecalho e lembrar apos recarregar
  const outro = TEMA === "mod" ? "ori" : "mod";
  await p.click(`.vis [data-tema="${outro}"]`); await espera(500); await foto("troca_" + outro);
  ok(await p.evaluate(t => document.body.classList.contains("tema-" + t), outro), "botao do cabecalho troca o visual para " + outro);
  await p.goto(URL.replace(/\?.*/, "")); await espera(1500);
  ok(await p.evaluate(t => document.body.classList.contains("tema-" + t), outro), "visual escolhido e lembrado apos recarregar");
  ok(erros.length === 0, "sem erros de console/pagina" + (erros.length ? ": " + erros.slice(0, 3).join(" | ") : ""));

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
