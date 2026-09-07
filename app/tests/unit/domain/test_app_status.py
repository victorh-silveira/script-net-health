"""Testes unitarios de identidade e status."""

from datetime import UTC, datetime

import pytest

from domain.constants import APP_VERSION
from domain.entities.app_identity import AppIdentity
from domain.entities.app_status import AppState, AppStatus
from domain.exceptions import DomainError


@pytest.mark.unit
@pytest.mark.domain
def test_app_identity_valid():
    identity = AppIdentity(name="script-net-health", version=APP_VERSION)
    assert identity.name == "script-net-health"
    assert identity.version == APP_VERSION


@pytest.mark.unit
@pytest.mark.domain
@pytest.mark.parametrize("name", ["", "   "])
def test_app_identity_rejects_blank_name(name: str):
    with pytest.raises(DomainError, match="nome"):
        AppIdentity(name=name, version="0.0.0")


@pytest.mark.unit
@pytest.mark.domain
@pytest.mark.parametrize("version", ["", "   "])
def test_app_identity_rejects_blank_version(version: str):
    with pytest.raises(DomainError, match="versao"):
        AppIdentity(name="script-net-health", version=version)


@pytest.mark.unit
@pytest.mark.domain
def test_app_status_as_text():
    identity = AppIdentity(name="snh", version="0.0.0")
    observed = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
    status = AppStatus(identity=identity, state=AppState.READY, observed_at=observed)
    assert status.as_text() == "snh 0.0.0 ready 2026-01-02T03:04:05+00:00"
