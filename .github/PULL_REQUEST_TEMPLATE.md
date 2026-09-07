## Summary

O que muda e por que (1-3 bullets).

## Crivo de higiene

| Vetor | OK? | Notas |
|-------|-----|--------|
| Dead code | | sem codigo morto; cobertura branch 100% |
| Domain puro | | `domain`/`application` sem IO nem logs |
| Settings | | knobs `SNH_*` em `.env.example` + loader |
| Probes | | allowlist sem `shell=True`; stdout no relatorio, nao em INFO |

## Test plan

- [ ] Pre-commit WSL verde (`make app-pre-commit-run`)
- [ ] Testes novos/alterados cobrem o contrato mudado
- [ ] Surface-sync se docs/rules/skills/AGENTS tocados
