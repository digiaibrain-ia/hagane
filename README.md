# Baggio — Sistema de filtragem

Supervisão do sistema de filtragem Baggio.

Dashboard HTML, com Node-RED como gateway central e PLC Siemens S7 (CPU 315-2 PN/DP) como controlador.

## Arquitetura
```
Sensores/atuadores ──► PLC S7 ──(S7/Modbus TCP)──► Node-RED (gateway + API HTTP) ──► Dashboard HTML
```
Detalhes: [docs/geral/arquitetura.md](docs/geral/arquitetura.md).

## Pastas
| Pasta | Conteúdo |
|---|---|
| `dashboard/` | App do operador (fonte em `src/`, build em `build/`, versões antigas em `arquivo/`) |
| `nodered/flows/` | Fluxos Node-RED (JSON exportado, sem credenciais) |
| `plc/` | Blocos SCL (`blocos/`), DBs e tags (`variaveis/`), versões antigas (`arquivo/`) |
| `docs/geral/` | Escopo, processo, arquitetura, glossário |
| `docs/padroes/` | Nomes, versões, alertas e falhas |
| `docs/contratos/` | Contratos PLC ↔ Node-RED ↔ HTML (endereços, payloads, endpoints) |
| `config/` | Exemplos de configuração (`*.example`), nunca valores reais |

## Estado
Escopo v0.1: 3 telas somente leitura (Overview, Alertas e falhas, I/O). Ver [docs/geral/escopo_v0.1.md](docs/geral/escopo_v0.1.md). Tags: `docs/contratos/tags_v0.1.csv`.

## Regras
- Nunca commitar `.env`, `flows_cred.json`, IPs reais ou dados de ensaio.
- Convenções de branch, commit e tag: [CONTRIBUTING.md](CONTRIBUTING.md).
- Regras de trabalho: [CLAUDE.md](CLAUDE.md).
