---
name: snh-surface-sync
description: >-
  Finalizes changes by synchronizing docs, rules, skills, AGENTS.md, matrix,
  mirroring to .cursor/, and validating all quality gates on WSL before commit.
---

# Sincronização de Superfícies (snh-surface-sync)

Checklist e protocolo obrigatório de fechamento de qualquer alteração no repositório.

## Checklist de Fechamento

Antes de cometer alterações ou abrir Pull Request:

1. **Mapeamento de Superfícies Afetadas:**
   - Identifique quais arquivos foram alterados e localize a respectiva linha na matriz em `docs/agent-coverage.md`.

2. **Sincronização de Documentação Técnica:**
   - Atualize os arquivos correspondentes em `docs/` se houver mudança em contratos, configurações ou arquitetura.

3. **Paridade Canônica e Ponte (.agents/ e .cursor/):**
   - Garanta que qualquer criação ou modificação em `.agents/rules/` e `.agents/skills/` seja espelhada para `.cursor/rules/` e `.cursor/skills/`.

4. **Atualização da Matriz de Cobertura e AGENTS.md:**
   - Certifique-se de que todas as novas rules e skills estão registradas em `docs/agent-coverage.md` e na tabela de leitura de `AGENTS.md`.

5. **Execução de Quality Gates no WSL Linux:**
   ```bash
   make app-lint
   make app-test
   make app-security
   ```

6. **Compromisso Git:**
   - Mensagem formatada no padrão Conventional Commits em PT-BR com tipo, escopo válido e corpo explicativo.
