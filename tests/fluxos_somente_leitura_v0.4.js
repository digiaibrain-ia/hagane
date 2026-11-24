// Garante que os fluxos do Hagane v0.1 NAO escrevem na CPU: so podem existir nos "s7 in"/"s7 endpoint".
// Uso: node tests/fluxos_somente_leitura_v0.1.js
const fs = require("fs"), path = require("path");
const dir = path.join(__dirname, "..", "nodered", "flows");
const PROIBIDOS = ["s7 out", "s7 control", "modbus-write", "modbus-flex-write", "mqtt out", "tcp out", "udp out", "exec", "file", "http request"];
let falhas = 0;
for (const f of fs.readdirSync(dir).filter(x => /^(baggio|hagane)_.*_v\d+\.\d+\.json$/.test(x))) {
  const nos = JSON.parse(fs.readFileSync(path.join(dir, f), "utf8"));
  const ruins = nos.filter(n => PROIBIDOS.includes(n.type)).map(n => n.type + ":" + n.id);
  const metodos = nos.filter(n => n.type === "http in" && n.method !== "get").map(n => n.url + " " + n.method);
  const ok = !ruins.length && !metodos.length;
  console.log((ok ? "OK   " : "FALHA ") + f + " (" + nos.length + " nos)" + (ok ? "" : " -> " + ruins.concat(metodos)));
  if (!ok) falhas++;
}
process.exit(falhas ? 1 : 0);
