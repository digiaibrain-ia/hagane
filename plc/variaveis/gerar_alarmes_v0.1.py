#!/usr/bin/env python3
"""Gera o CATALOGO DE ALERTAS E FALHAS do Baggio a partir dos blocos do PLC.

Uso:  python3 -B -I plc/variaveis/gerar_alarmes_v0.1.py
Entradas : plc/blocos/FC_ALARME_CRITICO.awl, plc/blocos/FC_ALARME_PERMISSIVEL.awl   (codigo do PLC = fonte dos FATOS)
           docs/contratos/tags_v0.1.json                                             (nome da tag -> endereco)
Saidas   : docs/contratos/alarmes_v0.1.json   (embutido no HTML)
           docs/contratos/alarmes_v0.1.md     (tabela para leitura)

O que vem do PLC (provado, nivel A): bit do alarme, bloco e rede, tempo de atraso, retentivo (selo + RESET), porta T31
(maquina em trabalho), entradas/saidas/temporizadores usados. Esses campos sao EXTRAIDOS do .awl, nao digitados.
O que e PROPOSTO (nivel C, a validar com quem opera a maquina): efeito, causas, teste rapido e solucao.
Verificacao automatica: todo endereco citado no texto "gatilho" tem de existir na rede do PLC correspondente.

Codigo no padrao do medidor: T-AAA-NNN  (T: F = Falha, A = Alerta, I = Informacao; AAA = familia; NNN = numero).
Mapeamento: bloco CRITICO -> F ; bloco PERMISSIVEL -> A ; estados (nao sao alarme) -> I. Numero nunca se reutiliza.
"""
import json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BLOCOS = {"FC_ALARME_CRITICO": "critico", "FC_ALARME_PERMISSIVEL": "permissivel"}
RESET = "ix_0.2_btResetFalhas"          # RESET FALHAS (I0.2)

FAMILIAS = {
    "DSJ": "Disjuntor desarmado", "CMD": "Comando sem retorno (motor)", "NIV": "Nível dos tanques",
    "PRS": "Pressão de ar", "SEG": "Segurança e emergência", "FLT": "Filtro (depressão)",
    "PRT": "Partida das bombas", "BND": "Banda filtrante", "OLE": "Óleo (reserva)", "ENC": "Enchimento",
    "AUX": "Auxiliares", "OUT": "Outros (lógica não fornecida)",
}
ONDE = {"operador": "Operador (botão/tela)", "painel": "Painel elétrico", "campo": "Campo (máquina)", "programa": "Programa (engenharia)"}

# ------------------------------------------------------------------ 1. leitura do PLC (fatos)
def enderecos():
    d = json.loads((RAIZ / "docs/contratos/tags_v0.1.json").read_text(encoding="utf-8"))
    return {t["nome"]: t["endereco"] for t in d["tags"]}, {t["endereco"]: t for t in d["tags"]}

NOME2END, END2TAG = enderecos()
def end(nome):
    return NOME2END.get(nome, nome)

def le_redes(bloco):
    txt = (RAIZ / f"plc/blocos/{bloco}.awl").read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n")
    redes = []
    for i, r in enumerate(re.split(r"\nNETWORK\n", txt)[1:], 1):
        tit = (re.search(r"TITLE =(.*)", r).group(1) or "").strip()
        ops = re.findall(r'^\s*(?:A|AN|O|ON)\s+"([^"]+)"', r, re.M)       # operandos de contato
        saidas = re.findall(r'^\s*=\s+"([^"]+)"', r, re.M)
        sd = re.findall(r'^\s*SD\s+"([^"]+)"', r, re.M)
        pre = re.findall(r"S5T#(\d+)(MS|S|M)", r)
        seg = None
        if pre:
            v, u = pre[0]; seg = int(v) * {"MS": 0.001, "S": 1, "M": 60}[u]
        redes.append({"n": i, "titulo": tit, "ops": ops, "saidas": saidas, "timers": sd, "preset_s": seg})
    return redes

def fatos():
    """Por bit de alarme (ex.: M10.4): rede, retentivo, T31, entradas, temporizadores (com atraso e condicao)."""
    out = {}
    for bloco, prio in BLOCOS.items():
        redes = le_redes(bloco)
        tim = {}                                   # timer -> (preset, operandos que o disparam)
        for r in redes:
            for t in r["timers"]:
                tim[t] = (r["preset_s"], [o for o in r["ops"] if not o.startswith("timer")], r["n"], r["ops"])
        for r in redes:
            if not r["saidas"]:
                continue
            for s in r["saidas"]:
                b = end(s)
                if not re.fullmatch(r"M\d+\.\d", b):
                    continue
                ops = [o for o in r["ops"] if o != s]
                retent = s in r["ops"] and RESET in r["ops"]
                tms = [o for o in ops if o.startswith("timer") and o != "timer31"]
                atr = [tim[t][0] for t in tms if t in tim]
                ent = []
                for o in ops:
                    if o.startswith("timer") or o == RESET:
                        continue
                    ent.append(o)
                for t in tms:
                    if t in tim:
                        ent += tim[t][1] + (["timer31"] if "timer31" in tim[t][3] else [])
                ent = list(dict.fromkeys(ent))
                out[b] = {"bloco": bloco, "prioridade": prio, "rede": r["n"], "titulo_plc": r["titulo"], "retentivo": retent,
                          "porta_t31": "timer31" in ops or any("timer31" in tim[t][3] for t in tms if t in tim),
                          "atraso_s": atr[0] if atr else None, "timers": [end(t) for t in tms],
                          "operandos": sorted(({end(o) for o in ent} | {end(t) for t in tms} | ({"T31"} if "timer31" in ops else set())
                                              | ({end(RESET)} if RESET in r["ops"] else set())) - {b} - {"T31"} | ({"T31"} if ("timer31" in ops or any("timer31" in tim[t][3] for t in tms if t in tim)) else set()))}
    return out

FATOS = fatos()

# ------------------------------------------------------------------ 2. textos propostos (nivel C)
def causas_disj(equip, entrada, extra=None):
    c = [
        {"t": "O disjuntor desarmou por sobrecorrente ou curto-circuito (motor travado, sobrecarga, isolação ruim).",
         "teste": "Olhe a alavanca do disjuntor no painel: está em TRIP/OFF? Se rearmar e ele desarmar de novo, a falha é real no motor ou no cabo.",
         "sol": [["Descubra e elimine a causa (travamento, sobrecarga, isolação) antes de rearmar.", "campo"],
                 ["Rearme o disjuntor e aperte RESET FALHAS.", "operador"]]},
        {"t": f"Contato auxiliar do disjuntor com defeito ou fio solto na entrada {entrada}.",
         "teste": f"Com o disjuntor ligado, a entrada {entrada} deve estar em 1 (veja na tela Entradas e saídas). Se continua em 0, o problema é o contato ou a fiação.",
         "sol": [[f"Troque o contato auxiliar ou refaça a ligação até a entrada {entrada}.", "painel"]]}]
    return c

def causas_cmd(equip, saida, retorno):
    return [
        {"t": f"O contator de {equip} não fechou (bobina, relé auxiliar ou relé térmico aberto).",
         "teste": f"A saída {saida} está acesa na tela Entradas e saídas? No painel, o contator está fechado?",
         "sol": [["Verifique bobina, relé térmico e fiação do contator.", "painel"], ["Depois de corrigir, aperte RESET FALHAS.", "operador"]]},
        {"t": f"O contato auxiliar do contator não devolve o sinal 'ligado' para a entrada {retorno} (fio solto ou contato com defeito).",
         "teste": f"Com o contator fechado, a entrada {retorno} deve ir para 1.",
         "sol": [[f"Corrija o contato auxiliar ou o fio até a entrada {retorno}.", "painel"]]}]

T = []   # entradas do catalogo
def add(bit, codigo, nome, gatilho, efeito, causas, obs=None):
    T.append(dict(bit=bit, codigo=codigo, nome=nome, gatilho=gatilho, efeito=efeito, causas=causas, obs=obs))

# ---- CRITICOS (F) ----
add("M10.4", "F-DSJ-001", "Disjuntor do transportador dragante desarmado",
    "Contato OK do disjuntor (I3.5) em 0 com a máquina em trabalho há 3 s (T31).",
    "O transportador dragante perde a alimentação: o lodo não é retirado do filtro.", causas_disj("transportador dragante", "I3.5"))
add("M10.5", "F-DSJ-002", "Disjuntor da bomba 1 desarmado",
    "Contato OK do disjuntor da bomba 1 (I1.0) em 0 com a máquina em trabalho há 3 s (T31).",
    "A bomba 1 fica sem alimentação: não parte ou para, e a filtragem perde vazão.", causas_disj("bomba 1", "I1.0"))
add("M10.6", "F-DSJ-003", "Disjuntor da bomba 2 desarmado",
    "Contato OK do disjuntor da bomba 2 (I1.4) em 0 com a máquina em trabalho há 3 s (T31).",
    "A bomba 2 fica sem alimentação: não parte ou para, e a filtragem perde vazão.", causas_disj("bomba 2", "I1.4"))
add("M11.1", "F-NIV-001", "Nível mínimo do líquido a filtrar (tanque sujo)",
    "Sensor de nível mínimo do tanque sujo (I6.1) em 0 com a máquina em trabalho (T31). Sem atraso adicional.",
    "Pouco líquido no tanque sujo: as bombas de filtragem podem ficar sem líquido (risco de rodar a seco).",
    [{"t": "Falta de alimentação do tanque sujo (retorno da produção parado ou válvula fechada).",
      "teste": "Olhe o nível do tanque sujo no Overview e a válvula de alimentação/retorno.",
      "sol": [["Restabeleça a alimentação do tanque sujo.", "campo"], ["Com o nível normal, aperte RESET FALHAS.", "operador"]]},
     {"t": "Sensor de nível mínimo (I6.1) sujo, desregulado ou com fio solto.",
      "teste": "Com o tanque com líquido acima do sensor, a entrada I6.1 deve estar em 1 (tela Entradas e saídas).",
      "sol": [["Limpe, regule ou troque o sensor; confira a fiação.", "campo"]]}])
add("M11.2", "F-PRS-001", "Pressão de ar comprimido insuficiente",
    "Entrada de presença de ar comprimido (I5.0) em 0 com a máquina em trabalho (T31).",
    "Sem ar: válvulas pneumáticas (sopro, quebra vácuo e outras) podem não atuar corretamente.",
    [{"t": "Compressor desligado ou rede de ar sem pressão.", "teste": "Veja o manômetro da rede de ar e se o compressor está em operação.",
      "sol": [["Religue o compressor ou corrija o vazamento na rede de ar.", "campo"], ["Com a pressão normal, aperte RESET FALHAS.", "operador"]]},
     {"t": "Pressostato desregulado ou com fio solto na entrada I5.0.", "teste": "Com a rede pressurizada, a entrada I5.0 deve ir para 1.",
      "sol": [["Regule ou troque o pressostato; confira a fiação.", "painel"]]}])
add("M11.5", "F-SEG-001", "Emergência atuada",
    "Botão de emergência do painel (I0.1) em 1, OU relé do circuito de segurança (I0.3) em 0, OU botão de emergência do filtro (I4.7) em 1. Sem atraso e sem retenção: acompanha a condição.",
    "O circuito de segurança está aberto: a máquina fica parada pela emergência.",
    [{"t": "Botão de emergência do painel (I0.1) ou do filtro (I4.7) pressionado.", "teste": "Olhe os dois botões de emergência: algum está travado em baixo?",
      "sol": [["Libere (destrave) o botão de emergência depois de confirmar que o local está seguro.", "campo"], ["Aperte RESET FALHAS e religue pelo procedimento normal.", "operador"]]},
     {"t": "Relé do circuito de segurança (I0.3) sem OK por falha no circuito (porta aberta, cabo, relé).", "teste": "Com os botões soltos, a entrada I0.3 deve estar em 1.",
      "sol": [["Verifique o circuito de segurança e o relé; corrija a causa.", "painel"]]}])
add("M11.6", "F-FLT-001", "Depressão do filtro",
    "Comando de depressão do filtro (I5.1) em 1 por 1 min (T10), com a máquina em trabalho (T31).",
    "A depressão (vácuo) do filtro permaneceu fora do esperado por mais de 1 minuto.",
    [{"t": "Vazamento de vácuo no filtro (válvula quebra vácuo travada aberta ou vedação ruim).", "teste": "Veja se a válvula quebra vácuo no Overview está aberta quando não deveria.",
      "sol": [["Verifique a válvula quebra vácuo e as vedações do filtro.", "campo"], ["Corrigida a causa, aperte RESET FALHAS.", "operador"]]},
     {"t": "Aspirador ou rotovac sem rendimento.", "teste": "Aspirador e rotovac estão em operação no Overview?",
      "sol": [["Verifique o aspirador e o rotovac.", "campo"]]}],
    obs="O significado exato de I5.1 (COMANDO DEPRESSÃO DO FILTRO) precisa ser confirmado com quem programou.")
add("M61.0", "F-PRT-001", "Soft-starter da bomba 1: partida fora do esperado",
    "Modo automático (M20.1) E ((fim de partida I1.2 E bomba 1 ligada I1.1) OU softstart sem OK I1.3 em 0) por 10 s (T2).",
    "A bomba 1 não completou a partida pelo soft-starter no tempo esperado.",
    [{"t": "Soft-starter em falha ou sem completar a rampa de partida.", "teste": "Veja os LEDs do soft-starter da bomba 1 e as entradas I1.1, I1.2 e I1.3 na tela Entradas e saídas.",
      "sol": [["Verifique o soft-starter (falha, parametrização, alimentação).", "painel"], ["Depois, aperte RESET FALHAS.", "operador"]]}],
    obs="Confirmar a polaridade de I1.2 (fim de partida) e I1.3 (falha soft-start): o programa trata a condição como '(I1.2 e I1.1) ou (I1.3 em 0)'. Pendência P-14.")
add("M61.1", "F-PRT-002", "Soft-starter da bomba 2: partida fora do esperado",
    "Modo automático (M20.1) E ((fim de partida I1.6 E bomba 2 ligada I1.5) OU softstart sem OK I1.7 em 0) por 10 s (T3).",
    "A bomba 2 não completou a partida pelo soft-starter no tempo esperado.",
    [{"t": "Soft-starter em falha ou sem completar a rampa de partida.", "teste": "Veja os LEDs do soft-starter da bomba 2 e as entradas I1.5, I1.6 e I1.7 na tela Entradas e saídas.",
      "sol": [["Verifique o soft-starter (falha, parametrização, alimentação).", "painel"], ["Depois, aperte RESET FALHAS.", "operador"]]}],
    obs="Confirmar a polaridade de I1.6 e I1.7 (mesma dúvida da bomba 1). Pendência P-14.")
add("M10.1", "F-PRT-003", "Bomba 1: partida não concluída no tempo",
    "Modo automático (M20.1), fim de partida (I1.2) e comando liga da bomba 1 (Q8.0) por 10 s (T13).",
    "A bomba 1 foi comandada a ligar, mas a partida não terminou no tempo esperado.",
    [{"t": "A bomba não parte (soft-starter, contator ou motor).", "teste": "Q8.0 está ligada e a bomba 1 mostra 'em operação' (I1.1) no Overview?",
      "sol": [["Verifique soft-starter, contator e motor da bomba 1.", "painel"], ["Depois, aperte RESET FALHAS.", "operador"]]}],
    obs="Polaridade de I1.2 a confirmar (P-14).")
add("M10.3", "F-PRT-004", "Bomba 2: partida não concluída no tempo",
    "Modo automático (M20.1), fim de partida (I1.6) e comando liga da bomba 2 (Q8.2) por 15 s (T14).",
    "A bomba 2 foi comandada a ligar, mas a partida não terminou no tempo esperado.",
    [{"t": "A bomba não parte (soft-starter, contator ou motor).", "teste": "Q8.2 está ligada e a bomba 2 mostra 'em operação' (I1.5) no Overview?",
      "sol": [["Verifique soft-starter, contator e motor da bomba 2.", "painel"], ["Depois, aperte RESET FALHAS.", "operador"]]}],
    obs="Polaridade de I1.6 a confirmar (P-14).")

# ---- PERMISSIVEIS (A) ----
add("M12.1", "A-CMD-001", "Bomba do trocador de calor: comando sem retorno",
    "Saída de comando da bomba do trocador de calor (Q8.4) ligada e retorno 'ligada' (I2.1) em 0 por 3 s (T12).",
    "Foi mandado ligar a bomba do trocador de calor, mas o retorno não chegou: ela pode não estar girando.",
    causas_cmd("a bomba do trocador de calor", "Q8.4", "I2.1"))
add("M13.1", "A-CMD-002", "Rotovac: comando sem retorno",
    "Saída de comando do rotovac (Q8.7) ligada e retorno 'ligado' (I3.1) em 0 por 3 s (T17).",
    "Foi mandado ligar o rotovac, mas o retorno não chegou: ele pode não estar girando.", causas_cmd("o rotovac", "Q8.7", "I3.1"))
add("M13.2", "A-CMD-003", "Transportador dragante: comando sem retorno",
    "Saída de comando do transportador dragante (Q9.0) ligada e retorno 'ligado' (I3.6) em 0 por 3 s (T20).",
    "Foi mandado ligar o transportador dragante, mas o retorno não chegou: ele pode não estar andando.",
    causas_cmd("o transportador dragante", "Q9.0", "I3.6"),
    obs="O programa usa a saída Q9.0, que na planilha de tags está com o nome 'reserva' (qx_09.0_res). Confirmar se é essa mesma a saída do contator.")
add("M13.4", "A-CMD-004", "Aspirador: comando sem retorno",
    "Saída de comando do aspirador (Q8.5) ligada e retorno 'ligado' (I2.3) em 0 por 3 s (T22).",
    "Foi mandado ligar o aspirador, mas o retorno não chegou: ele pode não estar girando.", causas_cmd("o aspirador", "Q8.5", "I2.3"))
add("M14.2", "A-CMD-005", "Extrator de lodo: comando sem retorno",
    "Saída de comando do extrator de lodo (Q8.6) ligada e retorno 'ligado' (I2.5) em 0 por 3 s (T30).",
    "Foi mandado ligar o extrator de lodo, mas o retorno não chegou: ele pode não estar girando.", causas_cmd("o extrator de lodo", "Q8.6", "I2.5"))
add("M13.6", "A-DSJ-004", "Disjuntor da bomba do trocador de calor desarmado",
    "Contato OK do disjuntor (I2.0) em 0 com a máquina em trabalho há 3 s (T31).",
    "A bomba do trocador de calor fica sem alimentação: o líquido refrigerante pode não circular.", causas_disj("bomba do trocador de calor", "I2.0"))
add("M15.0", "A-DSJ-005", "Disjuntor do rotovac desarmado",
    "Contato OK do disjuntor (I3.0) em 0 com a máquina em trabalho há 3 s (T31).",
    "O rotovac fica sem alimentação: não gira.", causas_disj("rotovac", "I3.0"))
add("M15.1", "A-DSJ-006", "Disjuntor do aspirador desarmado",
    "Contato OK do disjuntor (I2.2) em 0 com a máquina em trabalho há 3 s (T31).",
    "O aspirador fica sem alimentação: o vácuo do filtro cai.", causas_disj("aspirador", "I2.2"))
add("M15.2", "A-DSJ-007", "Disjuntor do extrator de lodo desarmado",
    "Contato OK do disjuntor (I2.4) em 0 com a máquina em trabalho há 3 s (T31).",
    "O extrator de lodo fica sem alimentação: o lodo se acumula.", causas_disj("extrator de lodo", "I2.4"))
add("M13.7", "A-NIV-002", "Nível mínimo do líquido filtrado (tanque limpo)",
    "Sensor de nível mínimo do tanque de compensação (I6.5) em 0 por 10 s (T24), com a máquina em trabalho (T31).",
    "Pouco líquido filtrado no tanque limpo: o consumo pode estar maior que a produção do filtro.",
    [{"t": "O filtro está produzindo menos que o consumo (banda/manta saturada, bombas paradas).", "teste": "Veja se as bombas e a banda estão em operação no Overview.",
      "sol": [["Verifique bombas, banda filtrante e manta.", "campo"], ["Com o nível normal, aperte RESET FALHAS.", "operador"]]},
     {"t": "Sensor de nível mínimo (I6.5) sujo, desregulado ou com fio solto.", "teste": "Com o tanque limpo cheio acima do sensor, a entrada I6.5 deve estar em 1.",
      "sol": [["Limpe, regule ou troque o sensor; confira a fiação.", "campo"]]}])
add("M14.0", "A-NIV-003", "Nível máximo do líquido a filtrar (tanque sujo)",
    "Sensor de nível máximo do tanque sujo (I6.0) em 1 por 10 s (T25), com a máquina em trabalho (T31).",
    "Tanque sujo cheio: o filtro não está dando conta da vazão que chega.",
    [{"t": "O filtro está lento (banda/manta saturada, bombas paradas ou vazão de entrada alta).", "teste": "Bombas e banda em operação? A manta está avançando (Overview)?",
      "sol": [["Verifique bombas, banda e manta; reduza a vazão de entrada se necessário.", "campo"], ["Com o nível normal, aperte RESET FALHAS.", "operador"]]},
     {"t": "Sensor de nível máximo (I6.0) sujo ou travado em 1.", "teste": "Com o tanque abaixo do máximo, a entrada I6.0 deve estar em 0.",
      "sol": [["Limpe ou troque o sensor.", "campo"]]}])
add("M15.5", "A-NIV-004", "Nível máximo do líquido filtrado (tanque limpo)",
    "Temporizador T15 (1 min) com a máquina em trabalho (T31). Ver observação: a condição de partida do T15 está contraditória no programa.",
    "Tanque limpo cheio demais (se o alarme funcionasse).",
    [{"t": "Alarme provavelmente nunca dispara (ver observação).", "teste": "Não há teste prático enquanto o programa tiver a contradição.",
      "sol": [["Corrigir a rede 'CONTROLE NÍVEL MAX LIQUIDO FILTRADO' no programa.", "programa"]]}],
    obs="Na rede 18 do FC_ALARME_PERMISSIVEL a condição é 'I6.4 E NÃO I6.4' (sempre falsa): o T15 nunca parte e este alarme não dispara. Confirmar com quem programou.")
add("M14.1", "A-BND-001", "Avanço da banda filtrante",
    "Transportador dragante ligado (I3.6) E controle de avanço da manta (I4.1) parado em 1 por 3 s (T26) OU parado em 0 por 3 s (T27).",
    "A banda filtrante não está avançando: o filtro tende a saturar.",
    [{"t": "A manta/banda acabou, rompeu ou travou.", "teste": "Olhe a banda no filtro: está andando? Há manta no rolo?",
      "sol": [["Troque a manta ou destrave a banda.", "campo"], ["Depois, aperte RESET FALHAS.", "operador"]]},
     {"t": "Sensor/controle de avanço da manta (I4.1) sem pulso (defeito ou fio solto).", "teste": "Com a banda andando, a entrada I4.1 deve alternar entre 0 e 1.",
      "sol": [["Verifique o sensor de avanço e a fiação.", "painel"]]}])
add("M15.4", "A-OLE-001", "Falta de óleo para enchimento (reserva)",
    "Entradas/saídas de reserva (I7.3 E Q9.2) com a máquina em trabalho (T31).",
    "Função em reserva: provavelmente sem uso nesta máquina.",
    [{"t": "Rede marcada como reserva no programa.", "teste": "Confirme com quem programou se a função existe.", "sol": [["Confirmar e, se não existir, remover o alarme do programa e da tela.", "programa"]]}],
    obs="A rede se chama 'FALTA ÓLEO P/ ENCHIMENTO (RESERVA)' e usa I7.3 e Q9.2, ambos com nome 'reserva' na planilha.")
add("M15.7", "A-ENC-001", "Duração máxima de enchimento",
    "Temporizador T54 (partida fora dos blocos fornecidos). O selo da rede está invertido: 'NÃO M15.7 E RESET'.",
    "O enchimento passou do tempo máximo (se o alarme funcionasse).",
    [{"t": "Tempo de enchimento acima do limite (sensor de fim de enchimento sem atuar, falta de vazão).", "teste": "Veja os sensores de início e fim de enchimento (I6.2 e I6.3) na tela Entradas e saídas.",
      "sol": [["Verifique sensores de enchimento e a alimentação do tanque.", "campo"]]}],
    obs="Na rede 21 o selo está invertido (NÃO M15.7 E I0.2): ao apertar RESET o bit liga em vez de desligar. Confirmar com quem programou.")

# ---- INFORMACOES (I): estados, nao sao alarme ----
add("M11.3", "I-AUX-001", "Auxiliares desabilitados",
    "Relé de controle desligado (I0.0 em 0) OU máquina não está em trabalho (M100.0 em 0). Sem atraso e sem retenção.",
    "Informação de estado: os auxiliares ficam desabilitados enquanto a máquina não está em trabalho.",
    [{"t": "Máquina parada ou relé de controle desligado (situação normal com a máquina desligada).", "teste": "Veja 'Comando ligado' no Overview.",
      "sol": [["Ligue o comando pelo procedimento normal, se a máquina deve operar.", "operador"]]}])
add("M17.7", "I-ENC-002", "Nível de enchimento (início)",
    "Nível de início de enchimento (I6.2) em 1, retido até RESET FALHAS.",
    "Informação de estado do ciclo de enchimento.",
    [{"t": "Condição normal do ciclo de enchimento.", "teste": "Veja os sensores de nível do tanque sujo no Overview.", "sol": [["Nenhuma ação: é só informação.", "operador"]]}])

# ------------------------------------------------------------------ 3. montagem + verificacao
def monta():
    erros, out = [], []
    vistos_cod, familias_cnt = set(), {}
    for t in T:
        f = FATOS.get(t["bit"])
        if not f:
            erros.append(f"{t['bit']}: nao existe saida no .awl"); continue
        tipo, fam, num = t["codigo"].split("-")
        if t["codigo"] in vistos_cod: erros.append(f"codigo repetido {t['codigo']}")
        vistos_cod.add(t["codigo"])
        # todo endereco citado no gatilho tem de existir na rede do PLC
        cit = set(re.findall(r"\b([IQM]\d+\.\d|T\d+)\b", t["gatilho"])) - {t["bit"]}
        extras = cit - set(f["operandos"]) - {"M20.1"} if "M20.1" in f["operandos"] else cit - set(f["operandos"])
        if extras: erros.append(f"{t['bit']}: gatilho cita {sorted(extras)} que nao estao na rede do PLC ({f['operandos']})")
        esperado = {"critico": "F", "permissivel": "A"}[f["prioridade"]]
        if tipo != "I" and tipo != esperado:
            erros.append(f"{t['bit']}: tipo {tipo} nao bate com o bloco ({f['prioridade']})")
        tag = END2TAG.get(t["bit"], {})
        out.append({**t, "tipo": tipo, "familia": fam, "familia_nome": FAMILIAS[fam], "prioridade": f["prioridade"],
                    "bloco": f["bloco"], "rede": f["rede"], "rede_titulo": f["titulo_plc"], "retentivo": f["retentivo"],
                    "reset": "I0.2 (RESET FALHAS)" if f["retentivo"] else None, "porta_t31": f["porta_t31"],
                    "atraso_s": f["atraso_s"], "timers": f["timers"], "operandos": f["operandos"],
                    "comentario_tag": tag.get("comentario", ""), "evidencia": {"logica": "A (extraída do PLC)", "texto": "C (proposto, a validar)"}})
    # alarmes da planilha sem logica fornecida (outros blocos)
    cobertos = {t["bit"] for t in T}
    ignora = {"M21.0", "M21.3", "M21.4"}                      # resumos/estado, ja sao mostrados no selo do cabecalho
    n = {"F": 0, "A": 0}
    for end_, tg in sorted(END2TAG.items(), key=lambda kv: (int(re.match(r"M(\d+)", kv[0]).group(1)) if kv[0].startswith("M") and re.match(r"M\d+\.\d", kv[0]) else 9999, kv[0])):
        if tg.get("classe") != "alarme" or end_ in cobertos or end_ in ignora: continue
        crit = bool(re.search(r"CRITICO|CRÍTICO", tg["comentario"], re.I))
        tp = "F" if crit else "A"; n[tp] += 1
        cod = f"{tp}-OUT-{n[tp]:03d}"
        out.append({"bit": end_, "codigo": cod, "tipo": tp, "familia": "OUT", "familia_nome": FAMILIAS["OUT"],
                    "nome": tg["comentario"].capitalize(), "prioridade": "critico" if crit else "permissivel", "bloco": None, "rede": None,
                    "rede_titulo": None, "retentivo": None, "reset": None, "porta_t31": None, "atraso_s": None, "timers": [], "operandos": [end_],
                    "gatilho": "A lógica deste alarme não está nos blocos fornecidos (FC_ALARME_CRITICO e FC_ALARME_PERMISSIVEL).",
                    "efeito": "Sem descrição: a lógica deste alarme está em outro bloco do programa.",
                    "causas": [{"t": "Causa a definir quando o bloco que gera este alarme for fornecido.", "teste": "Veja o comentário da tag na planilha: " + tg["comentario"], "sol": []}],
                    "obs": "Entrada gerada automaticamente da planilha de tags; sem lógica conhecida.", "comentario_tag": tg["comentario"],
                    "evidencia": {"logica": "sem fonte", "texto": "gerado da planilha"}})
    if erros:
        print("ERROS DE VERIFICACAO:"); [print("  -", e) for e in erros]; sys.exit(1)
    out.sort(key=lambda a: ({"F": 0, "A": 1, "I": 2}[a["tipo"]], a["codigo"]))
    return out

def main():
    alarmes = monta()
    cat = {"versao": "0.1", "fonte": ["plc/blocos/FC_ALARME_CRITICO.awl", "plc/blocos/FC_ALARME_PERMISSIVEL.awl"],
           "aviso": "Fatos (bit, bloco, rede, atraso, retenção, endereços) são extraídos do código do PLC. Efeito, causas, teste rápido e solução são PROPOSTOS e precisam da validação de quem opera a máquina.",
           "familias": FAMILIAS, "onde": ONDE, "alarmes": alarmes}
    dst = RAIZ / "docs/contratos"
    (dst / "alarmes_v0.1.json").write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
    L = ["# Catálogo de alertas e falhas (v0.1)", "", "Gerado por `plc/variaveis/gerar_alarmes_v0.1.py` a partir de `plc/blocos/*.awl`. **Não editar à mão.**",
         "Fatos do PLC = nível A. Efeito, causa e solução = **propostos (nível C)**, a validar com quem opera.", "",
         "| Código | Alarme | Bit | Atraso | Retém | Bloco · rede | Observação do programa |", "|---|---|---|---|---|---|---|"]
    for a in alarmes:
        L.append(f"| `{a['codigo']}` | {a['nome']} | {a['bit']} | {str(a['atraso_s']) + ' s' if a['atraso_s'] else '—'} | "
                 f"{'sim' if a['retentivo'] else ('não' if a['retentivo'] is False else '?')} | "
                 f"{(a['bloco'] or '—').replace('FC_ALARME_', '')} · {a['rede'] or '—'} | {(a.get('obs') or '').replace('|', '/')} |")
    (dst / "alarmes_v0.1.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    n = {k: sum(1 for a in alarmes if a["tipo"] == k) for k in "FAI"}
    print(f"{len(alarmes)} entradas (F={n['F']} A={n['A']} I={n['I']}); {sum(1 for a in alarmes if a['familia'] == 'OUT')} sem logica fornecida")

if __name__ == "__main__":
    main()
