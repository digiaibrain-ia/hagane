// [F] GET /baggio/api/estado  -> instantaneo atual + saude da comunicacao. SOMENTE LEITURA.
// [F] comunicacao = "ok" so se: existe instantaneo, ele tem menos de LIMITE_MS e o no S7 nao reportou falha.
// [F] Nunca devolve o ultimo valor como se fosse atual: a tela decide pelo campo "comunicacao".
const LIMITE_MS = 5000;
const snap = global.get("baggio_snap");
const com = global.get("baggio_com") || {};
const agora = Date.now();
const idade = snap ? agora - snap.ts : null;
let comunicacao = "ok", motivo = "";
if (!snap) { comunicacao = "sem_comunicacao"; motivo = "sem leitura ainda"; }
else if (idade > LIMITE_MS) { comunicacao = "sem_comunicacao"; motivo = "leitura parada ha " + Math.round(idade/1000) + " s"; }
else if (com.ok === false) { comunicacao = "sem_comunicacao"; motivo = "CPU: " + (com.texto || "desconectada"); }
msg.payload = {
  versao: "0.1", origem: snap ? snap.origem : null, agora: agora,
  ts: snap ? snap.ts : null, idade_ms: idade, comunicacao: comunicacao, motivo: motivo,
  bits: snap ? snap.bits : {}
};
msg.headers = { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", "Access-Control-Allow-Origin": "*" };
msg.statusCode = 200;
return msg;
