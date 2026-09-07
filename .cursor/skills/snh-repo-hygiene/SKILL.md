---
name: snh-repo-hygiene
description: >-
  Removes dead code or obsolete files from script-net-health only with evidence
  (vulture, grep, stale refs). Use when cleaning the repo, deleting unused
  modules, or the user mentions higiene, codigo morto, or purge.
---

# Repo hygiene

## Passos

1. Coletar evidencia (vulture / ruff / grep sem refs)
2. Remover o menor conjunto seguro
3. Atualizar matriz/AGENTS/docs se a superficie sumiu
4. `make app-lint` + `make app-test`

## Nunca

- Apagar skill/rule indexada sem atualizar `agent-coverage.md`
- Commitar limpeza sem prova

## Docs

`docs/engineering-repo-hygiene.md`
