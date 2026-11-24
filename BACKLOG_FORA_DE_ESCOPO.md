# Backlog fora de escopo

Achados que não pertencem à tarefa em andamento. Formato: `ID | data | gravidade | descrição`.

| ID | Data | Gravidade | Descrição |
|---|---|---|---|
| B-01 | 2026-11-24 | baixa | Mobile: sinótico do overview ocupa ~40 % da altura em 390x844 (meta do projeto BT2: >= 55 %). Rever layout do celular na v0.2 |
| B-02 | 2026-11-24 | baixa | `nodered/gerador/gerar_fluxos` embute o HTML no fluxo: após mudar o HTML é preciso gerar versão nova do core |
| B-03 | 2026-11-24 | media | Servir o HTML a partir de arquivo em disco (nó `file in` / `httpStatic`) em vez de embutir no fluxo: editar e atualizar a página com F5, sem regenerar e importar o fluxo. Avaliar também para o card do banco de cargas do bt-gerador (só lá, com OK; é produção) |
| B-04 | 2026-11-24 | media | Trazer do medidor o chip "Logs" (central de registros de eventos de comunicação) e o histórico de alertas no servidor (hoje fica só no navegador, 500 eventos). Avaliar com o uso real |
