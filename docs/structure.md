# Estrutura do Repositório

Inventário técnico e estruturação de pastas do projeto **Script Net Health**.

## Árvore do Repositório

```text
.
├── .agents/                      # Harness canônico de agentes de IA
│   ├── rules/                    # 10 rules operacionais canônicas
│   ├── skills/                   # 6 skills operacionais canônicas
│   ├── agents.json               # Catálogo de personas e responsabilidades
│   └── mcp.json                  # Manifesto canônico de MCP
├── .github/                      # Workflows de CI/CD e automação do GitHub Actions
│   ├── actions/
│   ├── templates/
│   └── workflows/
├── .vscode/                      # Configurações do VSCode / IDE
├── app/                          # Código fonte da aplicação e testes
│   ├── scripts/operations/       # Scripts operacionais de validação e limpeza
│   ├── src/                      # Código de produção (DDD Hexagonal)
│   │   ├── domain/               # Entidades e serviços puros (sem IO/logs)
│   │   ├── application/          # Use cases e portas (Protocol)
│   │   ├── infrastructure/       # Adaptadores de rede Windows, config e logs
│   │   └── presentation/         # CLI e Composition Root (bootstrap.py)
│   ├── tests/                    # Suíte unificada de testes (100% branch coverage)
│   │   ├── unit/                 # Testes unitários isolados por camada
│   │   └── integration/          # Testes integrados de CLI e settings
│   ├── pyproject.toml            # Configurações de ferramentas de QA
│   ├── requirements.txt          # Dependências de produção
│   ├── requirements-dev.txt      # Dependências de desenvolvimento e teste
│   └── run.py                    # Entrypoint interno da aplicação
├── docs/                         # Documentação técnica e matriz de cobertura
├── linters/                      # Configuração de commitlint e git hooks
├── .env.example                  # Template com todas as variáveis SNH_*
├── .gitignore                    # Regras estritas de exclusão do Git
├── AGENTS.md                     # Ponto de entrada canônico para agentes
├── Makefile                      # Orquestrador de tarefas no WSL Linux
├── prompt-model.md               # Contrato canônico de engenharia
├── README.md                     # Visão geral e guia rápido do projeto
└── run.py                        # Entrypoint oficial na raiz do repositório
```

## Regras de Dependência entre Camadas

| Camada | Pode Depender De | Proibido Depender De |
| :--- | :--- | :--- |
| `domain` | Nenhuma (Apenas tipos padrão Python) | `application`, `infrastructure`, `presentation` |
| `application` | `domain` | `infrastructure`, `presentation` |
| `infrastructure` | `application`, `domain` | `presentation` |
| `presentation` | `application`, `domain`, `infrastructure` | Nenhuma |
