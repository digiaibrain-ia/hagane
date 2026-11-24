#!/usr/bin/env python3
"""Gera os fluxos Node-RED do Baggio (v0.10, SOMENTE LEITURA).

v0.10: historico de versoes, contadores e diagnostico da cadeia no HTML; v0.9: cenario fixo do simulador (1 falha + 1 alerta), simulador do HTML = mesmo arquivo do fluxo; v0.8: T da alimentacao, alertas de demonstracao, filtros; v0.7: tubulacao padronizada, setas pelo tubo, simulador sem silencio; v0.6: alertas e falhas pelo catalogo do PLC, nome sem Hagane; v0.5: correcoes de UI (sem deslocamento, tubo emendado); v0.4: projeto renomeado para Baggio (sistema de filtragem; Hagane = fabrica); simulador compartilhado com o HTML.
v0.3: dois visuais; v0.2: Overview fiel ao WinCC; fonte S7 usa ${BAGGIO_PLC_IP} (nao colide com PLC_IP do bt-gerador).

Uso:  python3 -I nodered/gerador/gerar_fluxos_v0.1.py
Entradas: docs/contratos/tags_v0.1.json, dashboard/src/baggio_monitor_v0.1.html,
          nodered/gerador/js/*.js
Saidas (importar no Node-RED, nesta ordem):
  nodered/flows/baggio_core_v0.3.json        API + pagina + decodificador (sempre)
  nodered/flows/baggio_fonte_s7_v0.3.json    leitura REAL da CPU 315 (usa ${BAGGIO_PLC_IP})
  nodered/flows/baggio_fonte_demo_v0.3.json  simulador (so para teste, sem PLC)
Importe core + UMA fonte. As fontes se ligam ao core por nos link ("baggio-bruto").
Aborta se o destino ja existir (versao nova, nunca sobrescrever) — use --forcar so em teste.
"""
import json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
VERSAO = "0.10"
FORCAR = "--forcar" in sys.argv
CLASSES_LIDAS = {"entrada_digital", "saida_digital", "alarme", "estado"}
LINK = "baggio-bruto"

def ler_js(nome, **subs):
    s = (RAIZ / "nodered/gerador/js" / nome).read_text(encoding="utf-8")
    for k, v in subs.items():
        s = s.replace(k, v)
    return s

def nucleo_simulador():
    return (RAIZ / "nodered/gerador/js/50_simulador_core.js").read_text(encoding="utf-8")

def contrato_monitorado():
    """Subconjunto do contrato: so o que o v0.1 le (bits I/Q/M). Analogicas ficam so informativas."""
    d = json.loads((RAIZ / "docs/contratos/tags_v0.1.json").read_text(encoding="utf-8"))
    lidas, analog = [], []
    for t in d["tags"]:
        m = re.fullmatch(r"([IQM])(\d+)\.(\d)", t["endereco"])
        ehres = t["classe"] == "reserva" and m and m.group(1) in "IQ"
        sem_texto = t["classe"] == "estado" and not t["comentario"]   # M sem comentario: nao mostrar
        if m and (t["classe"] in CLASSES_LIDAS or ehres) and not sem_texto:
            lidas.append({"endereco": t["endereco"], "nome": t["nome"], "comentario": t["comentario"],
                          "classe": t["classe"], "area": m.group(1), "bit": True,
                          "byte": f"{m.group(1)}B{m.group(2)}", "nbit": int(m.group(3))})
        elif t["area"] in ("IW", "QW"):
            analog.append({"endereco": t["endereco"], "nome": t["nome"], "comentario": t["comentario"],
                           "lido": False})
    return {"versao": VERSAO, "origem": d["origem"], "tags": lidas, "analogicas": analog}

def no(id_, tipo, z, x, y, **kw):
    n = {"id": id_, "type": tipo, "z": z, "x": x, "y": y}
    n.update(kw); return n

def http_resp(id_, z, x, y, fio=None):
    return no(id_, "http response", z, x, y, name="", statusCode="", headers={}, wires=[])

def gerar_core(contrato):
    z = "baggio_core_tab"
    html = (RAIZ / f"dashboard/src/baggio_monitor_v{VERSAO}.html").read_text(encoding="utf-8")
    cab = f"Baggio core v{VERSAO}"
    return [
        {"id": z, "type": "tab", "label": cab, "disabled": False,
         "info": f"{cab}: decodifica bytes da CPU, guarda o instantaneo e serve a pagina e a API (somente leitura). "
                 "Rotas: GET /baggio, /baggio/api/estado, /baggio/api/tags."},
        no("hg_c_nota", "comment", z, 190, 40, name=f"{cab} - somente leitura", info="Nenhum no escreve na CPU."),
        no("hg_c_ini", "inject", z, 130, 100, name="ao iniciar", props=[], repeat="", crontab="", once=True,
           onceDelay="0.3", topic="", wires=[["hg_c_ini_fn"]]),
        no("hg_c_ini_fn", "function", z, 330, 100, name="carrega contrato", func=ler_js("00_inicio.js", __CONTRATO__=json.dumps(contrato, ensure_ascii=False)),
           outputs=1, initialize="", finalize="", libs=[], wires=[[]],
           info="Guarda o contrato de tags no contexto global (baggio_contrato)."),
        no("hg_c_in", "link in", z, 130, 180, name=LINK, links=[], wires=[["hg_c_dec"]],
           info="Entrada unica de bytes. Ligada a UMA fonte: S7 real OU demo."),
        no("hg_c_dec", "function", z, 330, 180, name="decodifica bits", func=ler_js("10_decodifica.js"), outputs=1,
           initialize="", finalize="", libs=[], wires=[[]], info="bytes -> bits; guarda baggio_snap."),
        no("hg_c_st_in", "link in", z, 130, 240, name="baggio-status-s7", links=[], wires=[["hg_c_st"]],
           info="Status do no S7 (so na fonte real)."),
        no("hg_c_st", "function", z, 330, 240, name="status s7 -> comunicacao", func=ler_js("20_status_s7.js"), outputs=1,
           initialize="", finalize="", libs=[], wires=[[]], info="Marca comunicacao ok/falha."),
        no("hg_c_h1", "http in", z, 130, 320, name="", url="/baggio/api/estado", method="get", upload=False, swaggerDoc="",
           wires=[["hg_c_f1"]]),
        no("hg_c_f1", "function", z, 330, 320, name="estado", func=ler_js("30_api_estado.js"), outputs=1, initialize="",
           finalize="", libs=[], wires=[["hg_c_r1"]], info="Instantaneo + saude da comunicacao."),
        http_resp("hg_c_r1", z, 520, 320),
        no("hg_c_h2", "http in", z, 130, 380, name="", url="/baggio/api/tags", method="get", upload=False, swaggerDoc="",
           wires=[["hg_c_f2"]]),
        no("hg_c_f2", "function", z, 330, 380, name="tags", func=ler_js("31_api_tags.js"), outputs=1, initialize="",
           finalize="", libs=[], wires=[["hg_c_r2"]], info="Contrato de tags monitoradas."),
        http_resp("hg_c_r2", z, 520, 380),
        no("hg_c_h3", "http in", z, 130, 440, name="", url="/baggio", method="get", upload=False, swaggerDoc="",
           wires=[["hg_c_f3"]]),
        no("hg_c_f3", "template", z, 330, 440, name="pagina HTML", field="payload", fieldType="msg", format="html",
           syntax="plain", template=html, output="str", wires=[["hg_c_f3b"]],
           info="Pagina completa (dashboard/src/baggio_monitor_v%s.html), sintaxe plain." % VERSAO),
        no("hg_c_f3b", "function", z, 520, 440, name="cabecalhos", func=ler_js("40_pagina.js"), outputs=1, initialize="",
           finalize="", libs=[], wires=[["hg_c_r3"]], info="Content-Type text/html."),
        http_resp("hg_c_r3", z, 700, 440),
    ]

def fonte_s7(contrato):
    z = "baggio_s7_tab"
    bytes_ = sorted({t["byte"] for t in contrato["tags"]}, key=lambda b: (b[0], int(b[2:])))
    vartable = [{"addr": b, "name": b} for b in bytes_]
    cab = f"Baggio fonte S7 v{VERSAO}"
    return [
        {"id": z, "type": "tab", "label": cab, "disabled": False,
         "info": f"{cab}: LE a CPU 315 por S7 (ISO-on-TCP). Endereco pela variavel de ambiente BAGGIO_PLC_IP (ou digitado no endpoint). Nenhum no de escrita."},
        no("hg_s_nota", "comment", z, 190, 40, name=f"{cab} - leitura {len(bytes_)} bytes", info="Rack 0 / slot 2 (CONFIRMAR na CPU 315)."),
        {"id": "hg_s_ep", "type": "s7 endpoint", "transport": "iso-on-tcp", "address": "${BAGGIO_PLC_IP}", "port": "102",
         "rack": "0", "slot": "2", "localtsaphi": "01", "localtsaplo": "00", "remotetsaphi": "01", "remotetsaplo": "00",
         "connmode": "rack-slot", "adapter": "", "busaddr": "", "cycletime": "1000", "timeout": "2000",
         "name": "CPU 315 (BAGGIO_PLC_IP)", "verbose": "default", "vartable": vartable},
        no("hg_s_in", "s7 in", z, 160, 120, endpoint="hg_s_ep", mode="all", variable="", diff=False,
           name="le CPU (todos os bytes)", wires=[["hg_s_marca"]]),
        no("hg_s_marca", "function", z, 380, 120, name="origem=real", func='msg.origem = "real";\nreturn msg;', outputs=1,
           initialize="", finalize="", libs=[], wires=[["hg_s_out"]], info="Marca a origem para a tela."),
        no("hg_s_out", "link out", z, 560, 120, name=LINK, mode="link", links=["hg_c_in"], wires=[]),
        no("hg_s_status", "status", z, 160, 200, name="", scope=["hg_s_in"], wires=[["hg_s_st_out"]]),
        no("hg_s_st_out", "link out", z, 380, 200, name="baggio-status-s7", mode="link", links=["hg_c_st_in"], wires=[]),
    ]

def fonte_demo():
    z = "baggio_demo_tab"
    cab = f"Baggio fonte DEMO v{VERSAO}"
    return [
        {"id": z, "type": "tab", "label": cab, "disabled": False,
         "info": f"{cab}: simulador SEM PLC, so para teste das telas. Nunca instalar no PC de producao junto com a fonte S7."},
        no("hg_d_nota", "comment", z, 190, 40, name=f"{cab} - SO TESTE", info="A tela mostra DEMO em destaque."),
        no("hg_d_tick", "inject", z, 130, 120, name="1 s", props=[{"p": "payload"}], repeat="1", crontab="", once=True,
           onceDelay="1", topic="", payload="", payloadType="date", wires=[["hg_d_sim"]]),
        no("hg_d_sim", "function", z, 330, 120, name="simula bytes da CPU", func=ler_js("50_simulador.js", __SIM_CORE__=nucleo_simulador()), outputs=1,
           initialize="", finalize="", libs=[], wires=[["hg_d_out"]], info="Ciclo de 180 s: aviso, falha, silencio."),
        no("hg_d_out", "link out", z, 530, 120, name=LINK, mode="link", links=["hg_c_in"], wires=[]),
    ]

def ligar_links(core, fonte_s7_, fonte_demo_):
    """Os link-in do core listam os link-out das fontes (e vice-versa)."""
    byid = {n["id"]: n for n in core}
    byid["hg_c_in"]["links"] = ["hg_s_out", "hg_d_out"]
    byid["hg_c_st_in"]["links"] = ["hg_s_st_out"]

def gravar(nome, nos):
    p = RAIZ / "nodered/flows" / nome
    if p.exists() and not FORCAR:
        print(f"ABORTA: {p.name} ja existe (versao nova, nunca sobrescrever)"); sys.exit(1)
    p.write_text(json.dumps(nos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("ok", p.relative_to(RAIZ), f"{p.stat().st_size//1024} KB")

def main():
    contrato = contrato_monitorado()
    core, s7, demo = gerar_core(contrato), fonte_s7(contrato), fonte_demo()
    ligar_links(core, s7, demo)
    gravar(f"baggio_core_v{VERSAO}.json", core)
    gravar(f"baggio_fonte_s7_v{VERSAO}.json", s7)
    gravar(f"baggio_fonte_demo_v{VERSAO}.json", demo)
    print(f"{len(contrato['tags'])} bits monitorados; {len({t['byte'] for t in contrato['tags']})} bytes lidos")

if __name__ == "__main__":
    main()
