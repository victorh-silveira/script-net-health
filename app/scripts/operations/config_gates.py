from __future__ import annotations

import json
import sys
from collections.abc import Iterable
from pathlib import Path

import yaml
from gate_runtime import REPO_ROOT, exit_if_violations, fail, run_command


SKIP_YAML_PARTS = {".venv", ".venv-win", "venv", "node_modules", "templates"}


def _iter_yaml_files() -> list[Path]:
    found: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".yml", ".yaml"}:
            continue
        if any(part in SKIP_YAML_PARTS for part in path.parts):
            continue
        found.append(path)
    extra = REPO_ROOT / ".pre-commit-config.yaml"
    if extra.is_file() and extra not in found:
        found.append(extra)
    return sorted(found)


def _iter_json_files() -> list[Path]:
    return [
        REPO_ROOT / ".vscode" / "settings.json",
    ]


def _missing(paths: Iterable[Path]) -> list[str]:
    return [str(path) for path in paths if not path.is_file()]


def stage_yaml_lint() -> None:
    files = _iter_yaml_files()
    if not files:
        fail("[ERRO] Nenhum YAML encontrado para lint")
    run_command(
        [sys.executable, "-m", "yamllint", *[str(path) for path in files]],
        "YAML Lint",
        cwd=REPO_ROOT,
    )


def stage_yaml_validate() -> None:
    violations: list[str] = []
    for path in _iter_yaml_files():
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            violations.append(f"{path}: {exc}")
    exit_if_violations("YAML invalido (safe_load):", violations)
    print("[OK] YAML validado com yaml.safe_load.")


def stage_json_lint() -> None:
    missing = _missing(_iter_json_files())
    exit_if_violations("JSON ausente:", missing)
    violations: list[str] = []
    for path in _iter_json_files():
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            violations.append(f"{path}: {exc}")
    exit_if_violations("JSON invalido:", violations)
    print("[OK] JSON parseado.")


def stage_json_validate() -> None:
    stage_json_lint()
    settings = json.loads((REPO_ROOT / ".vscode" / "settings.json").read_text(encoding="utf-8"))
    violations: list[str] = []
    if not isinstance(settings, dict):
        violations.append(".vscode/settings.json nao e objeto")
    exit_if_violations("JSON invalido estruturalmente:", violations)
    print("[OK] JSON estruturalmente valido.")


def stage_json_test() -> None:
    stage_json_validate()
    settings = json.loads((REPO_ROOT / ".vscode" / "settings.json").read_text(encoding="utf-8"))
    violations: list[str] = []
    paths = settings.get("python.analysis.extraPaths")
    if not isinstance(paths, list) or "app/src" not in paths:
        violations.append(".vscode/settings.json sem python.analysis.extraPaths contendo app/src")
    if settings.get("python.testing.pytestEnabled") is not True:
        violations.append(".vscode/settings.json sem python.testing.pytestEnabled")
    exit_if_violations("JSON testes:", violations)
    print("[OK] JSON testes: extraPaths e pytest.")


def _run_json(stage: str) -> None:
    if stage == "lint":
        stage_json_lint()
        return
    if stage == "validate":
        stage_json_validate()
        return
    if stage == "test":
        stage_json_test()
        return
    print(f"[OK] JSON estagio {stage} coberto por gitleaks")


def _run_yaml(stage: str) -> None:
    if stage == "lint":
        stage_yaml_lint()
        return
    if stage == "validate":
        stage_yaml_validate()
        return
    print(f"[OK] YAML estagio {stage} coberto por gitleaks")


def run_config_text(stage: str, kind: str = "all") -> None:
    if kind not in {"all", "json", "yaml"}:
        fail(f"[ERRO] config-text desconhecido: {kind}")
    if kind in {"all", "json"}:
        _run_json(stage)
    if kind in {"all", "yaml"}:
        _run_yaml(stage)
