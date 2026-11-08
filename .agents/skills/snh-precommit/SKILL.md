---
name: snh-precommit
description: >-
  Diagnoses and resolves pre-commit pipeline failures on WSL Linux, including
  commitlint, Python linters (Ruff, Interrogate), security audits, and 100%
  branch coverage pytest enforcement.
---

# Pre-Commit e Quality Gates (snh-precommit)

Procedimento de diagnóstico e resolução de falhas na esteira de pre-commit e qualidade no WSL Linux.

## Pipeline Crash-First

A esteira de validação é executada no estágio `commit-msg` com política fail-fast (`fail_fast: true`):
1. **Commitlint:** Validação estrita do padrão Conventional Commits em PT-BR.
2. **Python Lint:** Formatação e linting estrito com Ruff (`check` e `format`).
3. **JSON / YAML Lint:** Validação sintática e estrutural de arquivos de configuração.
4. **Validação de Código:** Verificação de docstrings com Interrogate e ausência de código morto com Vulture.
5. **Segurança:** Análise estática com Bandit e auditoria de vulnerabilidades com pip-audit.
6. **Testes e Cobertura:** Execução completa da suíte Pytest exigindo 100% de branch coverage.

## Resolução de Falhas Frequentes

### 1. Rejeição de Mensagem de Commit pelo Commitlint
- **Causa:** Assunto em inglês, ausência de escopo, tipo não reconhecido ou falta de linha em branco antes do corpo.
- **Correção:** Formatar a mensagem no padrão:
  ```text
  tipo(escopo): assunto claro em PT-BR

  Corpo explicativo do motivo e das alteracoes realizadas.
  ```

### 2. Queda de Cobertura de Testes (< 100%)
- **Causa:** Criação de novos caminhos condicionais (`if/else`, `match/case`, tratamento de exceções) sem testes unitários correspondentes.
- **Correção:** Escrever testes cobrindo todas as ramificações em `app/tests/unit/`. Nunca reduzir o threshold de `--cov-fail-under=100`.

### 3. Violação de Limite de Linhas (> 300)
- **Causa:** Arquivo em `app/src/` com mais de 300 linhas de código.
- **Correção:** Extrair responsabilidades para novos módulos coesos ou serviços auxiliares de domínio.
