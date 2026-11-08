# Prompt-Modelo de Engenharia — Script Net Health

Contrato canônico de engenharia de software para o projeto **Script Net Health**. Este documento serve como especificação formal para agentes de IA e desenvolvedores seniores manterem a integridade arquitetural, padrões de código e qualidade do ecossistema.

## 1. Missão e Universo do Projeto

O **Script Net Health** é um utilitário CLI profissional de diagnóstico de rede, construído em Python 3.13, voltado para ambientes Windows operados por analistas NetOps.
Sua finalidade é coletar probes de conectividade local e remota sem shell arbitrário, processar evidências brutas de forma determinística e sintetizar um relatório estruturado em 5 seções, isolando falhas entre LAN, WAN e Serviços de acordo com as 4 camadas do modelo TCP/IP (RFC 1122).

## 2. Invariantes de Arquitetura (DDD Hexagonal)

O projeto segue estritamente a separação em camadas concêntricas:

```text
presentation/   --> CLI, parsing de argumentos, formatação de saída e Composition Root
application/    --> Casos de uso (orquestração) e Portas (Protocol)
infrastructure/ --> Adaptadores concretos de sistema (probes, clock, config, logs)
domain/         --> Entidades puras, regras de negócio e cálculo de diagnóstico
```

### Regras Mandatórias de Dependência

1. **Pureza do Domínio (`domain/`):**
   - Zero dependência externa. Proibido importar `infrastructure`, `presentation` ou módulos de IO (`subprocess`, `socket`, `urllib`).
   - Proibido instanciar ou emitir logs em entidades ou use cases. Erros de negócio são modelados como exceções em `domain/exceptions.py`.
   - O diagnóstico classifica a camada afetada (Link, Internet, Transporte, Aplicação) ou define explicitamente como **Nenhuma** em caso de rede saudável.

2. **Portas e Casos de Uso (`application/`):**
   - Portas são interfaces puras (`typing.Protocol`) localizadas em `application/ports/`.
   - Casos de uso recebem portas no construtor via injeção de dependência e nunca instanciam adaptadores concretos.

3. **Adaptadores de Borda (`infrastructure/`):**
   - Implementam as portas definidas na aplicação.
   - Probes de rede executadas unicamente no host Windows utilizando allowlist estrita (`ipconfig`, `ping`, `arp`, `route`, `netstat`, `nslookup`, `tracert`) com `shell=False`.
   - Configurações centralizadas via `Settings.from_env()`.

4. **Composition Root (`presentation/cli/bootstrap.py`):**
   - Único ponto autorizado a realizar o wiring de adaptadores com casos de uso.

## 3. Padrões de Qualidade e Desenvolvimento (TDD)

1. **Meta de Cobertura 100% de Branch:**
   - Todo o código em `app/src/` deve atingir exatamente 100% de cobertura de testes, incluindo todos os desvios condicionais.
   - Testes unitários estruturados por camada em `app/tests/unit/`.

2. **Isolamento de Ambiente em Testes:**
   - A suíte de testes nunca consome arquivos `.env` locais, aplicando `SNH_DISABLE_DOTENV=1`.

3. **Estilo e Convenções:**
   - Sem emojis em código, mensagens de commit, logs ou documentação técnica.
   - Sem comentários explicativos inline no código: use nomes expressivos e docstrings completas.
   - Limite estrito de 300 linhas de código por arquivo em `app/src/`.

4. **Dual-Environment Operacional:**
   - **Host Windows (PowerShell):** Execução do utilitário e coleta de probes de rede física (`py -3.13 run.py`).
   - **WSL Linux (Bash):** Execução de Makefile, pre-commit, linters (Ruff, Interrogate, Bandit, pip-audit) e suíte de testes.

5. **Conventional Commits em PT-BR:**
   - Commits obrigatórios no formato: `tipo(escopo): assunto em PT-BR` com corpo explicativo.
   - Escopos permitidos: `all`, `app`, `cli`, `config`, `deps`, `domain`, `infra`, `linters`, `repo`, `scripts`, `test`.
