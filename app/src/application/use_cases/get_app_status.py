"""Caso de uso: obter status da aplicacao."""

from application.ports.clock import ClockPort
from domain.entities.app_identity import AppIdentity
from domain.entities.app_status import AppState, AppStatus


class GetAppStatus:
    """Monta o snapshot de status sem IO direto."""

    def __init__(self, clock: ClockPort) -> None:
        """Injeta o relogio usado para o snapshot."""
        self._clock = clock

    def execute(self, identity: AppIdentity) -> AppStatus:
        """Retorna o status ready no instante do relogio injetado."""
        return AppStatus(identity=identity, state=AppState.READY, observed_at=self._clock.now())
