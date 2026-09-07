"""Testes do caso de uso GetAppStatus com fake de ClockPort."""

from datetime import UTC, datetime

import pytest

from application.use_cases.get_app_status import GetAppStatus
from domain.entities.app_identity import AppIdentity
from domain.entities.app_status import AppState


class FakeClock:
    def __init__(self, instant: datetime) -> None:
        self._instant = instant

    def now(self) -> datetime:
        return self._instant


@pytest.mark.unit
@pytest.mark.application
def test_get_app_status_uses_injected_clock():
    instant = datetime(2026, 9, 7, 12, 0, tzinfo=UTC)
    use_case = GetAppStatus(clock=FakeClock(instant))
    identity = AppIdentity(name="script-net-health", version="0.0.0")

    status = use_case.execute(identity)

    assert status.identity == identity
    assert status.state is AppState.READY
    assert status.observed_at == instant
