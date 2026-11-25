#!/usr/bin/env python3
"""Gera dashboard/src/baggio_monitor_v0.12.html a partir da v0.11 (arquivada).

v0.12: SEM entradas/saidas analogicas (o equipamento nao tem): painel "Analogicas" removido da tela Entradas e saidas e
"analogicas" removido do contrato embutido. Uso: python3 -B -I dashboard/gerador/gerar_monitor_v0.12.py
(aborta se o destino existir, se a v0.11 mudou ou se o historico nao tem a versao)
"""
import json, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
VERSAO = "0.12"
ORIG = RAIZ / "dashboard/arquivo/baggio_monitor_v0.11.html"
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
        sys.exit(f"ABORTA: trecho da v0.11 mudou ({s.count(velho)}x): {velho[:90]!r}")
    s = s.replace(velho, novo)

def troca_entre(ini, fim, novo):
    global s
    a = s.find(ini); b = s.find(fim, a + 1)
    if a < 0 or b < 0:
        sys.exit(f"ABORTA: marcador nao encontrado: {ini[:60]!r} / {fim[:60]!r}")
    s = s[:a] + novo + s[b:]

troca('<meta name="app-version" content="0.11">', f'<meta name="app-version" content="{VERSAO}">')
troca('  BAGGIO MONITOR v0.11  (SOMENTE LEITURA)', f'  BAGGIO MONITOR v{VERSAO}  (SOMENTE LEITURA)')
troca('    v0.11 Bombas verdes', f'    v{VERSAO} Sem entradas/saidas analogicas (tela e contrato embutido).\n    v0.11 Bombas verdes')
troca('const VERSAO = "0.11";', f'const VERSAO = "{VERSAO}";')
a = s.find("const HIST_VERSOES = "); b = s.find(";\n", a)
s = s[:a] + "const HIST_VERSOES = " + json.dumps(HIST, ensure_ascii=False) + s[b:]

# analogicas: tela e contrato embutido
troca('  <h3 class="sec">Analógicas</h3>\n  <div class="painel" id="esAnalog"></div>\n','')
fimb='      this.montadoAnalog = true;\n    }\n'
a=s.find('    if (!this.montadoAnalog) {'); b=s.find(fimb, a)
if a<0 or b<0: sys.exit("ABORTA: bloco analogico nao encontrado")
s=s[:a]+s[b+len(fimb):]
troca(' montadoAnalog:false,','')
troca(' TelaES.montadoAnalog = false;','')
i=s.find("const CONTRATO_EMB = "); j=s.find(";\n",i)
c=json.loads(s[i+len("const CONTRATO_EMB = "):j]); c.pop("analogicas",None)
s=s[:i]+"const CONTRATO_EMB = "+json.dumps(c,ensure_ascii=False)+s[j:]

DEST.write_text(s, encoding="utf-8")
print("ok", DEST.relative_to(RAIZ), len(s)//1024, "KB")
