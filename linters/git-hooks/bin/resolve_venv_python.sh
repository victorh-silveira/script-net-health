#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

if [ -x "${ROOT}/.venv/bin/python" ]; then
  echo "${ROOT}/.venv/bin/python"
  exit 0
fi

if [ -x "${ROOT}/.venv/Scripts/python.exe" ]; then
  echo "${ROOT}/.venv/Scripts/python.exe"
  exit 0
fi

if command -v python3 >/dev/null 2>&1; then
  command -v python3
  exit 0
fi

if command -v python >/dev/null 2>&1; then
  command -v python
  exit 0
fi

echo "Python do projeto nao encontrado. Crie .venv e rode: make app-install" >&2
exit 1
