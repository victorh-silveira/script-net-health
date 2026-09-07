"""Testes das regras BOTTOM-UP do diagnoser."""

import pytest

from domain.entities.diagnosis_report import FindingStatus, Impact, Severity, TcpIpLayer
from domain.entities.network_evidence import (
    LinkEvidence,
    LinkState,
    NeighborEvidence,
    NetworkEvidence,
    PingEvidence,
    ThroughputEvidence,
)
from domain.services.bottom_up_diagnoser import BottomUpDiagnoser


def _ping(
    target: str,
    *,
    received: int,
    loss: float,
    rtt: float | None = 1.0,
    jitter: float | None = None,
    rtt_min: float | None = None,
    rtt_max: float | None = None,
) -> PingEvidence:
    return PingEvidence(
        target=target,
        transmitted=3,
        received=received,
        loss_pct=loss,
        rtt_avg_ms=rtt,
        rtt_min_ms=rtt_min,
        rtt_max_ms=rtt_max,
        jitter_ms=jitter,
    )


def _healthy_links() -> tuple[LinkEvidence, ...]:
    return (
        LinkEvidence(name="lo", state=LinkState.UP, has_address=True),
        LinkEvidence(name="eth0", state=LinkState.UP, has_address=True, mtu=1500),
    )


def _evidence(**overrides: object) -> NetworkEvidence:
    payload: dict[str, object] = {
        "links": _healthy_links(),
        "neighbors": (NeighborEvidence(address="172.28.0.1", device="eth0", state="REACHABLE"),),
        "default_gateway": "172.28.0.1",
        "default_iface": "eth0",
        "gateway_ping": _ping("172.28.0.1", received=3, loss=0.0),
        "wan_ping": _ping("1.1.1.1", received=3, loss=0.0),
        "dns_ok": True,
        "dns_name": "example.com",
        "wan_target": "1.1.1.1",
        "listening_sockets": ("0.0.0.0:22",),
        "missing_probes": (),
    }
    payload.update(overrides)
    return NetworkEvidence(**payload)


@pytest.mark.unit
@pytest.mark.domain
def test_access_failure_when_only_loopback():
    report = BottomUpDiagnoser().diagnose(
        _evidence(links=(LinkEvidence(name="lo", state=LinkState.UP, has_address=True),))
    )
    assert report.impact is Impact.LAN
    assert report.probable_layer is TcpIpLayer.ACCESS
    assert report.severity is Severity.CRITICAL
    assert "Acesso a Rede" in report.as_text()


@pytest.mark.unit
@pytest.mark.domain
def test_access_unknown_when_link_probe_missing():
    report = BottomUpDiagnoser().diagnose(_evidence(links=(), missing_probes=("ipconfig /all",)))
    assert "nao verificado" in report.as_text()


@pytest.mark.unit
@pytest.mark.domain
def test_access_failed_without_links_and_without_missing_probe():
    report = BottomUpDiagnoser().diagnose(_evidence(links=(), missing_probes=()))
    assert report.impact is Impact.LAN
    assert report.severity is Severity.CRITICAL


@pytest.mark.unit
@pytest.mark.domain
def test_access_degraded_when_one_down_one_up():
    links = (
        LinkEvidence(name="eth0", state=LinkState.UP, has_address=True, mtu=1500),
        LinkEvidence(name="wlan0", state=LinkState.DOWN, has_address=False),
    )
    report = BottomUpDiagnoser().diagnose(_evidence(links=links))
    assert report.impact is Impact.NONE
    assert "wlan0=down" in report.as_text()


@pytest.mark.unit
@pytest.mark.domain
def test_no_default_route():
    report = BottomUpDiagnoser().diagnose(_evidence(default_gateway=None, default_iface=None, gateway_ping=None))
    assert report.impact is Impact.LAN
    assert report.probable_layer is TcpIpLayer.INTERNET
    assert report.severity is Severity.HIGH


@pytest.mark.unit
@pytest.mark.domain
def test_missing_route_probe_is_unknown_not_no_gateway_fault():
    report = BottomUpDiagnoser().diagnose(
        _evidence(default_gateway=None, default_iface=None, gateway_ping=None, missing_probes=("route print",))
    )
    assert report.impact is Impact.NONE
    assert "route print" in report.as_text()


@pytest.mark.unit
@pytest.mark.domain
def test_gateway_total_loss():
    report = BottomUpDiagnoser().diagnose(_evidence(gateway_ping=_ping("172.28.0.1", received=0, loss=100.0, rtt=None)))
    assert report.impact is Impact.LAN
    assert report.probable_layer is TcpIpLayer.INTERNET


@pytest.mark.unit
@pytest.mark.domain
def test_wan_total_loss_with_gateway_ok():
    report = BottomUpDiagnoser().diagnose(_evidence(wan_ping=_ping("1.1.1.1", received=0, loss=100.0, rtt=None)))
    assert report.impact is Impact.WAN
    assert "Isolado a WAN" in report.root_cause or "WAN" in report.as_text()


@pytest.mark.unit
@pytest.mark.domain
def test_dns_failure():
    report = BottomUpDiagnoser().diagnose(_evidence(dns_ok=False))
    assert report.impact is Impact.SERVICE
    assert report.probable_layer is TcpIpLayer.APPLICATION
    assert report.severity is Severity.MEDIUM


@pytest.mark.unit
@pytest.mark.domain
def test_http_failure():
    report = BottomUpDiagnoser().diagnose(_evidence(http_ok=False, http_url="https://example.com"))
    assert report.impact is Impact.SERVICE
    assert "HTTP" in report.as_text()


@pytest.mark.unit
@pytest.mark.domain
def test_healthy_path():
    report = BottomUpDiagnoser().diagnose(_evidence())
    assert report.impact is Impact.NONE
    assert report.probable_layer is TcpIpLayer.NONE
    assert report.severity is Severity.LOW
    text = report.as_text()
    assert "#### 1. Resumo Executivo" in text
    assert "Resumo Executivo da Falha" not in text
    assert "- **Status:** Saudavel" in text
    assert "- **Camada Provavel da Falha:** Nenhuma" in text
    assert "ping -n 3 172.28.0.1" in text


@pytest.mark.unit
@pytest.mark.domain
def test_internet_unknown_when_pings_missing():
    report = BottomUpDiagnoser().diagnose(_evidence(gateway_ping=None, wan_ping=None, dns_ok=None))
    assert report.impact is Impact.NONE
    assert "nao verificado" in report.as_text()


@pytest.mark.unit
@pytest.mark.domain
def test_ping_without_stats_and_traceroute_hops():
    ping = PingEvidence("172.28.0.1", 3, 3, None, None)
    report = BottomUpDiagnoser().diagnose(
        _evidence(gateway_ping=ping, wan_ping=ping, traceroute_hops=("1", "2"), dns_ok=None)
    )
    assert "sem estatistica" in report.as_text()
    assert "traceroute_hops=2" in report.as_text()


@pytest.mark.unit
@pytest.mark.domain
def test_transport_missing_and_empty():
    missing = BottomUpDiagnoser().diagnose(_evidence(missing_probes=("netstat -ano",), listening_sockets=()))
    assert "netstat -ano" in missing.as_text()
    empty = BottomUpDiagnoser().diagnose(_evidence(listening_sockets=()))
    assert "LISTEN locais=0" in empty.as_text()
    noted = BottomUpDiagnoser().diagnose(_evidence(listening_sockets=("0.0.0.0:22",)))
    assert "LISTEN locais=1" in noted.as_text()
    assert noted.findings[2].status is FindingStatus.OK


@pytest.mark.unit
@pytest.mark.domain
def test_http_unchecked_and_ok():
    unchecked = BottomUpDiagnoser().diagnose(_evidence(http_url="https://example.com", http_ok=None))
    assert "nao verificado" in unchecked.as_text()
    ok = BottomUpDiagnoser().diagnose(_evidence(http_url="https://example.com", http_ok=True))
    assert "respondeu" in ok.as_text()


@pytest.mark.unit
@pytest.mark.domain
def test_missing_probe_appended_to_commands():
    report = BottomUpDiagnoser().diagnose(_evidence(missing_probes=("tracert -d 1.1.1.1",)))
    assert "tracert -d 1.1.1.1" in report.as_text()


@pytest.mark.unit
@pytest.mark.domain
def test_access_all_down_and_ok_without_mtu():
    down = BottomUpDiagnoser().diagnose(
        _evidence(links=(LinkEvidence(name="eth0", state=LinkState.UNKNOWN, has_address=False),))
    )
    assert down.impact is Impact.LAN
    assert down.severity is Severity.CRITICAL
    ok = BottomUpDiagnoser().diagnose(
        _evidence(links=(LinkEvidence(name="eth0", state=LinkState.UP, has_address=True, ipv4="10.0.0.8"),))
    )
    assert ok.impact is Impact.NONE
    assert "MTU=" not in ok.as_text()
    assert "eth0/10.0.0.8=up" in ok.as_text()


@pytest.mark.unit
@pytest.mark.domain
def test_tcp_failure_with_wan_ok():
    report = BottomUpDiagnoser().diagnose(_evidence(tcp_ok=False, tcp_endpoint="1.1.1.1:443"))
    assert report.impact is Impact.SERVICE
    assert report.probable_layer is TcpIpLayer.TRANSPORT
    assert "TCP 1.1.1.1:443 recusou" in report.as_text()


@pytest.mark.unit
@pytest.mark.domain
def test_throughput_sla_degrades_application():
    slow = ThroughputEvidence(download_mbps=1.0, upload_mbps=20.0, bytes_transferred=1000, duration_s=1.0)
    report = BottomUpDiagnoser().diagnose(_evidence(throughput=slow, min_download_mbps=10.0))
    assert report.impact is Impact.NONE
    assert report.findings[3].status is FindingStatus.DEGRADED
    assert "throughput down=1.00Mbps" in report.as_text()
    assert report.executive_status() == "Degradado"


@pytest.mark.unit
@pytest.mark.domain
def test_wan_jitter_and_loss_degrade_without_failure():
    jittered = BottomUpDiagnoser().diagnose(_evidence(wan_ping=_ping("1.1.1.1", received=3, loss=0.0, jitter=80.0)))
    assert jittered.impact is Impact.NONE
    assert jittered.findings[1].status is FindingStatus.DEGRADED
    lossy = BottomUpDiagnoser().diagnose(_evidence(wan_ping=_ping("1.1.1.1", received=2, loss=33.0, rtt=4.0)))
    assert lossy.findings[1].status is FindingStatus.DEGRADED
    assert lossy.probable_layer is TcpIpLayer.NONE


@pytest.mark.unit
@pytest.mark.domain
def test_ping_rtt_zero_and_minmax_labels():
    zero = BottomUpDiagnoser().diagnose(_evidence(gateway_ping=_ping("172.28.0.1", received=3, loss=0.0, rtt=0.0)))
    assert "rtt=<1ms" in zero.as_text()
    ranged = _ping("172.28.0.1", received=3, loss=0.0, rtt=2.0, rtt_min=1.0, rtt_max=3.0)
    text = BottomUpDiagnoser().diagnose(_evidence(gateway_ping=ranged)).as_text()
    assert "min=1.0ms med=2.0ms max=3.0ms" in text
