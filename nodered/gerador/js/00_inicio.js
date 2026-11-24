// [F] Ao implantar/iniciar: carrega o contrato de tags na memoria GLOBAL do Node-RED.
// [F] Quem usa: decodificador (bits), API /baggio/api/tags e simulador.
// [F] O conteudo e gerado por nodered/gerador/gerar_fluxos_v0.1.py a partir de
// [F] docs/contratos/tags_v0.1.json (planilha do TIA). Nao editar a mao.
const contrato = __CONTRATO__;
global.set("baggio_contrato", contrato);
global.set("baggio_snap", null);
global.set("baggio_com", { ok: null, texto: "aguardando 1a leitura" });
node.status({ fill: "grey", shape: "dot", text: "contrato " + contrato.versao + " (" + contrato.tags.length + " tags)" });
return null;
