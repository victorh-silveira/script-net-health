# GitHub Actions

CI da stack real do script-net-health (Python + Workflows). JSON e YAML nao sao stacks: validam-se em steps `Python | JSON *` e `Python | YAML *`. Actionlint vive em `CI - Workflows`. CD = semantic-release apos CI verde. Sem jobs Docker/Shell (nao ha essas areas no orquestrador).

## Visao (push em `master`)

```mermaid
flowchart LR
  subgraph ci [CI paralelo]
    PY[Python]
    WF[Workflows]
  end
  PY --> R[Release]
  WF --> R
  R --> S[Resumo]
```

| Fase | Job | Steps (formato `Area \| Stage`) |
|------|-----|----------------------------------|
| CI | Python | Lint, JSON/YAML, Validate, Seguranca, Testes, Build |
| CI | Workflows | Lint (actionlint) |
| Release | Release | Tags, Semantic (+ Baseline/Status) |
| Resumo | Resumo | Pipeline (Docker/Shell = skipped) |

Crash-first na stack Python: lint, validate, security, test, build. Jobs por tecnologia; cada stage e um step unico (sem `strategy.matrix`).

## Workflows

| Workflow | Gatilho | Uso |
|----------|---------|-----|
| [ci.yml](workflows/ci.yml) | push/PR `master`, manual | CI Python/Workflows; release no push `master` |

## Composite actions

```text
.github/actions/
├── shared/pipeline-summary/
└── ci/
    ├── setup-python/
    ├── workflows/
    ├── release/
    └── sync-tags/
```

Pre-commit (stage `commit-msg`) e CI usam os mesmos nomes de stage (`Python | Lint`).
