# Dependencias Python

## Arquivos SSOT

| Arquivo | Papel |
|---------|-------|
| `app/requirements.txt` | Runtime |
| `app/requirements-dev.txt` | Lint, tipos, testes, seguranca, yamllint |
| `app/pyproject.toml` | Ruff, mypy, coverage, pytest, bandit, vulture |

Runtime atual: **CPython 3.13** (`requires-python = ">=3.13,<3.14"`). Dois venvs: `.venv` no WSL (Make/lint/test) e `.venv-win` no Windows (app/probes). Sem Conda e sem CUDA neste esqueleto.

Nao duplicar a mesma lib em runtime e dev sem necessidade. Preferir ranges minimos coerentes com o restante do repo.

Runtime hoje: apenas `python-dotenv`. Sem Polars ate existir processamento tabular; se tabelas forem adicionadas, DataFrame SSOT = **Polars only**.

## Fluxo de mudanca

1. Justificar a dependencia (problema concreto).
2. Atualizar o requirements correto.
3. Instalar no venv WSL: `make app-install`. Runtime Windows: `py -3.13 -m pip install -r app/requirements.txt` em `.venv-win`.
4. Rodar `make app-lint` e `make app-test`.
5. Se houver CVE: `make app-security` (pip-audit); so ignore com justificativa e lista no orquestrador.

## Anti-padroes

- Adicionar framework web/DB sem port/adapter.
- Pins soltos que quebram mypy/ruff sem atualizar configs.
- Dependencia so para um script one-off (preferir stdlib ou script fora do runtime).
- Pandas ou mix de DataFrame libs se houver tabelas.

Rule: `snh-python-deps`. Skill: `snh-python-deps`.
