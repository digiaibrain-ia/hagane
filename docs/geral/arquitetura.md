# Arquitetura — Baggio (sistema de filtragem, fábrica Hagane)

```
Sensores/atuadores ──► PLC S7 ──► Node-RED (único cliente do PLC + API HTTP) ──► Dashboard HTML
```

## Princípios
- Node-RED é o único cliente do PLC; o HTML nunca fala direto com o PLC.
- Lógica e intertravamentos no PLC; Node-RED só transporta e organiza; HTML só exibe e comanda.
- Contrato de dados em `docs/contratos/`.

## Hardware (projeto TIA `WU_HAGANE`)
| Item | Detalhe |
|---|---|
| CPU | SIMATIC S7-300 **CPU 315-2 PN/DP**, 6ES7 315-2EH14-0AB0, firmware V3.2 (384 KB, PROFINET + MPI/DP) |
| Supervisório local | PC station SIMATIC com **WinCC Unified RT** (`HMI_RT_1`, `HMI_RT_2`) via CP IE, rede `PN/IE_1` |
| Rede | `PN/IE_1`, CPU em 192.168.0.2/24 (ver [processo_filtragem.md](processo_filtragem.md)) |
| Engenharia | TIA Portal (sem S7-1200/1500: **SCL clássico**, DBs sempre não otimizados) |

Consequências:
- Node-RED fala com a CPU 315 por S7 (ISO-on-TCP, porta 102) pela interface PROFINET [X2]; rack 0 / slot 2 (confirmar).
- Acesso por DB com endereço absoluto: o contrato em `docs/contratos/` lista DB, offset e tipo de cada tag.
- Blocos em SCL clássico/FC/FB para S7-300; sem recursos exclusivos de 1200/1500.
- O WinCC Unified RT é um segundo cliente do PLC; definir qual é o dono dos comandos (ver contrato).

## A definir (preencher com o equipamento)
- Lista de sensores, válvulas, bombas e modos de operação (filtragem, retrolavagem, etc.).
- Telas do dashboard.
