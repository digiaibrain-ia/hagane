#!/usr/bin/env python3
"""Gera dashboard/src/baggio_monitor_v0.5.html a partir da v0.4 (arquivada).

v0.5 (correcoes de UI):
  * SEM DESLOCAMENTO: a faixa "SEM COMUNICACAO" deixa de empurrar a pagina (fica fixa no rodape; o espaco do rodape e
    sempre reservado); barra de rolagem com espaco reservado; selos do cabecalho com largura minima.
  * TUBO EMENDADO: o tubo do extrator de lodo agora comeca na borda do funil do filtro (estava 30 unidades solto).
Uso: python3 -B -I dashboard/gerador/gerar_monitor_v0.5.py   (aborta se o destino existir ou se a v0.4 mudou)
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ORIG = RAIZ / "dashboard/arquivo/baggio_monitor_v0.4.html"
DEST = RAIZ / "dashboard/src/baggio_monitor_v0.5.html"
if DEST.exists() and "--forcar" not in sys.argv:
    sys.exit(f"ABORTA: {DEST.name} ja existe (versao nova, nunca sobrescrever)")
s = ORIG.read_text(encoding="utf-8")

def troca(velho, novo, n=1):
    global s
    if s.count(velho) != n:
        sys.exit(f"ABORTA: trecho da v0.4 mudou ({s.count(velho)}x): {velho[:80]!r}")
    s = s.replace(velho, novo)

troca('<meta name="app-version" content="0.4">', '<meta name="app-version" content="0.5">')
troca('  BAGGIO MONITOR v0.4  (SOMENTE LEITURA)', '  BAGGIO MONITOR v0.5  (SOMENTE LEITURA)')
troca('    v0.4  Nome Baggio', '    v0.5  Sem deslocamento de UI (aviso fixo no rodape, espaco reservado); tubo do extrator emendado no funil.\n    v0.4  Nome Baggio')
troca('const VERSAO = "0.4";', 'const VERSAO = "0.5";')

# tubo emendado: do funil (borda inclinada em x~216 na altura 172) para a direita e para baixo
troca('M248 172 H239 Q231 172 231 180 V412 Q231 420 239 420 H313 V390', 'M214 172 H223 Q231 172 231 180 V412 Q231 420 239 420 H313 V390')

# bomba marcada como equipamento (o teste de pontas de tubo reconhece)
troca('return `<g transform="translate(${x},${y})">\n      <rect x="-34"', 'return `<g class="bmb" transform="translate(${x},${y})">\n      <rect x="-34"')

# rotulo da banda: mais folga ate a lampada (a medida varia com o tamanho da tela)
troca('[100,338,"ROTAÇÃO BANDA"],[100,350,"FILTRANTE"]', '[90,338,"ROTAÇÃO BANDA"],[90,350,"FILTRANTE"]')

# CSS: nada se mexe
troca('</style>', r'''
/* ============ v0.5 · sem deslocamento de UI ============ */
html{scrollbar-gutter:stable}
main{padding-bottom:44px}                                   /* reserva fixa para a faixa do rodape: nunca empurra nem cobre */
#aviso{position:fixed;left:0;right:0;bottom:0;z-index:25;padding:8px 16px;font-size:14px;box-shadow:0 -2px 10px rgba(0,0,0,.3)}
#aviso small{display:inline;margin-left:10px;font-weight:400}
#pEstado,#pCom,#pOrigem{justify-content:center;text-align:center}
#pEstado{min-width:128px}
#pCom{min-width:166px}
#pOrigem{min-width:172px}
.cnt{min-width:24px}
body{--alt-svg:194px}                                         /* desenho cabe na tela com a reserva do rodape */
body.tema-mod{--alt-svg:164px}
</style>''')

DEST.write_text(s, encoding="utf-8")
print("ok", DEST.relative_to(RAIZ), len(s)//1024, "KB")
