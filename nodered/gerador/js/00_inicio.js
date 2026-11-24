// [F] Ao implantar/iniciar: carrega o contrato de tags na memoria GLOBAL do Node-RED.
// [F] Quem usa: decodificador (bits), API /hagane/api/tags e simulador.
// [F] O conteudo e gerado por nodered/gerador/gerar_fluxos_v0.1.py a partir de
// [F] docs/contratos/tags_v0.1.json (planilha do TIA). Nao editar a mao.
const contrato = __CONTRATO__;
global.set("hagane_contrato", contrato);
global.set("hagane_snap", null);
global.set("hagane_com", { ok: null, texto: "aguardando 1a leitura" });
node.status({ fill: "grey", shape: "dot", text: "contrato " + contrato.versao + " (" + contrato.tags.length + " tags)" });
return null;
