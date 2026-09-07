"""Regras de achado por camada TCP/IP (sem IO)."""

from __future__ import annotations

from domain.constants import LAN_JITTER_DEGRADED_MS, LOSS_DEGRADED_PCT, WAN_JITTER_DEGRADED_MS
from domain.entities.diagnosis_report import FindingStatus, LayerFinding, TcpIpLayer
from domain.entities.network_evidence import LinkEvidence, LinkState, NetworkEvidence, PingEvidence, ThroughputEvidence


def access_finding(evidence: NetworkEvidence) -> LayerFinding:
    """Avalia enlace e endereco nas ifaces de dados."""
    links = [item for item in evidence.links if not item.is_loopback()]
    if not links:
        if "ipconfig /all" in evidence.missing_probes:
            text = "nao verificado: probe ipconfig /all ausente ou falhou"
            return LayerFinding(TcpIpLayer.ACCESS, FindingStatus.UNKNOWN, text)
        return LayerFinding(TcpIpLayer.ACCESS, FindingStatus.FAILED, "nenhuma interface de dados observada")
    up_addr = [item for item in links if item.state is LinkState.UP and item.has_address]
    down = [item for item in links if item.state is LinkState.DOWN]
    names = ", ".join(_link_label(item) for item in links)
    extra = f"ARP/NUD entradas={len(evidence.neighbors)}"
    if up_addr and down:
        text = f"ifaces {names}; {extra}; UP com endereco em {up_addr[0].name}"
        return LayerFinding(TcpIpLayer.ACCESS, FindingStatus.DEGRADED, text)
    if up_addr:
        mtu = up_addr[0].mtu
        mtu_txt = f" MTU={mtu}" if mtu is not None else ""
        return LayerFinding(TcpIpLayer.ACCESS, FindingStatus.OK, f"ifaces {names}{mtu_txt}; {extra}")
    return LayerFinding(TcpIpLayer.ACCESS, FindingStatus.FAILED, f"ifaces {names}; nenhuma UP com endereco; {extra}")


def internet_finding(evidence: NetworkEvidence) -> LayerFinding:
    """Avalia rota default e ICMP de gateway/WAN."""
    gw = evidence.default_gateway
    iface = evidence.default_iface
    if gw is None:
        if "route print" in evidence.missing_probes:
            return LayerFinding(
                TcpIpLayer.INTERNET,
                FindingStatus.UNKNOWN,
                "nao verificado: probe route print ausente ou falhou",
            )
        return LayerFinding(TcpIpLayer.INTERNET, FindingStatus.FAILED, "sem rota default (gateway ausente)")
    route = f"default via {gw}" + (f" dev {iface}" if iface else "")
    gw_txt = ping_text("gateway", evidence.gateway_ping)
    wan_txt = ping_text("WAN", evidence.wan_ping)
    hops = f" traceroute_hops={len(evidence.traceroute_hops)}" if evidence.traceroute_hops else ""
    text = f"{route}; {gw_txt}; {wan_txt}{hops}"
    if _total_loss(evidence.gateway_ping):
        return LayerFinding(TcpIpLayer.INTERNET, FindingStatus.FAILED, text)
    if _has_reply(evidence.gateway_ping) and _total_loss(evidence.wan_ping):
        return LayerFinding(TcpIpLayer.INTERNET, FindingStatus.FAILED, text)
    if _has_reply(evidence.gateway_ping) and _has_reply(evidence.wan_ping):
        if _degraded_path(evidence.gateway_ping, LAN_JITTER_DEGRADED_MS) or _degraded_path(
            evidence.wan_ping, WAN_JITTER_DEGRADED_MS
        ):
            return LayerFinding(TcpIpLayer.INTERNET, FindingStatus.DEGRADED, text)
        return LayerFinding(TcpIpLayer.INTERNET, FindingStatus.OK, text)
    return LayerFinding(TcpIpLayer.INTERNET, FindingStatus.UNKNOWN, text)


def transport_finding(evidence: NetworkEvidence) -> LayerFinding:
    """Avalia perda/jitter ICMP e TCP; sockets LISTEN sao nota, nao criterio de OK."""
    parts = [ping_text("gw", evidence.gateway_ping), ping_text("WAN", evidence.wan_ping)]
    if evidence.tcp_endpoint:
        if evidence.tcp_ok is True:
            parts.append(f"TCP {evidence.tcp_endpoint} abriu")
        elif evidence.tcp_ok is False:
            parts.append(f"TCP {evidence.tcp_endpoint} recusou/timeout")
        else:
            parts.append(f"TCP {evidence.tcp_endpoint} nao verificado")
    else:
        parts.append("TCP nao verificado")
    parts.append(f"LISTEN locais={len(evidence.listening_sockets)}")
    text = "; ".join(parts)
    if _total_loss(evidence.gateway_ping) and _total_loss(evidence.wan_ping):
        return LayerFinding(TcpIpLayer.TRANSPORT, FindingStatus.FAILED, text)
    if evidence.tcp_ok is False and _has_reply(evidence.wan_ping):
        return LayerFinding(TcpIpLayer.TRANSPORT, FindingStatus.FAILED, text)
    if _has_reply(evidence.gateway_ping) and _has_reply(evidence.wan_ping) and evidence.tcp_ok is not False:
        if _degraded_path(evidence.wan_ping, WAN_JITTER_DEGRADED_MS) or _degraded_path(
            evidence.gateway_ping, LAN_JITTER_DEGRADED_MS
        ):
            return LayerFinding(TcpIpLayer.TRANSPORT, FindingStatus.DEGRADED, text)
        return LayerFinding(TcpIpLayer.TRANSPORT, FindingStatus.OK, text)
    return LayerFinding(TcpIpLayer.TRANSPORT, FindingStatus.UNKNOWN, text)


def application_finding(evidence: NetworkEvidence) -> LayerFinding:
    """Avalia DNS, HTTP opcional e throughput."""
    parts: list[str] = []
    status = FindingStatus.UNKNOWN
    if evidence.dns_ok is None:
        parts.append(f"DNS {evidence.dns_name} nao verificado")
    elif evidence.dns_ok:
        parts.append(f"DNS {evidence.dns_name} resolveu")
        status = FindingStatus.OK
    else:
        parts.append(f"DNS {evidence.dns_name} falhou")
        status = FindingStatus.FAILED
    if evidence.http_url:
        if evidence.http_ok is None:
            parts.append(f"HTTP {evidence.http_url} nao verificado")
        elif evidence.http_ok:
            parts.append(f"HTTP {evidence.http_url} respondeu")
        else:
            parts.append(f"HTTP {evidence.http_url} falhou")
            status = FindingStatus.FAILED
    parts.append(_throughput_text(evidence.throughput))
    if status is not FindingStatus.FAILED and _below_sla(evidence):
        status = FindingStatus.DEGRADED
    return LayerFinding(TcpIpLayer.APPLICATION, status, "; ".join(parts))


def ping_text(label: str, ping: PingEvidence | None) -> str:
    """Formata perda e RTT de uma probe ICMP."""
    if ping is None:
        return f"{label} ping nao verificado"
    if ping.loss_pct is None:
        return f"{label} ping {ping.target} sem estatistica"
    rtt = f" rtt={_rtt_label(ping)}" if ping.rtt_avg_ms is not None or ping.has_reply() else ""
    jitter = f" jitter={ping.jitter_ms}ms" if ping.jitter_ms is not None else ""
    return f"{label} ping {ping.target} loss={ping.loss_pct}%{rtt}{jitter}"


def _link_label(item: LinkEvidence) -> str:
    """Monta rotulo nome/ipv4=estado."""
    addr = f"/{item.ipv4}" if item.ipv4 else ""
    return f"{item.name}{addr}={item.state.value}"


def _rtt_label(ping: PingEvidence) -> str:
    """Resume min/med/max ou <1ms quando a media Windows e zero."""
    if ping.has_reply() and (ping.rtt_avg_ms is None or ping.rtt_avg_ms == 0):
        return "<1ms"
    if ping.rtt_min_ms is not None and ping.rtt_max_ms is not None and ping.rtt_avg_ms is not None:
        return f"min={ping.rtt_min_ms}ms med={ping.rtt_avg_ms}ms max={ping.rtt_max_ms}ms"
    if ping.rtt_avg_ms is not None:
        return f"med={ping.rtt_avg_ms}ms"
    return "n/d"


def _total_loss(ping: PingEvidence | None) -> bool:
    """True se ICMP teve 100% de perda."""
    return ping is not None and ping.is_total_loss() is True


def _has_reply(ping: PingEvidence | None) -> bool:
    """True se ICMP teve resposta."""
    return ping is not None and ping.has_reply() is True


def _degraded_path(ping: PingEvidence | None, jitter_limit: float) -> bool:
    """True se perda parcial ou jitter acima do limiar."""
    if ping is None:
        return False
    if ping.loss_pct is not None and ping.loss_pct > LOSS_DEGRADED_PCT and ping.loss_pct < 100.0:
        return True
    return ping.jitter_ms is not None and ping.jitter_ms > jitter_limit


def _throughput_text(item: ThroughputEvidence | None) -> str:
    """Formata Mbps de download/upload."""
    if item is None:
        return "throughput nao medido"
    down = f"{item.download_mbps:.2f}Mbps" if item.download_mbps is not None else "n/d"
    up = f"{item.upload_mbps:.2f}Mbps" if item.upload_mbps is not None else "n/d"
    return f"throughput down={down} up={up}"


def _below_sla(evidence: NetworkEvidence) -> bool:
    """True se a medicao ficou abaixo do minimo configurado."""
    tp = evidence.throughput
    if tp is None:
        return False
    if (
        evidence.min_download_mbps > 0
        and tp.download_mbps is not None
        and tp.download_mbps < evidence.min_download_mbps
    ):
        return True
    return evidence.min_upload_mbps > 0 and tp.upload_mbps is not None and tp.upload_mbps < evidence.min_upload_mbps
