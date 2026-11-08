---
name: snh-settings-change
description: >-
  Procedure for safely adding, modifying, or deprecating SNH_* operational
  settings across .env.example, the Settings loader entity, and automated tests.
---

# Mudança de Configurações Operacionais (snh-settings-change)

Procedimento seguro para criar, alterar ou remover variáveis de ambiente no `script-net-health`.

## Fluxo de Implementação de Nova Configuração

1. **Atualizar `.env.example`:**
   - Adicionar a nova chave com o prefixo obrigatório `SNH_`.
   - Incluir comentário explicativo e valor padrão seguro para execução imediata.

2. **Atualizar a Entidade `Settings` (`app/src/infrastructure/config/settings.py`):**
   - Declarar o campo na dataclass com type hint estrito (`str`, `int`, `bool`, etc.).
   - Mapear a leitura em `Settings.from_env()`, implementando tratamento de erro, parsing e valor de fallback.

3. **Atualizar Testes Unitários (`app/tests/unit/infrastructure/config/test_settings.py`):**
   - Testar o valor padrão quando a variável não está definida no ambiente.
   - Testar o parsing correto do valor informado.
   - Testar a resiliência contra valores inválidos.

4. **Atualizar a Documentação:**
   - Adicionar a nova variável na tabela de SSOT em `docs/engineering-settings-ssot.md`.
