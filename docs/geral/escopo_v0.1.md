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

## v0.3 (24/11/2026)
- **Dois visuais** no mesmo HTML: Moderno (identidade do medidor: tinta `#1a4a78`, acento `#ec7000`, modo escuro automático) e Original (= v0.2, fiel ao WinCC). Mesma geometria e mesmos dados.
- **Menos repetição:** um único selo de estado (Em operação, Aviso, Falha, Parada, Sem dado) no cabeçalho no lugar da faixa de luzes; local mostrado uma vez por visual; na E/S o nome da tag sai da linha.
- Arquivos: `dashboard/src/hagane_monitor_v0.3.html` (gerado por `dashboard/gerador/gerar_monitor_v0.3.py` a partir da v0.2 em `arquivo/`), `nodered/flows/hagane_*_v0.3.json`. Teste: `tests/telas_v0.3.js` nos dois visuais.

## v0.4 (24/11/2026)
- **Nome:** o sistema é **Baggio — Sistema de filtragem**; **Hagane** é a fábrica que o usa (projeto TIA `WU_HAGANE`). Arquivos, rotas (`/baggio`), variável `BAGGIO_PLC_IP` e chaves do navegador passaram a `baggio_*`. As versões anteriores (v0.1–v0.3) ficam em `arquivo/` com os nomes antigos `hagane_*`.
- **Fonte dos dados no próprio HTML:** `CPU` (Node-RED) ou `Simulação` embutida. A página funciona sem Node-RED e sem PLC (abre com dois cliques). Selo DEMO sempre visível na simulação.
- **Nível dos tanques pelos sensores de nível** (`I6.x`, sensor ativo = coberto; polaridade a validar, P-10), com ondas na água e fluxo nos tubos das bombas. Botão **Animação** liga/desliga (lembrado).
- **Textos:** 6 colisões medidas e corrigidas nos dois visuais (`tests/colisao_textos.js` = 0).
- Teste: `tests/telas_v0.4.js` (nos dois visuais) + `tests/colisao_textos.js` + `tests/fluxos_somente_leitura_v0.4.js`.

## v0.5 (24/11/2026) — correções de UI
- **Sem deslocamento:** a faixa "SEM COMUNICAÇÃO" ficou fixa no rodapé (espaço sempre reservado), a barra de rolagem tem espaço reservado e os selos do cabeçalho têm largura mínima. Teste: layout idêntico em normal, aviso, falha e sem comunicação, nas 3 abas.
- **Tubo emendado:** o tubo do extrator de lodo começava solto, 30 unidades antes do funil. `tests/colisao_textos.js` agora também confere que cada ponta de tubo encosta em outro tubo, equipamento ou bomba (entradas livres: ar, alimentação e retorno).
- Os testes novos foram provados por mutação: na v0.4 eles falham (tubo solto e deslocamento detectados).
- Arquivos: `baggio_monitor_v0.5.html` (`dashboard/gerador/gerar_monitor_v0.5.py`), `baggio_*_v0.5.json`, `tests/telas_v0.5.js`.

## v0.6 (24/11/2026)
- **"Hagane" saiu da tela e do projeto.** Origem dos dados com nome claro: **Dados: PLC | Simulados** (antes "CPU | Simulação").
- **Tubulação conferida com o WinCC:** o tubo que desce ao lado do filtro sai da **parede do tanque limpo** (na v0.5 eu o tinha ligado ao funil, errado). **Válvula quebra vácuo:** lâmpada, rótulo e válvula juntos na caixa, válvula sobre o tubo, com atuador desenhado.
- **Alertas e falhas no padrão do medidor**, alimentado pelos blocos do PLC (`plc/blocos/FC_ALARME_CRITICO.awl` e `FC_ALARME_PERMISSIVEL.awl`): código `T-AAA-NNN`, **efeito → causa (teste rápido) → solução (onde)**, **como o PLC decide** (gatilho, atraso, retenção, endereços ao vivo), histórico persistente (500), Exportar (txt, md, csv, PDF). Catálogo gerado por `plc/variaveis/gerar_alarmes_v0.1.py` → `docs/contratos/alarmes_v0.1.json`.
- **Alarmes deduzidos de entradas removidos:** o PLC é a única fonte. A dedução `I1.3 = 1 → falha` estava invertida (P-14).
- Achados nos blocos: `M15.5` nunca dispara (condição contraditória), `M15.7` com selo invertido, `Q9.0` com nome de reserva (P-15 a P-17).
- Teste: `tests/telas_v0.6.js` (nos dois visuais), `tests/colisao_textos.js`, `tests/fluxos_somente_leitura_v0.6.js`.

## v0.7 (24/11/2026) — tubulação, setas e válvulas por regras medidas
- **Simulador sem o silêncio** (já não derruba a comunicação a cada 3 minutos). O teste de "sem comunicação" continua nos testes automáticos.
- **Setas geradas do próprio tubo**, a 12 unidades do eixo, só em trecho reto e longe de curvas, válvulas, instrumentos, lâmpadas, textos e outros tubos. A animação da água usa o mesmo caminho, então **seta e movimento têm sempre o mesmo sentido** (provado medindo o tracejado em movimento).
- **Tubulação padronizada:** tubos paralelos com no mínimo 24 unidades de afastamento (antes 34, 28, 19…); tubo do filtro afastado do canto do tanque; **ponte** no único cruzamento sem ligação (tubo do filtro × recalque da bomba 1); linha tracejada fora do tubo.
- **Válvulas alinhadas ao eixo do tubo**, com flanges e atuador sempre do mesmo lado (direita no tubo vertical, acima no horizontal). Rótulo da compensação não atravessa mais a parede do tanque; rótulo da lavagem centrado na válvula.
- **Corrida corrigida:** trocar "PLC → Simulados" com uma leitura do PLC pendente fazia o erro tardio derrubar a simulação; respostas de fonte já trocada são descartadas.
- Teste: `tests/telas_v0.7.js` (nos dois visuais; regras de afastamento, ponte, setas, válvulas e sentido da animação) + `tests/colisao_textos.js` (amostragem de 1 em 1 e folga de 2).

## v0.8 (24/11/2026) — T da alimentação, alertas de demonstração, filtros
- **T da alimentação como no WinCC:** o tubo horizontal chega ao T e se divide; um ramo **sobe** (alimentação) e o outro **desce** (lavagem). Na v0.7 o tubo inteiro subia. Novo teste de conservação do fluxo: toda junção de pontas tem entrada e saída; acima do T a seta sobe e abaixo desce. Tubos emendados com ponta reta (sem "bolha" na junção).
- **Simulação nunca gera falha de comunicação** (o estado simulado é sempre "ok"). A faixa "simulador em silêncio" que apareceu nos prints era da versão antiga.
- **Alertas e falhas de demonstração:** com dados simulados há sempre uma Falha (`F-DEM-001`) e um Alerta (`A-DEM-001`) fictícios, autoexplicativos (explicam o que é falha/alerta, causa, teste e solução). Não existem no PLC, não entram no histórico e não mudam o selo de estado; contam no contador da aba.
- **Filtros:** botões Falha/Alerta/Informação com contagem, lista de Família, busca, "Limpar filtros" e "Mostrando X de Y". **Seleção:** caixa por linha + "selecionar todos"; Exportar usa os selecionados (ou os ativos, se nada estiver selecionado).
- Testes: `tests/telas_v0.8.js` (nos dois visuais) cobre T, junções, simulação sem falha (relógio forçado ao instante do antigo silêncio), demonstração, filtros e seleção.
- **Registro honesto:** na primeira execução do teste v0.8, as verificações da simulação (arquivo aberto direto) falharam e não se repetiram depois (4 execuções completas e 15 aberturas isoladas sem erro). Causa não identificada; ficou como observação.

## v0.9 (24/11/2026) — simulador corrigido na raiz, cabeçalho limpo, proporção
- **Defeito de construção achado e corrigido:** cada HTML era gerado a partir do HTML anterior, então o **simulador embutido ficou velho desde a v0.4**: minhas correções do simulador (alarmes reais, sem silêncio) só chegavam aos fluxos do Node-RED. Por isso a "falta de comunicação" e os alarmes antigos (`A-OUT-001/006 Alarme bomba 1`) continuavam aparecendo no HTML. Agora o gerador **reembute** `nodered/gerador/js/50_simulador_core.js` e o teste confere que o texto embutido é **idêntico** ao arquivo (também confere o catálogo de alarmes).
- **Cenário fixo na simulação:** sempre 1 **Falha** (`F-PRS-001`, pressão de ar insuficiente) e 1 **Alerta** (`A-DSJ-006`, disjuntor do aspirador desarmado), com a lógica real do PLC; sem ciclos de alarme e **sem silêncio**. Os alarmes fictícios `DEM` da v0.8 saíram. A tela de alertas avisa "Dados simulados".
- **Cabeçalho de uma linha e sem bordas:** marca, abas, selo de estado, **chip de origem dos dados** ("Dados simulados" amarelo / "PLC ao vivo" / "PLC sem comunicação"), relógio e engrenagem. **Opções** (engrenagem ou chip): origem dos dados e visual por botões de escolha com **"em uso"**, animação da água e **tela cheia**.
- **Proporção (1366×768):** o cabeçalho ficou 44 px (antes ~90); o texto do Overview subiu de ~7 para ~13 px reais e o desenho ocupa ~97% da largura; Alertas e E/S ficam menores (zoom 0,88 em telas até 1500 px; linhas de 29 px).
- Sem os dígitos 1/0 nos endereços (cor + dica); rótulo **TRANSP. DRAGANTE**; a tela se atualiza ao voltar de outra aba do navegador.
- Defeitos meus achados nos prints e corrigidos: texto da aba selecionada invisível (azul sobre azul) e barra de seleção sempre visível (`hidden` perdia para `display:flex`). Os testes agora medem **contraste real** e **visibilidade real** (provado por mutação).
- Testes: `tests/telas_v0.9.js` (dois visuais), `tests/colisao_textos.js`, `tests/fluxos_somente_leitura_v0.9.js`.
