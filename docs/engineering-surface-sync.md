# Sincronização de Superfícies

Procedimento obrigatório de fechamento de alterações e garantia de integridade entre documentação, regras e código.

## Checklist de Superfícies

Sempre que uma alteração envolver contratos arquiteturais, configurações operacionais ou esteiras de qualidade:

1. **Documentação Técnica:**
   - Atualizar os documentos pertinentes em `docs/`.
   - Manter `README.md` alinhado caso a interface ou modo de uso tenha sido alterado.

2. **Matriz de Cobertura de Agentes:**
   - Garantir que `docs/agent-coverage.md` liste com exatidão todas as regras e skills ativas no projeto.

3. **Ponto de Entrada Canônico:**
   - Atualizar `AGENTS.md` se houver mudanças em personas, escopos de commit ou roteamento de tarefas.

4. **Harness Canônico (.agents/):**
   - Assegurar que regras em `.agents/rules/`, skills em `.agents/skills/` e manifestos (`agents.json`, `mcp.json`) estejam íntegros e genéricos para qualquer IA.

5. **Execução de Quality Gates:**
   - Executar no WSL Linux: `make app-lint` e `make app-test`.
   - Verificar ausência de arquivos temporários com `git status`.
