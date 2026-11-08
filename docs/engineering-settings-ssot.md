# SSOT de Configurações Operacionais

Especificação da única fonte de verdade (SSOT) para parâmetros de runtime do **Script Net Health**.

## Variáveis de Ambiente Suportadas

Todas as variáveis de configuração utilizam obrigatoriamente o prefixo `SNH_`.

| Variável | Tipo | Valor Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `SNH_APP_NAME` | `str` | `"script-net-health"` | Nome identificador da aplicação |
| `SNH_LOG_LEVEL` | `str` | `"INFO"` | Nível de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `SNH_TARGET_HOST` | `str` | `"1.1.1.1"` | Alvo WAN padrão para testes de conectividade ICMP/TCP |
| `SNH_TARGET_PORT` | `int` | `443` | Porta padrão para teste de conexão TCP direta |
| `SNH_COMMAND_TIMEOUT_SECONDS` | `int` | `10` | Timeout máximo em segundos para execução de probes comuns |
| `SNH_TRACERT_TIMEOUT_SECONDS` | `int` | `30` | Timeout dedicado para o utilitário `tracert` |
| `SNH_ENABLE_TRACEROUTE` | `bool` | `False` | Habilita a execução do rastreamento de rota completo |
| `SNH_ENABLE_SPEEDTEST` | `bool` | `False` | Habilita a medição de throughput via requisições HTTP |
| `SNH_THROUGHPUT_URLS` | `list[str]` | `[]` | URLs customizadas para medição de download/upload |
| `SNH_DISABLE_DOTENV` | `bool` | `False` | Desativa o carregamento de `.env` para isolamento de testes |

## Regras de Gestão

1. Toda nova variável adicionada em `Settings` deve ser obrigatoriamente registrada neste documento e no arquivo `.env.example`.
2. Arquivos `.env` locais contendo parâmetros específicos do desenvolvedor nunca devem ser comitados no controle de versão.
