"""Testes dos parsers de probes Windows."""

import pytest

from domain.entities.network_evidence import LinkState
from infrastructure.adapters.probe_parsers import (
    is_safe_host,
    parse_arp,
    parse_ipconfig,
    parse_netstat,
    parse_nslookup,
    parse_ping,
    parse_route_print,
    parse_tracert_hops,
)


IPCONFIG_EN = """
Windows IP Configuration

Ethernet adapter Ethernet:

   Media State . . . . . . . . . . . : Media disconnected
   Description . . . . . . . . . . . : Intel Ethernet

Wireless LAN adapter Wi-Fi:

   Connection-specific DNS Suffix  . : lan
   IPv4 Address. . . . . . . . . . . : 192.168.1.10(Preferred)
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : 192.168.1.1

Tunnel adapter isatap.{guid}:

   Media State . . . . . . . . . . . : Media disconnected
"""

IPCONFIG_PT = """
Configuracao de IP do Windows

Adaptador de Ethernet Ethernet:

   Estado da midia . . . . . . . . . : Midia desconectada

Adaptador de LAN sem fio Wi-Fi:

   Endereco IPv4 . . . . . . . . . . : 10.0.0.5
   Mascara de Sub-rede . . . . . . . : 255.255.255.0
"""


@pytest.mark.unit
@pytest.mark.infrastructure
def test_is_safe_host_accepts_ip_and_hostname():
    assert is_safe_host("1.1.1.1") is True
    assert is_safe_host("::1") is True
    assert is_safe_host("example.com") is True
    assert is_safe_host("bad name") is False
    assert is_safe_host("") is False
    assert is_safe_host("a." + "b" * 64) is False
    assert is_safe_host("a" * 254) is False
    assert is_safe_host("example.com.") is False


@pytest.mark.unit
@pytest.mark.infrastructure
def test_parse_ipconfig_english_up_down_and_unknown():
    links, mapping = parse_ipconfig(IPCONFIG_EN)
    by_name = {item.name: item for item in links}
    assert by_name["Ethernet"].state is LinkState.DOWN
    assert by_name["Ethernet"].has_address is False
    assert by_name["Wi-Fi"].state is LinkState.UP
    assert by_name["Wi-Fi"].has_address is True
    assert by_name["Wi-Fi"].ipv4 == "192.168.1.10"
    assert mapping["192.168.1.10"] == "Wi-Fi"
    assert by_name["isatap.{guid}"].state is LinkState.DOWN


@pytest.mark.unit
@pytest.mark.infrastructure
def test_parse_ipconfig_portuguese_and_no_address_unknown():
    links, mapping = parse_ipconfig(IPCONFIG_PT)
    by_name = {item.name: item for item in links}
    assert by_name["Ethernet"].state is LinkState.DOWN
    assert by_name["Wi-Fi"].state is LinkState.UP
    assert mapping["10.0.0.5"] == "Wi-Fi"
    assert by_name["Wi-Fi"].ipv4 == "10.0.0.5"
    empty, _ = parse_ipconfig("Wireless LAN adapter Bare:\n   Description : x\n")
    assert empty[0].state is LinkState.UNKNOWN
    assert empty[0].has_address is False
    accent, _ = parse_ipconfig("Ethernet adapter Eth:\n   Estado da midia : Mídia desconectada\n")
    assert accent[0].state is LinkState.DOWN


@pytest.mark.unit
@pytest.mark.infrastructure
def test_parse_route_print_variants():
    stdout = (
        "Network Destination        Netmask          Gateway       Interface  Metric\n"
        "          0.0.0.0          0.0.0.0      192.168.1.1     192.168.1.10     35\n"
        "        127.0.0.0        255.0.0.0         On-link         127.0.0.1    331\n"
    )
    assert parse_route_print(stdout) == ("192.168.1.1", "192.168.1.10")
    assert parse_route_print("10.0.0.0 255.0.0.0 10.0.0.1 10.0.0.2 1\n") == (None, None)
    assert parse_route_print("0.0.0.0 0.0.0.0 On-link 192.168.1.10 1\n") == (None, None)
    assert parse_route_print("0.0.0.0 0.0.0.0 0.0.0.0 192.168.1.10 1\n") == (None, None)
    assert parse_route_print("0.0.0.0 0.0.0.0 not_a_host 192.168.1.10 1\n") == (None, None)
    assert parse_route_print("0.0.0.0 0.0.0.0 192.168.1.1 not_a_host 1\n") == ("192.168.1.1", None)
    assert parse_route_print("short\n") == (None, None)


@pytest.mark.unit
@pytest.mark.infrastructure
def test_parse_arp_netstat_nslookup():
    neigh = parse_arp(
        "Interface: 192.168.1.10 --- 0xc\n"
        "  Internet Address      Physical Address      Type\n"
        "  192.168.1.1           aa-bb-cc-dd-ee-ff     dynamic\n"
        "  bad_host              aa-bb-cc-dd-ee-ff     static\n"
        "Interface :\n"
        "  10.0.0.2              aa-bb-cc-dd-ee-00     static\n"
    )
    assert neigh[0].device == "192.168.1.10"
    assert neigh[0].state == "dynamic"
    assert neigh[1].device is None
    sockets = parse_netstat(
        "  Proto  Local Address          Foreign Address        State           PID\n"
        "  TCP    0.0.0.0:22             0.0.0.0:0              LISTENING       1234\n"
        "  TCP    [::]:445               [::]:0                 OUVINDO         4\n"
        "  UDP    0.0.0.0:53             *:*                                    88\n"
        "  TCP\n"
    )
    assert "0.0.0.0:22" in sockets
    assert "[::]:445" in sockets
    assert parse_nslookup("Server: dns\nAddress: 1.1.1.1\nName: example.com\nAddress: 93.184.216.34\n") is True
    assert parse_nslookup("Nome: example.com\n") is True
    assert parse_nslookup("*** UnKnown can't find example.com: Non-existent domain\n") is False
    assert parse_nslookup("nao encontrado\n") is False
    assert parse_nslookup("domínio não encontrado\n") is False
    assert parse_nslookup("\n") is False


@pytest.mark.unit
@pytest.mark.infrastructure
def test_parse_ping_english_portuguese_and_empty():
    en = (
        "Packets: Sent = 3, Received = 3, Lost = 0 (0% loss),\n"
        "Approximate round trip times in milli-seconds:\n"
        "    Minimum = 1ms, Maximum = 2ms, Average = 4ms\n"
    )
    ping = parse_ping(en, "1.1.1.1")
    assert ping.loss_pct == 0.0
    assert ping.rtt_avg_ms == 4.0
    pt = (
        "Resposta de 1.1.1.1: bytes=32 tempo=2ms TTL=64\n"
        "Pacotes: Enviados = 3, Recebidos = 0, Perdidos = 3 (100% de perda),\n    Media = 1ms\n"
    )
    lost = parse_ping(pt, "1.1.1.1")
    assert lost.received == 0
    assert lost.loss_pct == 100.0
    assert parse_ping("no stats", "1.1.1.1").transmitted is None
    no_rtt = parse_ping("Packets: Sent = 1, Received = 1, Lost = 0 (0% loss),\n", "1.1.1.1")
    assert no_rtt.rtt_avg_ms is None
    samples = (
        "Reply from 1.1.1.1: bytes=32 time=1ms TTL=64\n"
        "Reply from 1.1.1.1: bytes=32 time=3ms TTL=64\n"
        "Packets: Sent = 2, Received = 2, Lost = 0 (0% loss),\n"
        "    Minimum = 0ms, Maximum = 0ms, Average = 0ms\n"
    )
    sampled = parse_ping(samples, "1.1.1.1")
    assert sampled.rtt_min_ms == 1.0
    assert sampled.rtt_max_ms == 3.0
    assert sampled.rtt_avg_ms == 2.0
    assert sampled.jitter_ms == 2.0
    sub1 = parse_ping(
        "Reply from 192.168.1.1: bytes=32 time<1ms TTL=128\n"
        "Packets: Sent = 1, Received = 1, Lost = 0 (0% loss),\n"
        "    Average = 0ms\n",
        "192.168.1.1",
    )
    assert sub1.rtt_avg_ms == 0.5
    summary = parse_ping(
        "Packets: Sent = 3, Received = 3, Lost = 0 (0% loss),\n    Minimum = 1ms, Maximum = 5ms, Average = 2ms\n",
        "1.1.1.1",
    )
    assert summary.rtt_min_ms == 1.0
    assert summary.rtt_max_ms == 5.0
    assert summary.jitter_ms == 4.0


@pytest.mark.unit
@pytest.mark.infrastructure
def test_parse_tracert_hops():
    hops = parse_tracert_hops("  1    1 ms    1 ms    1 ms  192.168.1.1\n  2    *    *    *  Request timed out.\n")
    assert hops[0] == "192.168.1.1"
    assert parse_tracert_hops("  1: *\n") == ()
