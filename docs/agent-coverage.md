# Matriz de Cobertura de Agentes (100%)

Cada superfície arquitetural e operacional do projeto possui documentação correspondente, regra canônica em [`.agents/rules/`](../.agents/rules/) e skill operacional em [`.agents/skills/`](../.agents/skills/). Ponto de entrada canônico: [`AGENTS.md`](../AGENTS.md).

## Matriz de Rastreabilidade

| Superfície Arquitetural | Documento de Engenharia | Rule Canônica (`.agents/rules/`) | Skill Operacional (`.agents/skills/`) |
| :--- | :--- | :--- | :--- |
| Engenharia e Qualidade | [engineering-standards.md](engineering-standards.md) | `snh-engineering.mdc` + `snh-testing.mdc` | `snh-precommit` |
| Domínio Puro NetOps | [arquitetura.md](arquitetura.md) + [structure.md](structure.md) | `snh-domain-pure.mdc` | — |
| Hexagonal e Portas | [arquitetura.md](arquitetura.md) + [structure.md](structure.md) | `snh-hexagonal.mdc` | `snh-ops-runbook` |
| Probes Windows | [arquitetura.md](arquitetura.md) + [structure.md](structure.md) | `snh-probes-windows.mdc` | `snh-ops-runbook` |
| Observabilidade e Logs | [engineering-observability.md](engineering-observability.md) | `snh-logging.mdc` | `snh-ops-runbook` |
| Configurações e SSOT | [engineering-settings-ssot.md](engineering-settings-ssot.md) | `snh-settings-ssot.mdc` | `snh-settings-change` |
| Dependências Python | [engineering-python-deps.md](engineering-python-deps.md) | `snh-python-deps.mdc` | `snh-python-deps` |
| Higiene do Repositório | [engineering-repo-hygiene.md](engineering-repo-hygiene.md) | `snh-repo-hygiene.mdc` | `snh-repo-hygiene` |
| Sincronização de Superfície | [engineering-surface-sync.md](engineering-surface-sync.md) | `snh-surface-sync.mdc` | `snh-surface-sync` |
| Contrato Prompt-Modelo | [prompt-model.md](../prompt-model.md) | `snh-engineering.mdc` | `snh-surface-sync` |
| Scripts e Automação | [engineering-standards.md](engineering-standards.md) + [structure.md](structure.md) | `snh-scripts.mdc` | `snh-ops-runbook` |
| CI/CD GitHub Actions | [.github/README.md](../.github/README.md) + [engineering-standards.md](engineering-standards.md) | `snh-scripts.mdc` | `snh-ops-runbook` |

## Mapeamento de Camadas DDD ↔ Matriz

| Diretório no Repositório | Superfície Correspondente |
| :--- | :--- |
| `app/src/domain/` | Domínio Puro NetOps |
| `app/src/application/ports/` | Hexagonal e Portas |
| `app/src/application/use_cases/` | Hexagonal e Portas + Domínio Puro NetOps |
| `app/src/infrastructure/adapters/` | Probes Windows + Hexagonal e Portas |
| `app/src/infrastructure/config/` | Configurações e SSOT |
| `app/src/infrastructure/logging/` | Observabilidade e Logs |
| `app/src/presentation/` | Scripts e Automação + Hexagonal e Portas |
| `app/scripts/operations/` | Scripts e Automação + Higiene do Repositório |
| `app/tests/` | Engenharia e Qualidade |
| `.agents/` | Contrato Prompt-Modelo + Sincronização de Superfície |
| `.env.example` | Configurações e SSOT |
| `.github/` | CI/CD GitHub Actions |

## Invariante alwaysApply

Todas as regras em `.agents/rules/*.mdc` contêm obrigatoriamente `alwaysApply: true`.
