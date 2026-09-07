"""Relogio de sistema."""

from datetime import UTC, datetime


class SystemClock:
    """ClockPort baseado em datetime UTC."""

    def now(self) -> datetime:
        """Retorna o instante UTC atual."""
        return datetime.now(UTC)
