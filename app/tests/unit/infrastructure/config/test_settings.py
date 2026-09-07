"""Testes unitarios de Settings."""

from pathlib import Path

import pytest

from infrastructure.config.settings import Settings


@pytest.mark.unit
@pytest.mark.infrastructure
def test_settings_from_env_defaults(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("SNH_DISABLE_DOTENV", "1")
    monkeypatch.delenv("SNH_APP_NAME", raising=False)
    monkeypatch.delenv("SNH_LOG_LEVEL", raising=False)
    monkeypatch.delenv("SNH_PROBE_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("SNH_PING_COUNT", raising=False)
    monkeypatch.delenv("SNH_WAN_PING_TARGET", raising=False)
    monkeypatch.delenv("SNH_DNS_PROBE_NAME", raising=False)
    monkeypatch.delenv("SNH_ENABLE_TRACEROUTE", raising=False)
    monkeypatch.delenv("SNH_HTTP_PROBE_URL", raising=False)
    monkeypatch.delenv("SNH_ENABLE_SPEEDTEST", raising=False)
    monkeypatch.delenv("SNH_SPEEDTEST_BYTES", raising=False)
    monkeypatch.delenv("SNH_SPEEDTEST_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("SNH_SPEEDTEST_DOWNLOAD_URL", raising=False)
    monkeypatch.delenv("SNH_SPEEDTEST_UPLOAD_URL", raising=False)
    monkeypatch.delenv("SNH_MIN_DOWNLOAD_MBPS", raising=False)
    monkeypatch.delenv("SNH_MIN_UPLOAD_MBPS", raising=False)
    monkeypatch.delenv("SNH_TCP_PROBE_PORT", raising=False)
    monkeypatch.delenv("SNH_TRACERT_TIMEOUT_SECONDS", raising=False)

    settings = Settings.from_env(tmp_path)
    assert settings.app_name == "script-net-health"
    assert settings.log_level == "INFO"
    assert settings.probe_timeout_seconds == 5
    assert settings.ping_count == 3
    assert settings.wan_ping_target == "1.1.1.1"
    assert settings.dns_probe_name == "example.com"
    assert settings.enable_traceroute is False
    assert settings.http_probe_url == ""
    assert settings.enable_speedtest is True
    assert settings.speedtest_bytes == 2000000
    assert settings.speedtest_timeout_seconds == 20
    assert settings.speedtest_download_url == ""
    assert settings.speedtest_upload_url == ""
    assert settings.min_download_mbps == 0.0
    assert settings.min_upload_mbps == 0.0
    assert settings.tcp_probe_port == 443
    assert settings.tracert_timeout_seconds == 30


@pytest.mark.unit
@pytest.mark.infrastructure
def test_settings_from_env_custom(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("SNH_DISABLE_DOTENV", "1")
    monkeypatch.setenv("SNH_APP_NAME", "custom-app")
    monkeypatch.setenv("SNH_LOG_LEVEL", "debug")

    settings = Settings.from_env(tmp_path)
    assert settings.app_name == "custom-app"
    assert settings.log_level == "DEBUG"


@pytest.mark.unit
@pytest.mark.infrastructure
def test_settings_probe_knobs_and_invalid_ints(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("SNH_DISABLE_DOTENV", "1")
    monkeypatch.setenv("SNH_PROBE_TIMEOUT_SECONDS", "9")
    monkeypatch.setenv("SNH_PING_COUNT", "2")
    monkeypatch.setenv("SNH_WAN_PING_TARGET", "8.8.8.8")
    monkeypatch.setenv("SNH_DNS_PROBE_NAME", "example.org")
    monkeypatch.setenv("SNH_ENABLE_TRACEROUTE", "yes")
    monkeypatch.setenv("SNH_HTTP_PROBE_URL", " https://example.com ")
    monkeypatch.setenv("SNH_ENABLE_SPEEDTEST", "1")
    monkeypatch.setenv("SNH_SPEEDTEST_BYTES", "1000")
    monkeypatch.setenv("SNH_SPEEDTEST_TIMEOUT_SECONDS", "15")
    monkeypatch.setenv("SNH_SPEEDTEST_DOWNLOAD_URL", " https://example.com/down ")
    monkeypatch.setenv("SNH_SPEEDTEST_UPLOAD_URL", "https://example.com/up")
    monkeypatch.setenv("SNH_MIN_DOWNLOAD_MBPS", "10.5")
    monkeypatch.setenv("SNH_MIN_UPLOAD_MBPS", "2")
    monkeypatch.setenv("SNH_TCP_PROBE_PORT", "80")
    monkeypatch.setenv("SNH_TRACERT_TIMEOUT_SECONDS", "45")
    settings = Settings.from_env(tmp_path)
    assert settings.probe_timeout_seconds == 9
    assert settings.ping_count == 2
    assert settings.wan_ping_target == "8.8.8.8"
    assert settings.enable_traceroute is True
    assert settings.http_probe_url == "https://example.com"
    assert settings.enable_speedtest is True
    assert settings.speedtest_bytes == 1000
    assert settings.speedtest_timeout_seconds == 15
    assert settings.speedtest_download_url == "https://example.com/down"
    assert settings.speedtest_upload_url == "https://example.com/up"
    assert settings.min_download_mbps == 10.5
    assert settings.min_upload_mbps == 2.0
    assert settings.tcp_probe_port == 80
    assert settings.tracert_timeout_seconds == 45

    monkeypatch.setenv("SNH_PROBE_TIMEOUT_SECONDS", "abc")
    monkeypatch.setenv("SNH_PING_COUNT", "0")
    monkeypatch.setenv("SNH_ENABLE_TRACEROUTE", "0")
    monkeypatch.setenv("SNH_ENABLE_SPEEDTEST", "0")
    monkeypatch.setenv("SNH_MIN_DOWNLOAD_MBPS", "abc")
    monkeypatch.setenv("SNH_MIN_UPLOAD_MBPS", "-1")
    monkeypatch.setenv("SNH_TCP_PROBE_PORT", "0")
    invalid = Settings.from_env(tmp_path)
    assert invalid.probe_timeout_seconds == 5
    assert invalid.ping_count == 3
    assert invalid.enable_traceroute is False
    assert invalid.enable_speedtest is False
    assert invalid.min_download_mbps == 0.0
    assert invalid.min_upload_mbps == 0.0
    assert invalid.tcp_probe_port == 443


@pytest.mark.unit
@pytest.mark.infrastructure
def test_settings_loads_dotenv_file(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("SNH_DISABLE_DOTENV", raising=False)
    monkeypatch.delenv("SNH_APP_NAME", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("SNH_APP_NAME=from-dotenv\n", encoding="utf-8")

    settings = Settings.from_env(tmp_path)
    assert settings.app_name == "from-dotenv"


@pytest.mark.unit
@pytest.mark.infrastructure
def test_settings_missing_dotenv_file(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("SNH_DISABLE_DOTENV", raising=False)
    monkeypatch.setenv("SNH_APP_NAME", "from-process")

    settings = Settings.from_env(tmp_path)
    assert settings.app_name == "from-process"


@pytest.mark.unit
@pytest.mark.infrastructure
@pytest.mark.parametrize("flag", ["1", "true", "yes", "TRUE"])
def test_settings_disable_dotenv_flags(monkeypatch, tmp_path: Path, flag: str):
    monkeypatch.setenv("SNH_DISABLE_DOTENV", flag)
    monkeypatch.setenv("SNH_APP_NAME", "from-process")
    env_file = tmp_path / ".env"
    env_file.write_text("SNH_APP_NAME=from-dotenv\n", encoding="utf-8")

    settings = Settings.from_env(tmp_path)
    assert settings.app_name == "from-process"
