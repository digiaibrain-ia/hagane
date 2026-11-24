// [F] SIMULADOR (DEMO): gera os MESMOS bytes que a CPU enviaria, para testar telas sem PLC.
// [F] Ciclo de 180 s: 40-70 s aviso (permissivel); 100-140 s falha critica na bomba 1;
// [F] 150-165 s o simulador CALA (testa "sem comunicacao"). Nivel do tanque oscila a cada 60 s.
// [F] Nunca usar em producao: a tela exibe "DEMO" em destaque (licao Demo x Real).
const contrato = global.get("hagane_contrato");
if (!contrato) return null;
const t = (Date.now() / 1000) % 180;
if (t >= 150 && t < 165) { return null; }           // silencio: sem comunicacao
const B = {};                                         // bytes
const set = (end, v) => {                             // liga/desliga um bit pelo endereco
  const m = /^([IQM])(\d+)\.(\d)$/.exec(end); if (!m) return;
  const k = m[1] + "B" + m[2]; B[k] = (B[k] || 0);
  if (v) B[k] |= (1 << Number(m[3])); else B[k] &= ~(1 << Number(m[3]));
};
for (const tg of contrato.tags) if (tg.bit && B[tg.byte] === undefined) B[tg.byte] = 0;

const falhaBomba1 = t >= 100 && t < 140, aviso = t >= 40 && t < 70;
const fase = (t % 60) / 60, nivel = fase < 0.5 ? fase * 2 : 2 - fase * 2;   // 0..1
const limpeza = (t % 90) >= 20 && (t % 90) < 50;

// base: comando, seguranca, disjuntores OK, ar, modo automatico
["I0.0","I0.3","I0.6","I4.2","I4.4","I5.0","I5.2","I5.4","I5.6","I1.0","I1.4","I2.0","I2.2","I2.4","I3.0","I3.5","Q12.1","Q12.2"].forEach(a => set(a, true));
// niveis do tanque sujo (entradas I6 e lampadas Q)
const max = nivel > 0.9, alto = nivel > 0.7, baixo = nivel < 0.4, min = nivel < 0.15;
set("I6.0", max); set("I6.3", alto); set("I6.2", baixo); set("I6.1", !min);
set("Q14.6", max); set("Q14.7", alto); set("Q15.0", baixo); set("Q15.1", min);
set("I6.5", true); set("Q14.4", true);
// bombas
const b1 = !falhaBomba1, b2 = nivel > 0.5;
set("I1.1", b1); set("I1.2", b1); set("Q13.0", b1);
set("I1.5", b2); set("I1.6", b2); set("Q13.1", b2);
set("I2.1", true); set("Q13.6", true);
// ciclo de autolimpeza
set("Q12.4", limpeza);
set("I2.3", limpeza); set("Q13.4", limpeza); set("Q14.1", limpeza);
set("I3.1", limpeza); set("Q13.5", limpeza);
set("I3.6", true); set("Q13.2", true); set("I2.5", true); set("Q13.3", true);
set("Q15.3", true); set("Q15.4", true); set("Q14.0", true);
// coluna sinaleira
set("Q11.4", !falhaBomba1);
if (aviso) { set("M13.7", true); set("M21.3", true); set("Q11.6", true); }
if (falhaBomba1) { set("M12.2", true); set("M122.2", true); set("M21.0", true); set("Q11.5", true); set("Q11.7", true); }
msg.payload = B; msg.origem = "demo";
return msg;
