// [F] Traduz o status do no "s7 in" em estado de comunicacao (so para o diagnostico).
// [F] Verde = conectado e lendo. Qualquer outra cor = sem comunicacao com a CPU.
// [F] A decisao final de "sem comunicacao" tambem usa a IDADE do ultimo instantaneo (API).
const s = msg.status || {};
const ok = s.fill === "green";
global.set("baggio_com", { ok: ok, texto: s.text || "", desde: Date.now() });
return null;
