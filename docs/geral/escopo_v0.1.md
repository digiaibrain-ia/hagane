# Escopo v0.1 — Hagane

**Objetivo:** substituir a IHM (queimou) e o WinCC Unified RT (resultado ruim) por HTML servido pelo Node-RED. O programa do PLC já está pronto e **não é alterado**.

## 3 telas
| Tela | Conteúdo | Fonte |
|---|---|---|
| **Overview** | Sinótico do processo (tanque sujo, filtro de banda, tanque limpo, bombas 1/2, válvulas, motores) e estado dos modos | tags `Q10.x–Q15.x` (sinóticos), `I`/`M` de estado |
| **Alertas e falhas** | Lista de alarmes ativos (`M10–M16`, `M21`, `M61`, `M122`), com hora de início, ordenada por prioridade; histórico da sessão | tags classe `alarme` |
| **Entradas e saídas** | Grade de I e Q (e analógicas) com endereço, nome, comentário e estado ao vivo; filtro e busca | todas `I`, `Q`, `IW`, `QW` |

## Decisões de arquitetura
1. Node-RED é o único cliente S7 da CPU; lê em lote, serve a API; HTML nunca fala com a CPU.
2. Contrato de dados = `docs/contratos/tags_v0.1.json`, gerado da planilha do TIA.
3. HTML único, offline (sem CDN), pensado para tablet/celular e PC.
4. Dado sem comunicação nunca parece atual (HG: lição de tela).
5. **v0.1 somente leitura.** Comandos (reset de falhas, silenciar sirene, ciclos) só em versão posterior, depois de levantar o que o operador fazia no WinCC.

## Fora de escopo agora
Histórico em banco, relatórios, tendências, comandos de máquina, acesso remoto externo.
