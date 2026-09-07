"""Testes das entidades de evidencia de rede."""

import pytest

from domain.entities.network_evidence import (
    LinkEvidence,
    LinkState,
    NeighborEvidence,
    NetworkEvidence,
    PingEvidence,
    ProbeTranscript,
)
from domain.exceptions import DomainError


def _evidence(**overrides: object) -> NetworkEvidence:
    payload: dict[str, object] = {
        "links": (),
        "neighbors": (),
        "default_gateway": None,
        "default_iface": None,
        "gateway_ping": None,
        "wan_ping": None,
        "dns_ok": None,
        "dns_name": "example.com",
        "wan_target": "1.1.1.1",
        "listening_sockets": (),
        "missing_probes": (),
    }
    payload.update(overrides)
    return NetworkEvidence(**payload)


@pytest.mark.unit
@pytest.mark.domain
def test_link_rejects_blank_name():
    with pytest.raises(DomainError):
        LinkEvidence(name="  ", state=LinkState.UP, has_address=True)


@pytest.mark.unit
@pytest.mark.domain
def test_neighbor_rejects_blank_address():
    with pytest.raises(DomainError):
        NeighborEvidence(address="", device="eth0", state="REACHABLE")


@pytest.mark.unit
@pytest.mark.domain
def test_ping_rejects_blank_target():
    with pytest.raises(DomainError):
        PingEvidence(target=" ", transmitted=1, received=1, loss_pct=0.0, rtt_avg_ms=1.0)


@pytest.mark.unit
@pytest.mark.domain
def test_evidence_rejects_blank_dns_and_wan():
    with pytest.raises(DomainError):
        _evidence(dns_name=" ")
    with pytest.raises(DomainError):
        _evidence(wan_target="")


@pytest.mark.unit
@pytest.mark.domain
def test_loopback_is_not_up_addressed_link():
    linux = _evidence(
        links=(LinkEvidence(name="lo", state=LinkState.UP, has_address=True),),
    )
    windows = _evidence(
        links=(LinkEvidence(name="Loopback Pseudo-Interface 1", state=LinkState.UP, has_address=True),),
    )
    assert linux.has_up_addressed_link() is False
    assert windows.has_up_addressed_link() is False


@pytest.mark.unit
@pytest.mark.domain
def test_transcript_rejects_blank_command():
    with pytest.raises(DomainError):
        ProbeTranscript(command="  ", returncode=0, stdout="", skipped=False, timed_out=False)


@pytest.mark.unit
@pytest.mark.domain
def test_link_keeps_ipv4():
    link = LinkEvidence(name="eth0", state=LinkState.UP, has_address=True, ipv4="10.0.0.8")
    assert link.ipv4 == "10.0.0.8"


@pytest.mark.unit
@pytest.mark.domain
def test_ping_loss_and_reply_helpers():
    lost = PingEvidence(target="1.1.1.1", transmitted=3, received=0, loss_pct=100.0, rtt_avg_ms=None)
    ok = PingEvidence(target="1.1.1.1", transmitted=3, received=3, loss_pct=0.0, rtt_avg_ms=1.2, jitter_ms=0.4)
    unknown = PingEvidence(target="1.1.1.1", transmitted=None, received=None, loss_pct=None, rtt_avg_ms=None)
    assert lost.is_total_loss() is True
    assert lost.has_reply() is False
    assert ok.is_total_loss() is False
    assert ok.has_reply() is True
    assert ok.jitter_ms == 0.4
    assert unknown.is_total_loss() is None
    assert unknown.has_reply() is None
