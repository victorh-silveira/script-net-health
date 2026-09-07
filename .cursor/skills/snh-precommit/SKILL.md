---
name: snh-precommit
description: >-
  Diagnoses and fixes script-net-health pre-commit failures (commitlint first,
  Python lint/validate/security/test/build with YAML/JSON via --config-text,
  300-line limit, pytest branch coverage 100%). Use when pre-commit fails,
  coverage drops, a file exceeds 300 lines, or the user mentions
  clean_workspace, fail-under, or commitlint.
---

# Pre-commit script-net-health

Crash-first no stage `commit-msg` (`fail_fast: true`): commitlint → Python | Lint → JSON/YAML Lint → Validate → JSON/YAML Validate → Seguranca → Testes → JSON Testes → Build → limpeza.

Instalar o hook no WSL com `make app-pre-commit` (`linters/git-hooks/install.sh`). YAML/JSON rodam com `--config-text json|yaml`. Mensagem invalida aborta antes dos gates Python.

## Passos

1. Ler o trecho FAIL do hook
2. Commitlint: tipo, escopo e corpo obrigatorios; assunto PT-BR (primeiro do crash-first)
3. Python | Lint: Ruff, Interrogate, Vulture
4. Python | JSON/YAML Lint: `--config-text json|yaml`
5. Python | Validate: mypy, camadas, 300 linhas
6. Python | JSON/YAML Validate: parse estrutural e `yaml.safe_load`
7. Python | Seguranca: Bandit, pip-audit, Gitleaks se estiver no PATH
8. Python | Testes: reproduzir o teste; cobrir misses/branches
9. Python | JSON Testes: `.vscode/settings.json` (`extraPaths`, pytest)
10. Python | Build: `compileall`
11. Reexecutar no **WSL**: `make app-lint` / `make app-test` / `make app-security` (ou `make app-pre-commit-run`)

## Docs

`docs/engineering-standards.md`, `AGENTS.md`
