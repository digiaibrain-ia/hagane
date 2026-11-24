// [F] DECODIFICADOR: recebe o objeto de bytes lido da CPU (ou do simulador) e gera
// [F] o "instantaneo" com um booleano por bit monitorado. Formato de entrada, igual ao
// [F] do no "s7 in" modo "all variables": msg.payload = { "IB0": 255, "QB8": 3, "MB21": 0, ... }
// [F] msg.origem = "real" | "demo" (definido por cada fonte; a tela mostra em destaque).
// [F] Byte ausente ou nao numerico => o bit fica FORA do instantaneo (a tela mostra "sem dado").
const contrato = global.get("hagane_contrato");
const bytes = msg.payload;
if (!contrato || !bytes || typeof bytes !== "object") { node.warn("payload invalido"); return null; }
const bits = {};
for (const t of contrato.tags) {
  if (!t.bit) continue;                       // so bits (I, Q, M)
  const v = bytes[t.byte];
  if (typeof v !== "number" || v < 0 || v > 255) continue;
  bits[t.endereco] = ((v >> t.nbit) & 1) === 1;
}
global.set("hagane_snap", { ts: Date.now(), origem: msg.origem || "real", bits: bits });
node.status({ fill: "green", shape: "dot", text: Object.keys(bits).length + " bits " + (msg.origem || "real") });
return null;
