"""Carrega Settings a partir de variaveis de ambiente."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _int_env(name: str, default: int, *, minimum: int = 1) -> int:
    """Le inteiro do ambiente com piso minimo."""
    raw = os.environ.get(name, str(default))
    try:
        value = int(raw)
    except ValueError:
        return default
    if value < minimum:
        return default
    return value


def _float_env(name: str, default: float) -> float:
    """Le float nao-negativo do ambiente."""
    raw = os.environ.get(name, str(default))
    try:
        value = float(raw)
    except ValueError:
        return default
    if value < 0:
        return default
    return value


def _flag_env(name: str, *, default: bool = False) -> bool:
    """Interpreta flag 1/true/yes do ambiente."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes"}


@dataclass(frozen=True)
class Settings:
    """Configuracao runtime carregada do ambiente."""

    app_name: str
    log_level: str
    probe_timeout_seconds: int
    ping_count: int
    wan_ping_target: str
    dns_probe_name: str
    enable_traceroute: bool
    http_probe_url: str
    enable_speedtest: bool
    speedtest_bytes: int
    speedtest_timeout_seconds: int
    speedtest_download_url: str
    speedtest_upload_url: str
    min_download_mbps: float
    min_upload_mbps: float
    tcp_probe_port: int
    tracert_timeout_seconds: int

    @classmethod
    def from_env(cls, repo_root: Path) -> Settings:
        """Carrega .env (salvo se desabilitado) e o ambiente do processo."""
        disabled = os.environ.get("SNH_DISABLE_DOTENV", "").lower() in {"1", "true", "yes"}
        if not disabled:
            env_path = repo_root / ".env"
            if env_path.exists():
                load_dotenv(env_path, override=False)

        return cls(
            app_name=os.environ.get("SNH_APP_NAME", "script-net-health"),
            log_level=os.environ.get("SNH_LOG_LEVEL", "INFO").upper(),
            probe_timeout_seconds=_int_env("SNH_PROBE_TIMEOUT_SECONDS", 5),
            ping_count=_int_env("SNH_PING_COUNT", 3),
            wan_ping_target=os.environ.get("SNH_WAN_PING_TARGET", "1.1.1.1"),
            dns_probe_name=os.environ.get("SNH_DNS_PROBE_NAME", "example.com"),
            enable_traceroute=_flag_env("SNH_ENABLE_TRACEROUTE"),
            http_probe_url=os.environ.get("SNH_HTTP_PROBE_URL", "").strip(),
            enable_speedtest=_flag_env("SNH_ENABLE_SPEEDTEST", default=True),
            speedtest_bytes=_int_env("SNH_SPEEDTEST_BYTES", 2000000),
            speedtest_timeout_seconds=_int_env("SNH_SPEEDTEST_TIMEOUT_SECONDS", 20),
            speedtest_download_url=os.environ.get("SNH_SPEEDTEST_DOWNLOAD_URL", "").strip(),
            speedtest_upload_url=os.environ.get("SNH_SPEEDTEST_UPLOAD_URL", "").strip(),
            min_download_mbps=_float_env("SNH_MIN_DOWNLOAD_MBPS", 0.0),
            min_upload_mbps=_float_env("SNH_MIN_UPLOAD_MBPS", 0.0),
            tcp_probe_port=_int_env("SNH_TCP_PROBE_PORT", 443),
            tracert_timeout_seconds=_int_env("SNH_TRACERT_TIMEOUT_SECONDS", 30),
        )
