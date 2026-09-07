from __future__ import annotations

import json
import subprocess

import pytest
from gate_runtime import REPO_ROOT


HOOKS = REPO_ROOT / "linters" / "git-hooks"
INSTALL = HOOKS / "install.sh"
COMMIT_MSG = HOOKS / "commit-msg"
EARLY = HOOKS / "bin" / "commitlint-early.sh"
RESOLVE = HOOKS / "bin" / "resolve_venv_python.sh"
COMMITLINT = REPO_ROOT / "linters" / "commitlint.config.mjs"
MAKEFILE = REPO_ROOT / "Makefile"


@pytest.mark.unit
def test_git_hook_scripts_exist():
    for path in (INSTALL, COMMIT_MSG, EARLY, RESOLVE, HOOKS / "bin" / "python"):
        assert path.is_file(), f"ausente: {path}"


@pytest.mark.unit
def test_install_sh_copies_commit_msg_and_is_valid_bash():
    text = INSTALL.read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env bash")
    assert "commit-msg" in text
    assert "resolve_venv_python.sh" in text
    assert "pre-commit" not in text
    subprocess.run(["bash", "-n", str(INSTALL)], check=True, cwd=REPO_ROOT)


@pytest.mark.unit
def test_commit_msg_wrapper_uses_venv_and_snh_config():
    text = COMMIT_MSG.read_text(encoding="utf-8")
    assert "linters/pre-commit-config.yaml" in text
    assert "resolve_venv_python.sh" in text
    assert "resolve_conda_python.sh" not in text
    subprocess.run(["bash", "-n", str(COMMIT_MSG)], check=True, cwd=REPO_ROOT)
    subprocess.run(["bash", "-n", str(EARLY)], check=True, cwd=REPO_ROOT)
    subprocess.run(["bash", "-n", str(RESOLVE)], check=True, cwd=REPO_ROOT)


@pytest.mark.unit
def test_makefile_installs_hooks_via_install_sh():
    text = MAKEFILE.read_text(encoding="utf-8")
    assert "linters/git-hooks/install.sh" in text
    assert "App" in text
    assert "Qualidade" in text
    assert "--config-text json" in text


@pytest.mark.unit
def test_pre_commit_config_has_config_text_hooks():
    text = (REPO_ROOT / "linters" / "pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "--config-text json" in text
    assert "--config-text yaml" in text
    assert "python-json-test" in text
    assert "stages: [pre-commit]" not in text


@pytest.mark.unit
def test_ci_workflow_triggers_on_master():
    text = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "branches: [master]" in text
    assert "branches: [main]" not in text
    assert "name: CI - Release" in text
    assert "name: CI - Resumo" in text
    assert "name: CI - Workflows" in text
    assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24" in text
    assert "  docker:\n" not in text
    assert "  shell:\n" not in text
    assert "docker: skipped" in text
    assert "shell: skipped" in text


@pytest.mark.unit
def test_releaserc_targets_master():
    payload = json.loads((REPO_ROOT / "linters" / "releaserc.json").read_text(encoding="utf-8"))
    assert payload["branches"] == ["master"]
    changelog = payload["plugins"][2][1]
    git_plugin = payload["plugins"][3][1]
    assert changelog["changelogFile"] == "docs/CHANGELOG.md"
    assert "app/pyproject.toml" in git_plugin["assets"]


@pytest.mark.unit
def test_ci_composite_actions_exist():
    root = REPO_ROOT / ".github" / "actions"
    expected = (
        root / "ci" / "setup-python" / "action.yml",
        root / "ci" / "release" / "action.yml",
        root / "ci" / "sync-tags" / "action.yml",
        root / "ci" / "workflows" / "action.yml",
        root / "shared" / "pipeline-summary" / "action.yml",
    )
    for path in expected:
        assert path.is_file(), f"ausente: {path}"


@pytest.mark.unit
def test_commitlint_requires_scope_and_body():
    text = COMMITLINT.read_text(encoding="utf-8")
    assert '"scope-empty": [2, "never"]' in text
    assert '"body-empty": [2, "never"]' in text
    assert '"body-leading-blank": [2, "always"]' in text
    assert "//" not in text
