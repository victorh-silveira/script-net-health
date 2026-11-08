# AGENTS.md — Script Net Health

Ponto de entrada canônico para agentes de IA neste repositório.

## Idioma e ambiente de execução

- Respostas, documentações e mensagens de commit em **PT-BR**
- **Execução da aplicação e probes:** PowerShell no host Windows (`py -3.13 run.py`)
- **Qualidade, linters e git:** WSL Linux (`make`, `pre-commit`, `commitlint`, GitHub Actions)
- **Runtime da aplicação:** Python 3.13 (`.venv-win` no Windows, `.venv` no WSL). Sem Conda e sem Docker
- **Arquitetura:** Domain-Driven Design (DDD) puro e Arquitetura Hexagonal (Ports & Adapters)
- **Estilo:** Sem emojis em código, logs, commits ou documentação técnica
- **Comentários:** Sem comentários explicativos inline no código (usar apenas docstrings completas)

## Personas e papéis operacionais

1. **NetOps Senior Copilot**:
   - Diagnóstico determinístico de rede local (LAN) e remota (WAN / Serviço)
   - Abordagem BOTTOM-UP seguindo as 4 camadas do modelo TCP/IP (Link, Internet, Transporte, Aplicação)
   - Execução de probes Windows via allowlist sem shell arbitrário
   - Geração de relatório estruturado em 5 seções obrigatórias
   - Em caminhos sem falhas, o diagnóstico classifica a camada afetada como **Nenhuma**

2. **Hexagonal Architect**:
   - Manutenção estrita da separação de camadas: `domain`, `application`, `infrastructure`, `presentation`
   - O domínio é 100% puro: proibido IO, sockets, chamadas a subprocess e loggers em entidades ou use cases
   - Portas são contratos formais (`Protocol`) em `application/ports`
   - Adaptadores implementam as portas em `infrastructure/adapters`
   - Composition root centralizado exclusivamente em `presentation/cli/bootstrap.py`

3. **Quality Gatekeeper**:
   - Cobertura de testes mantida em **100%** de branch em toda a aplicação
   - Testes unitários estruturados por camada em `app/tests/unit/`
   - Isolamento de variáveis de ambiente com `SNH_DISABLE_DOTENV=1`
   - Limite estrito de **300 linhas** por arquivo em `app/src/`
   - Conventional Commits em PT-BR com escopos válidos

## Proibições globais

- Importar `infrastructure` ou `presentation` a partir de `domain` ou `application`
- Inserir emissão de logs em entidades de domínio ou em casos de uso
- Fazer dump de segredos, tokens ou transcrições completas de probes em nível INFO de log
- Invocar subprocessos com `shell=True` ou com executáveis fora da allowlist
- Arquivos de código em `app/src/**/*.py` excedendo 300 linhas
- Cobertura de testes inferior a 100% de branch
- Cometer `.env` ou chaves de acesso ao controle de versão
- Assuntos de commit em inglês ou sem escopo/corpo obrigatórios
- Afrouxar configurações de linters ou gates para contornar falhas

## SSOT de configuração e agentes

- **Configurações operacionais:** `.env` e `.env.example` com prefixo obrigatório `SNH_` (`docs/engineering-settings-ssot.md`)
- **Manifesto canônico de agentes:** [`.agents/agents.json`](.agents/agents.json)
- **Rules canônicas:** [`.agents/rules/`](.agents/rules/) (espelhadas em [`.cursor/rules/`](.cursor/rules/))
- **Skills canônicas:** [`.agents/skills/`](.agents/skills/) (espelhadas em [`.cursor/skills/`](.cursor/skills/))
- **Matriz de cobertura 100%:** [`docs/agent-coverage.md`](docs/agent-coverage.md)
- **Contrato de engenharia:** [`prompt-model.md`](prompt-model.md)

## Escopos commitlint

Escopos permitidos: `all`, `app`, `cli`, `config`, `deps`, `domain`, `infra`, `linters`, `repo`, `scripts`, `test`.

Formato do commit:
```text
tipo(escopo): assunto descritivo em PT-BR

Corpo detalhado explicando o motivo da alteracao e impactos operacionais.
```

Tipos permitidos: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `qa`, `refactor`, `revert`, `style`, `test`.

## Roteamento de leitura por tarefa

| Tarefa pretendida | Documentos e skills prioritários |
| :--- | :--- |
| Qualquer alteração no projeto | [`AGENTS.md`](AGENTS.md) + [`docs/agent-coverage.md`](docs/agent-coverage.md) |
| Diagnóstico e operação de probes | [`docs/arquitetura.md`](docs/arquitetura.md) + skill `snh-ops-runbook` |
| Qualidade e testes (WSL) | [`docs/engineering-standards.md`](docs/engineering-standards.md) + skill `snh-precommit` |
| Fechamento de mudanças e sync | [`docs/engineering-surface-sync.md`](docs/engineering-surface-sync.md) + skill `snh-surface-sync` |
| Domínio, entidades e use cases | [`docs/arquitetura.md`](docs/arquitetura.md) + [`docs/structure.md`](docs/structure.md) |
| Observabilidade e logging | [`docs/engineering-observability.md`](docs/engineering-observability.md) |
| Configuração e variáveis SNH_* | [`docs/engineering-settings-ssot.md`](docs/engineering-settings-ssot.md) + skill `snh-settings-change` |
| Dependências Python | [`docs/engineering-python-deps.md`](docs/engineering-python-deps.md) + skill `snh-python-deps` |
| Higiene e código morto | [`docs/engineering-repo-hygiene.md`](docs/engineering-repo-hygiene.md) + skill `snh-repo-hygiene` |
| CI/CD e workflows do GitHub | [`.github/README.md`](.github/README.md) + [`docs/engineering-standards.md`](docs/engineering-standards.md) |
| Contrato e scaffold de engenharia | [`prompt-model.md`](prompt-model.md) + skill `snh-surface-sync` |
