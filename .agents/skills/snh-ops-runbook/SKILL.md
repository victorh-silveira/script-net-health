---
name: snh-ops-runbook
description: >-
  Operates script-net-health diagnostics on Windows PowerShell and quality gates
  on WSL Linux. Use when running network probes, CLI status checks, or operating
  the dual-environment runtime.
---

# Runbook de Operações: Script Net Health (snh-ops-runbook)

Guia operacional para execução do diagnóstico de integridade de rede no Windows e qualidade no WSL.

## 1. Execução de Diagnóstico (Host Windows / PowerShell)

O diagnóstico de rede mede a NIC física do host Windows. Não execute o diagnóstico dentro do WSL, pois o WSL utiliza NAT virtual e mede um ambiente isolado.

```powershell
# Execucao do diagnostico completo de rede (alvos padrao ou definidos em .env)
py -3.13 run.py

# Verificacao de identidade e status da aplicacao
py -3.13 run.py --status

# Execucao com caminho explicito do ambiente virtual Windows
.\.venv-win\Scripts\python.exe run.py
```

### Probes Executadas e Controles

- **Comandos Nativos:** `ipconfig`, `ping`, `arp`, `route`, `netstat`, `nslookup`, `tracert`.
- **Traceroute:** Desabilitado por padrão para respostas rápidas. Ative com `SNH_ENABLE_TRACEROUTE=1`.
- **Speedtest / Throughput:** Opcional via HTTP/HTTPS. Ative com `SNH_ENABLE_SPEEDTEST=1`.
- **Relatório de Saída:** Gerado em 5 seções estruturadas (Resumo, Achados por Camada TCP/IP, Métricas de Throughput, Configuração Operacional e Transcrições Brutas de Probes).

## 2. Qualidade e Desenvolvimento (WSL Linux / Bash)

A suíte de validação e linters é executada via Makefile no WSL:

```bash
# Menu de ajuda e comandos disponiveis
make help

# Instalacao completa de dependencias de producao e desenvolvimento
make app-install

# Execucao completa de linters (Ruff, validação JSON/YAML)
make app-lint

# Execucao de testes unitarios e integrados com cobertura de branch 100%
make app-test

# Auditoria de seguranca (Bandit e pip-audit)
make app-security

# Execucao completa da esteira pre-commit em modo crash-first
make app-pre-commit-run
```
