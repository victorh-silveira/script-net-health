# Script Net Health

[![CI/CD Pipeline](https://github.com/victorh-silveira/script-net-health/actions/workflows/ci.yml/badge.svg)](https://github.com/victorh-silveira/script-net-health/actions/workflows/ci.yml)
[![GitHub Release](https://img.shields.io/github/v/release/victorh-silveira/script-net-health?color=blue&label=release)](https://github.com/victorh-silveira/script-net-health/releases)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Architecture: Hexagonal / DDD](https://img.shields.io/badge/architecture-Hexagonal%20%2F%20DDD-purple.svg)](docs/arquitetura.md)
[![Coverage: 100% Branch](https://img.shields.io/badge/coverage-100%25%20branch-brightgreen.svg)](docs/engineering-standards.md)
[![Type Checker: Mypy Strict](https://img.shields.io/badge/types-mypy%20strict-blue.svg)](https://mypy.readthedocs.io/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Docstrings: Interrogate 100%](https://img.shields.io/badge/docstrings-interrogate%20100%25-brightgreen.svg)](https://interrogate.readthedocs.io/)
[![Security: Bandit | Pip-Audit | Gitleaks](https://img.shields.io/badge/security-bandit%20%7C%20pip--audit%20%7C%20gitleaks-success.svg)](docs/engineering-standards.md)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![Platform: Windows Host + WSL](https://img.shields.io/badge/platform-Windows%20Host%20%7C%20WSL%20Linux-informational.svg)](README.md)

Copiloto NetOps senior deterministico para auditoria, diagnostico e isolamento de falhas de rede local (LAN), borda (WAN) e servicos de aplicacao no host Windows.

A solucao adota os padroes de **Clean Architecture (Hexagonal / Ports and Adapters)** e **Domain-Driven Design (DDD)**, operando a avaliacao de saude de rede atraves da metodologia **BOTTOM-UP** cobrindo rigorosamente as 4 camadas da pilha TCP/IP.

O ciclo de vida da solucao opera sob uma separacao clara de responsabilidades de ambiente:
- **Execucao e Probes de Rede**: Host Windows nativo via PowerShell (`py -3.13 run.py`), acessando sockets, adaptadores fisicos e binarios do sistema operacional.
- **Engenharia, Qualidade e Git**: WSL Linux (`make`, pre-commit, linters, testes e CI/CD no GitHub Actions).

---

## Indice

- [Visao Geral e Metodologia NetOps](#visao-geral-e-metodologia-netops)
- [Arquitetura Hexagonal e DDD](#arquitetura-hexagonal-e-ddd)
- [Estrutura do Relatorio Tecnico](#estrutura-do-relatorio-tecnico)
- [Matriz de Ambientes e Requisitos](#matriz-de-ambientes-e-requisitos)
- [Instalacao e Configuracao](#instalacao-e-configuracao)
- [Guia de Comandos e Operacao](#guia-de-comandos-e-operacao)
- [Padroes de Engenharia e Quality Gates](#padroes-de-engenharia-e-quality-gates)
- [Variaveis de Ambiente (SSOT)](#variaveis-de-ambiente-ssot)
- [Estrutura do Repositorio](#estrutura-do-repositorio)
- [Documentacao Complementar](#documentacao-complementar)

---

## Visao Geral e Metodologia NetOps

O motor de diagnostico opera segundo a metodologia analitica **BOTTOM-UP** (da camada fisica para a de aplicacao), garantindo que causas raizes em camadas inferiores sejam identificadas antes de inferir falhas em servicos superiores.

| Camada TCP/IP | Probes e Evidencias Coletadas | Criterios de Avaliacao e Diagnostico |
|:---|:---|:---|
| **1. Enlace / Interface (Fisica)** | `ipconfig /all`, `arp -a` | Identificacao de adaptadores ativos, presenca de link operacional, atribuicao de IPv4 e deteccao de gateway padrao na sub-rede. |
| **2. Internet / Rede (IPv4)** | `ping` (Gateway LAN e WAN `1.1.1.1`), `route print` | Medicao de RTT (minimo, medio, maximo), calculo de jitter, integridade de pacotes ICMP e consistencia das rotas padrao. |
| **3. Transporte** | `netstat -ano`, probe TCP SYN/ACK (default: 443) | Conectividade de sockets TCP ponto a ponto, perdas parciais e variabilidade de latencia. Sockets em LISTEN sao catalogados como nota. |
| **4. Aplicacao** | `nslookup`, sonda HTTP, medicao de throughput | Resolucao de nomes DNS, validacao de rotas HTTP opcionais e medicao de largura de banda util de Download/Upload contra SLAs minimos. |

Um caminho saudavel sem degradacao utiliza a classificacao de camada **Nenhuma**, evitando falsas declaracoes de causa raiz sem subsidio analitico.

---

## Arquitetura Hexagonal e DDD

O projeto segue estritamente a inversao de dependencia e isolamento de fronteiras:

```mermaid
flowchart TB
  subgraph presentation [Camada de Apresentacao]
    CLI["CLI / Argumentos"]
    Root["Composition Root (bootstrap.py)"]
    LogSetup["Setup de Observabilidade"]
  end

  subgraph application [Camada de Aplicacao]
    DiagUC["DiagnoseNetworkHealth"]
    StatusUC["GetAppStatus"]
    Ports["ProbeCollectorPort / ClockPort"]
  end

  subgraph domain [Camada de Dominio (Puro)]
    Identity["AppIdentity"]
    Evidence["NetworkEvidence"]
    Diagnoser["BottomUpDiagnoser"]
    Findings["tcp_layer_findings"]
    Report["DiagnosisReport"]
  end

  subgraph infrastructure [Camada de Infraestrutura]
    Clock["SystemClock"]
    Collector["WindowsProbeCollector"]
    Runner["AllowlistedCommandRunner"]
    Settings["Settings (SSOT .env)"]
  end

  CLI --> Root
  Root --> DiagUC
  Root --> StatusUC
  DiagUC --> Ports
  DiagUC --> Diagnoser
  Diagnoser --> Evidence
  Diagnoser --> Report
  Collector -.->|implementa| Ports
  Collector --> Runner
  Root --> Collector
  Root --> Clock
  Root --> Settings
```

### Regras de Dependencia

1. **Domain**: Entidades, value objects e domain services puros. Proibida qualquer importacao de `infrastructure`, `presentation` ou `application`. Sem IO, sem logs.
2. **Application**: Use cases e interfaces de contrato (`ports`). Conhece apenas o `domain`.
3. **Infrastructure**: Implementacao dos adaptadores concretos (`WindowsProbeCollector`, `AllowlistedCommandRunner`, `Settings`). Depende apenas de `application` e `domain`.
4. **Presentation**: Ponto de entrada CLI, parsing de argumentos e wiring de injecao de dependencias (`bootstrap.py`).

---

## Estrutura do Relatorio Tecnico

A execucao padrao gera no terminal um relatorio com 5 secoes padronizadas:

1. **Resumo Executivo**:
   - Status global: `Saudavel`, `Degradado`, `Falha` ou `Inconclusivo`.
   - Camada afetada: Apontada formalmente ou `Nenhuma` se o caminho estiver integro.
   - Sumario objetivo do impacto diagnosticado.
2. **Analise por Camadas**:
   - Classificacao individualizada para Enlace, Internet, Transporte e Aplicacao (`[ok]`, `[degraded]`, `[failed]`, `[unknown]`).
3. **Causa Raiz Sustentada**:
   - Conclusao analitica apoiada exclusivamente nas evidencias coletadas.
4. **Plano de Acao Recomendado**:
   - Medidas operacionais prescritas para engenharia de telecomunicacoes e NOC.
5. **Evidencias Brutas de Rede**:
   - Transcricao integral do stdout de cada comando executado (`ipconfig`, `ping`, `arp`, `route`, `netstat`, `nslookup`, `tracert`, medições de throughput).

---

## Matriz de Ambientes e Requisitos

| Componente | Host Windows 10/11 | WSL Linux (Ubuntu) |
|:---|:---:|:---:|
| **Finalidade** | Runtime do App e Probes de Rede | Engenharia, Make, Qualidade, Git e CI/CD |
| **Shell** | PowerShell (`pwsh`) | Bash (`/bin/bash`) |
| **Python** | Python 3.13 (`py -3.13`) em `.venv-win` | Python 3.13 em `.venv` |
| **Dependencias** | `app/requirements.txt` | `app/requirements.txt` + `app/requirements-dev.txt` |
| **Ferramental** | `ipconfig`, `ping`, `arp`, `route`, `netstat`, `nslookup` | `make`, `git`, `curl`, `gitleaks`, `node` / `npx` |

---

## Instalacao e Configuracao

### 1. Ambiente de Qualidade e Desenvolvimento (WSL Linux)

Execute no terminal WSL:

```bash
# Criacao do ambiente virtual
python3.13 -m venv .venv
source .venv/bin/activate

# Instalacao de dependencias e configuracao dos git hooks crash-first
make app-setup
```

### 2. Ambiente de Execucao do Diagnostico (Windows Host)

Execute no PowerShell do Windows:

```powershell
# Criacao do ambiente virtual dedicado para o host
py -3.13 -m venv .venv-win

# Instalacao dos requisitos de execucao do app
.\.venv-win\Scripts\python.exe -m pip install -r app\requirements.txt
```

### 3. Configuracao de Variaveis de Ambiente

Copie o catalogo de configuracao para seu arquivo local (nunca commitado):

```bash
cp .env.example .env
```

---

## Guia de Comandos e Operacao

### Diagnostico de Rede (PowerShell - Windows)

```powershell
# Execucao do diagnostico completo de saude de rede (Default CLI)
py -3.13 run.py

# Verificacao de status e integridade da aplicacao (GetAppStatus)
py -3.13 run.py --status
```

### Menu de Qualidade e QA (WSL Linux)

```bash
# Exibe menu interativo de ajuda
make help

# Executa bateria completa de linter, tipagem e regras estruturais
make app-lint

# Executa testes unitarios e de integracao com branch coverage obrigatorio de 100%
make app-test

# Executa auditoria de seguranca (Bandit + Pip-audit + Gitleaks)
make app-security

# Valida localmente toda a esteira pre-commit crash-first
make app-pre-commit-run

# Limpa caches e artefatos temporarios locais
make app-clean
```

---

## Padroes de Engenharia e Quality Gates

O repositorio implementa invariantes inegociaveis auditados por esteira automatizada:

- **Limite Estrutural de Arquivos**: Maximo de **300 linhas** por arquivo de codigo em `app/src/**/*.py`.
- **Cobertura de Testes**: **100% de cobertura de branch** nas camadas de aplicacao (`coverage run --branch -m pytest`).
- **Clean Code e Convencoes**: Zero comentarios no codigo de aplicacao (docstrings Google style aceitas); proibicao de emojis em codigo, logs e documentacao tecnica.
- **Injecao Segura de Comandos**: Proibicao absoluta de `subprocess` com `shell=True` ou argumentos fora da allowlist auditada.
- **Pre-commit Crash-First**: Execucao no estagio `commit-msg` com `fail_fast: true`:
  `Commitlint` -> `Python Lint` -> `JSON Lint` -> `YAML Lint` -> `Python Validate` -> `JSON Validate` -> `YAML Validate` -> `Seguranca` -> `Testes 100%` -> `JSON Testes` -> `Build` -> `Limpeza`.
- **Conventional Commits (PT-BR)**: Assunto e corpo obrigatorios em Portugues (PT-BR), sob escopos formais: `all`, `app`, `cli`, `config`, `deps`, `domain`, `infra`, `linters`, `repo`, `scripts`, `test`.

---

## Variaveis de Ambiente (SSOT)

Catalogo unificado das configuracoes suportadas via `.env`:

| Variavel | Tipo | Valor Padrao | Descricao Operacional |
|:---|:---:|:---:|:---|
| `SNH_APP_NAME` | string | `script-net-health` | Nome formal validado em `AppIdentity`. |
| `SNH_LOG_LEVEL` | string | `INFO` | Nivel de log da aplicacao. Logs nao despejam outputs de probes em INFO. |
| `SNH_DISABLE_DOTENV` | bool | `0` | Se ativo (`1`), desabilita leitura automatica de `.env` (usado nos testes). |
| `SNH_PROBE_TIMEOUT_SECONDS` | int | `5` | Tempo limite padrao para cada comando allowlisted. |
| `SNH_PING_COUNT` | int | `3` | Quantidade de pacotes ICMP enviados por probe de ping. |
| `SNH_WAN_PING_TARGET` | string | `1.1.1.1` | Endereco IP WAN utilizado para atestar conectividade externa. |
| `SNH_DNS_PROBE_NAME` | string | `example.com` | Hostname resolvido via `nslookup` para validar camada 4. |
| `SNH_ENABLE_TRACEROUTE` | bool | `0` | Habilita execucao do `tracert` para analise de rota salto a salto. |
| `SNH_TRACERT_TIMEOUT_SECONDS`| int | `30` | Timeout dedicado para a conclusao do traceroute. |
| `SNH_HTTP_PROBE_URL` | string | `""` | URL opcional para checagem de handshake HTTP GET. |
| `SNH_TCP_PROBE_PORT` | int | `443` | Porta de destino utilizada para o teste de transporte TCP. |
| `SNH_ENABLE_SPEEDTEST` | bool | `1` | Ativa afericao de throughput de download e upload. |
| `SNH_SPEEDTEST_BYTES` | int | `2000000` | Volume de bytes trafegados no teste de taxa util de transmissao. |
| `SNH_SPEEDTEST_TIMEOUT_SECONDS` | int | `20` | Timeout global da rotina de teste de velocidade. |
| `SNH_MIN_DOWNLOAD_MBPS` | float | `0` | Banda minima de download. Se `> 0`, reporta degradacao caso fique abaixo. |
| `SNH_MIN_UPLOAD_MBPS` | float | `0` | Banda minima de upload. Se `> 0`, reporta degradacao caso fique abaixo. |

---

## Estrutura do Repositorio

```text
.
├── .github/
│   ├── actions/                  # Composite actions otimizadas (setup, workflows, release, summary)
│   ├── workflows/ci.yml          # Pipeline principal de CI/CD (Python, Workflows, Release, Resumo)
│   └── README.md                 # Documentacao tecnica da esteira do GitHub Actions
├── .cursor/                      # Rules e skills da stack operacional do agente
├── app/
│   ├── src/
│   │   ├── domain/               # Entidades, domain services e constantes (Puro, sem IO/Logs)
│   │   ├── application/          # Use cases e portas de contrato (Protocols)
│   │   ├── infrastructure/       # Adaptadores de sistema, probes de rede, config e observabilidade
│   │   └── presentation/         # Composition root, CLI e setup de logging
│   ├── tests/
│   │   ├── unit/                 # Testes unitarios por camada (Domain, App, Infra, Presentation, Scripts)
│   │   └── integration/          # Testes de integracao de adaptadores e probes
│   ├── scripts/operations/       # Orquestrador unico clean_workspace.py e gates de qualidade
│   ├── requirements.txt          # Requisitos de producao do app
│   ├── requirements-dev.txt      # Requisitos de QA e desenvolvimento
│   └── pyproject.toml            # Configuracoes do Ruff, Mypy, Pytest, Coverage, Bandit, Interrogate
├── docs/                         # Documentacao aprofundada de arquitetura, standards, logs e SSOT
├── linters/                      # Configuracoes de commitlint, releaserc e git-hooks
├── Makefile                      # Interface unificada de automacao para engenharia (WSL)
├── AGENTS.md                     # Ponto de entrada e regras operacionais para agentes e copilotos
├── prompt-model.md               # Contrato reutilizavel de engenharia
├── run.py                        # Entrypoint executavel no host Windows
└── .env.example                  # Catalogo modelo de variaveis de ambiente
```

---

## Documentacao Complementar

Para aprofundamento nos modulos e padroes do projeto:

- [Arquitetura Tecnica Hexagonal](docs/arquitetura.md)
- [Inventario e Mapeamento de Camadas](docs/structure.md)
- [Padroes de Engenharia e Quality Gates](docs/engineering-standards.md)
- [Single Source of Truth para Configuracoes](docs/engineering-settings-ssot.md)
- [Arquitetura de Observabilidade e Logging](docs/engineering-observability.md)
- [Matriz de Cobertura de Agente (100%)](docs/agent-coverage.md)
- [Pipeline de CI/CD no GitHub Actions](.github/README.md)
