#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="$ROOT/linters/git-hooks"
DEST="$ROOT/.git/hooks"

if [ ! -d "$DEST" ]; then
  echo "Diretorio .git/hooks ausente. Inicialize o repositorio git primeiro." >&2
  exit 1
fi

install -m 755 "$SRC/commit-msg" "$DEST/commit-msg"
chmod +x "$SRC/bin/python" "$SRC/bin/resolve_venv_python.sh"
if [ -f "$SRC/bin/commitlint-early.sh" ]; then
  chmod +x "$SRC/bin/commitlint-early.sh"
fi

echo "Hook commit-msg instalado em .git/hooks"
