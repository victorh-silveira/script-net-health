"""Relatorio de diagnostico NetOps no formato obrigatorio."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from domain.entities.network_evidence import ProbeTranscript
from domain.exceptions import DomainError


class Impact(Enum):
    """Escopo do impacto."""

    LAN = "LAN"
    WAN = "WAN"
    SERVICE = "Especifico de Servico"
    NONE = "Nenhum"


class TcpIpLayer(Enum):
    """Camada da pilha TCP/IP de 4 niveis."""

    ACCESS = "Acesso"
    INTERNET = "Internet"
    TRANSPORT = "Transporte"
    APPLICATION = "Aplicacao"
    NONE = "Nenhuma"


class Severity(Enum):
    """Gravidade operacional."""

    LOW = "Baixa"
    MEDIUM = "Media"
    HIGH = "Alta"
    CRITICAL = "Critica"


class FindingStatus(Enum):
    """Status da evidencia na camada."""

    OK = "ok"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class LayerFinding:
    """Achado de uma camada TCP/IP."""

    layer: TcpIpLayer
    status: FindingStatus
    evidence: str

    def __post_init__(self) -> None:
        """Valida o texto de evidencia."""
        if not self.evidence.strip():
            raise DomainError("evidencia da camada nao pode ser vazia")
        if self.layer is TcpIpLayer.NONE:
            raise DomainError("finding nao pode usar camada Nenhuma")


@dataclass(frozen=True)
class DiagnosisReport:
    """Relatorio BOTTOM-UP formatado para o operador."""

    impact: Impact
    probable_layer: TcpIpLayer
    severity: Severity
    preliminary: str
    findings: tuple[LayerFinding, ...]
    root_cause: str
    validation_commands: tuple[str, ...]
    mitigation_steps: tuple[str, ...]
    transcripts: tuple[ProbeTranscript, ...] = ()

    def __post_init__(self) -> None:
        """Valida textos obrigatorios e as quatro camadas."""
        if not self.preliminary.strip():
            raise DomainError("diagnostico preliminar nao pode ser vazio")
        if not self.root_cause.strip():
            raise DomainError("causa raiz nao pode ser vazia")
        layers = {item.layer for item in self.findings}
        expected = {TcpIpLayer.ACCESS, TcpIpLayer.INTERNET, TcpIpLayer.TRANSPORT, TcpIpLayer.APPLICATION}
        if layers != expected:
            raise DomainError("relatorio deve conter as quatro camadas TCP/IP")

    def executive_status(self) -> str:
        """Deriva o status do resumo a partir dos achados."""
        statuses = {item.status for item in self.findings}
        if FindingStatus.FAILED in statuses:
            return "Falha"
        if FindingStatus.DEGRADED in statuses:
            return "Degradado"
        if FindingStatus.UNKNOWN in statuses:
            return "Inconclusivo"
        return "Saudavel"

    def as_text(self) -> str:
        """Formata o payload no contrato de resposta NetOps."""
        by_layer = {item.layer: item for item in self.findings}
        access = by_layer[TcpIpLayer.ACCESS]
        internet = by_layer[TcpIpLayer.INTERNET]
        transport = by_layer[TcpIpLayer.TRANSPORT]
        application = by_layer[TcpIpLayer.APPLICATION]
        commands = "; ".join(self.validation_commands) if self.validation_commands else "nenhum"
        steps = "; ".join(self.mitigation_steps) if self.mitigation_steps else "nenhum"
        return (
            "#### 1. Resumo Executivo\n"
            f"- **Status:** {self.executive_status()}\n"
            f"- **Impacto:** {self.impact.value}\n"
            f"- **Camada Provavel da Falha:** {self.probable_layer.value}\n"
            f"- **Gravidade:** {self.severity.value}\n"
            f"- **Diagnostico Preliminar:** {self.preliminary}\n"
            "\n"
            "#### 2. Analise por Camadas (TCP/IP)\n"
            f"- **Acesso a Rede [{access.status.value}]:** {access.evidence}\n"
            f"- **Internet (Rede) [{internet.status.value}]:** {internet.evidence}\n"
            f"- **Transporte [{transport.status.value}]:** {transport.evidence}\n"
            f"- **Aplicacao [{application.status.value}]:** {application.evidence}\n"
            "\n"
            "#### 3. Causa Raiz Mais Provavel\n"
            f"{self.root_cause}\n"
            "\n"
            "#### 4. Plano de Acao e Troubleshooting\n"
            f"- **Comandos de Validacao Imediata:** {commands}\n"
            f"- **Passos para Mitigacao/Resolucao:** {steps}\n"
            "\n"
            "#### 5. Evidencias brutas\n"
            f"{_format_transcripts(self.transcripts)}"
        )


def _format_transcripts(transcripts: tuple[ProbeTranscript, ...]) -> str:
    """Monta blocos de stdout por comando."""
    if not transcripts:
        return "(nenhuma transcript coletada)"
    blocks: list[str] = []
    for item in transcripts:
        if item.skipped:
            exit_label = "skipped"
        elif item.timed_out:
            exit_label = "timeout"
        elif item.returncode is None:
            exit_label = "exit ?"
        else:
            exit_label = f"exit {item.returncode}"
        payload = item.stdout if item.stdout else "(sem stdout)"
        blocks.append(f"=== {item.command} ({exit_label}) ===\n{payload}")
    return "\n\n".join(blocks)
