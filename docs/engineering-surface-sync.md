# Surface sync (fechamento de mudanca)

Toda atualizacao material deve fechar com superficie de agentes coerente, gates verdes e working tree limpo.

Rule: `snh-surface-sync`. Skill: `snh-surface-sync`.

## O que sincronizar

| Mudanca | Superficie tipica |
|---------|-------------------|
| Camadas / ports | `arquitetura.md`, `structure.md`, rules hexagonal/domain |
| Logging | `engineering-observability.md`, rule `snh-logging` |
| Settings / `.env` | `engineering-settings-ssot.md`, skill `snh-settings-change` |
| Gates / QA | `engineering-standards.md`, skill `snh-precommit` |
| CI/CD GitHub | `.github/README.md`, `linters/releaserc.json` |
| Deps pip | `engineering-python-deps.md`, skill `snh-python-deps` |
| Nova skill/rule | `agent-coverage.md` + tabela em `AGENTS.md` |
| Contrato cross-repo | `prompt-model.md` |

## Ordem de fechamento

1. Codigo + testes
2. Docs / rules / skills / `AGENTS.md` / `agent-coverage.md`
3. Remover sujeira local
4. Gates WSL: `make app-lint`, `make app-test`, `make app-security` (ou `make app-pre-commit-run`)
5. Commit Conventional Commits PT-BR

## Criterio de pronto

- Matriz aponta para arquivos existentes
- Rules com `alwaysApply: true`
- Cobertura 100% branch; sem artefatos temporarios no diff
