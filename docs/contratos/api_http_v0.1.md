# Contrato HTTP v0.1 (Node-RED → HTML) — somente leitura

Só existem rotas `GET`. Nenhuma escreve na CPU. Teste: `tests/fluxos_somente_leitura_v0.1.js`.

| Rota | Resposta |
|---|---|
| `GET /baggio` | Página HTML (`dashboard/src/baggio_monitor_v0.10.html`, embutida no fluxo core) |
| `GET /baggio/api/tags` | Contrato monitorado: `{versao, origem, tags[]}` |
| `GET /baggio/api/estado` | Instantâneo atual (abaixo) |

## `/baggio/api/estado`
```json
{ "versao":"0.1", "origem":"real|demo", "agora":1795484448506, "ts":1795484448136,
  "idade_ms":370, "comunicacao":"ok|sem_comunicacao", "motivo":"", "bits":{"I0.0":true,"M12.2":false} }
```
- `comunicacao = "ok"` só se o último instantaneo tem < 5 s **e** o nó S7 não reportou falha.
- A tela usa só `comunicacao`/`idade_ms` para decidir se mostra valores; sem comunicação ela apaga tudo.
- `bits` traz só endereços do contrato (I, Q e M com comentário). Byte ausente → bit ausente → "sem dado".

## Origem dos bytes
Fonte S7 real: nó `s7 in` (modo *all variables*, `diff` desligado, ciclo 1000 ms) lendo `IB0..IB8`, `QB8..QB15`, `QB28/29` e os `MB` listados em `tags_v0.1.json` (35 bytes). Endereço da CPU: variável de ambiente `PLC_IP`; rack 0, slot 2 (**confirmar**).
Fonte demo: simulador, `origem = "demo"`; a tela mostra "DEMO" em amarelo. Desde a v0.4 o mesmo simulador também roda dentro do HTML (Fonte = Simulação), sem chamar a API.

## Sem analógicas
O equipamento não tem entrada nem saída analógica (confirmado pelo usuário em 25/11/2026). Desde a v0.12 a API não traz `analogicas[]` e a tela não mostra o painel. `IW352`, `IW356` e `QW336` continuam na planilha do PLC, mas não são lidos nem exibidos (P-03 encerrada).
