// [F] SIMULADOR PURO (DEMO): simularBytes(contrato, agoraMs) devolve os MESMOS bytes que a CPU enviaria
// [F] ({"IB0":n,...}). Sem PLC, sem rede, SEM silencio: nunca simula falta de comunicacao.
// [F] CENARIO FIXO (v0.9), para demonstracao: sempre ha 1 FALHA e 1 ALERTA ativos, com a logica real do PLC:
// [F]   FALHA  F-PRS-001 (M11.2): pressao de ar insuficiente -> I5.0 = 0, coluna vermelha e sirene;
// [F]   ALERTA A-DSJ-006 (M15.1): disjuntor do aspirador desarmado -> I2.2 = 0, aspirador parado, coluna amarela.
// [F] O que se mexe sozinho (ciclo de 180 s): nivel do tanque sujo (60 s) e do limpo (90 s) pelos SENSORES
// [F]   (sensor ativo = coberto; I6.1 >= 15 %, I6.2 >= 40 %, I6.3 >= 70 %, I6.0 >= 90 %; limpo I6.5 >= 15 %, I6.4 >= 85 %),
// [F]   bomba 2 conforme o nivel e autolimpeza (rotovac) a cada 90 s.
// [F] Este MESMO arquivo e embutido no HTML e usado no fluxo demo do Node-RED (o gerador do HTML confere isso).
// [F] Nunca usar em producao: a tela mostra "Dados simulados" em destaque (licao Demo x Real).
function simularBytes(contrato, agoraMs) {
  var t = (agoraMs / 1000) % 180;
  var B = {};
  var set = function (end, v) {
    var m = /^([IQM])(\d+)\.(\d)$/.exec(end); if (!m) return;
    var k = m[1] + "B" + m[2]; B[k] = (B[k] || 0);
    if (v) B[k] |= (1 << Number(m[3])); else B[k] &= ~(1 << Number(m[3]));
  };
  contrato.tags.forEach(function (tg) { if (tg.bit && B[tg.byte] === undefined) B[tg.byte] = 0; });

  var fase = (t % 60) / 60, nivel = fase < 0.5 ? fase * 2 : 2 - fase * 2;          // tanque sujo 0..1
  var nl = 0.55 + 0.35 * Math.sin(2 * Math.PI * t / 90);                           // tanque limpo 0..1
  var limpeza = (t % 90) >= 20 && (t % 90) < 50;

  // base: comando, seguranca, disjuntores OK (menos o do aspirador), modo automatico
  ["I0.0","I0.3","I0.6","I4.2","I4.4","I5.2","I5.4","I5.6","I1.0","I1.4","I2.0","I2.4","I3.0","I3.5","Q12.1","Q12.2"].forEach(function (a) { set(a, true); });
  // sensores de nivel do tanque sujo (entradas) e lampadas do sinotico (saidas)
  set("I6.1", nivel >= 0.15); set("I6.2", nivel >= 0.40); set("I6.3", nivel >= 0.70); set("I6.0", nivel >= 0.90);
  set("Q14.6", nivel >= 0.90); set("Q14.7", nivel >= 0.70); set("Q15.0", nivel < 0.40); set("Q15.1", nivel < 0.15);
  // tanque limpo
  set("I6.5", nl >= 0.15); set("I6.4", nl >= 0.85); set("Q14.4", nl >= 0.85); set("Q14.5", nl < 0.15);
  // bombas
  var b1 = true, b2 = nivel > 0.5;
  set("I1.1", b1); set("I1.2", b1); set("Q13.0", b1);
  set("I1.5", b2); set("I1.6", b2); set("Q13.1", b2);
  set("I2.1", true); set("Q13.6", true);
  // autolimpeza: rotovac e quebra vacuo (o aspirador esta com o disjuntor desarmado)
  set("Q12.4", limpeza); set("Q14.1", limpeza);
  set("I3.1", limpeza); set("Q13.5", limpeza);
  set("I3.6", true); set("Q13.2", true); set("I2.5", true); set("Q13.3", true);
  set("Q15.3", true); set("Q15.4", true); set("Q15.6", b2); set("Q14.2", nl > 0.5);

  // ---- ALARMES FIXOS (demonstracao) ----
  // FALHA F-PRS-001: pressao de ar insuficiente (I5.0 = 0): coluna vermelha + sirene; sem ar o sopro e a lampada de ar ficam apagados
  set("M11.2", true); set("M21.0", true); set("Q11.5", true); set("Q11.7", true);
  // ALERTA A-DSJ-006: disjuntor do aspirador desarmado (I2.2 = 0): coluna amarela
  set("M15.1", true); set("M21.3", true); set("Q11.6", true);
  return B;
}
