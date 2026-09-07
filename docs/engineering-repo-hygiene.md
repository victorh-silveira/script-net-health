# Higienizacao do repositorio

Remover codigo ou arquivos mortos **somente com evidencia**.

## Evidencia aceita

- Vulture / ruff F401 apontando simbolo nao usado
- Grep sem referencias (imports, docs, matriz, Makefile)
- Teste/documentacao obsoleta apos migracao

## Procedimento

1. Listar candidatos e prova (comando + resultado).
2. Remover o menor conjunto seguro.
3. Atualizar docs/rules/skills/matriz se a superficie sumiu.
4. `make app-lint` + `make app-test`.

## Nao fazer

- Apagar “por limpeza” sem grep
- Remover skill/rule indexada em `docs/agent-coverage.md` sem atualizar a matriz e `AGENTS.md`
- Deixar `_tmp*`, `COMMIT_MSG.txt`, probes ou `.env` no tree

Rule: `snh-repo-hygiene`. Skill: `snh-repo-hygiene`.
