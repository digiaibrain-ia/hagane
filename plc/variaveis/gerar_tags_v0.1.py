#!/usr/bin/env python3
"""Gera o contrato de tags (CSV + JSON) a partir da planilha exportada do TIA.

Uso:  python3 -I plc/variaveis/gerar_tags_v0.1.py
Entrada: plc/variaveis/PLCTags_v0.1.xlsx   (fonte de verdade, HG-001)
Saida:   docs/contratos/tags_v0.1.csv  (BOM UTF-8, abre no Excel)
         docs/contratos/tags_v0.1.json (consumido pelo Node-RED e pelo HTML)
         docs/contratos/pendencias.md  (inconsistencias achadas na planilha)
"""
import csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
import openpyxl

RAIZ = Path(__file__).resolve().parents[2]
ENTRADA = RAIZ / "plc/variaveis/PLCTags_v0.1.xlsx"
SAIDA = RAIZ / "docs/contratos"

# Palavras que marcam alarme/falha numa memoria (M). A classe critico/permissivel
# vem do programa do PLC e NAO esta na planilha: fica "alarme" ate confirmar.
PAL_ALARME = ("ALARME", "DISJUNTOR DESARMADO", "FALTA ", "EMERGÊNCIA ATUADA",
              "PRESSÃO AR INSUFICIENTE", "NÍVEL MIN. LIQUIDO P/ FILTRAR")
# Memorias que sao apenas apoio do programa/WinCC (nao mostrar ao operador)
PAL_APOIO = ("merker", "PAGINA", "pulso p/", "incremento", "INCREMENTO", "CONTA MINUTOS",
             "SET TIMER", "habilita papel descartável", "desabilita papel descartável")

def area_de(addr):
    m = re.match(r"%(IW|QW|MW|IB|QB|MB|I|Q|M|T|C)", addr)
    return m.group(1) if m else "?"

def classe(path, area, nome, comentario):
    c = (comentario or "")
    if "reserva" in nome.lower() and not c.strip() or c.strip().upper() == "RESERVA":
        return "reserva"
    if area in ("T", "C"):
        return "temporizador" if area == "T" else "contador"
    if area in ("IW", "QW", "MW"):
        return "analogico_ou_palavra"
    if area in ("I",):
        return "entrada_digital"
    if area in ("Q",):
        return "saida_digital"
    if area == "M":
        if any(p in c for p in PAL_APOIO) or any(p in nome for p in PAL_APOIO):
            return "apoio_programa"
        if any(p in c.upper() for p in PAL_ALARME):
            return "alarme"
        return "estado"
    return "outro"

def main():
    ws = openpyxl.load_workbook(ENTRADA)["PLC Tags"]
    linhas = list(ws.iter_rows(values_only=True))
    cab, dados = linhas[0], linhas[1:]
    tags, por_end = [], defaultdict(list)
    for r in dados:
        nome, path, tipo, end, com = (r[0], r[1], r[2], r[3], r[4])
        if not nome or not end:
            continue
        a = area_de(end)
        t = {"nome": nome, "grupo": path, "tipo": tipo, "endereco": end.lstrip("%"),
             "area": a, "comentario": (com or "").strip(), "classe": classe(path, a, nome, com)}
        tags.append(t); por_end[t["endereco"]].append(t)

    def chave(t):
        m = re.match(r"([A-Z]+)(\d+)(?:\.(\d))?", t["endereco"])
        return (m.group(1), int(m.group(2)), int(m.group(3) or 0))
    tags.sort(key=chave)

    SAIDA.mkdir(parents=True, exist_ok=True)
    campos = ["endereco", "nome", "tipo", "grupo", "classe", "comentario"]
    with open(SAIDA / "tags_v0.1.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, campos, extrasaction="ignore"); w.writeheader(); w.writerows(tags)
    (SAIDA / "tags_v0.1.json").write_text(
        json.dumps({"versao": "0.1", "origem": ENTRADA.name, "tags": tags}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    # --- pendencias (HG-002) ---
    pend = []
    for e, ts in por_end.items():
        if len(ts) > 1:
            pend.append(f"- **Endereço repetido** `{e}`: " + "; ".join(t["nome"] for t in ts))
    for t in tags:
        if t["nome"].endswith("_res") and t["comentario"].strip().upper() not in ("", "RESERVA"):
            pend.append(f"- **Nome diz reserva, comentário diz outra coisa** `{t['endereco']}` `{t['nome']}`: {t['comentario']}")
    for t in tags:
        if t["tipo"] in ("Word",) and not t["comentario"] and t["area"] in ("IW", "QW"):
            pend.append(f"- **Analógica sem comentário** `{t['endereco']}` `{t['nome']}`")
    (SAIDA / "pendencias_geradas.md").write_text(
        "# Pendências geradas pela planilha (não editar à mão)\n\n" + "\n".join(pend) + "\n", encoding="utf-8")

    res = Counter(t["classe"] for t in tags)
    print(f"{len(tags)} tags; classes: {dict(res)}; pendencias: {len(pend)}")

if __name__ == "__main__":
    sys.exit(main())
