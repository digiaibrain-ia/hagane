// [F] FONTE DEMO: a cada tick chama o simulador puro (codigo abaixo) e entrega os bytes como se vieram da CPU.
__SIM_CORE__
const contrato = global.get("baggio_contrato");
if (!contrato) return null;
const B = simularBytes(contrato, Date.now());
if (!B) return null;                      // silencio: simula queda de comunicacao
msg.payload = B; msg.origem = "demo";
return msg;
