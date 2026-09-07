"""Configuracao de logging da apresentacao."""

from __future__ import annotations

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configura o logger raiz e silencia clientes HTTP ruidosos."""
    root = logging.getLogger()
    root.handlers.clear()
    resolved = getattr(logging, level.upper(), logging.INFO)
    if not isinstance(resolved, int):
        resolved = logging.INFO
    root.setLevel(resolved)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    root.addHandler(handler)

    for name in ("urllib3", "requests", "urllib3.connectionpool", "httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)
