# Gestão de Dependências Python

Políticas e instruções de manutenção de pacotes e ambientes virtuais no **Script Net Health**.

## Runtime Homologado

- **Python:** Versão 3.13 (`requires-python = ">=3.13,<3.14"`).
- **Sem Docker e sem Conda:** O projeto opera nativamente com ambientes virtuais venv.

## Ambientes Virtuais

1. **Host Windows (`.venv-win`):**
   - Destinado ao runtime da aplicação e execução direta das probes de rede nativas.
   - Instalação:
     ```powershell
     py -3.13 -m venv .venv-win
     .\.venv-win\Scripts\pip install -r app\requirements.txt
     ```

2. **WSL Linux (`.venv`):**
   - Destinado ao ferramental de desenvolvimento, linters, pre-commit e execução de testes.
   - Instalação:
     ```bash
     python3.13 -m venv .venv
     .venv/bin/pip install -r app/requirements-dev.txt
     ```

## Fixação e Auditoria de Segurança

- Todas as dependências devem possuir versões fixadas para garantir determinismo.
- Auditoria contínua de vulnerabilidades executada via `pip-audit`.
