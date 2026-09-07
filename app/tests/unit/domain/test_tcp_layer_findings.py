"""Testes das regras por camada TCP/IP."""

import pytest

from domain.entities.diagnosis_report import FindingStatus
from domain.entities.network_evidence import (
    LinkEvidence,
    LinkState,
    NeighborEvidence,
    NetworkEvidence,
    PingEvidence,
    ThroughputEvidence,
)
from domain.services.tcp_layer_findings import (
    _degraded_path,
    _rtt_label,
    application_finding,
    ping_text,
    transport_finding,
)


def _base(**overrides: object) -> NetworkEvidence:
    payload: dict[str, object] = {
        "links": (LinkEvidence(name="eth0", state=LinkState.UP, has_address=True),),
        "neighbors": (NeighborEvidence(address="10.0.0.1", device="eth0", state="REACHABLE"),),
        "default_gateway": "10.0.0.1",
        "default_iface": "eth0",
        "gateway_ping": PingEvidence("10.0.0.1", 3, 3, 0.0, 1.0),
        "wan_ping": PingEvidence("1.1.1.1", 3, 3, 0.0, 1.0),
        "dns_ok": True,
        "dns_name": "example.com",
        "wan_target": "1.1.1.1",
        "listening_sockets": (),
        "missing_probes": (),
    }
    payload.update(overrides)
    return NetworkEvidence(**payload)


@pytest.mark.unit
@pytest.mark.domain
def test_rtt_label_and_degraded_helpers():
    none_avg = PingEvidence("1.1.1.1", 3, 0, 100.0, None)
    assert _rtt_label(none_avg) == "n/d"
    assert _degraded_path(None, 10.0) is False
    assert "jitter=2.0ms" in ping_text("WAN", PingEvidence("1.1.1.1", 3, 3, 0.0, 1.0, jitter_ms=2.0))


@pytest.mark.unit
@pytest.mark.domain
def test_transport_tcp_states():
    opened = transport_finding(_base(tcp_ok=True, tcp_endpoint="1.1.1.1:443"))
    assert opened.status is FindingStatus.OK
    assert "TCP 1.1.1.1:443 abriu" in opened.evidence
    unchecked = transport_finding(_base(tcp_ok=None, tcp_endpoint="1.1.1.1:443"))
    assert "TCP 1.1.1.1:443 nao verificado" in unchecked.evidence
    both_lost = transport_finding(
        _base(
            gateway_ping=PingEvidence("10.0.0.1", 3, 0, 100.0, None),
            wan_ping=PingEvidence("1.1.1.1", 3, 0, 100.0, None),
        )
    )
    assert both_lost.status is FindingStatus.FAILED
    lan_jitter = transport_finding(_base(gateway_ping=PingEvidence("10.0.0.1", 3, 3, 0.0, 1.0, jitter_ms=11.0)))
    assert lan_jitter.status is FindingStatus.DEGRADED


@pytest.mark.unit
@pytest.mark.domain
def test_application_upload_sla_and_partial_throughput():
    partial = ThroughputEvidence(download_mbps=None, upload_mbps=2.0, bytes_transferred=100, duration_s=1.0)
    finding = application_finding(_base(throughput=partial, min_upload_mbps=10.0))
    assert finding.status is FindingStatus.DEGRADED
    assert "down=n/d" in finding.evidence
    assert "up=2.00Mbps" in finding.evidence
    none_rates = ThroughputEvidence(download_mbps=None, upload_mbps=None, bytes_transferred=0, duration_s=0.1)
    plain = application_finding(_base(throughput=none_rates))
    assert "down=n/d" in plain.evidence
    assert "up=n/d" in plain.evidence
    assert plain.status is FindingStatus.OK
    download_missing = application_finding(_base(throughput=partial, min_download_mbps=10.0))
    assert download_missing.status is FindingStatus.OK
    upload_missing = application_finding(
        _base(
            throughput=ThroughputEvidence(download_mbps=20.0, upload_mbps=None, bytes_transferred=100, duration_s=1.0),
            min_upload_mbps=10.0,
        )
    )
    assert upload_missing.status is FindingStatus.OK
