#!/usr/bin/env python3
"""Gera dashboard/src/baggio_monitor_v0.13.html a partir da v0.12 (arquivada).

v0.13: (1) BOMBA 2 espelhada 180 graus (motor a direita, voluta a esquerda) e tubulacao de succao refeita (curta, entra
pela esquerda); (2) titulo "Baggio · Sistema de Filtragem" sempre visivel no tema Moderno, com ICONE ANIMADO (funil com
gotas; anima junto com o botao Animacao).
Uso: python3 -B -I dashboard/gerador/gerar_monitor_v0.13.py   (aborta se o destino existir, se a v0.12 mudou ou se o historico nao tem a versao)
"""
import json, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
VERSAO = "0.13"
ORIG = RAIZ / "dashboard/arquivo/baggio_monitor_v0.12.html"
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
        sys.exit(f"ABORTA: trecho da v0.12 mudou ({s.count(velho)}x): {velho[:90]!r}")
    s = s.replace(velho, novo)

troca('<meta name="app-version" content="0.12">', f'<meta name="app-version" content="{VERSAO}">')
troca('  BAGGIO MONITOR v0.12  (SOMENTE LEITURA)', f'  BAGGIO MONITOR v{VERSAO}  (SOMENTE LEITURA)')
troca('    v0.12 Sem entradas/saidas analogicas', f'    v{VERSAO} Bomba 2 espelhada; titulo Sistema de Filtragem e icone animado.\n    v0.12 Sem entradas/saidas analogicas')
troca('const VERSAO = "0.12";', f'const VERSAO = "{VERSAO}";')
a = s.find("const HIST_VERSOES = "); b = s.find(";\n", a)
s = s[:a] + "const HIST_VERSOES = " + json.dumps(HIST, ensure_ascii=False) + s[b:]

# 1) bomba espelhada (esp=true): motor a direita, voluta a esquerda; x e o ponto onde a voluta fica 20 a esquerda
troca('  bomba(x,y,id){\n    return `<g class="bmb nd" data-bmb="${id}" transform="translate(${x},${y})">',
      '  bomba(x,y,id,esp){\n    return `<g class="bmb nd" data-bmb="${id}" transform="translate(${x},${y})${esp?" scale(-1,1)":""}">')
troca('${this.bomba(424,530,"bomba2")}', '${this.bomba(464,530,"bomba2",true)}')
# succao da bomba 2: do fundo da caixa de saida direto para a voluta (entra pela esquerda)
troca('${this.tubo("M360 390 V598 Q360 606 368 606 H463 Q471 606 471 598 V538 Q471 530 463 530 H452","","b2",false,-1)}',
      '${this.tubo("M360 390 V522 Q360 530 368 530 H432","","b2",false,-1)}')
# quadro tracejado do grupo das bombas: sem o laco de baixo, fica mais baixo
troca('<rect class="seg" x="105" y="440" width="500" height="196"', '<rect class="seg" x="105" y="440" width="500" height="150"')

# 2) titulo + icone animado
troca('<h1><span class="h-marca">Baggio</span><small id="site">Sistema de filtragem</small></h1>',
      '''<h1><svg class="h-ico" viewBox="0 0 28 28" aria-hidden="true" focusable="false">
      <path class="hi-funil" d="M4 5 H24 L16.5 14 V22 L11.5 24.5 V14 Z"/>
      <path class="hi-agua" d="M7.2 8.2 H20.8 L16.5 13.4 H11.5 Z"/>
      <circle class="hi-g hi-g1" cx="14" cy="26" r="1.5"/><circle class="hi-g hi-g2" cx="14" cy="26" r="1.5"/>
    </svg><span class="h-marca">Baggio</span><small id="site">Sistema de Filtragem</small></h1>''')
troca('<title>Baggio — Sistema de filtragem</title>', '<title>Baggio — Sistema de Filtragem</title>')
troca('</style>', r'''
/* ============ v0.13 · titulo com icone animado ============ */
.h-ico{width:26px;height:26px;vertical-align:-7px;margin-right:7px;overflow:visible}
.hi-funil{fill:rgba(255,255,255,.16);stroke:#fff;stroke-width:1.8;stroke-linejoin:round}
.hi-agua{fill:#7fc4f3}
.hi-g{fill:#7fc4f3;opacity:0}
body.anim .hi-agua{animation:hiOnda 1.6s ease-in-out infinite}
body.anim .hi-g{animation:hiGota 1.5s ease-in infinite}
body.anim .hi-g2{animation-delay:.75s}
@keyframes hiGota{0%{transform:translateY(-9px);opacity:0}15%{opacity:1}80%{opacity:1}100%{transform:translateY(0);opacity:0}}
@keyframes hiOnda{0%,100%{transform:translateY(0)}50%{transform:translateY(-1.2px)}}
body:not(.anim) .hi-g{opacity:.9;transform:translateY(-3px)}
body.tema-ori .h-ico{display:none}
@media (min-width:1280px){ header h1 small{display:inline} }
</style>''')
DEST.write_text(s, encoding="utf-8")
print("ok", DEST.relative_to(RAIZ), len(s)//1024, "KB")
