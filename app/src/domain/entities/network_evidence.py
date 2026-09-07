"""Evidencias estruturadas de conectividade do host."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from domain.exceptions import DomainError


class LinkState(Enum):
    """Estado operacional da interface."""

    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"


_LOOPBACK = {"lo", "lo0"}


@dataclass(frozen=True)
class ProbeTranscript:
    """Stdout integral de uma probe allowlisted."""

    command: str
    returncode: int | None
    stdout: str
    skipped: bool
    timed_out: bool

    def __post_init__(self) -> None:
        """Valida o comando da transcript."""
        if not self.command.strip():
            raise DomainError("comando da transcript nao pode ser vazio")


@dataclass(frozen=True)
class ThroughputEvidence:
    """Medicao de download/upload em Mbps."""

    download_mbps: float | None
    upload_mbps: float | None
    bytes_transferred: int
    duration_s: float


@dataclass(frozen=True)
class LinkEvidence:
    """Interface de rede observada."""

    name: str
    state: LinkState
    has_address: bool
    mtu: int | None = None
    ipv4: str | None = None

    def __post_init__(self) -> None:
        """Valida o nome da interface."""
        if not self.name.strip():
            raise DomainError("nome da interface nao pode ser vazio")

    def is_loopback(self) -> bool:
        """Indica se a interface e de loopback (Linux ou Windows)."""
        return self.name in _LOOPBACK or "loopback" in self.name.casefold()


@dataclass(frozen=True)
class NeighborEvidence:
    """Entrada ARP/NUD resumida."""

    address: str
    device: str | None
    state: str | None

    def __post_init__(self) -> None:
        """Valida o endereco do vizinho."""
        if not self.address.strip():
            raise DomainError("endereco de vizinho nao pode ser vazio")


@dataclass(frozen=True)
class PingEvidence:
    """Resultado de probe ICMP."""

    target: str
    transmitted: int | None
    received: int | None
    loss_pct: float | None
    rtt_avg_ms: float | None
    rtt_min_ms: float | None = None
    rtt_max_ms: float | None = None
    jitter_ms: float | None = None

    def __post_init__(self) -> None:
        """Valida o alvo do ping."""
        if not self.target.strip():
            raise DomainError("alvo de ping nao pode ser vazio")

    def is_total_loss(self) -> bool | None:
        """True se perda for 100%."""
        if self.loss_pct is None:
            return None
        return self.loss_pct >= 100.0

    def has_reply(self) -> bool | None:
        """True se houve resposta."""
        if self.received is None:
            return None
        return self.received > 0


@dataclass(frozen=True)
class NetworkEvidence:
    """Snapshot estruturado das probes L1-L4."""

    links: tuple[LinkEvidence, ...]
    neighbors: tuple[NeighborEvidence, ...]
    default_gateway: str | None
    default_iface: str | None
    gateway_ping: PingEvidence | None
    wan_ping: PingEvidence | None
    dns_ok: bool | None
    dns_name: str
    wan_target: str
    listening_sockets: tuple[str, ...]
    missing_probes: tuple[str, ...]
    traceroute_hops: tuple[str, ...] = ()
    http_ok: bool | None = None
    http_url: str | None = None
    transcripts: tuple[ProbeTranscript, ...] = ()
    throughput: ThroughputEvidence | None = None
    tcp_ok: bool | None = None
    tcp_endpoint: str | None = None
    min_download_mbps: float = 0.0
    min_upload_mbps: float = 0.0

    def __post_init__(self) -> None:
        """Valida nomes de probe DNS/WAN."""
        if not self.dns_name.strip():
            raise DomainError("nome DNS de probe nao pode ser vazio")
        if not self.wan_target.strip():
            raise DomainError("alvo WAN de probe nao pode ser vazio")

    def has_up_addressed_link(self) -> bool:
        """True se existe iface nao-loopback UP com endereco."""
        return any((not link.is_loopback()) and link.state is LinkState.UP and link.has_address for link in self.links)
