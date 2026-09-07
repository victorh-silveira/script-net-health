# Estrutura do repositorio

## Arvore

```text
.
├── app/
│   ├── src/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   ├── services/
│   │   │   └── constants.py
│   │   ├── application/
│   │   │   ├── ports/
│   │   │   └── use_cases/
│   │   ├── infrastructure/
│   │   │   ├── adapters/
│   │   │   ├── config/
│   │   │   └── logging/
│   │   └── presentation/
│   │       ├── cli/
│   │       └── logging/
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── domain/
│   │   │   ├── application/
│   │   │   ├── infrastructure/
│   │   │   ├── presentation/
│   │   │   └── scripts/
│   │   └── integration/
│   ├── scripts/operations/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── snh_paths.py
│   └── run.py
├── docs/
├── linters/
│   ├── commitlint.config.mjs
│   ├── pre-commit-config.yaml
│   └── git-hooks/
│       ├── install.sh
│       ├── commit-msg
│       └── bin/
├── .cursor/
├── Makefile
├── AGENTS.md
├── prompt-model.md
├── README.md
├── .env.example
└── run.py
```

Nao ha `infra/` neste esqueleto.

## Regras de dependencia

| Camada | Pode depender de |
|--------|------------------|
| domain | apenas domain |
| application | domain |
| infrastructure | application, domain |
| presentation | application, domain, infrastructure |

Ports sao contratos (`Protocol`) em `application/ports`. Adapters implementam ports em `infrastructure/adapters`.

Imports limpos (pythonpath = `app/src`):

```python
from domain.entities.network_evidence import NetworkEvidence
from application.use_cases.diagnose_network_health import DiagnoseNetworkHealth
from infrastructure.adapters.windows_probe_collector import WindowsProbeCollector
from presentation.cli.bootstrap import main
```

O gate de validate Python (`clean_workspace.py --area python --stage validate`) falha se `domain`/`application` importarem camadas externas.
