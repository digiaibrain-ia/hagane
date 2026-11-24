// [F] SIMULADOR PURO (DEMO): simularBytes(contrato, agoraMs) devolve os MESMOS bytes que a CPU enviaria
// [F] ({"IB0":n,...}). Sem PLC, sem rede. (v0.7: sem silencio simulado; o teste de "sem comunicacao" fica nos testes automaticos.)
// [F] Usado em 2 lugares com o MESMO codigo: fluxo demo do Node-RED e simulador embutido no HTML.
// [F] Ciclo de 180 s: 40-70 s ALERTA A-NIV-002 (nivel minimo do tanque limpo: M13.7); 100-140 s FALHA F-DSJ-002
// [F] (disjuntor da bomba 1 desarmado: I1.0 = 0 e M10.5). Os alarmes seguem a logica real do PLC.
// [F] Nivel do tanque sujo sobe e desce a cada 60 s e e entregue pelos SENSORES (sensor ativo = coberto):
// [F]   I6.1 minimo >= 15 %, I6.2 inicio de enchimento >= 40 %, I6.3 fim de enchimento >= 70 %, I6.0 maximo >= 90 %.
// [F] Tanque limpo (compensacao) oscila a cada 90 s: I6.5 minimo >= 15 %, I6.4 maximo >= 85 %.
// [F] Nunca usar em producao: a tela exibe "DEMO" em destaque (licao Demo x Real).
function simularBytes(contrato, agoraMs) {
  var t = (agoraMs / 1000) % 180;
  var B = {};
  var set = function (end, v) {
    var m = /^([IQM])(\d+)\.(\d)$/.exec(end); if (!m) return;
    var k = m[1] + "B" + m[2]; B[k] = (B[k] || 0);
    if (v) B[k] |= (1 << Number(m[3])); else B[k] &= ~(1 << Number(m[3]));
  };
  contrato.tags.forEach(function (tg) { if (tg.bit && B[tg.byte] === undefined) B[tg.byte] = 0; });

  var falhaBomba1 = t >= 100 && t < 140, aviso = t >= 40 && t < 70;
  var fase = (t % 60) / 60, nivel = fase < 0.5 ? fase * 2 : 2 - fase * 2;          // tanque sujo 0..1
  var nl = aviso ? 0.08 : 0.55 + 0.35 * Math.sin(2 * Math.PI * t / 90);            // tanque limpo 0..1 (no alerta: abaixo do minimo)
  var limpeza = (t % 90) >= 20 && (t % 90) < 50;

  // base: comando, seguranca, disjuntores OK, ar, modo automatico
  ["I0.0","I0.3","I0.6","I4.2","I4.4","I5.0","I5.2","I5.4","I5.6","I1.4","I2.0","I2.2","I2.4","I3.0","I3.5","Q12.1","Q12.2"].forEach(function (a) { set(a, true); });
  // sensores de nivel do tanque sujo (entradas) e lampadas do sinotico (saidas)
  set("I6.1", nivel >= 0.15); set("I6.2", nivel >= 0.40); set("I6.3", nivel >= 0.70); set("I6.0", nivel >= 0.90);
  set("Q14.6", nivel >= 0.90); set("Q14.7", nivel >= 0.70); set("Q15.0", nivel < 0.40); set("Q15.1", nivel < 0.15);
  // tanque limpo
  set("I6.5", nl >= 0.15); set("I6.4", nl >= 0.85); set("Q14.4", nl >= 0.85); set("Q14.5", nl < 0.15);
  // bombas
  set("I1.0", !falhaBomba1);                                                       // contato OK do disjuntor da bomba 1
  var b1 = !falhaBomba1, b2 = nivel > 0.5;
  set("I1.1", b1); set("I1.2", b1); set("Q13.0", b1);
  set("I1.5", b2); set("I1.6", b2); set("Q13.1", b2);
  set("I2.1", true); set("Q13.6", true);
  // ciclo de autolimpeza
  set("Q12.4", limpeza);
  set("I2.3", limpeza); set("Q13.4", limpeza); set("Q14.1", limpeza); set("Q14.3", limpeza);
  set("I3.1", limpeza); set("Q13.5", limpeza);
  set("I3.6", true); set("Q13.2", true); set("I2.5", true); set("Q13.3", true);
  set("Q15.3", true); set("Q15.4", true); set("Q14.0", true); set("Q15.6", b2); set("Q14.2", nl > 0.5);
  // coluna sinaleira
  set("Q11.4", !falhaBomba1);
  if (aviso) { set("M13.7", true); set("M21.3", true); set("Q11.6", true); }          // A-NIV-002
  if (falhaBomba1) { set("M10.5", true); set("M21.0", true); set("Q11.5", true); set("Q11.7", true); }   // F-DSJ-002
  return B;
}
