---
name: snh-python-deps
description: >-
  Changes or audits Python dependencies for script-net-health (requirements.txt,
  requirements-dev.txt, pyproject). Use when adding/removing packages, fixing
  pip-audit, or the user mentions deps, requirements, or mypy stubs.
---

# Deps Python

## Passos

1. Escolher runtime vs dev requirements
2. Evitar redundancia e pins desnecessarios
3. `make app-install` no WSL (`.venv`). Runtime Windows: pip em `.venv-win`
4. `make app-lint`, `make app-test`, `make app-security`
5. Atualizar `docs/engineering-python-deps.md` se a politica mudar
6. Tabelas: Polars only; nao adicionar pandas

## Docs

`docs/engineering-python-deps.md`
