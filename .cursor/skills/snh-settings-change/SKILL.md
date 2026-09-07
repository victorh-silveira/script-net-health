---
name: snh-settings-change
description: >-
  Changes SNH_* environment settings safely (.env.example, Settings loader,
  tests). Use when adding config knobs, changing log level/app name, or the
  user mentions .env, Settings, SNH_DISABLE_DOTENV, or SNH_PROBE_*.
---

# Settings change

## Passos

1. Atualizar `.env.example` (sem segredos)
2. Ajustar `infrastructure/config/settings.py` e testes em `tests/unit/infrastructure/config`
3. Documentar em `docs/engineering-settings-ssot.md`
4. Garantir testes com `SNH_DISABLE_DOTENV=1`
5. Rodar gates

## Docs

`docs/engineering-settings-ssot.md`, rule `snh-settings-ssot`
