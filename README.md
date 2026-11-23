# Hagane — supervisão e controle do sistema de filtragem

Sistema de filtragem industrial supervisionado por dashboard HTML, com Node-RED
como gateway central e PLC Siemens S7 como controlador.

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
| `docs/geral/` | Arquitetura, glossário, dicionário de dados |
| `docs/padroes/` | Nomes, versões, alertas e falhas |
| `docs/contratos/` | Contratos PLC ↔ Node-RED ↔ HTML (endereços, payloads, endpoints) |
| `config/` | Exemplos de configuração (`*.example`), nunca valores reais |

## Regras
- Nunca commitar `.env`, `flows_cred.json`, IPs reais ou dados de ensaio.
- Convenções de branch, commit e tag: [CONTRIBUTING.md](CONTRIBUTING.md).
- Regras de trabalho: [CLAUDE.md](CLAUDE.md).
