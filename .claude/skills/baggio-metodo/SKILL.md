---
name: baggio-metodo
description: Metodo de trabalho do Baggio (portoes, versao nova, teste, relatorio honesto). Use ao alterar HTML, fluxos Node-RED, contratos ou ao montar entrega para a maquina.
---

# Método Baggio (enxuto, herdado do BT2)
1. **Responder só o que foi pedido.** Ambíguo: dizer a leitura em uma linha e agir; perguntar só o que muda o resultado, com recomendação.
2. **Proposta → decisão → execução.** "Autorizado" não vale para o próximo assunto.
3. **Espelhar o que já existe e funciona** (PLC pronto, planilha de tags) antes de inventar.
4. **Escopo = o que existe hoje:** 3 telas (Overview, Alertas e falhas, I/O).
5. **Versão nova, nunca sobrescrever**; gerar por script; o antigo vai para `arquivo/`.
6. **Contrato primeiro** (`docs/contratos/`), depois PLC/Node-RED/HTML juntos.
7. **Teste falho vira `todo`** com ID e gravidade; nunca enfraquecer teste.
8. **Fora de escopo** → `BACKLOG_FORA_DE_ESCOPO.md`.
9. **Relatório honesto**: primeira linha diz o que o teste NÃO cobre; provado no PLCSIM ≠ provado na máquina.
10. **Entrega** = `.html` ou `.json` pronto + `COMO_USAR.txt` de até 15 linhas. Sem zips nem textos extras sem pedido.
11. Nada de IP real, senha ou token no Git (`[IP_CPU]` como marcador).
