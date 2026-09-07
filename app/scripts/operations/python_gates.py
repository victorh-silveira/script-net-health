from __future__ import annotations

import ast
import compileall
import shutil
import subprocess
import sys
from pathlib import Path

from gate_runtime import APP_ROOT, REPO_ROOT, SRC_ROOT, exit_if_violations, fail, run_command, run_tool


FORBIDDEN_IMPORTS = {
    "domain": {"infrastructure", "presentation", "application"},
    "application": {"infrastructure", "presentation"},
}


def _module_root(module_name: str) -> str | None:
    top = module_name.split(".", 1)[0]
    if top in {"domain", "application", "infrastructure", "presentation"}:
        return top
    return None


def stage_lint() -> None:
    print("\n>>> Executando: Ruff Check (auto-fix)")
    fix_cmd = [sys.executable, "-m", "ruff", "check", "--fix", "."]
    print(f"Command: {' '.join(fix_cmd)}")
    subprocess.run(fix_cmd, check=True, text=True, cwd=APP_ROOT)
    run_tool("ruff", ["check", "."], "Ruff Check")
    run_tool("ruff", ["format", "."], "Ruff Format")
    run_tool("interrogate", ["-vv", "src"], "Interrogate Docstrings")
    run_tool("vulture", [], "Vulture Dead Code Detection")


def stage_layer_dependencies() -> None:
    print("\n>>> Executando: Verificacao de dependencias entre camadas")
    violations: list[str] = []
    for path in SRC_ROOT.rglob("*.py"):
        relative = path.relative_to(SRC_ROOT)
        if not relative.parts:
            continue
        layer = relative.parts[0]
        if layer not in FORBIDDEN_IMPORTS:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            imported: list[str] = []
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported = [node.module]
            for name in imported:
                target = _module_root(name)
                if target and target in FORBIDDEN_IMPORTS[layer]:
                    violations.append(f"{path}: {layer} importa {name}")
    exit_if_violations("Violacao de dependencias entre camadas:", violations)
    print("[OK] Regras de dependencia entre camadas respeitadas.")


def stage_structure(max_lines: int = 300) -> None:
    print(f"\n>>> Executando: Verificacao Estrutural (Max {max_lines} linhas)")
    violations: list[str] = []
    for path in APP_ROOT.rglob("*.py"):
        if ".venv" in path.parts or ".venv-win" in path.parts or "venv" in path.parts or ".git" in path.parts:
            continue
        count = len(path.read_text(encoding="utf-8").splitlines())
        if count > max_lines:
            violations.append(f"{path}: {count} linhas")
    exit_if_violations("Violacao de limite de linhas encontrada:", violations)
    print(f"[OK] Todos os arquivos estao abaixo de {max_lines} linhas.")


def stage_validate() -> None:
    run_tool("mypy", ["--config-file", "pyproject.toml"], "Mypy Strict")
    stage_layer_dependencies()
    stage_structure()


def stage_test(fail_under: int = 100) -> None:
    run_tool("coverage", ["run", "--branch", "-m", "pytest"], "Pytest execution (branch coverage)")
    run_tool("coverage", ["report", f"--fail-under={fail_under}"], f"Coverage report (min {fail_under}%)")


def stage_security() -> None:
    ignore_args: list[str] = []
    run_tool("bandit", ["-r", "src", "-c", "pyproject.toml"], "Bandit Security Scan")
    run_tool("pip_audit", ignore_args, "Pip-audit Vulnerability Scan")
    gitleaks = shutil.which("gitleaks")
    if gitleaks is None:
        print("[OK] Gitleaks nao encontrado no PATH; pulado")
        return
    run_command(
        [gitleaks, "detect", "--source", str(REPO_ROOT), "--verbose", "--redact"],
        "Gitleaks",
        cwd=REPO_ROOT,
    )


def stage_build() -> None:
    print("\n>>> Executando: compileall")
    targets = [SRC_ROOT, REPO_ROOT / "run.py", APP_ROOT / "run.py"]
    for target in targets:
        ok = (
            compileall.compile_dir(str(target), quiet=1)
            if target.is_dir()
            else compileall.compile_file(str(target), quiet=1)
        )
        if not ok:
            fail(f"[ERRO] Falha no compileall: {target}")
    print("[OK] compileall concluido.")


def stage_clean() -> None:
    print("\n>>> Running: Limpeza de lixo e caches")

    def safe_remove(path: Path) -> None:
        try:
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removido diretorio: {path}")
            elif path.is_file():
                path.unlink()
                print(f"Removido arquivo: {path}")
        except OSError as exc:
            print(f"Erro ao remover {path}: {exc}")

    for scan_root in (APP_ROOT, REPO_ROOT):
        for path in scan_root.rglob("__pycache__"):
            if path.is_dir():
                safe_remove(path)
        for ext in ("*.pyc", "*.pyo", "*.pyd"):
            for path in scan_root.rglob(ext):
                if path.is_file():
                    safe_remove(path)
    for name in (".pytest_cache", ".ruff_cache", ".coverage", "htmlcov", "dist", "build", ".mypy_cache"):
        candidate = APP_ROOT / name
        if candidate.exists():
            safe_remove(candidate)
    for name in ("data", "logs"):
        candidate = REPO_ROOT / name
        if candidate.exists():
            safe_remove(candidate)
