"""Probe HTTP opcional via urllib."""

from __future__ import annotations

from urllib.error import URLError
from urllib.request import Request, urlopen


def probe_http(url: str, timeout: float) -> bool | None:
    """GET curto; None se a URL nao for http(s)."""
    stripped = url.strip()
    if not stripped.startswith(("http://", "https://")):
        return None
    try:
        request = Request(stripped, method="GET")
        with urlopen(request, timeout=timeout) as response:  # noqa: S310
            status = int(getattr(response, "status", 0))
    except (OSError, URLError, ValueError):
        return False
    return 200 <= status < 400
