# Padroes de engenharia e QA

## Gates obrigatorios

Orquestrador unico: `app/scripts/operations/clean_workspace.py`.

| Gate | Comando | Intencao |
|------|---------|----------|
| Lint | `make app-lint` | Python lint+validate e `--config-text json|yaml` |
| Test | `make app-test` | pytest + coverage branch fail-under 100 |
| Security | `make app-security` | bandit + pip-audit + Gitleaks (se no PATH) |
| Setup | `make app-setup` | install + hook `commit-msg` via `linters/git-hooks/install.sh` |
| Hooks all | `make app-pre-commit-run` | pre-commit run --all-files no stage `commit-msg` |

Ajuda: `make help`.

Pre-commit (`linters/pre-commit-config.yaml`): stage `commit-msg` com `fail_fast` — commitlint → Python | Lint, JSON/YAML Lint, Validate, JSON/YAML Validate, Seguranca, Testes, JSON Testes, Build, limpeza (`--config-text json|yaml`).

Entrypoint do app: no **PowerShell**, `py -3.13 run.py` (diagnostico NetOps; `py -3.13 run.py --status` para identidade). Make/hooks so no WSL.

CI/CD GitHub: [`.github/README.md`](../.github/README.md) — jobs Python + Workflows (actionlint); Release (semantic-release em `master`); Resumo. Docker/Shell skipped. Config: [`linters/releaserc.json`](../linters/releaserc.json).

## Invariantes

- `app/src/**/*.py` <= 300 linhas
- Cobertura 100% com branch coverage nas camadas de app
- Sem comentarios no codigo (docstrings OK)
- Docs PT-BR; sem emojis
- Conventional Commits: `tipo(escopo): assunto PT-BR` com escopo e corpo obrigatorios (escopos em `linters/commitlint.config.mjs`)
- Qualidade/git: WSL Linux (`make`, pre-commit)
- App/probes: PowerShell no host Windows
- Runtime app: CPython 3.13 em `.venv-win`; QA em `.venv` no WSL (sem Conda, sem Docker neste esqueleto)

## Camadas

Ver [`structure.md`](structure.md) e [`arquitetura.md`](arquitetura.md). Gate de imports impede `domain`/`application` de importar `infrastructure`/`presentation`.

## Skills

- Falha de hook: skill `snh-precommit`
- Fechamento de mudanca: skill `snh-surface-sync`
- Make / CLI: skill `snh-ops-runbook`
