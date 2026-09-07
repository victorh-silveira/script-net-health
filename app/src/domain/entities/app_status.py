"""Status operacional da aplicacao."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from domain.entities.app_identity import AppIdentity


class AppState(Enum):
    """Estado operacional conhecido."""

    READY = "ready"


@dataclass(frozen=True)
class AppStatus:
    """Snapshot de identidade, estado e instante observado."""

    identity: AppIdentity
    state: AppState
    observed_at: datetime

    def as_text(self) -> str:
        """Formata o payload de saida do status."""
        stamp = self.observed_at.isoformat()
        return f"{self.identity.name} {self.identity.version} {self.state.value} {stamp}"
