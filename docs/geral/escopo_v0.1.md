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

## Estado (24/11/2026)
- Fluxos: `nodered/flows/hagane_core_v0.1.json` + uma fonte (`hagane_fonte_s7_v0.1.json` ou `hagane_fonte_demo_v0.1.json`), gerados por `nodered/gerador/gerar_fluxos_v0.1.py`.
- Tela: `dashboard/src/hagane_monitor_v0.1.html` (embutida no core). Contrato: `docs/contratos/api_http_v0.1.md`.
- **Provado aqui (simulado):** telas em 1536x694 e 390x844, estados normal/aviso/falha/sem comunicação, leitura S7 bit a bit contra servidor snap7 simulado, queda e recuperação, fluxos sem nó de escrita.
- **Não provado (depende do notebook/CPU):** rack/slot e acesso S7 da CPU 315, polaridade dos sensores e alarmes derivados (P-10, P-11), leitura analógica (P-03).

## v0.2 (24/11/2026)
- Overview **fiel à tela do WinCC** (mesma disposição, lâmpadas dinâmicas, toque = estado + endereço). Fonte S7 usa `HAGANE_PLC_IP`.
- Arquivos: `dashboard/src/hagane_monitor_v0.2.html` (gerado por `dashboard/gerador/gerar_monitor_v0.2.py`), `nodered/flows/hagane_*_v0.2.json`. v0.1 em `arquivo/`.
- Teste com PLCSIM: `docs/testes/roteiro_plcsim_v0.1.md`.
