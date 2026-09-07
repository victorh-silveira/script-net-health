"""Testes de integracao de Settings e dotenv."""

from pathlib import Path

import pytest

from infrastructure.config.settings import Settings
from presentation.cli import bootstrap


@pytest.mark.integration
def test_settings_dotenv_override_false_keeps_process_env(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("SNH_DISABLE_DOTENV", raising=False)
    monkeypatch.setenv("SNH_APP_NAME", "already-set")
    env_file = tmp_path / ".env"
    env_file.write_text("SNH_APP_NAME=from-file\nSNH_LOG_LEVEL=debug\n", encoding="utf-8")

    settings = Settings.from_env(tmp_path)
    assert settings.app_name == "already-set"
    assert settings.log_level == "DEBUG"


@pytest.mark.integration
def test_bootstrap_end_to_end(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("SNH_DISABLE_DOTENV", "1")
    monkeypatch.setenv("SNH_APP_NAME", "script-net-health")
    monkeypatch.setenv("SNH_LOG_LEVEL", "INFO")
    monkeypatch.setattr("sys.argv", ["snh", "--status"])

    bootstrap.bootstrap(tmp_path)
    output = capsys.readouterr().out
    assert "script-net-health 0.0.0 ready" in output
