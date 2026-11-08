## [1.0.2](https://github.com/victorh-silveira/script-net-health/compare/v1.0.1...v1.0.2) (2026-11-08)

### Correcoes de Bug

* **repo:** corrigir sintaxe do diagrama mermaid no README e docs ([1fbfd90](https://github.com/victorh-silveira/script-net-health/commit/1fbfd904dae0b3394de5ad0a44c4234d88397190))

### Refatoracoes Tecnicas

* **repo:** eliminar retrocompatibilidade do cursor e consolidar .agents/ agnostico ([f3db63e](https://github.com/victorh-silveira/script-net-health/commit/f3db63eddb2e15bd73da2caee8ee40e1c116f6d2))
* **repo:** reescrever harness de agentes e migrar para .agents/ ([4c937f2](https://github.com/victorh-silveira/script-net-health/commit/4c937f238bc905978871fd78fbb2455023c650bc))

### Documentacao

* **repo:** reestruturar readme principal com badges e arquitetura ([3381f3e](https://github.com/victorh-silveira/script-net-health/commit/3381f3e4a048f399b17c5c5406bd1c2668e1f2d4))
* **repo:** renomeia documentacao para WORKFLOWS.md ([628f10e](https://github.com/victorh-silveira/script-net-health/commit/628f10ee8338316ee197a9e475e5e08b282c48ad))

## [1.0.1](https://github.com/victorh-silveira/script-net-health/compare/v1.0.0...v1.0.1) (2026-10-03)

### Melhorias de Performance

* **repo:** otimizar desempenho e tempo da pipeline ([4684315](https://github.com/victorh-silveira/script-net-health/commit/4684315e183657fb9007fd867cd084fed87b77a3))

## 1.0.0 (2026-09-07)

### Funcionalidades

* **all:** disponibilizar copiloto NetOps hexagonal ([ec4ca57](https://github.com/victorh-silveira/script-net-health/commit/ec4ca5741abf8a114724a8514ad782927a6a67b3))

# Changelog

## 0.0.0

- Esqueleto de engenharia (DDD hexagonal, TDD, gates Make, superficie Cursor `snh-*`).
- Diagnostico NetOps: coleta local no host Windows + relatorio BOTTOM-UP.
- Qualidade/git no WSL; app/probes no PowerShell (`.venv-win`).
- Higiene git/Make/hooks com qualidade crash-first (`install.sh`, escopo e corpo de commit obrigatorios), sem Conda/Docker.
- CI/CD Python com YAML/JSON separados (`--config-text json|yaml`), sem jobs Docker/shell.
- Workflow GitHub Actions dispara em `master` (branch padrao).
- Release semantica (`linters/releaserc.json`) e resumo do pipeline apos CI verde.
- `GetAppStatus` permanece em `--status`.
