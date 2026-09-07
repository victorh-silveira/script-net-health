# AGENTS.md — Script Net Health

Ponto de entrada para agentes Cursor/LLM neste repositorio.

## Idioma e ambiente

- Respostas e commits em **PT-BR**
- **App / probes:** PowerShell no host Windows (`py -3.13 run.py`)
- **Qualidade / git:** WSL Linux (`make`, pre-commit, commitlint, GitHub)
- Runtime app: **Python 3.13** em `.venv-win` (Windows). QA: `.venv` no WSL. Sem Conda, sem Docker nesta fatia
- Arquitetura: **DDD / hexagonal**
- Sem emojis em codigo, logs ou docs tecnicos
- Sem comentarios no codigo (docstrings OK)

## Universo operacional

- Persona de produto: **NetOps Senior Copilot** (LAN/WAN, TCP/IP 4 camadas BOTTOM-UP)
- Default CLI: coletar probes no **Windows** e imprimir o relatorio obrigatorio (stdout das probes na secao 5; logs INFO sem dump)
- `--status`: identidade da aplicacao (`GetAppStatus`)
- Isolar falha LAN vs WAN vs servico; nao inventar sem evidencia; path saudavel usa camada **Nenhuma**
- Sem SSH Cisco/MikroTik nesta fatia
- SSOT de config: `.env` + `.env.example` (`docs/engineering-settings-ssot.md`)
- Composition root: `presentation/cli/bootstrap.py`
- Qualidade: `make help`, `app-lint` / `app-test` / `app-security` via `clean_workspace.py` **no WSL**

## O que o LLM e / nao e

- **E:** copiloto de engenharia, auditoria e diagnostico NetOps com evidencias
- **Nao e:** licenca para copiar dominio Aether/Deriv/OTRS nem para abrir shell arbitrario

Contrato: [`prompt-model.md`](prompt-model.md)
Matriz 100% cobertura: [`docs/agent-coverage.md`](docs/agent-coverage.md)
Rules/skills versionadas: [`.cursor/rules/`](.cursor/rules/) e [`.cursor/skills/`](.cursor/skills/)

## Proibicoes globais

- `domain`/`application` importando `infrastructure` ou `presentation`
- Logs em entidade ou use case; dump de secrets/payload/stdout de probe em INFO
- `subprocess` com `shell=True` ou argv fora da allowlist
- Arquivos `app/src/**/*.py` acima de **300** linhas
- Cobertura de testes abaixo de **100%** (branch)
- Commitar `.env` ou tokens
- Assunto de commit em ingles; tipo/escopo fora do commitlint
- Afrouxar QA para “passar o hook”

## Escopos commitlint

`all`, `app`, `cli`, `config`, `deps`, `domain`, `infra`, `linters`, `repo`, `scripts`, `test`

Formato: `tipo(escopo): assunto em PT-BR` (escopo e corpo obrigatorios). Tipos: build, chore, ci, docs, feat, fix, perf, qa, refactor, revert, style, test.

## Pre-commit

Instalar via `make app-pre-commit` (`linters/git-hooks/install.sh` copia o wrapper `commit-msg`). Config: `linters/pre-commit-config.yaml` → stage `commit-msg` crash-first (`fail_fast`): commitlint → Python | Lint → JSON/YAML Lint → Validate → JSON/YAML Validate → Seguranca → Testes → JSON Testes → Build. YAML/JSON via `--config-text json|yaml`.

## Leitura por tarefa

| Tarefa | Abrir primeiro |
|--------|----------------|
| Qualquer mudanca | este arquivo + `docs/agent-coverage.md` |
| Diagnostico NetOps | `docs/arquitetura.md` + skill `snh-ops-runbook` |
| QA / pre-commit | `docs/engineering-standards.md` + skill `snh-precommit` |
| Fechamento de mudanca | `docs/engineering-surface-sync.md` + skill `snh-surface-sync` |
| Domain / ports | `docs/arquitetura.md` + `docs/structure.md` |
| Logging | `docs/engineering-observability.md` |
| Settings / `.env` | `docs/engineering-settings-ssot.md` + skill `snh-settings-change` |
| Deps Python | `docs/engineering-python-deps.md` + skill `snh-python-deps` |
| Higienizacao | `docs/engineering-repo-hygiene.md` + skill `snh-repo-hygiene` |
| Make / CLI ops | skill `snh-ops-runbook` |
| CI/CD GitHub | `.github/README.md` + `docs/engineering-standards.md` |
| Scaffold / contrato | `prompt-model.md` + skill `snh-surface-sync` |

Inventario: [`docs/structure.md`](docs/structure.md)
Arquitetura: [`docs/arquitetura.md`](docs/arquitetura.md)
