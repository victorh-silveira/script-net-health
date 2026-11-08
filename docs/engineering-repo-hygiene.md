# Higiene do Repositório

Padrões de limpeza e integridade contínua do código fonte no **Script Net Health**.

## Práticas Mandatórias

1. **Eliminação de Código Morto:**
   - Auditoria regular com Vulture e checagem de variáveis e imports não utilizados via Ruff.
   - Qualquer elemento sem uso comprovado deve ser removido sem deixar referências comentadas.

2. **Proibição de Pastas Fantasmas:**
   - Nenhuma pasta vazia deve persistir no repositório.
   - Toda estrutura sob `app/src/` e `app/tests/` deve abrigar módulos ativos com testes correspondentes.

3. **Limpeza de Artefatos Locais:**
   - Manter o repositório livre de relatórios temporários (`.coverage*`, `coverage.xml`), logs de execução e arquivos transitórios.
   - Utilizar o comando `python app/scripts/operations/clean_workspace.py --stage clean` para purgar caches.
