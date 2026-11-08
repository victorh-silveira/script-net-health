---
name: snh-repo-hygiene
description: >-
  Audits and eliminates dead code, phantom folders, orphaned imports, and local
  temporary artifacts from script-net-health based on concrete evidence.
---

# Higiene do Repositório (snh-repo-hygiene)

Procedimento mandatório de higienização contínua do repositório para evitar acúmulo de lixo técnico.

## Diretrizes de Limpeza com Evidências

1. **Detecção de Código Morto:**
   - Execute análise com Vulture e Ruff:
     ```bash
     wsl python3 -m ruff check --select F401,F841 .
     ```
   - Elimine funções, métodos ou variáveis não referenciadas após confirmação via busca global.

2. **Detecção e Remoção de Diretórios Fantasmas:**
   - Verifique a árvore em busca de pastas vazias ou sem arquivos rastreados no Git:
     ```powershell
     Get-ChildItem -Directory -Recurse | Where-Object { (Get-ChildItem -Path $_.FullName -Recurse -File).Count -eq 0 }
     ```
   - Remova pastas residuais imediatemente.

3. **Limpeza de Artefatos Locais:**
   - Execute o stage de limpeza:
     ```bash
     wsl python3 app/scripts/operations/clean_workspace.py --stage clean
     ```
   - Garanta que arquivos `.coverage*`, `*.log`, `__pycache__` e caches de ferramentas não sejam cometidos no Git.
