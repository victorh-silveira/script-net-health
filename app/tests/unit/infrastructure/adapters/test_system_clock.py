"""Testes do adapter SystemClock."""

from datetime import datetime

import pytest

from infrastructure.adapters.system_clock import SystemClock


@pytest.mark.unit
@pytest.mark.infrastructure
def test_system_clock_returns_aware_datetime():
    clock = SystemClock()
    now = clock.now()
    assert isinstance(now, datetime)
    assert now.tzinfo is not None
