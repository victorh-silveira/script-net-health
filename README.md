# Script Net Health

Copilot NetOps hexagonal: coleta evidencias no **host Windows** (PowerShell) e imprime diagnostico BOTTOM-UP (LAN/WAN, 4 camadas TCP/IP). Qualidade, Make, pre-commit, Git e GitHub rodam no **WSL**.

Contrato de engenharia: [`prompt-model.md`](prompt-model.md).

## Requisitos

- Windows 10/11 (pilha de rede do host)
- PowerShell + Python 3.13 (`py -3.13`) para o app
- WSL Linux para Make, hooks, lint, testes e git
- Node.js/`npx` no WSL para commitlint
- Binarios Windows: `ipconfig`, `ping`, `arp`, `route`, `netstat`, `nslookup` (opcional `tracert`)

## Setup

Qualidade (WSL):

```bash
python3.13 -m venv .venv
source .venv/bin/activate
make app-setup
```

Runtime do diagnostico (PowerShell):

```powershell
py -3.13 -m venv .venv-win
.\.venv-win\Scripts\python.exe -m pip install -r app\requirements.txt
```

Copie `.env.example` para `.env` e ajuste se necessario. Nunca commite `.env`. Dois venvs: `.venv` (WSL/QA) e `.venv-win` (Windows/app).

## Comandos

| Onde | Comando | Efeito |
|------|---------|--------|
| PowerShell | `py -3.13 run.py` | Diagnostico NetOps no host Windows |
| PowerShell | `py -3.13 run.py --status` | Status da aplicacao |
| WSL | `make help` | Menu de qualidade |
| WSL | `make app-lint` | Ruff, Interrogate, Vulture, mypy, camadas, 300 linhas, JSON/YAML (`--config-text`) |
| WSL | `make app-test` | pytest + coverage branch 100% |
| WSL | `make app-security` | Bandit + pip-audit (+ Gitleaks se no PATH) |
| WSL | `make app-clean` | Caches locais |
| WSL | `make app-pre-commit` | Instala hook `commit-msg` (`linters/git-hooks/install.sh`) |
| WSL | `make app-pre-commit-run` | Hooks crash-first |

`make app-run` so lembra o caminho PowerShell; nao executa probes no WSL.

## Arquitetura

Ver [`docs/arquitetura.md`](docs/arquitetura.md) e [`AGENTS.md`](AGENTS.md).
