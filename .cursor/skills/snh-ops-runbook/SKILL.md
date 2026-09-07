---
name: snh-ops-runbook
description: >-
  Operates script-net-health: diagnose on Windows PowerShell, quality gates on
  WSL. Use when setting up the env, running NetOps diagnose, --status, make
  help, app-setup, ping/tracert probes, or two venvs.
---

# Ops runbook

## Diagnostico (PowerShell / host Windows)

```powershell
py -3.13 run.py
py -3.13 run.py --status
.\.venv-win\Scripts\python.exe run.py
```

Probes: allowlist `ipconfig`, `ping`, `arp`, `route`, `netstat`, `nslookup`, `tracert`. Sem `shell=True`. Tracert off por default (`SNH_ENABLE_TRACEROUTE=0`); timeout proprio `SNH_TRACERT_TIMEOUT_SECONDS`. TCP 443 no alvo WAN. Throughput urllib (Cloudflare se URLs vazias) via `SNH_ENABLE_SPEEDTEST`. Stdout integral no relatorio, nao no log INFO.

## Qualidade (WSL)

```bash
make help
make app-setup
make app-pre-commit
make app-lint && make app-test && make app-security
make app-pre-commit-run
```

`make app-pre-commit` chama `linters/git-hooks/install.sh` (wrapper `commit-msg` no WSL). Python do Make: `.venv/bin/python` se existir. Nao usar `make app-run` para diagnosticar (mede o WSL, nao a NIC Windows).

CI/CD: push/PR em `master` (`.github/README.md`). Sem jobs Docker/Shell.

## Docs

`README.md`, `docs/engineering-standards.md`, rule `snh-scripts`
