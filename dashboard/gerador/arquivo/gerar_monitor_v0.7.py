#!/usr/bin/env python3
"""Gera dashboard/src/baggio_monitor_v0.7.html a partir da v0.6 (arquivada).

v0.7 (visual do Overview, por REGRAS medidas em teste):
  * SETAS geradas do proprio tubo, a 12 unidades do eixo, com o MESMO sentido da animacao da agua
    (antes: glifos soltos em posicoes digitadas a mao).
  * TUBULACAO padronizada: tubos paralelos com afastamento minimo de 24 unidades (antes 34, 28, 19...);
    tubo do filtro afastado do canto do tanque; PONTE no cruzamento que nao e ligacao; linha tracejada fora do tubo.
  * VALVULAS alinhadas ao eixo do tubo, com flanges e atuador sempre do mesmo lado.
  * ROTULOS: "Valvula de compensacao" nao atravessa mais a parede do tanque; "Valvula de lavagem" centrada na valvula.
  * Simulador sem o silencio (sem teste de queda embutido).
Uso: python3 -B -I dashboard/gerador/gerar_monitor_v0.7.py   (aborta se o destino existir ou se a v0.6 mudou)
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ORIG = RAIZ / "dashboard/arquivo/baggio_monitor_v0.6.html"
DEST = RAIZ / "dashboard/src/baggio_monitor_v0.7.html"
if DEST.exists() and "--forcar" not in sys.argv:
    sys.exit(f"ABORTA: {DEST.name} ja existe (versao nova, nunca sobrescrever)")
s = ORIG.read_text(encoding="utf-8")

def troca(velho, novo, n=1):
    global s
    if s.count(velho) != n:
        sys.exit(f"ABORTA: trecho da v0.6 mudou ({s.count(velho)}x): {velho[:90]!r}")
    s = s.replace(velho, novo)

def troca_entre(ini, fim, novo):
    global s
    a = s.find(ini); b = s.find(fim, a + 1)
    if a < 0 or b < 0:
        sys.exit(f"ABORTA: marcador nao encontrado: {ini[:60]!r} / {fim[:60]!r}")
    s = s[:a] + novo + s[b:]

# ---------------------------------------------------------------- versao
troca('<meta name="app-version" content="0.6">', '<meta name="app-version" content="0.7">')
troca('  BAGGIO MONITOR v0.6  (SOMENTE LEITURA)', '  BAGGIO MONITOR v0.7  (SOMENTE LEITURA)')
troca('    v0.6  Sem "Hagane" na tela', '    v0.7  Setas geradas do tubo (mesmo sentido da animacao); afastamento padrao de 24 entre tubos; ponte no cruzamento;\n          valvulas alinhadas ao eixo do tubo; sem sobreposicao de rotulos; simulador sem silencio.\n    v0.6  Sem "Hagane" na tela')
troca('const VERSAO = "0.6";', 'const VERSAO = "0.7";')

# ---------------------------------------------------------------- corrida ao trocar de fonte (PLC -> Simulados)
# uma leitura do PLC ainda pendente terminava depois da troca e derrubava a simulacao para "sem dado"
troca('''    try {
      if (!this.contrato) await this.carregarContrato();
      const e = await this.buscar("/baggio/api/estado");
      this.falhas = 0; this.estado = e;''', '''    const f0 = this.fonte;                 // fonte no inicio desta leitura
    try {
      if (!this.contrato) await this.carregarContrato();
      if (this.fonte !== f0) { this.contrato = null; return; }          // trocou de fonte durante a espera: descarta
      const e = await this.buscar("/baggio/api/estado");
      if (this.fonte !== f0) return;                                     // idem: resposta velha de outra fonte
      this.falhas = 0; this.estado = e;''')
troca('''    } catch (err) {
      this.falhas++;''', '''    } catch (err) {
      if (this.fonte !== f0) return;                                     // erro de uma fonte que ja foi trocada
      this.falhas++;''')

# ---------------------------------------------------------------- mapa: posicoes de lampadas e valvulas
troca('{id:"banda",    nome:"Rotação da banda filtrante",       x:200, y:340, bit:"Q15.3"}', '{id:"banda",    nome:"Rotação da banda filtrante",       x:190, y:340, bit:"Q15.3"}')
troca('{id:"comp",     nome:"Válvula de compensação aberta",    x:492, y:155, bit:"Q14.2"}', '{id:"comp",     nome:"Válvula de compensação aberta",    x:546, y:146, bit:"Q14.2"}')
troca('{id:"vQv",    nome:"Válvula quebra vácuo",   x:231, y:262, vert:true,  bit:"Q14.1"}', '{id:"vQv",    nome:"Válvula quebra vácuo",   x:213, y:262, vert:true,  bit:"Q14.1"}')
troca('{id:"vComp",  nome:"Válvula de compensação", x:469, y:155, vert:true,  bit:"Q14.2"}', '{id:"vComp",  nome:"Válvula de compensação", x:468, y:146, vert:true,  bit:"Q14.2"}')
troca('{id:"vLav",   nome:"Válvula de lavagem",     x:828, y:268, vert:false, bit:"Q15.6"}', '{id:"vLav",   nome:"Válvula de lavagem",     x:800, y:256, vert:false, bit:"Q15.6"}')

# ---------------------------------------------------------------- valvula alinhada ao eixo; instrumento marcado
troca_entre('  valvula(v){', '  /* tubo: contorno + miolo;', r'''  /* valvula no eixo do tubo: duas pontas de triangulo ao longo do tubo, flanges nas extremidades e atuador
     SEMPRE do mesmo lado (direita no tubo vertical, acima no horizontal), ligado por haste */
  valvula(v){
    const V = v.vert;
    const corpo = V ? "M-7 -9 L7 -9 L-7 9 L7 9 Z" : "M-9 -7 L-9 7 L9 -7 L9 7 Z";
    const flange = V ? "M-8 -10 H8 M-8 10 H8" : "M-10 -8 V8 M10 -8 V8";
    const haste = V ? "M7 0 H13" : "M0 -7 V-13";
    const at = V ? {x:13,y:-4,w:8,h:8} : {x:-4,y:-21,w:8,h:8};
    return `<g class="vl nd" data-vl="${v.id}" data-eixo="${V?"v":"h"}" transform="translate(${v.x},${v.y})"><title></title>
      <path class="vl-fl" d="${flange}"/><path d="${corpo}"/><path class="vl-hs" d="${haste}"/><rect class="vl-at" x="${at.x}" y="${at.y}" width="${at.w}" height="${at.h}"/></g>`;
  },
''')
troca('retencao(x,y){ return `<g transform="translate(${x},${y})">', 'retencao(x,y){ return `<g class="inst" transform="translate(${x},${y})">')

# ---------------------------------------------------------------- tubo com direcao/seta; setas geradas
troca('''  tubo(d,cls,flux,rev){ return `<path class="tb-o ${cls||""}" d="${d}"/><path class="tb-i ${cls||""}" d="${d}"/>`+(flux?`<path class="tb-f${rev?" rev":""}" data-flux="${flux}" d="${d}"/>`:""); },''',
'''  tubo(d,cls,flux,rev,seta){ return `<path class="tb-o ${cls||""}" d="${d}" data-seta="${seta||0}" data-rev="${rev?1:0}"/><path class="tb-i ${cls||""}" d="${d}"/>`+(flux?`<path class="tb-f${rev?" rev":""}" data-flux="${flux}" d="${d}"/>`:""); },
  /* SETAS DE SENTIDO: geradas do proprio tubo (a animacao usa o mesmo caminho, entao nunca divergem).
     Ficam a 12 unidades do eixo, em trecho reto, longe de curvas, valvulas, instrumentos, lampadas, textos e outros tubos. */
  setas(){
    const svg = $("#svg"), NS = "http://www.w3.org/2000/svg", grp = $("#setas"); grp.innerHTML = "";
    const tubos = Array.from(svg.querySelectorAll(".tb-o"));
    const pts = tubos.map(p=>{ const L=p.getTotalLength(), a=[]; for (let s=0;s<=L;s+=5) a.push(p.getPointAtLength(s)); return a; });
    const caixa = el => { const b = el.getBBox(), m = /translate\\(([-\\d.]+),([-\\d.]+)\\)/.exec(el.getAttribute("transform")||""); return {x:b.x+(m?+m[1]:0), y:b.y+(m?+m[2]:0), w:b.width, h:b.height}; };
    const obst = Array.from(svg.querySelectorAll("[data-vl],.inst,[data-lp],.bmb,:scope > text")).map(caixa);
    const bate = (x,y,m) => obst.some(o => x > o.x-m && x < o.x+o.w+m && y > o.y-m && y < o.y+o.h+m);
    tubos.forEach((p,pi)=>{
      const lado = +p.dataset.seta; if (!lado) return;
      const rev = p.dataset.rev==="1", L = p.getTotalLength(), n = Math.max(1, Math.round(L/170));
      for (let i=0;i<n;i++){
        const alvo = L*(i+0.5)/n; let feito = false;
        for (const d of [0,14,-14,28,-28,42,-42,56,-56,70,-70]){
          const s = alvo+d; if (s < 26 || s > L-26) continue;
          const P = p.getPointAtLength(s), A = p.getPointAtLength(s-3), B = p.getPointAtLength(s+3);
          let ux = B.x-A.x, uy = B.y-A.y; const tl = Math.hypot(ux,uy); ux/=tl; uy/=tl;
          const tg = q=>{ const a=p.getPointAtLength(q-2), b=p.getPointAtLength(q+2), l=Math.hypot(b.x-a.x,b.y-a.y); return [(b.x-a.x)/l,(b.y-a.y)/l]; };
          const T1 = tg(s-16), T2 = tg(s+16);
          if (T1[0]*T2[0]+T1[1]*T2[1] < 0.999 || T1[0]*ux+T1[1]*uy < 0.999) continue;    // so em trecho reto (sem curva na janela de 32)
          const cx = P.x - uy*lado*12, cy = P.y + ux*lado*12;
          if (bate(cx,cy,8)) continue;
          if (pts.some((a,qi)=>qi!==pi && a.some(q=>Math.hypot(q.x-cx,q.y-cy) < 14))) continue;   // longe de outros tubos
          let ang = Math.atan2(uy,ux)*180/Math.PI + (rev?180:0);
          const ch = document.createElementNS(NS,"path"); ch.setAttribute("class","seta-ch"); ch.setAttribute("d","M-3.5 -4 L2.5 0 L-3.5 4");
          ch.setAttribute("transform",`translate(${cx.toFixed(1)},${cy.toFixed(1)}) rotate(${ang.toFixed(1)})`);
          ch.dataset.tubo = pi; ch.dataset.dir = rev?"rev":"fwd"; grp.appendChild(ch); feito = true; break;
        }
      }
    });
  },''')
troca('    // clique/toque numa lampada ou valvula: mostra nome, estado e endereco (ajuda no teste)', '    this.setas();\n    // clique/toque numa lampada ou valvula: mostra nome, estado e endereco (ajuda no teste)')

# ---------------------------------------------------------------- desenho: setas antigas saem, geometria padronizada
troca_entre('    const setas = [[218,195,"↓"]', '    const rot = [', '')
troca('[222,234,"VÁLVULA","end"],[222,246,"QUEBRA VÁCUO","end"]', '[198,234,"VÁLVULA","end"],[198,246,"QUEBRA VÁCUO","end"]')
troca('[68,99,"VÁLVULA"],[68,111,"SOPRO"]', '[86,99,"VÁLVULA"],[86,111,"SOPRO"]')
troca('[90,338,"ROTAÇÃO BANDA"],[90,350,"FILTRANTE"]', '[78,338,"ROTAÇÃO BANDA"],[78,350,"FILTRANTE"]')
troca('[506,152,"VÁLVULA DE"],[506,164,"COMPENSAÇÃO"]', '[560,143,"VÁLVULA DE"],[560,155,"COMPENSAÇÃO"]')
troca('[722,96,"RETORNO"]', '[738,94,"RETORNO","middle"]')
troca('[806,290,"VÁLVULA DE"],[806,302,"LAVAGEM"]', '[800,282,"VÁLVULA DE","middle"],[800,294,"LAVAGEM","middle"]')
troca('      ${setas.map(a=>`<text class="seta" x="${a[0]}" y="${a[1]}">${a[2]}</text>`).join("")}\n', '      <g id="setas"></g>\n')
troca('<rect class="seg" x="105" y="416" width="447" height="220"', '<rect class="seg" x="105" y="440" width="447" height="196"')
troca('points="150,95 195,95 268,360 245,360 180,276 132,276 132,200 150,200"', 'points="150,95 195,95 268,360 245,360 180,276 108,276 108,200 150,200"')
troca('<rect class="eqp2" x="132" y="200" width="94" height="76"/>', '<rect class="eqp2" x="108" y="200" width="96" height="76"/>')
troca_entre('      ${this.tubo("M55 62 V198', '      <circle class="tb-ponta"', r'''      ${this.tubo("M55 62 V198 Q55 213 70 213 H108","ar","ar",false,-1)}
      ${this.tubo("M312 160 H221 Q213 160 213 168 V412 Q213 420 221 420 H304 Q312 420 312 412 V390","","ali",false,-1)}
      <path class="tb-halo" d="M261 406 V434"/>
      ${this.tubo("M261 520 V216 Q261 208 269 208 H690","","b1",false,1)}
      ${this.tubo("M273 530 H328 Q336 530 336 522 V390","","b1",true,-1)}
      ${this.tubo("M444 520 V208","","b2",false,-1)}
      ${this.tubo("M360 390 V598 Q360 606 368 606 H463 Q471 606 471 598 V538 Q471 530 463 530 H452","","b2",false,-1)}
      ${this.tubo("M468 208 V126","","comp",false,1)}
      ${this.tubo("M690 256 V52","","ali",false,-1)}
      ${this.tubo("M690 256 H853 Q861 256 861 248 V240","","lav",false,-1)}
      ${this.tubo("M738 105 V228","","ret",false,-1)}
''')
troca('<circle class="tb-ponta" cx="469" cy="118" r="7"/><circle class="tb-ponta" cx="865" cy="240" r="7"/>', '<circle class="tb-ponta" cx="468" cy="126" r="7"/><circle class="tb-ponta" cx="861" cy="240" r="7"/>')
troca('${this.retencao(265,467)}${this.retencao(450,467)}${this.retencao(745,140)}', '${this.retencao(261,467)}${this.retencao(444,467)}${this.retencao(738,150)}')

# ---------------------------------------------------------------- fluxo: novos grupos
troca('''                   ar:()=>Dados.bit("Q14.3")===true, lav:()=>Dados.bit("Q15.6")===true};''',
      '''                   ar:()=>Dados.bit("Q14.3")===true, lav:()=>Dados.bit("Q15.6")===true,
                   ali:()=>this.estadoEq("bomba1").k==="run"||this.estadoEq("bomba2").k==="run", ret:()=>this.estadoEq("bomba1").k==="run"||this.estadoEq("bomba2").k==="run",
                   comp:()=>Dados.bit("Q14.2")===true};''')

# ---------------------------------------------------------------- CSS
troca('</style>', r'''
/* ============ v0.7 · tubulacao: setas, ponte, valvula ============ */
body{--cvc:#d5d9dc}
body.tema-mod{--cvc:var(--panel)}
.seta-ch{fill:none;stroke:var(--ink);stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
body.tema-mod .seta-ch{stroke:var(--muted)}
.tb-halo{fill:none;stroke:var(--cvc);stroke-width:15;stroke-linecap:butt}
.vl-fl,.vl-hs{fill:none;stroke:#59646a;stroke-width:1.6;stroke-linecap:round}
body.tema-mod .vl-fl,body.tema-mod .vl-hs{stroke:var(--muted)}
.vl.on .vl-fl,.vl.on .vl-hs{stroke:#0f6a2c}
.vl-at{stroke-width:1.2}
</style>''')

DEST.write_text(s, encoding="utf-8")
print("ok", DEST.relative_to(RAIZ), len(s)//1024, "KB")
