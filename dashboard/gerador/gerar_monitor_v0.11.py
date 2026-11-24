#!/usr/bin/env python3
"""Gera dashboard/src/baggio_monitor_v0.11.html a partir da v0.10 (arquivada).

v0.11: BOMBAS 1 e 2 mostram o estado no proprio desenho: motor e bomba VERDES quando funcionando, CINZA quando desligadas
(VERMELHAS se houver falha; tracejadas sem dado). O rotor gira com a animacao ligada. A sinalizacao de hertz (-- Hz)
foi retirada; nao ha legenda de cores. Estado = mesmo calculo das lampadas (retorno de motor ligado e alarmes do PLC).
Uso: python3 -B -I dashboard/gerador/gerar_monitor_v0.11.py   (aborta se o destino existir, se a v0.10 mudou ou se o historico nao tem a versao)
"""
import json, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
VERSAO = "0.11"
ORIG = RAIZ / "dashboard/arquivo/baggio_monitor_v0.10.html"
DEST = RAIZ / f"dashboard/src/baggio_monitor_v{VERSAO}.html"
if DEST.exists() and "--forcar" not in sys.argv:
    sys.exit(f"ABORTA: {DEST.name} ja existe (versao nova, nunca sobrescrever)")
HIST = json.loads((RAIZ / "docs/historico_versoes.json").read_text(encoding="utf-8"))
if HIST["atual"] != VERSAO or HIST["versoes"][0]["v"] != VERSAO:
    sys.exit(f"ABORTA: docs/historico_versoes.json nao esta atualizado para a v{VERSAO}")
s = ORIG.read_text(encoding="utf-8")

def troca(velho, novo, n=1):
    global s
    if s.count(velho) != n:
        sys.exit(f"ABORTA: trecho da v0.10 mudou ({s.count(velho)}x): {velho[:90]!r}")
    s = s.replace(velho, novo)

def troca_entre(ini, fim, novo):
    global s
    a = s.find(ini); b = s.find(fim, a + 1)
    if a < 0 or b < 0:
        sys.exit(f"ABORTA: marcador nao encontrado: {ini[:60]!r} / {fim[:60]!r}")
    s = s[:a] + novo + s[b:]

troca('<meta name="app-version" content="0.10">', f'<meta name="app-version" content="{VERSAO}">')
troca('  BAGGIO MONITOR v0.10  (SOMENTE LEITURA)', f'  BAGGIO MONITOR v{VERSAO}  (SOMENTE LEITURA)')
troca('    v0.10 Dialogo "Versao do programa"', f'    v{VERSAO} Bombas verdes (funcionando) / cinza (desligadas); sem a sinalizacao de Hz.\n    v0.10 Dialogo "Versao do programa"')
troca('const VERSAO = "0.10";', f'const VERSAO = "{VERSAO}";')
a = s.find("const HIST_VERSOES = "); b = s.find(";\n", a)
s = s[:a] + "const HIST_VERSOES = " + json.dumps(HIST, ensure_ascii=False) + s[b:]

# 1) sem a sinalizacao de Hz
troca_entre('      <rect class="hz" x="209"', '      ${O.valvulas.map', '')

# 2) bomba com partes coloriveis e rotor
troca_entre('  bomba(x,y){', '  /* valvula de retencao', r'''  bomba(x,y,id){
    return `<g class="bmb nd" data-bmb="${id}" transform="translate(${x},${y})"><title></title>
      <rect class="bm-motor" x="-34" y="-10" width="40" height="20" rx="4" fill="url(#gMotor)" stroke="#6f7a80"/>
      ${[-27,-20,-13,-6].map(a=>`<line class="bm-aleta" x1="${a}" y1="-9" x2="${a}" y2="9" stroke="#8d969c" stroke-width="1"/>`).join("")}
      <rect x="4" y="-6" width="5" height="12" fill="#9aa3a8" stroke="#6f7a80"/>
      <circle class="bm-voluta" cx="20" cy="0" r="12" fill="url(#gMotor)" stroke="#6f7a80"/>
      <g class="imp"><path d="M20 -8 V8 M12 0 H28" stroke="#4b565c" stroke-width="2.2" stroke-linecap="round"/></g><circle cx="20" cy="0" r="2.6" fill="#4b565c"/>
      <rect x="-30" y="10" width="56" height="4" fill="#8d969c"/></g>`;
  },
''')
troca('${this.bomba(241,530)}${this.bomba(424,530)}', '${this.bomba(241,530,"bomba1")}${this.bomba(424,530,"bomba2")}')

# 3) estado das bombas no desenho (mesmo calculo das lampadas)
troca('    // fluxo nos tubos: so onde o equipamento esta ativo', r'''    // bombas: verde funcionando, cinza desligada, vermelha em falha, tracejada sem dado
    $$("#svg [data-bmb]").forEach(g=>{ const r = this.estadoEq(g.dataset.bmb);
      g.setAttribute("class","bmb "+r.k); g.querySelector("title").textContent = Mapa.eq[g.dataset.bmb].nome+": "+r.t+(r.d?" ("+r.d+")":""); });
    // fluxo nos tubos: so onde o equipamento esta ativo''')

# 4) CSS
troca('</style>', r'''
/* ============ v0.11 · bombas: verde = funcionando, cinza = desligada ============ */
.bm-motor,.bm-voluta{transition:fill .3s,stroke .3s}
.bmb.run .bm-motor,.bmb.run .bm-voluta{fill:#4cd36b;stroke:#1f7a3a}
.bmb.stop .bm-motor,.bmb.stop .bm-voluta{fill:#c3c8cc;stroke:#6f7a80}
.bmb.fail .bm-motor,.bmb.fail .bm-voluta{fill:#e0594f;stroke:#8a1f18}
.bmb.nd .bm-motor,.bmb.nd .bm-voluta{fill:#e4e7e9;stroke:#8d969c;stroke-dasharray:3 2}
.bmb.run .bm-aleta{stroke:#1f7a3a}
.bmb.run .imp path{stroke:#fff}
body.tema-mod .bmb.run .bm-motor,body.tema-mod .bmb.run .bm-voluta{fill:var(--run);stroke:var(--run)}
body.tema-mod .bmb.fail .bm-motor,body.tema-mod .bmb.fail .bm-voluta{fill:var(--bad);stroke:var(--bad)}
body.tema-mod .bmb.stop .bm-motor,body.tema-mod .bmb.stop .bm-voluta{fill:#d3dae2;stroke:#8a98a8}
.imp{transform-box:fill-box;transform-origin:center}
body.anim .bmb.run .imp{animation:gira .7s linear infinite}
@keyframes gira{to{transform:rotate(360deg)}}
</style>''')

DEST.write_text(s, encoding="utf-8")
print("ok", DEST.relative_to(RAIZ), len(s)//1024, "KB")
