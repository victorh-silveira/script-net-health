"""Garante que a matriz agent-coverage aponta para arquivos existentes."""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
MATRIX = REPO_ROOT / "docs" / "agent-coverage.md"
RULES_DIR = REPO_ROOT / ".cursor" / "rules"
SKILLS_DIR = REPO_ROOT / ".cursor" / "skills"


@pytest.mark.unit
def test_agent_coverage_matrix_files_exist():
    text = MATRIX.read_text(encoding="utf-8")
    rules = set(re.findall(r"`(snh-[a-z0-9-]+\.mdc)`", text))
    skills = set(re.findall(r"`(snh-[a-z0-9-]+)`", text))
    skills = {name for name in skills if not name.endswith(".mdc")}

    assert rules, "matriz deve listar rules"
    assert skills, "matriz deve listar skills"

    missing_rules = sorted(name for name in rules if not (RULES_DIR / name).is_file())
    missing_skills = sorted(name for name in skills if not (SKILLS_DIR / name / "SKILL.md").is_file())

    assert not missing_rules, f"rules ausentes: {missing_rules}"
    assert not missing_skills, f"skills ausentes: {missing_skills}"


@pytest.mark.unit
def test_all_cursor_rules_are_always_apply_true():
    files = sorted(RULES_DIR.glob("*.mdc"))
    assert files, "deve haver rules em .cursor/rules"
    for path in files:
        content = path.read_text(encoding="utf-8")
        assert "alwaysApply: true" in content, f"{path.name} sem alwaysApply: true"


@pytest.mark.unit
def test_all_skill_directories_have_skill_md():
    dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    assert dirs, "deve haver skills em .cursor/skills"
    for path in dirs:
        assert (path / "SKILL.md").is_file(), f"faltando SKILL.md em {path.name}"
