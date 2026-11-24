---
name: hagane-licoes
description: Licoes aprendidas (herdadas do bt-gerador e novas do Hagane) sobre HTML de supervisao, Node-RED e PLC S7-300. Use ao criar ou revisar qualquer tela, fluxo, bloco SCL ou contrato do Hagane.
---

# Lições do Hagane
Herdadas do projeto BT2 (bt-gerador) e já filtradas para este escopo. Lição nova entra no fim, com ID `HG-nnn`.

## HTML
- **Janela sempre inteira na tela**; todo diálogo tem ✕ e Esc. (BT2 LL-020/021)
- **Todo acesso a storage em try/catch**; a tela funciona sem storage. (LL-024)
- **Texto longo vira popover ⓘ**, não fica na tela; só um resumo curto. (LL-056)
- **Layout estável**: hover/foco não muda posição nem tamanho; testar em 1536×694 e 390×844. (LL-047/061)
- **Estado nunca só por cor**: símbolo ou texto junto. Normal discreto, anormal evidente. (LL-060, ISA-101)
- **Tela de operador mostra se o dado é velho**: se o Node-RED ou o PLC parar de responder, a tela diz "SEM COMUNICAÇÃO" e congela os valores com carimbo de hora; nunca mostra o último valor como se fosse atual.
- Arquivo HTML único, sem dependência de internet (CDN), gerado por script a partir de `dashboard/src/`. Versão nova, nunca sobrescrever.

## Node-RED
- **Um cliente S7 só**; leitura em lote com intervalo fixo; a API serve o último valor lido. (BT2 LL-010..012)
- **Resposta incerta é honesta**: timeout vira estado `incerto`, não "ok". (LL-012)
- Endereço/IP só por variável de ambiente (`${PLC_IP}`); nunca no fluxo versionado. `${PLC_IP}` não definido → erro `getaddrinfo ENOTFOUND` no Debug.
- Fluxo no padrão: versão do arquivo = versão da aba = info; info em todo nó; nota ≤ 80 caracteres; grupos por rota. (LL-053/054)
- Todo teste de correção deve **falhar na versão que tinha o erro** (mutação). (LL-015)

## PLC (S7-300, CPU 315-2 PN/DP)
- **Intertravamento e alarme moram no PLC**; HTML e Node-RED nunca são a única proteção. (LL-001)
- SCL clássico: sem `S7_Optimized_Access`, sem `DB_ANY`/`PEEK`/`POKE` no S7-300 sem teste; `TON` (não `TON_TIME`). (LL-055)
- Comentário de bloco SCL em 2 etiquetas `//[F]` funcionamento e `//[M]` montagem. (LL-067)
- Demo × Real: o que foi provado no PLCSIM **não prova** o PLC real. (LL-040)
- O programa do PLC **já está pronto e em operação**: este repositório não o altera. Leitura apenas.

## Hagane (novas)
- **HG-001** Planilha de tags exportada do TIA é a fonte de verdade dos endereços; o contrato é gerado dela por script, não digitado à mão.
- **HG-002** Nome de tag no TIA pode mentir (`ix_3.2_res` tem comentário "NÍVEL DE ENCHIMENTO"; `ix_8.x_res` idem). Vale endereço + comentário; dúvida vai para `docs/contratos/pendencias.md`.
- **HG-003** O programa herdou restos de outra máquina (bomba 3/4, desoleador, separador magnético, inverter). Não exibir o que não existe fisicamente; confirmar com quem conhece a máquina antes.
- **HG-004** O IHM WinCC Unified RT queimou: o HTML precisa cobrir **a operação que o WinCC cobria**, não só mostrar. Levantar o que o operador fazia ali antes de decidir só-leitura.
