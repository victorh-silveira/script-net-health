"""Parsers de saida de probes Windows."""

from __future__ import annotations

import ipaddress
import re

from domain.entities.network_evidence import LinkEvidence, LinkState, NeighborEvidence, PingEvidence


_ADAPTER_EN = re.compile(r"(?i)^.+\badapter\s+(.+):\s*$")
_ADAPTER_PT = re.compile(r"(?i)^adaptador(?:\s+de)?(?:\s+(?:ethernet|lan sem fio|bluetooth))?\s+(.+):\s*$")
_IPV4 = re.compile(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b")
_PING_EN = re.compile(r"Sent = (\d+).*?Received = (\d+).*?Lost = \d+ \((\d+(?:\.\d+)?)%", re.IGNORECASE | re.DOTALL)
_PING_PT = re.compile(
    r"Enviados = (\d+).*?Recebidos = (\d+).*?Perdidos = \d+ \((\d+(?:\.\d+)?)%",
    re.IGNORECASE | re.DOTALL,
)
_RTT_EN = re.compile(r"Average = (\d+(?:\.\d+)?)ms", re.IGNORECASE)
_RTT_PT = re.compile(r"M[eé]dia = (\d+(?:\.\d+)?)ms", re.IGNORECASE)
_RTT_MIN_EN = re.compile(r"Minimum = (\d+(?:\.\d+)?)ms", re.IGNORECASE)
_RTT_MAX_EN = re.compile(r"Maximum = (\d+(?:\.\d+)?)ms", re.IGNORECASE)
_RTT_MIN_PT = re.compile(r"M[ií]nimo = (\d+(?:\.\d+)?)ms", re.IGNORECASE)
_RTT_MAX_PT = re.compile(r"M[aá]ximo = (\d+(?:\.\d+)?)ms", re.IGNORECASE)
_REPLY_TIME = re.compile(r"(?i)(?:time|tempo)\s*=\s*(\d+(?:\.\d+)?)\s*ms")
_REPLY_LT1 = re.compile(r"(?i)(?:time|tempo)\s*<\s*1\s*ms")
_DEFAULT_DEST = ".".join(("0",) * 4)


def is_safe_host(value: str) -> bool:
    """Aceita IPv4/IPv6 ou hostname DNS simples."""
    stripped = value.strip()
    if not stripped or len(stripped) > 253 or any(ch.isspace() for ch in stripped):
        return False
    try:
        ipaddress.ip_address(stripped)
    except ValueError:
        labels = stripped.split(".")
        if not labels or any(not label or len(label) > 63 for label in labels):
            return False
        return all(ch.isalnum() or ch == "-" for label in labels for ch in label)
    return True


def _adapter_name(line: str) -> str | None:
    """Extrai o nome do adaptador de uma linha de ipconfig."""
    stripped = line.strip()
    match = _ADAPTER_EN.match(stripped)
    if match:
        return match.group(1).strip()
    match = _ADAPTER_PT.match(stripped)
    if match:
        return match.group(1).strip()
    return None


def parse_ipconfig(stdout: str) -> tuple[tuple[LinkEvidence, ...], dict[str, str]]:
    """Interpreta `ipconfig /all` em EN/PT-BR."""
    links: list[LinkEvidence] = []
    ipv4_to_name: dict[str, str] = {}
    name: str | None = None
    disconnected = False
    addresses: list[str] = []

    def flush() -> None:
        """Fecha o adaptador em construcao."""
        nonlocal name, disconnected, addresses
        if name is None:
            return
        if disconnected:
            state = LinkState.DOWN
        elif addresses:
            state = LinkState.UP
        else:
            state = LinkState.UNKNOWN
        ipv4 = addresses[0] if addresses else None
        links.append(LinkEvidence(name=name, state=state, has_address=bool(addresses), ipv4=ipv4))
        for ip_text in addresses:
            ipv4_to_name[ip_text] = name
        name = None
        disconnected = False
        addresses = []

    for raw in stdout.splitlines():
        adapter = _adapter_name(raw)
        if adapter is not None:
            flush()
            name = adapter
            continue
        if name is None:
            continue
        lower = raw.casefold()
        if "media disconnected" in lower or "midia desconectada" in lower or "mídia desconectada" in lower:
            disconnected = True
        if "ipv4" in lower and "mask" not in lower and "mascara" not in lower and "máscara" not in lower:
            for ip_text in _IPV4.findall(raw):
                if is_safe_host(ip_text) and not ip_text.startswith("255."):
                    addresses.append(ip_text)
    flush()
    return tuple(links), ipv4_to_name


def parse_route_print(stdout: str) -> tuple[str | None, str | None]:
    """Extrai gateway e IP da iface da rota default IPv4."""
    for raw in stdout.splitlines():
        parts = raw.split()
        if len(parts) < 4 or parts[0] != _DEFAULT_DEST or parts[1] != _DEFAULT_DEST:
            continue
        gateway, iface_ip = parts[2], parts[3]
        if gateway.casefold() in {"on-link"} or gateway == _DEFAULT_DEST:
            continue
        if is_safe_host(gateway):
            iface = iface_ip if is_safe_host(iface_ip) else None
            return gateway, iface
    return None, None


def parse_arp(stdout: str) -> tuple[NeighborEvidence, ...]:
    """Interpreta `arp -a`."""
    items: list[NeighborEvidence] = []
    current_dev: str | None = None
    for raw in stdout.splitlines():
        lower = raw.casefold()
        if lower.startswith("interface:") or lower.startswith("interface :"):
            found = _IPV4.findall(raw)
            current_dev = found[0] if found else None
            continue
        parts = raw.split()
        if len(parts) < 3:
            continue
        try:
            ipaddress.ip_address(parts[0])
        except ValueError:
            continue
        items.append(NeighborEvidence(address=parts[0], device=current_dev, state=parts[-1]))
    return tuple(items)


def parse_ping(stdout: str, target: str) -> PingEvidence:
    """Interpreta estatisticas de ping do Windows (EN/PT-BR)."""
    match = _PING_EN.search(stdout) or _PING_PT.search(stdout)
    if match is None:
        return PingEvidence(target=target, transmitted=None, received=None, loss_pct=None, rtt_avg_ms=None)
    samples = _ping_samples(stdout)
    rtt_match = _RTT_EN.search(stdout) or _RTT_PT.search(stdout)
    rtt_avg = float(rtt_match.group(1)) if rtt_match else None
    rtt_min = _first_float(_RTT_MIN_EN.search(stdout) or _RTT_MIN_PT.search(stdout))
    rtt_max = _first_float(_RTT_MAX_EN.search(stdout) or _RTT_MAX_PT.search(stdout))
    jitter = None
    if samples:
        rtt_min = min(samples)
        rtt_max = max(samples)
        rtt_avg = sum(samples) / len(samples)
        jitter = rtt_max - rtt_min
    elif rtt_min is not None and rtt_max is not None:
        jitter = rtt_max - rtt_min
    return PingEvidence(
        target=target,
        transmitted=int(match.group(1)),
        received=int(match.group(2)),
        loss_pct=float(match.group(3)),
        rtt_avg_ms=rtt_avg,
        rtt_min_ms=rtt_min,
        rtt_max_ms=rtt_max,
        jitter_ms=jitter,
    )


def _ping_samples(stdout: str) -> list[float]:
    """Coleta amostras de RTT das linhas de reply."""
    values: list[float] = []
    for raw in stdout.splitlines():
        if _REPLY_LT1.search(raw):
            values.append(0.5)
            continue
        found = _REPLY_TIME.search(raw)
        if found:
            values.append(float(found.group(1)))
    return values


def _first_float(match: re.Match[str] | None) -> float | None:
    """Extrai o primeiro grupo numerico de um match."""
    if match is None:
        return None
    return float(match.group(1))


def parse_netstat(stdout: str) -> tuple[str, ...]:
    """Extrai endpoints LISTENING de `netstat -ano`."""
    sockets: list[str] = []
    for raw in stdout.splitlines():
        upper = raw.upper()
        if "LISTENING" not in upper and "OUVINDO" not in upper:
            continue
        parts = raw.split()
        if len(parts) < 2:
            continue
        sockets.append(parts[1])
    return tuple(sockets)


def parse_nslookup(stdout: str) -> bool:
    """True se nslookup devolveu um nome resolvido."""
    lower = stdout.casefold()
    if "non-existent" in lower or "can't find" in lower or "nao encontrado" in lower or "não encontrado" in lower:
        return False
    return "name:" in lower or "nome:" in lower


def parse_tracert_hops(stdout: str) -> tuple[str, ...]:
    """Coleta IPv4 vistos em tracert."""
    hops: list[str] = []
    for raw in stdout.splitlines():
        for ip_text in _IPV4.findall(raw):
            if ip_text not in hops and is_safe_host(ip_text):
                hops.append(ip_text)
    return tuple(hops)
