# Padrões de Engenharia e Qualidade

Especificação de padrões técnicos, ferramentas e esteira de qualidade do **Script Net Health**.

## Dual-Environment Operacional

O projeto utiliza intencionalmente dois ambientes para máxima precisão e reprodutibilidade:
1. **Host Windows:**
   - Execução do utilitário e coleta de probes de rede física (`py -3.13 run.py`).
   - Ambiente virtual: `.venv-win`.
2. **WSL Linux:**
   - Execução de tarefas de engenharia, linters, pre-commit e testes automatizados.
   - Ambiente virtual: `.venv`.

## Invariantes de Código e Estilo

- **Sem Emojis:** Proibido uso de emojis em arquivos de código, commits, logs ou documentação.
- **Sem Comentários no Código:** O código deve ser autoexplicativo, utilizando docstrings completas (PEP 257) em todas as classes, métodos e funções públicas.
- **Limite de 300 Linhas:** Nenhum arquivo Python dentro de `app/src/` pode exceder 300 linhas de código.
- **Tipagem Estrita:** Uso de `typing` e checagem estática via Mypy.

## Suíte de Ferramentas de Qualidade

A esteira de qualidade é orquestrada via Makefile no WSL Linux:

| Ferramenta | Finalidade | Comando Makefile |
| :--- | :--- | :--- |
| **Ruff** | Linter e formatador de código Python | `make app-lint` |
| **Interrogate** | Garantia de 100% de docstrings no código | `make app-lint` |
| **Vulture** | Detecção e eliminação de código morto | `make app-lint` |
| **Bandit** | Análise estática de segurança | `make app-security` |
| **pip-audit** | Auditoria de vulnerabilidades em dependências | `make app-security` |
| **Pytest + Coverage** | Execução de testes com exigência de 100% branch coverage | `make app-test` |
| **Commitlint** | Validação de mensagens de commit no padrão Conventional Commits | `make app-pre-commit-run` |

## Política Fail-Fast (Crash-First)

Toda a cadeia de validação opera no modelo crash-first. A detecção de qualquer inconformidade encerra a execução imediatamente com código de erro, impedindo a continuidade de alterações fora do padrão.
