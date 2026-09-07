"""Porta de coleta de evidencias de rede."""

from typing import Protocol

from domain.entities.network_evidence import NetworkEvidence


class ProbeCollectorPort(Protocol):
    """Contrato para coletar evidencias no host."""

    def collect(self) -> NetworkEvidence:
        """Retorna o snapshot estruturado das probes."""
        ...
