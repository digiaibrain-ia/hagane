# Pendências do contrato (humanas)

Geradas da planilha: [pendencias_geradas.md](pendencias_geradas.md).

| ID | Pergunta | Por que importa | Estado |
|---|---|---|---|
| P-01 | `I3.2–I3.4` têm nome `_res` e comentário de nível: são cópia não usada de `I6.2–I6.4`? | Duplicata na grade de I/O confunde o operador | aberta |
| P-02 | `I8.0–I8.6` (nome `_res`, comentário "SAE/SBE…", com `KAA23.5`): é um segundo módulo de entradas real, em uso? | Entram na tela de I/O? | aberta |
| P-03 | `IW352` (contador de banda rasgada), `IW356` (transdutor de pressão), `QW336` (saída p/ inversor): escala e unidade? Endereços de periferia (`PIW`)? | Overview mostra Hz das bombas | aberta |
| P-04 | Quais `M` são alarme **crítico** e quais **permissível**? A planilha não diz | Prioridade e cor na tela de alertas | aberta (precisa do programa ou da lista de alarmes do WinCC) |
| P-05 | O que `PT1` e `PT2` significam (pontos de comando local?) | Texto da tela | aberta |
| P-06 | Restos de outra máquina (bomba 3/4, desoleador, separador magnético, inverter): ocultar? | HG-003 | aberta |
| P-07 | O que o operador fazia no WinCC além de ver? (reset, silenciar, ciclos) | Decide se v0.2 tem comandos | aberta |
| P-08 | Qual o endereço dos DBs/tags que o WinCC lia (se houver DB)? | Planilha só tem I/Q/M/T/C | aberta |
| P-09 | PUT/GET ou comunicação S7 liberada na CPU 315 V3.2 para o Node-RED (rack 0, slot 2)? | Sem isso o Node-RED não lê | a testar |

Respondidas pela planilha: **T.C. = trocador de calor** (bomba e válvula T.C.).
