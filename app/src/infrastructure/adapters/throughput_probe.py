"""Medicao de throughput HTTP(S) via urllib."""

from __future__ import annotations

import time
from urllib.error import URLError
from urllib.request import Request, urlopen

from domain.constants import CLOUDFLARE_DOWNLOAD, CLOUDFLARE_UPLOAD
from domain.entities.network_evidence import ThroughputEvidence


def measure_throughput(
    download_url: str,
    upload_url: str,
    payload_bytes: int,
    timeout: float,
) -> ThroughputEvidence | None:
    """GET de download e POST de upload; None se URLs invalidas."""
    down = download_url.strip() or CLOUDFLARE_DOWNLOAD.format(bytes=payload_bytes)
    up = upload_url.strip() or CLOUDFLARE_UPLOAD
    if not down.startswith(("http://", "https://")) or not up.startswith(("http://", "https://")):
        return None
    started = time.perf_counter()
    download_mbps = _download_mbps(down, timeout)
    upload_mbps = _upload_mbps(up, payload_bytes, timeout)
    duration = time.perf_counter() - started
    if download_mbps is None and upload_mbps is None:
        return None
    return ThroughputEvidence(
        download_mbps=download_mbps,
        upload_mbps=upload_mbps,
        bytes_transferred=payload_bytes,
        duration_s=duration,
    )


def _download_mbps(url: str, timeout: float) -> float | None:
    """GET e converte bytes lidos em Mbps."""
    try:
        request = Request(url, method="GET")
        started = time.perf_counter()
        with urlopen(request, timeout=timeout) as response:
            payload = response.read()
        elapsed = time.perf_counter() - started
    except (OSError, URLError, ValueError):
        return None
    if elapsed <= 0 or not payload:
        return None
    return (len(payload) * 8) / elapsed / 1_000_000


def _upload_mbps(url: str, payload_bytes: int, timeout: float) -> float | None:
    """POST de payload sintetico e converte em Mbps."""
    body = b"x" * max(payload_bytes, 1)
    try:
        request = Request(url, data=body, method="POST")
        started = time.perf_counter()
        with urlopen(request, timeout=timeout) as response:
            response.read()
        elapsed = time.perf_counter() - started
    except (OSError, URLError, ValueError):
        return None
    if elapsed <= 0:
        return None
    return (len(body) * 8) / elapsed / 1_000_000
