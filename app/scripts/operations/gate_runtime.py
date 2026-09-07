from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = APP_ROOT.parent
SRC_ROOT = APP_ROOT / "src"

STAGES = ("lint", "validate", "security", "test", "build", "clean", "pytest")
AREAS = ("python",)
AREA_STAGES = {
    "python": {"lint", "validate", "security", "test", "build", "clean", "pytest"},
}


def use_app_cwd() -> None:
    os.chdir(APP_ROOT)


def fail(message: str, code: int = 1) -> None:
    print(message)
    sys.exit(code)


def run_command(command: list[str], description: str, cwd: Path | None = None) -> None:
    print(f"\n>>> Executando: {description}")
    print(f"Command: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, text=True, cwd=cwd)
    except subprocess.CalledProcessError as exc:
        print(f"Erro durante {description}: {exc}")
        sys.exit(exc.returncode)


def run_tool(module: str, args: list[str], description: str) -> None:
    run_command([sys.executable, "-m", module, *args], description, cwd=APP_ROOT)


def exit_if_violations(header: str, violations: list[str]) -> None:
    if not violations:
        return
    print(f"\n[ERRO] {header}")
    for item in violations:
        print(f"  - {item}")
    sys.exit(1)
