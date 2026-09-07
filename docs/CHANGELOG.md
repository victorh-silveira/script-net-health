## 1.0.0 (2026-09-07)

### Funcionalidades

* **all:** disponibilizar copiloto NetOps hexagonal ([ec4ca57](https://github.com/victorh-silveira/script-net-health/commit/ec4ca5741abf8a114724a8514ad782927a6a67b3))

# Changelog

## 0.0.0

- Esqueleto de engenharia (DDD hexagonal, TDD, gates Make, superficie Cursor `snh-*`).
- Diagnostico NetOps: coleta local no host Windows + relatorio BOTTOM-UP.
- Qualidade/git no WSL; app/probes no PowerShell (`.venv-win`).
- Higiene git/Make/hooks no formato Aether (`install.sh`, escopo e corpo de commit obrigatorios), sem Conda/Docker.
- CI/CD Python com YAML/JSON separados (`--config-text json|yaml`), sem jobs Docker/shell.
- Workflow GitHub Actions dispara em `master` (branch padrao).
- Release semantica (`linters/releaserc.json`) e resumo do pipeline apos CI verde.
- `GetAppStatus` permanece em `--status`.
