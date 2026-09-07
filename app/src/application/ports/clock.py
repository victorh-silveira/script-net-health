"""Porta de relogio do caso de uso."""

from datetime import datetime
from typing import Protocol


class ClockPort(Protocol):
    """Contrato de relogio injetavel."""

    def now(self) -> datetime:
        """Retorna o instante atual com fuso."""
        ...
