"""Testes do use case DiagnoseNetworkHealth com fake do port."""

import pytest

from application.use_cases.diagnose_network_health import DiagnoseNetworkHealth
from domain.entities.diagnosis_report import Impact, TcpIpLayer
from domain.entities.network_evidence import (
    LinkEvidence,
    LinkState,
    NetworkEvidence,
    PingEvidence,
)
from domain.services.bottom_up_diagnoser import BottomUpDiagnoser


class FakeCollector:
    def __init__(self, evidence: NetworkEvidence) -> None:
        self.evidence = evidence

    def collect(self) -> NetworkEvidence:
        return self.evidence


@pytest.mark.unit
@pytest.mark.application
def test_diagnose_network_health_uses_collector_and_diagnoser():
    evidence = NetworkEvidence(
        links=(LinkEvidence(name="eth0", state=LinkState.UP, has_address=True),),
        neighbors=(),
        default_gateway="10.0.0.1",
        default_iface="eth0",
        gateway_ping=PingEvidence("10.0.0.1", 3, 3, 0.0, 1.0),
        wan_ping=PingEvidence("1.1.1.1", 3, 0, 100.0, None),
        dns_ok=True,
        dns_name="example.com",
        wan_target="1.1.1.1",
        listening_sockets=("0.0.0.0:22",),
        missing_probes=(),
    )
    use_case = DiagnoseNetworkHealth(collector=FakeCollector(evidence), diagnoser=BottomUpDiagnoser())
    report = use_case.execute()
    assert report.impact is Impact.WAN
    assert report.probable_layer is TcpIpLayer.INTERNET


def _base(**overrides: object) -> NetworkEvidence:
    payload: dict[str, object] = {
        "links": (LinkEvidence(name="eth0", state=LinkState.UP, has_address=True),),
        "neighbors": (),
        "default_gateway": "10.0.0.1",
        "default_iface": "eth0",
        "gateway_ping": PingEvidence("10.0.0.1", 3, 3, 0.0, 1.0),
        "wan_ping": PingEvidence("1.1.1.1", 3, 3, 0.0, 1.0),
        "dns_ok": True,
        "dns_name": "example.com",
        "wan_target": "1.1.1.1",
        "listening_sockets": ("0.0.0.0:22",),
        "missing_probes": (),
    }
    payload.update(overrides)
    return NetworkEvidence(**payload)


@pytest.mark.unit
@pytest.mark.application
@pytest.mark.parametrize(
    ("evidence", "impact"),
    [
        (_base(links=()), Impact.LAN),
        (_base(default_gateway=None, default_iface=None, gateway_ping=None), Impact.LAN),
        (_base(gateway_ping=PingEvidence("10.0.0.1", 3, 0, 100.0, None)), Impact.LAN),
        (_base(dns_ok=False), Impact.SERVICE),
        (_base(), Impact.NONE),
    ],
)
def test_diagnose_network_health_priority_table(evidence: NetworkEvidence, impact: Impact):
    report = DiagnoseNetworkHealth(collector=FakeCollector(evidence), diagnoser=BottomUpDiagnoser()).execute()
    assert report.impact is impact
