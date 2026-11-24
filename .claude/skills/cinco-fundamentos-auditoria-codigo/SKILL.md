---
name: cinco-fundamentos-auditoria-codigo
description: Os 5 prompts de auditoria de codigo feito com IA (testes de integracao, nunca confie no cliente, race condition, idempotencia, separacao de responsabilidades), publicados pelo Mano Deyvin no Substack. Use ao auditar, endurecer ou refatorar o HTML ou os fluxos do Hagane, ou quando o usuario pedir "os 5 fundamentos".
---

# Os 5 fundamentos de auditoria de código

Origem: 5 prompts do Mano Deyvin (Substack), em `references/` na íntegra (copiados do bt-gerador, sem alterar).
Todos terminam com "mostre o plano antes de alterar": plano → OK do usuário → executar.

## Ordem recomendada
1. `05_testes_de_integracao.md` — trava o comportamento atual.
2. `03_nunca_confie_no_cliente.md` — segurança.
3. `01_race_condition.md` e `02_idempotencia.md` — consistência.
4. `04_separacao_de_responsabilidades.md` — por último, já protegido pelos testes.

## Adaptação ao Hagane (HTML + Node-RED + CPU 315)
| Fundamento | Equivalente no Hagane |
|---|---|
| Testes de integração | Fluxo Node-RED real lido do disco, com o nó S7 trocado por PLC simulado em memória; HTML testado com Playwright contra esse fluxo |
| Nunca confie no cliente | v0.x é **somente leitura**. Se um dia houver escrita (reset de falha, silenciar sirene): validar no Node-RED e no PLC, nunca só no HTML; intertravamento fica no PLC |
| Race condition | Dois clientes na CPU (Node-RED e, se ainda ligado, WinCC): um dono por comando; leitura em lote única, nunca um cliente por tela |
| Idempotência | Reenviar o mesmo comando (se existir) não pode repetir a ação; alarme reconhecido duas vezes = uma vez |
| Separação de responsabilidades | HTML só exibe; Node-RED só lê, normaliza e serve; regra de processo e alarme só no PLC |

Estado: nada executado ainda (projeto novo). Registrar aqui cada fundamento aplicado, com a evidência.
