"""Garante que a matriz agent-coverage e estrutura .agents/ e ponte .cursor/ existem."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
MATRIX = REPO_ROOT / "docs" / "agent-coverage.md"
CANONICAL_AGENTS_DIR = REPO_ROOT / ".agents"
CANONICAL_RULES_DIR = CANONICAL_AGENTS_DIR / "rules"
CANONICAL_SKILLS_DIR = CANONICAL_AGENTS_DIR / "skills"
CANONICAL_MCP_JSON = CANONICAL_AGENTS_DIR / "mcp.json"
CANONICAL_AGENTS_JSON = CANONICAL_AGENTS_DIR / "agents.json"

LEGACY_CURSOR_DIR = REPO_ROOT / ".cursor"
LEGACY_RULES_DIR = LEGACY_CURSOR_DIR / "rules"
LEGACY_SKILLS_DIR = LEGACY_CURSOR_DIR / "skills"


@pytest.mark.unit
def test_agent_coverage_matrix_files_exist():
    text = MATRIX.read_text(encoding="utf-8")
    rules = set(re.findall(r"`(snh-[a-z0-9-]+\.mdc)`", text))
    skills = set(re.findall(r"`(snh-[a-z0-9-]+)`", text))
    skills = {name for name in skills if not name.endswith(".mdc")}

    assert rules, "matriz deve listar rules"
    assert skills, "matriz deve listar skills"

    missing_rules = sorted(name for name in rules if not (CANONICAL_RULES_DIR / name).is_file())
    missing_skills = sorted(name for name in skills if not (CANONICAL_SKILLS_DIR / name / "SKILL.md").is_file())

    assert not missing_rules, f"rules canonicas ausentes: {missing_rules}"
    assert not missing_skills, f"skills canonicas ausentes: {missing_skills}"


@pytest.mark.unit
def test_canonical_manifests_exist_and_valid():
    assert CANONICAL_MCP_JSON.is_file(), "mcp.json canonico deve existir em .agents/mcp.json"
    mcp_content = json.loads(CANONICAL_MCP_JSON.read_text(encoding="utf-8"))
    assert isinstance(mcp_content, dict), "mcp.json deve conter um objeto JSON"
    assert "mcpServers" in mcp_content, "mcp.json deve conter a chave mcpServers"

    assert CANONICAL_AGENTS_JSON.is_file(), "agents.json canonico deve existir em .agents/agents.json"
    agents_content = json.loads(CANONICAL_AGENTS_JSON.read_text(encoding="utf-8"))
    assert isinstance(agents_content, dict), "agents.json deve conter um objeto JSON"
    assert "agents" in agents_content, "agents.json deve conter a lista de agents"
    assert len(agents_content["agents"]) >= 3, "deve conter pelo menos 3 personas catalogadas"


@pytest.mark.unit
def test_all_rules_are_always_apply_true():
    files = sorted(CANONICAL_RULES_DIR.glob("*.mdc"))
    assert files, "deve haver rules em .agents/rules"
    for path in files:
        content = path.read_text(encoding="utf-8")
        assert "alwaysApply: true" in content, f"{path.name} sem alwaysApply: true"


@pytest.mark.unit
def test_all_skill_directories_have_skill_md():
    dirs = sorted(p for p in CANONICAL_SKILLS_DIR.iterdir() if p.is_dir())
    assert dirs, "deve haver skills em .agents/skills"
    for path in dirs:
        assert (path / "SKILL.md").is_file(), f"faltando SKILL.md em {path.name}"


@pytest.mark.unit
def test_cursor_backward_compatibility_bridge():
    assert LEGACY_RULES_DIR.is_dir(), ".cursor/rules deve existir para retrocompatibilidade"
    assert LEGACY_SKILLS_DIR.is_dir(), ".cursor/skills deve existir para retrocompatibilidade"

    canonical_rules = {p.name for p in CANONICAL_RULES_DIR.glob("*.mdc")}
    cursor_rules = {p.name for p in LEGACY_RULES_DIR.glob("*.mdc")}
    assert canonical_rules == cursor_rules, "ponte .cursor/rules deve espelhar .agents/rules"

    canonical_skills = {p.name for p in CANONICAL_SKILLS_DIR.iterdir() if p.is_dir()}
    cursor_skills = {p.name for p in LEGACY_SKILLS_DIR.iterdir() if p.is_dir()}
    assert canonical_skills == cursor_skills, "ponte .cursor/skills deve espelhar .agents/skills"
