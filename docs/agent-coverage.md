# Matriz de cobertura do agente (100%)

Cada superficie do esqueleto tem **doc + rule + skill** (ou `—` justificado). Entrada: [`AGENTS.md`](../AGENTS.md).

Rules/skills vivem em [`.cursor/`](../.cursor/) e sao **versionadas** no git.

## Matriz

| Superficie | Doc | Rule (`.cursor/rules/`) | Skill (`.cursor/skills/`) |
|------------|-----|-------------------------|---------------------------|
| Engenharia / QA | [engineering-standards.md](engineering-standards.md) | `snh-engineering.mdc` + `snh-testing.mdc` | `snh-precommit` |
| Domain puro | [arquitetura.md](arquitetura.md) + [structure.md](structure.md) | `snh-domain-pure.mdc` | — |
| Hexagonal / ports | [arquitetura.md](arquitetura.md) + [structure.md](structure.md) | `snh-hexagonal.mdc` | `snh-ops-runbook` |
| Logging | [engineering-observability.md](engineering-observability.md) | `snh-logging.mdc` | `snh-ops-runbook` |
| Settings / `.env` | [engineering-settings-ssot.md](engineering-settings-ssot.md) | `snh-settings-ssot.mdc` | `snh-settings-change` |
| Deps Python | [engineering-python-deps.md](engineering-python-deps.md) | `snh-python-deps.mdc` | `snh-python-deps` |
| Higienizacao | [engineering-repo-hygiene.md](engineering-repo-hygiene.md) | `snh-repo-hygiene.mdc` | `snh-repo-hygiene` |
| Surface sync | [engineering-surface-sync.md](engineering-surface-sync.md) | `snh-surface-sync.mdc` | `snh-surface-sync` |
| Contrato prompt-modelo | [prompt-model.md](../prompt-model.md) | `snh-engineering.mdc` | `snh-surface-sync` |
| Scripts / Make | [engineering-standards.md](engineering-standards.md) + [structure.md](structure.md) | `snh-scripts.mdc` | `snh-ops-runbook` |
| Diagnostico NetOps | [arquitetura.md](arquitetura.md) | `snh-hexagonal.mdc` | `snh-ops-runbook` |

## Pastas DDD ↔ matriz

| Pasta | Linha da matriz |
|-------|-----------------|
| `app/src/domain/` | Domain puro + Diagnostico NetOps |
| `app/src/application/ports/` | Hexagonal / ports |
| `app/src/application/use_cases/` | Hexagonal / ports + Diagnostico NetOps |
| `app/src/infrastructure/adapters/` | Hexagonal / ports |
| `app/src/infrastructure/config/` | Settings / `.env` |
| `app/src/infrastructure/logging/` | Logging |
| `app/src/presentation/` | Scripts / Make + Logging |
| `app/scripts/operations/` | Scripts / Make |
| `app/tests/` | Engenharia / QA |
| `.env.example` | Settings / `.env` |

## Rules alwaysApply

Todas as rules em `.cursor/rules/*.mdc` usam `alwaysApply: true`.
