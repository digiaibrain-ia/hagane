#!/usr/bin/env python3
"""Servidor S7 SIMULADO (snap7) para testar a leitura real do Node-RED sem PLC.
Uso: python3 tests/servidor_s7_simulado_v0.1.py [porta]   (porta 102 exige root)
Escreve valores conhecidos em I/Q/M e muda M12.2 (ALARME BOMBA 1) a cada 10 s, para o
teste conferir bit a bit. NAO prova nada sobre a CPU 315 real (rack/slot, PUT/GET, firmware)."""
import ctypes, sys, time
import snap7
from snap7.server import Server
from snap7.type import SrvArea, Area

porta = int(sys.argv[1]) if len(sys.argv) > 1 else 102
PE = (ctypes.c_ubyte * 16)(); PA = (ctypes.c_ubyte * 32)(); MK = (ctypes.c_ubyte * 160)()
srv = Server()
srv.register_area(SrvArea.PE, 0, PE); srv.register_area(SrvArea.PA, 0, PA); srv.register_area(SrvArea.MK, 0, MK)
srv.start_to("0.0.0.0", tcp_port=porta)
print("servidor S7 simulado na porta", porta, flush=True)
# A memoria registrada no servidor nao e compartilhada com o ctypes: grava por um cliente local.
cli = snap7.Client(); cli.connect("127.0.0.1", 0, 2, porta)
# valores conhecidos (conferidos pelo teste): I0.0, I0.3, I0.6, I1.0, I1.1, I1.4, Q12.1, Q11.4
cli.write_area(Area.PE, 0, 0, bytearray([0b01001001, 0b00010011]))
cli.write_area(Area.PA, 0, 11, bytearray([0b00010000, 0b00000010]))     # Q11.4 e Q12.1
t0 = time.time()
while True:
    m = 0b00000100 if int((time.time() - t0) / 10) % 2 else 0           # M12.2 alterna a cada 10 s
    cli.write_area(Area.MK, 0, 12, bytearray([m]))
    time.sleep(0.5)
