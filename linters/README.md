# Linters e qualidade

Configuracao centralizada de hooks. Qualidade e git no WSL; diagnostico do app no PowerShell.

| Arquivo | Uso |
|---------|-----|
| `pre-commit-config.yaml` | Gates crash-first no stage `commit-msg` |
| `commitlint.config.mjs` | Conventional Commits: tipo, escopo e corpo obrigatorios; assunto PT-BR |
| `git-hooks/install.sh` | Copia `commit-msg` para `.git/hooks` (`make app-pre-commit`) |
| `git-hooks/commit-msg` | Wrapper WSL: PATH em `git-hooks/bin` e `python -m pre_commit` |
| `git-hooks/bin/python` | Resolve o Python do `.venv` no WSL |
| `git-hooks/bin/commitlint-early.sh` | Commitlint com workaround `wslpath` / `COMMIT_EDITMSG` |

Instalar: `make app-pre-commit` (chama `linters/git-hooks/install.sh`). Nao ha hook de stage `pre-commit`; os gates rodam no `commit-msg`.

Os gates executam `app/scripts/operations/clean_workspace.py --area python --stage ...`. YAML/JSON usam `--config-text json|yaml` (hooks e CI separados do lint Python).
