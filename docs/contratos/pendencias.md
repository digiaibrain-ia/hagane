# Pendências do contrato (humanas)

Geradas da planilha: [pendencias_geradas.md](pendencias_geradas.md).

| ID | Pergunta | Por que importa | Estado |
|---|---|---|---|
| P-01 | `I3.2–I3.4` têm nome `_res` e comentário de nível: são cópia não usada de `I6.2–I6.4`? | Duplicata na grade de I/O confunde o operador | aberta |
| P-02 | `I8.0–I8.6` (nome `_res`, comentário "SAE/SBE…", com `KAA23.5`): é um segundo módulo de entradas real, em uso? | Entram na tela de I/O? | aberta |
| P-03 | `IW352` (contador de banda rasgada), `IW356` (transdutor de pressão), `QW336` (saída p/ inversor): escala e unidade? Endereços de periferia (`PIW`)? | Overview mostra Hz das bombas | aberta |
| P-04 | Quais `M` são alarme **crítico** e quais **permissível**? A planilha não diz | Prioridade e cor na tela de alertas | **respondida em parte (24/11):** os blocos `FC_ALARME_CRITICO` e `FC_ALARME_PERMISSIVEL` definem 24 alarmes (ver `alarmes_v0.1.md`). Faltam os outros 11 (M12.2/M12.3, M122.x, M13.0, M16.x, M21.x), cuja lógica está em outro bloco |
| P-05 | O que `PT1` e `PT2` significam (pontos de comando local?) | Texto da tela | aberta |
| P-06 | Restos de outra máquina (bomba 3/4, desoleador, separador magnético, inverter): ocultar? | BG-003 | aberta |
| P-07 | O que o operador fazia no WinCC além de ver? (reset, silenciar, ciclos) | Decide se v0.2 tem comandos | aberta |
| P-08 | Qual o endereço dos DBs/tags que o WinCC lia (se houver DB)? | Planilha só tem I/Q/M/T/C | aberta |
| P-09 | PUT/GET ou comunicação S7 liberada na CPU 315 V3.2 para o Node-RED (rack 0, slot 2)? | Sem isso o Node-RED não lê | a testar |

Respondidas pela planilha: **T.C. = trocador de calor** (bomba e válvula T.C.).

| P-10 | Sensores de nível: lâmpada/entrada ativa significa "nível atingido" (coberto)? Vale para mínimo e baixo também? | A barra de nível do overview é uma **estimativa** pela suposição "ativo = atingido" | aberta |
| P-11 | Alarmes derivados de entrada: `I0.1`/`I4.7` ativos = emergência; `I0.3` e disjuntores `OK` em 0 = falha; `I1.3`/`I1.7` ativos = falha de soft-start. Polaridade correta? | Evita falso alarme ou alarme que não aparece | aberta (validar na máquina) |
| P-12 | CPU 315: acesso S7 sem PUT/GET extra, rack 0 / slot 2, e o Node-RED enxerga `192.168.0.2` do notebook? | Sem isso a leitura real não conecta | a testar no notebook |
| P-13 | O nível dos tanques na tela vem dos sensores `I6.x` com a suposição "sensor ativo = coberto". Confere com a máquina? E a lâmpada "Nível mínimo" do sinótico (`Q14.5`/`Q15.1`) acende com nível baixo ou com nível presente? | A água do desenho e as lâmpadas têm que contar a mesma história | aberta (validar no PLCSIM/CPU) |
| P-14 | Polaridade de `I1.2`/`I1.6` (fim de partida) e `I1.3`/`I1.7` (falha soft-start): o programa dispara `M61.x` com `(I1.2 e I1.1) ou (I1.3 em 0)` e `M10.1/M10.3` com `I1.2 = 1` por 10 s. Qual é o sentido real dos contatos? | A v0.5 tratava `I1.3 = 1` como falha: era o inverso. Removido; o HTML só usa os `M` do PLC | aberta |
| P-15 | O alarme `A-CMD-003` (dragante) usa a saída `Q9.0`, cujo nome na planilha é `qx_09.0_res` (reserva). É o contator do dragante mesmo? | Texto do alarme e lista de saídas | aberta |
| P-16 | `A-NIV-004` (`M15.5`): a rede 18 tem `I6.4 E NÃO I6.4` (sempre falso): o T15 nunca parte e o alarme não dispara | Alarme de nível máximo do tanque limpo inoperante | aberta (programa) |
| P-17 | `A-ENC-001` (`M15.7`): selo invertido (`NÃO M15.7 E I0.2`): ao apertar RESET o bit liga. O T54 é iniciado fora dos blocos fornecidos | Alarme de duração de enchimento | aberta (programa) |
| P-18 | Efeito, causa, teste rápido e solução dos alarmes são **texto proposto** a partir da lógica do PLC. Quem opera a máquina precisa validar/corrigir (`plc/variaveis/gerar_alarmes_v0.1.py`) | Evitar orientação errada ao operador | aberta |
| P-19 | `F-PRT-001/002` e `F-FLT-001`: confirmar o significado de `I5.1` (comando depressão do filtro) e se `M20.1` é mesmo "automático selecionado" | Texto do gatilho | aberta |

