---
name: snh-surface-sync
description: >-
  Closes script-net-health changes by syncing docs/rules/skills/AGENTS/matrix,
  running quality gates on WSL, and removing local clutter. Use when finishing
  a feature, settings change, docs update, or when the user mentions sync de
  superficie, fechar PR, atualizar agents, or checklist pos-mudanca.
---

# Surface sync

## Checklist

1. Listar arquivos tocados e superficies em `docs/agent-coverage.md`
2. Atualizar docs cujo significado operacional mudou
3. Alinhar `.cursor/rules/*.mdc` e `.cursor/skills/*/SKILL.md` se o procedimento mudou
4. Atualizar `AGENTS.md` (Leitura por tarefa) + linha na matriz
5. Se o contrato DDD/QA mudou: `prompt-model.md`
6. Remover `_tmp*`, probes, msgs de commit soltas
7. Gates WSL: `make app-lint`, `make app-test`, `make app-security` (ou `make app-pre-commit-run`)
8. Commit Conventional Commits PT-BR

## Docs

`docs/engineering-surface-sync.md`, `docs/agent-coverage.md`, `AGENTS.md`
