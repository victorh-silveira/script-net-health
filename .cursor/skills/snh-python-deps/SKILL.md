---
name: snh-python-deps
description: >-
  Audits, updates, and manages Python dependencies for script-net-health across
  dual virtual environments (.venv on WSL and .venv-win on Windows host).
---

# Gestão de Dependências Python (snh-python-deps)

Procedimento estrito para auditoria, adição e atualização de bibliotecas no projeto.

## Estrutura de Arquivos de Dependências

- `app/requirements.txt`: Dependências de runtime da aplicação de produção.
- `app/requirements-dev.txt`: Ferramentas de desenvolvimento, testes, linters e pre-commit (`-r requirements.txt`).
- `app/pyproject.toml`: Metadados do projeto, configuração de ferramentas (Ruff, Pytest, Coverage, Bandit).

## Dual Virtual Environments

1. **WSL Linux (`.venv`):**
   - Utilizado pelo Makefile para rodar linters, formatters, gates de segurança e testes.
   - Instalação: `make app-install` ou `pip install -r app/requirements-dev.txt`.
2. **Windows Host (`.venv-win`):**
   - Utilizado para execução da aplicação e captura direta de probes de rede.
   - Instalação: `.\.venv-win\Scripts\pip install -r app\requirements.txt`.

## Checklist para Adicionar uma Dependência

1. **Avaliação Arquitetural:** Dependências de runtime devem respeitar as regras do DDD Hexagonal (nunca adicionar bibliotecas de IO no domínio).
2. **Atualização dos Arquivos de Requisitos:** Inserir o pacote com versão fixada em `app/requirements.txt` ou `app/requirements-dev.txt`.
3. **Auditoria de Vulnerabilidades:** Rodar `pip-audit` via `make app-security` no WSL.
4. **Sincronização de Superfície:** Atualizar `docs/engineering-python-deps.md` caso a biblioteca introduza novo requisito operacional.
