"""Probe TCP curto sem dump de payload."""

from __future__ import annotations

import socket

from infrastructure.adapters.probe_parsers import is_safe_host


def probe_tcp(host: str, port: int, timeout: float) -> bool | None:
    """True se o handshake TCP completar; None se o host for invalido."""
    if not is_safe_host(host) or port < 1 or port > 65535:
        return None
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False
