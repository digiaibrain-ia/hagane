# Processo — Baggio, Sistema de Água (filtragem)

Fonte: telas do WinCC (Overview e I/O Status) do projeto `WU_HAGANE`.

## Rede e CPU
- CPU 315-2 PN/DP, interface X2 na sub-rede `PN/IE_1`, IP **192.168.0.2 / 255.255.255.0**.
- Web server da CPU: **desativado** no projeto atual (print de 24/11). Foi visto ativo e sem HTTPS antes; manter desativado.

## Equipamentos (tela Overview)
- **Tanque sujo** com 4 níveis: máximo, fim de enchimento, início de enchimento, mínimo.
- **Tanque limpo** (compensação) com nível alto e mínimo, válvula de compensação.
- **Bombas de filtragem 1 e 2** com softstarter e indicação em Hz (confirmar se há inversor).
- **Filtro**: rotovac, aspirador, extrator de lodo, transportador dragante, válvula quebra-vácuo, válvula sopro (ar comprimido), rotação da banda filtrante, rolo de papel (manta descartável).
- Válvulas: alimentação, retorno, lavagem, compensação, sopro, quebra-vácuo.
- Modos: filtro automático / manual, ciclo automático ligado/desligado, autolimpeza, autolimpeza contínua, ciclo de fim de semana, vácuo no filtro.

## Entradas digitais
64 entradas (I0.0 a I7.7) em [entradas_digitais.csv](entradas_digitais.csv), copiadas da tela I/O Status.
Planilha completa de tags (305): [../contratos/tags_v0.1.csv](../contratos/tags_v0.1.csv), gerada por `plc/variaveis/gerar_tags_v0.1.py`. Bombas têm inversor (`QW336`).

## Pontos a confirmar
Ver [../contratos/pendencias.md](../contratos/pendencias.md).
