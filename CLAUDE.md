# Regras do projeto Baggio (sistema de filtragem)

Valem para qualquer sessão neste repositório. Em português.

## Segurança e produção
- Nunca alterar PLC, Node-RED ou PC de produção a partir do repositório ou de uma sessão.
- Nenhuma mudança em PLC ou Node-RED de produção sem backup antes e OK explícito.
- Nada de senha, token, chave ou IP real no Git.
- Intertravamentos de segurança ficam no PLC; HTML e Node-RED nunca são a única proteção.

## Método de trabalho
- Antes de alterar arquivo de produção: mostrar plano e causa, e esperar OK.
- Mudança vai para versão nova (ex.: `v0.2`), nunca sobrescrever a anterior; a antiga vai para `arquivo/`.
- Teste que falha é registrado como `todo` com ID e gravidade, não apagado nem enfraquecido.
- Achado fora do escopo vai para `BACKLOG_FORA_DE_ESCOPO.md`.
- Relatório honesto: dizer o que foi provado (simulado) e o que depende de bancada/campo.
- Código modular, comentado em PT-BR, com `.md` de apoio.

## Contrato único
PLC, Node-RED e HTML conversam só pelo que está em `docs/contratos/`. Mudou endereço, tag ou payload:
atualizar o contrato primeiro, depois os três lados juntos.

## Comunicação
Respostas curtas e diretas, em português.
