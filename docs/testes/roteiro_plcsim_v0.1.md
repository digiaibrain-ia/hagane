# Roteiro de teste com PLCSIM clássico — Hagane v0.2

Cadeia: **PLCSIM V5.4 (CPU 315) → NetToPLCsim → Node-RED → HTML**. Tudo no notebook. Somente leitura.
Teste no PLCSIM **não substitui** o teste na CPU real (manual do NetToPLCsim).

## 1. Preparar (uma vez)
| Item | Valor |
|---|---|
| Adaptador "Ethernet 2" (Siemens PLCSIM Virtual Ethernet Adapter) | IPv4 `192.168.0.10` / `255.255.255.0`, sem gateway |
| Set PG/PC Interface | `S7ONLINE → PLCSIM.TCPIP.1` |
| Wi-Fi | não mexer |

## 2. Ordem de abertura (importa!)
1. Serviço **S7DOS Help Service** rodando (`Get-Service s7oiehsx64` = Running; se não, PowerShell **admin**: `Start-Service s7oiehsx64`).
2. PLCSIM clássico, caixa em `PLCSIM(TCP/IP)`.
3. TIA: Download (hardware + software) para `192.168.0.2`; CPU em **RUN-P**; depois **Go offline**.
4. NetToPLCsim **como administrador** → "Sim" para parar o serviço → estação: Network IP `192.168.0.10`, Plcsim IP `192.168.0.2` (pelo botão `...`), Rack/Slot `0/2` → **Start Server** → "Port 102 OK".
5. Node-RED: endpoint da fonte S7 com Address `192.168.0.10` (ou `$env:HAGANE_PLC_IP="192.168.0.10"` antes de abrir, na v0.2).
6. Abrir `http://localhost:1880/hagane` → topo "CPU REAL" + "✔ comunicação OK".

Para voltar ao TIA depois: fechar NetToPLCsim e `Start-Service s7oiehsx64` (admin).

## 3. Colocar a máquina "normal" no PLCSIM
Com todas as entradas em 0 o programa vê disjuntores desarmados: **muitas lâmpadas vermelhas e alarmes são o esperado**.
No PLCSIM: *Insert → Input Variable* e digite (formato HEX):

| Byte | Valor | Bits ligados |
|---|---|---|
| IB0 | `49` | I0.0 relé controle, I0.3 circuito segurança OK, I0.6 comando ligado |
| IB1 | `11` | I1.0 disj. bomba 1 OK, I1.4 disj. bomba 2 OK |
| IB2 | `15` | I2.0 disj. bomba T.C., I2.2 disj. aspirador, I2.4 disj. extrator |
| IB3 | `21` | I3.0 disj. rotovac, I3.5 disj. transp. dragante |

## 4. Provocar e conferir (entradas — efeito direto na tela)
Toque na lâmpada no HTML para ver o endereço e o estado.

| Forçar no PLCSIM | Esperado no HTML |
|---|---|
| `I1.1 = 1` | Lâmpada **Bomba 1** verde |
| `I1.5 = 1` | Lâmpada **Bomba 2** verde |
| `I3.1 = 1` | **Rotovac** verde |
| `I2.3 = 1` | **Aspirador** verde |
| `I2.5 = 1` | **Extrator lodo** verde |
| `I3.6 = 1` | **Transp. filtro** verde |
| `I6.0 / I6.3 / I6.2 / I6.1 = 1` | Lâmpadas de nível do tanque sujo (Máximo / Fim / Início / Mínimo) |
| `I1.0 = 0` | **Bomba 1** vermelha com "!" + alerta "Disjuntor da bomba 1 não OK" |
| `I1.3 = 1` | **Bomba 1** vermelha + alerta "Falha no soft-start da bomba 1" |
| `I0.1 = 1` | Alerta **EMERGÊNCIA** "Botão de emergência do painel pressionado" |
| qualquer `I` | Aba **Entradas e saídas** acompanha bit a bit |

## 5. Saídas e memórias (dependem do programa do PLC)
`Q12.x`, `Q14.x`, `Q15.x` (painel e válvulas) e `M` (alarmes) são calculados pelo programa. Exemplo provável: `I4.2 = 1` (sistema em AUT) → `Q12.1` → painel **Filtro Automático** verde. Anotar o que acontecer: confirma a lógica real e as pendências P-10/P-11.

## 6. Registrar
Para cada linha: OK / diferente (print). Diferença de polaridade → atualizar `docs/contratos/pendencias.md`.
