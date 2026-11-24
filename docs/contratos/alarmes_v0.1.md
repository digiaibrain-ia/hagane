# Catálogo de alertas e falhas (v0.1)

Gerado por `plc/variaveis/gerar_alarmes_v0.1.py` a partir de `plc/blocos/*.awl`. **Não editar à mão.**
Fatos do PLC = nível A. Efeito, causa e solução = **propostos (nível C)**, a validar com quem opera.

| Código | Alarme | Bit | Atraso | Retém | Bloco · rede | Observação do programa |
|---|---|---|---|---|---|---|
| `F-DSJ-001` | Disjuntor do transportador dragante desarmado | M10.4 | — | sim | CRITICO · 1 |  |
| `F-DSJ-002` | Disjuntor da bomba 1 desarmado | M10.5 | — | sim | CRITICO · 2 |  |
| `F-DSJ-003` | Disjuntor da bomba 2 desarmado | M10.6 | — | sim | CRITICO · 3 |  |
| `F-FLT-001` | Depressão do filtro | M11.6 | 60 s | sim | CRITICO · 9 | O significado exato de I5.1 (COMANDO DEPRESSÃO DO FILTRO) precisa ser confirmado com quem programou. |
| `F-NIV-001` | Nível mínimo do líquido a filtrar (tanque sujo) | M11.1 | — | sim | CRITICO · 4 |  |
| `F-OUT-001` | Aux 2 alarme critico | M16.0 | — | ? | — · — | Entrada gerada automaticamente da planilha de tags; sem lógica conhecida. |
| `F-OUT-002` | Alarme critico p/ nível min liquido filtrado | M16.1 | — | ? | — · — | Entrada gerada automaticamente da planilha de tags; sem lógica conhecida. |
| `F-OUT-003` | Aux 3 alarme critico | M16.3 | — | ? | — · — | Entrada gerada automaticamente da planilha de tags; sem lógica conhecida. |
| `F-OUT-004` | Aux 1 alarme critico | M21.5 | — | ? | — · — | Entrada gerada automaticamente da planilha de tags; sem lógica conhecida. |
| `F-PRS-001` | Pressão de ar comprimido insuficiente | M11.2 | — | sim | CRITICO · 5 |  |
| `F-PRT-001` | Soft-starter da bomba 1: partida fora do esperado | M61.0 | 10 s | sim | CRITICO · 10 | Confirmar a polaridade de I1.2 (fim de partida) e I1.3 (falha soft-start): o programa trata a condição como '(I1.2 e I1.1) ou (I1.3 em 0)'. Pendência P-14. |
| `F-PRT-002` | Soft-starter da bomba 2: partida fora do esperado | M61.1 | 10 s | sim | CRITICO · 11 | Confirmar a polaridade de I1.6 e I1.7 (mesma dúvida da bomba 1). Pendência P-14. |
| `F-PRT-003` | Bomba 1: partida não concluída no tempo | M10.1 | 10 s | sim | CRITICO · 12 | Polaridade de I1.2 a confirmar (P-14). |
| `F-PRT-004` | Bomba 2: partida não concluída no tempo | M10.3 | 15 s | sim | CRITICO · 13 | Polaridade de I1.6 a confirmar (P-14). |
| `F-SEG-001` | Emergência atuada | M11.5 | — | não | CRITICO · 7 |  |
| `A-BND-001` | Avanço da banda filtrante | M14.1 | 3 s | sim | PERMISSIVEL · 12 |  |
| `A-CMD-001` | Bomba do trocador de calor: comando sem retorno | M12.1 | 3 s | sim | PERMISSIVEL · 1 |  |
| `A-CMD-002` | Rotovac: comando sem retorno | M13.1 | 3 s | sim | PERMISSIVEL · 2 |  |
| `A-CMD-003` | Transportador dragante: comando sem retorno | M13.2 | 3 s | sim | PERMISSIVEL · 3 | O programa usa a saída Q9.0, que na planilha de tags está com o nome 'reserva' (qx_09.0_res). Confirmar se é essa mesma a saída do contator. |
| `A-CMD-004` | Aspirador: comando sem retorno | M13.4 | 3 s | sim | PERMISSIVEL · 4 |  |
| `A-CMD-005` | Extrator de lodo: comando sem retorno | M14.2 | 3 s | sim | PERMISSIVEL · 13 |  |
| `A-DSJ-004` | Disjuntor da bomba do trocador de calor desarmado | M13.6 | — | sim | PERMISSIVEL · 5 |  |
| `A-DSJ-005` | Disjuntor do rotovac desarmado | M15.0 | — | sim | PERMISSIVEL · 14 |  |
| `A-DSJ-006` | Disjuntor do aspirador desarmado | M15.1 | — | sim | PERMISSIVEL · 15 |  |
| `A-DSJ-007` | Disjuntor do extrator de lodo desarmado | M15.2 | — | sim | PERMISSIVEL · 16 |  |
| `A-ENC-001` | Duração máxima de enchimento | M15.7 | — | sim | PERMISSIVEL · 21 | Na rede 21 o selo está invertido (NÃO M15.7 E I0.2): ao apertar RESET o bit liga em vez de desligar. Confirmar com quem programou. |
| `A-NIV-002` | Nível mínimo do líquido filtrado (tanque limpo) | M13.7 | 10 s | sim | PERMISSIVEL · 7 |  |
| `A-NIV-003` | Nível máximo do líquido a filtrar (tanque sujo) | M14.0 | 10 s | sim | PERMISSIVEL · 9 |  |
| `A-NIV-004` | Nível máximo do líquido filtrado (tanque limpo) | M15.5 | 60 s | sim | PERMISSIVEL · 19 | Na rede 18 do FC_ALARME_PERMISSIVEL a condição é 'I6.4 E NÃO I6.4' (sempre falsa): o T15 nunca parte e este alarme não dispara. Confirmar com quem programou. |
| `A-OLE-001` | Falta de óleo para enchimento (reserva) | M15.4 | — | sim | PERMISSIVEL · 17 | A rede se chama 'FALTA ÓLEO P/ ENCHIMENTO (RESERVA)' e usa I7.3 e Q9.2, ambos com nome 'reserva' na planilha. |
| `A-OUT-001` | Alarme bomba 1 | M12.2 | — | ? | — · — | Entrada gerada automaticamente da planilha de tags; sem lógica conhecida. |
| `A-OUT-002` | Alarme bomba 2 | M12.3 | — | ? | — · — | Entrada gerada automaticamente da planilha de tags; sem lógica conhecida. |
| `A-OUT-003` | Alarme temperatura armário elétrico | M13.0 | — | ? | — · — | Entrada gerada automaticamente da planilha de tags; sem lógica conhecida. |
| `A-OUT-004` | Aux 1 alarme permissível | M21.1 | — | ? | — · — | Entrada gerada automaticamente da planilha de tags; sem lógica conhecida. |
| `A-OUT-005` | Aux 2 alarme permissível | M21.2 | — | ? | — · — | Entrada gerada automaticamente da planilha de tags; sem lógica conhecida. |
| `A-OUT-006` | Alarme bomba 1 | M122.2 | — | ? | — · — | Entrada gerada automaticamente da planilha de tags; sem lógica conhecida. |
| `A-OUT-007` | Alarme bomba 2 | M122.3 | — | ? | — · — | Entrada gerada automaticamente da planilha de tags; sem lógica conhecida. |
| `I-AUX-001` | Auxiliares desabilitados | M11.3 | — | não | CRITICO · 6 |  |
| `I-ENC-002` | Nível de enchimento (início) | M17.7 | — | sim | PERMISSIVEL · 20 |  |
