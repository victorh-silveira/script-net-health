"""Testes do WindowsProbeCollector com runner fake."""

from __future__ import annotations

import pytest

from domain.entities.network_evidence import ThroughputEvidence
from infrastructure.adapters.command_runner import CommandResult
from infrastructure.adapters.windows_probe_collector import WindowsProbeCollector
from infrastructure.config.settings import Settings


def _settings(**overrides: object) -> Settings:
    payload: dict[str, object] = {
        "app_name": "snh",
        "log_level": "INFO",
        "probe_timeout_seconds": 5,
        "ping_count": 3,
        "wan_ping_target": "1.1.1.1",
        "dns_probe_name": "example.com",
        "enable_traceroute": False,
        "http_probe_url": "",
        "enable_speedtest": False,
        "speedtest_bytes": 2000000,
        "speedtest_timeout_seconds": 20,
        "speedtest_download_url": "",
        "speedtest_upload_url": "",
        "min_download_mbps": 0.0,
        "min_upload_mbps": 0.0,
        "tcp_probe_port": 443,
        "tracert_timeout_seconds": 30,
    }
    payload.update(overrides)
    return Settings(**payload)


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    monkeypatch.setattr(
        "infrastructure.adapters.windows_probe_collector.probe_tcp",
        lambda *a, **k: True,
    )
    monkeypatch.setattr(
        "infrastructure.adapters.windows_probe_collector.measure_throughput",
        lambda *a, **k: None,
    )


class MapRunner:
    def __init__(self, mapping: dict[tuple[str, ...], CommandResult]) -> None:
        self.mapping = mapping

    def run(self, argv: list[str], timeout: float) -> CommandResult:
        key = tuple(argv)
        if key in self.mapping:
            return self.mapping[key]
        return CommandResult(key, None, "", "", skipped=True, timed_out=False)


def _ok(argv: list[str], stdout: str, code: int = 0) -> CommandResult:
    return CommandResult(tuple(argv), code, stdout, "", skipped=False, timed_out=False)


def _skip(argv: list[str]) -> CommandResult:
    return CommandResult(tuple(argv), None, "", "", skipped=True, timed_out=False)


def _timeout(argv: list[str]) -> CommandResult:
    return CommandResult(tuple(argv), None, "", "", skipped=False, timed_out=True)


IPCONFIG = (
    "Ethernet adapter Ethernet:\n"
    "   Media State . . . . . . . . . . . : Media disconnected\n"
    "Wireless LAN adapter Wi-Fi:\n"
    "   IPv4 Address. . . . . . . . . . . : 192.168.1.10\n"
)

ROUTE = "0.0.0.0          0.0.0.0      192.168.1.1     192.168.1.10     35\n"
ARP = "Interface: 192.168.1.10 --- 0xc\n  192.168.1.1           aa-bb-cc-dd-ee-ff     dynamic\n"
NETSTAT = "  TCP    0.0.0.0:22             0.0.0.0:0              LISTENING       1234\n"
PING = "Packets: Sent = 3, Received = 3, Lost = 0 (0% loss),\n    Average = 2ms\n"
NSLOOKUP = "Name: example.com\nAddress: 93.184.216.34\n"


def _base_mapping() -> dict[tuple[str, ...], CommandResult]:
    return {
        ("ipconfig", "/all"): _ok(["ipconfig", "/all"], IPCONFIG),
        ("route", "print"): _ok(["route", "print"], ROUTE),
        ("arp", "-a"): _ok(["arp", "-a"], ARP),
        ("netstat", "-ano"): _ok(["netstat", "-ano"], NETSTAT),
        ("ping", "-n", "3", "192.168.1.1"): _ok(["ping", "-n", "3", "192.168.1.1"], PING),
        ("ping", "-n", "3", "1.1.1.1"): _ok(["ping", "-n", "3", "1.1.1.1"], PING, 1),
        ("nslookup", "example.com"): _ok(["nslookup", "example.com"], NSLOOKUP),
    }


@pytest.mark.unit
@pytest.mark.infrastructure
def test_collector_parses_happy_path():
    evidence = WindowsProbeCollector(MapRunner(_base_mapping()), _settings()).collect()
    assert evidence.default_gateway == "192.168.1.1"
    assert evidence.default_iface == "Wi-Fi"
    assert evidence.has_up_addressed_link() is True
    assert evidence.dns_ok is True
    assert evidence.gateway_ping is not None
    assert "0.0.0.0:22" in evidence.listening_sockets
    assert evidence.tcp_ok is True
    assert evidence.tcp_endpoint == "1.1.1.1:443"
    assert evidence.throughput is None
    assert evidence.transcripts[0].command == "ipconfig /all"
    assert "Windows IP" in evidence.transcripts[0].stdout or "Ethernet adapter" in evidence.transcripts[0].stdout
    wifi = next(item for item in evidence.links if item.name == "Wi-Fi")
    assert wifi.ipv4 == "192.168.1.10"


@pytest.mark.unit
@pytest.mark.infrastructure
def test_collector_records_skips_and_timeouts():
    mapping = {
        ("ipconfig", "/all"): _skip(["ipconfig", "/all"]),
        ("route", "print"): _timeout(["route", "print"]),
        ("arp", "-a"): _ok(["arp", "-a"], ""),
        ("netstat", "-ano"): _skip(["netstat", "-ano"]),
        ("ping", "-n", "3", "1.1.1.1"): _skip(["ping", "-n", "3", "1.1.1.1"]),
        ("nslookup", "example.com"): _timeout(["nslookup", "example.com"]),
    }
    evidence = WindowsProbeCollector(MapRunner(mapping), _settings(enable_traceroute=True)).collect()
    assert "ipconfig /all" in evidence.missing_probes
    assert evidence.dns_ok is None
    assert evidence.default_gateway is None
    assert evidence.traceroute_hops == ()


@pytest.mark.unit
@pytest.mark.infrastructure
def test_collector_tracert_and_http(monkeypatch):
    mapping = _base_mapping()
    mapping[("tracert", "-d", "-h", "5", "-w", "1000", "1.1.1.1")] = _ok(
        ["tracert", "-d", "-h", "5", "-w", "1000", "1.1.1.1"],
        "  1  192.168.1.1\n  2  1.1.1.1\n",
    )
    monkeypatch.setattr(
        "infrastructure.adapters.windows_probe_collector.probe_http",
        lambda url, timeout: True,
    )
    settings = _settings(enable_traceroute=True, http_probe_url="https://example.com")
    evidence = WindowsProbeCollector(MapRunner(mapping), settings).collect()
    assert evidence.traceroute_hops[0] == "192.168.1.1"
    assert evidence.http_ok is True


@pytest.mark.unit
@pytest.mark.infrastructure
def test_collector_unsafe_targets_and_http_fail(monkeypatch):
    mapping = {
        ("ipconfig", "/all"): _ok(["ipconfig", "/all"], IPCONFIG),
        ("route", "print"): _ok(["route", "print"], "10.0.0.0 255.0.0.0 10.0.0.1 10.0.0.2 1\n"),
        ("arp", "-a"): _ok(["arp", "-a"], ""),
        ("netstat", "-ano"): _ok(["netstat", "-ano"], ""),
    }
    monkeypatch.setattr(
        "infrastructure.adapters.windows_probe_collector.probe_http",
        lambda url, timeout: False,
    )
    settings = _settings(
        wan_ping_target="not a host",
        dns_probe_name="also bad",
        enable_traceroute=True,
        http_probe_url="https://example.com",
    )
    evidence = WindowsProbeCollector(MapRunner(mapping), settings).collect()
    assert evidence.default_gateway is None
    assert evidence.wan_ping is None
    assert evidence.dns_ok is None
    assert evidence.http_ok is False
    assert evidence.traceroute_hops == ()


@pytest.mark.unit
@pytest.mark.infrastructure
def test_collector_empty_ping_stdout_and_dns_false():
    mapping = _base_mapping()
    mapping[("ping", "-n", "3", "192.168.1.1")] = _ok(["ping", "-n", "3", "192.168.1.1"], "")
    mapping[("nslookup", "example.com")] = _ok(["nslookup", "example.com"], "")
    evidence = WindowsProbeCollector(MapRunner(mapping), _settings()).collect()
    assert evidence.gateway_ping is not None
    assert evidence.gateway_ping.transmitted is None
    assert evidence.dns_ok is False


@pytest.mark.unit
@pytest.mark.infrastructure
def test_collector_tracert_timeout_and_http_none(monkeypatch):
    mapping = _base_mapping()
    mapping[("tracert", "-d", "-h", "5", "-w", "1000", "1.1.1.1")] = _timeout(
        ["tracert", "-d", "-h", "5", "-w", "1000", "1.1.1.1"]
    )
    monkeypatch.setattr(
        "infrastructure.adapters.windows_probe_collector.probe_http",
        lambda url, timeout: None,
    )
    settings = _settings(enable_traceroute=True, http_probe_url="https://example.com")
    evidence = WindowsProbeCollector(MapRunner(mapping), settings).collect()
    assert evidence.traceroute_hops == ()
    assert evidence.http_ok is None


@pytest.mark.unit
@pytest.mark.infrastructure
def test_collector_ping_timeout_returns_empty_stats():
    mapping = _base_mapping()
    mapping[("ping", "-n", "3", "192.168.1.1")] = _timeout(["ping", "-n", "3", "192.168.1.1"])
    evidence = WindowsProbeCollector(MapRunner(mapping), _settings()).collect()
    assert evidence.gateway_ping is not None
    assert evidence.gateway_ping.loss_pct is None


@pytest.mark.unit
@pytest.mark.infrastructure
def test_collector_iface_falls_back_to_route_ip():
    mapping = _base_mapping()
    mapping[("route", "print")] = _ok(
        ["route", "print"],
        "0.0.0.0 0.0.0.0 192.168.1.1 10.9.8.7 25\n",
    )
    mapping[("ping", "-n", "3", "192.168.1.1")] = _ok(["ping", "-n", "3", "192.168.1.1"], PING)
    evidence = WindowsProbeCollector(MapRunner(mapping), _settings()).collect()
    assert evidence.default_iface == "10.9.8.7"


@pytest.mark.unit
@pytest.mark.infrastructure
def test_collector_speedtest_and_tcp_variants(monkeypatch):
    measured = ThroughputEvidence(download_mbps=12.0, upload_mbps=4.0, bytes_transferred=2000, duration_s=1.0)
    monkeypatch.setattr(
        "infrastructure.adapters.windows_probe_collector.measure_throughput",
        lambda *a, **k: measured,
    )
    ok = WindowsProbeCollector(MapRunner(_base_mapping()), _settings(enable_speedtest=True)).collect()
    assert ok.throughput is measured
    monkeypatch.setattr(
        "infrastructure.adapters.windows_probe_collector.measure_throughput",
        lambda *a, **k: None,
    )
    failed = WindowsProbeCollector(MapRunner(_base_mapping()), _settings(enable_speedtest=True)).collect()
    assert failed.throughput is None
    monkeypatch.setattr(
        "infrastructure.adapters.windows_probe_collector.probe_tcp",
        lambda *a, **k: False,
    )
    refused = WindowsProbeCollector(MapRunner(_base_mapping()), _settings()).collect()
    assert refused.tcp_ok is False
    monkeypatch.setattr(
        "infrastructure.adapters.windows_probe_collector.probe_tcp",
        lambda *a, **k: None,
    )
    unknown = WindowsProbeCollector(MapRunner(_base_mapping()), _settings()).collect()
    assert unknown.tcp_ok is None
