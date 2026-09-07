"""Testes do runner allowlisted."""

import subprocess
from unittest.mock import MagicMock

import pytest

from infrastructure.adapters.command_runner import AllowlistedCommandRunner, CommandResult


@pytest.mark.unit
@pytest.mark.infrastructure
def test_runner_skips_unknown_binary():
    result = AllowlistedCommandRunner().run(["rm", "-rf", "/"], timeout=1)
    assert result.skipped is True
    empty = AllowlistedCommandRunner().run([], timeout=1)
    assert empty.skipped is True


@pytest.mark.unit
@pytest.mark.infrastructure
def test_runner_skips_when_which_is_none(monkeypatch):
    monkeypatch.setattr("infrastructure.adapters.command_runner.shutil.which", lambda name: None)
    result = AllowlistedCommandRunner().run(["ipconfig", "/all"], timeout=1)
    assert result.skipped is True


@pytest.mark.unit
@pytest.mark.infrastructure
def test_runner_success(monkeypatch):
    completed = MagicMock(returncode=0, stdout=None, stderr=None)
    monkeypatch.setattr(
        "infrastructure.adapters.command_runner.shutil.which", lambda name: "C:\\Windows\\System32\\ipconfig.exe"
    )
    monkeypatch.setattr("infrastructure.adapters.command_runner.subprocess.run", lambda *a, **k: completed)
    result = AllowlistedCommandRunner().run(["ipconfig", "/all"], timeout=1)
    assert result.skipped is False
    assert result.stdout == ""
    assert result.returncode == 0


@pytest.mark.unit
@pytest.mark.infrastructure
def test_runner_uses_oem_encoding_on_windows(monkeypatch):
    captured: dict[str, object] = {}
    completed = MagicMock(returncode=0, stdout="ok", stderr="")

    def fake_run(*args, **kwargs):
        captured.update(kwargs)
        return completed

    monkeypatch.setattr("infrastructure.adapters.command_runner.sys.platform", "win32")
    monkeypatch.setattr("infrastructure.adapters.command_runner.shutil.which", lambda name: "ping.exe")
    monkeypatch.setattr("infrastructure.adapters.command_runner.subprocess.run", fake_run)
    AllowlistedCommandRunner().run(["ping", "-n", "1", "1.1.1.1"], timeout=1)
    assert captured["encoding"] == "oem"
    assert captured["errors"] == "replace"


@pytest.mark.unit
@pytest.mark.infrastructure
def test_runner_timeout_with_bytes_output(monkeypatch):
    monkeypatch.setattr("infrastructure.adapters.command_runner.shutil.which", lambda name: "/usr/bin/ping")

    def boom(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="ping", timeout=1, output=b"x", stderr=b"y")

    monkeypatch.setattr("infrastructure.adapters.command_runner.subprocess.run", boom)
    result = AllowlistedCommandRunner().run(["ping", "-n", "1", "1.1.1.1"], timeout=1)
    assert result.timed_out is True
    assert result.stdout == ""
    assert isinstance(result, CommandResult)


@pytest.mark.unit
@pytest.mark.infrastructure
def test_runner_timeout_with_str_output(monkeypatch):
    monkeypatch.setattr("infrastructure.adapters.command_runner.shutil.which", lambda name: "/usr/bin/ping")

    def boom(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="ping", timeout=1, output="out", stderr="err")

    monkeypatch.setattr("infrastructure.adapters.command_runner.subprocess.run", boom)
    result = AllowlistedCommandRunner().run(["ping", "-n", "1", "1.1.1.1"], timeout=1)
    assert result.stdout == "out"
    assert result.stderr == "err"


@pytest.mark.unit
@pytest.mark.infrastructure
def test_runner_timeout_with_none_output(monkeypatch):
    monkeypatch.setattr("infrastructure.adapters.command_runner.shutil.which", lambda name: "/usr/bin/ping")

    def boom(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="ping", timeout=1, output=None, stderr=None)

    monkeypatch.setattr("infrastructure.adapters.command_runner.subprocess.run", boom)
    result = AllowlistedCommandRunner().run(["ping", "-n", "1", "1.1.1.1"], timeout=1)
    assert result.timed_out is True
    assert result.stdout == ""
    assert result.stderr == ""
