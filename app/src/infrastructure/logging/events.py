"""API unica de logging semantico."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlsplit, urlunsplit


def redact_url(url: str) -> str:
    """Remove query strings de URLs para log seguro."""
    parts = urlsplit(url)
    if not parts.query:
        return url
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "***", parts.fragment))


def log_event(
    logger: logging.Logger,
    level: int,
    event: str,
    *,
    exc_info: bool = False,
    **fields: Any,
) -> None:
    """Emite um evento semantico nomeado com campos estruturados."""
    safe_fields: dict[str, Any] = {}
    for key, value in fields.items():
        if key in {"url", "request_url", "target_url"} and isinstance(value, str):
            safe_fields[key] = redact_url(value)
        elif key in {"secret", "anon_key", "token", "password", "authorization"}:
            safe_fields[key] = "***"
        else:
            safe_fields[key] = value

    extras = " ".join(f"{k}={v}" for k, v in safe_fields.items())
    message = f"event={event}" if not extras else f"event={event} {extras}"
    use_exc = exc_info and logger.isEnabledFor(logging.DEBUG)
    logger.log(level, message, exc_info=use_exc)
