# Arquitetura — Hagane

```
Sensores/atuadores ──► PLC S7 ──► Node-RED (único cliente do PLC + API HTTP) ──► Dashboard HTML
```

## Princípios
- Node-RED é o único cliente do PLC; o HTML nunca fala direto com o PLC.
- Lógica e intertravamentos no PLC; Node-RED só transporta e organiza; HTML só exibe e comanda.
- Contrato de dados em `docs/contratos/`.

## A definir (preencher com o equipamento)
- Modelo do PLC e protocolo (S7 / Modbus TCP).
- Lista de sensores, válvulas, bombas e modos de operação (filtragem, retrolavagem, etc.).
- Telas do dashboard.
