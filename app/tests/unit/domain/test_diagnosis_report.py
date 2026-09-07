"""Testes do relatorio de diagnostico."""

import pytest

from domain.entities.diagnosis_report import (
    DiagnosisReport,
    FindingStatus,
    Impact,
    LayerFinding,
    Severity,
    TcpIpLayer,
)
from domain.entities.network_evidence import ProbeTranscript
from domain.exceptions import DomainError


def _findings() -> tuple[LayerFinding, ...]:
    return (
        LayerFinding(TcpIpLayer.ACCESS, FindingStatus.OK, "up"),
        LayerFinding(TcpIpLayer.INTERNET, FindingStatus.OK, "gw"),
        LayerFinding(TcpIpLayer.TRANSPORT, FindingStatus.OK, "ss"),
        LayerFinding(TcpIpLayer.APPLICATION, FindingStatus.OK, "dns"),
    )


def _report(**overrides: object) -> DiagnosisReport:
    payload: dict[str, object] = {
        "impact": Impact.LAN,
        "probable_layer": TcpIpLayer.ACCESS,
        "severity": Severity.HIGH,
        "preliminary": "Enlace caiu.",
        "findings": _findings(),
        "root_cause": "Iface DOWN.",
        "validation_commands": (),
        "mitigation_steps": (),
    }
    payload.update(overrides)
    return DiagnosisReport(**payload)


@pytest.mark.unit
@pytest.mark.domain
def test_layer_finding_rejects_blank_evidence():
    with pytest.raises(DomainError):
        LayerFinding(TcpIpLayer.ACCESS, FindingStatus.OK, "  ")


@pytest.mark.unit
@pytest.mark.domain
def test_layer_finding_rejects_none_layer():
    with pytest.raises(DomainError):
        LayerFinding(TcpIpLayer.NONE, FindingStatus.OK, "x")


@pytest.mark.unit
@pytest.mark.domain
def test_report_rejects_blank_preliminary_and_root_cause():
    with pytest.raises(DomainError):
        _report(preliminary=" ")
    with pytest.raises(DomainError):
        _report(root_cause="")


@pytest.mark.unit
@pytest.mark.domain
def test_report_requires_four_layers():
    with pytest.raises(DomainError, match="quatro camadas"):
        _report(findings=_findings()[:3], validation_commands=("ip route",), mitigation_steps=("checar",))


@pytest.mark.unit
@pytest.mark.domain
def test_as_text_matches_contract_and_empty_lists():
    text = _report().as_text()
    assert "#### 1. Resumo Executivo" in text
    assert "- **Status:** Saudavel" in text
    assert "- **Impacto:** LAN" in text
    assert "- **Camada Provavel da Falha:** Acesso" in text
    assert "- **Gravidade:** Alta" in text
    assert "#### 2. Analise por Camadas (TCP/IP)" in text
    assert "- **Acesso a Rede [ok]:** up" in text
    assert "- **Internet (Rede) [ok]:** gw" in text
    assert "- **Transporte [ok]:** ss" in text
    assert "- **Aplicacao [ok]:** dns" in text
    assert "#### 3. Causa Raiz Mais Provavel" in text
    assert "#### 4. Plano de Acao e Troubleshooting" in text
    assert "- **Comandos de Validacao Imediata:** nenhum" in text
    assert "- **Passos para Mitigacao/Resolucao:** nenhum" in text
    assert "#### 5. Evidencias brutas" in text
    assert "(nenhuma transcript coletada)" in text


@pytest.mark.unit
@pytest.mark.domain
def test_executive_status_and_transcript_blocks():
    failed = _report(
        findings=(
            LayerFinding(TcpIpLayer.ACCESS, FindingStatus.FAILED, "down"),
            LayerFinding(TcpIpLayer.INTERNET, FindingStatus.OK, "gw"),
            LayerFinding(TcpIpLayer.TRANSPORT, FindingStatus.OK, "ss"),
            LayerFinding(TcpIpLayer.APPLICATION, FindingStatus.OK, "dns"),
        )
    )
    assert failed.executive_status() == "Falha"
    degraded = _report(
        findings=(
            LayerFinding(TcpIpLayer.ACCESS, FindingStatus.DEGRADED, "mix"),
            LayerFinding(TcpIpLayer.INTERNET, FindingStatus.OK, "gw"),
            LayerFinding(TcpIpLayer.TRANSPORT, FindingStatus.OK, "ss"),
            LayerFinding(TcpIpLayer.APPLICATION, FindingStatus.OK, "dns"),
        )
    )
    assert degraded.executive_status() == "Degradado"
    unknown = _report(
        findings=(
            LayerFinding(TcpIpLayer.ACCESS, FindingStatus.OK, "up"),
            LayerFinding(TcpIpLayer.INTERNET, FindingStatus.UNKNOWN, "gw"),
            LayerFinding(TcpIpLayer.TRANSPORT, FindingStatus.OK, "ss"),
            LayerFinding(TcpIpLayer.APPLICATION, FindingStatus.OK, "dns"),
        )
    )
    assert unknown.executive_status() == "Inconclusivo"
    transcripts = (
        ProbeTranscript("ipconfig /all", 0, "Windows IP", skipped=False, timed_out=False),
        ProbeTranscript("route print", None, "", skipped=True, timed_out=False),
        ProbeTranscript("ping", None, "", skipped=False, timed_out=True),
        ProbeTranscript("arp -a", None, "", skipped=False, timed_out=False),
        ProbeTranscript("netstat", 1, "err", skipped=False, timed_out=False),
    )
    text = _report(
        transcripts=transcripts, validation_commands=("ipconfig /all",), mitigation_steps=("checar",)
    ).as_text()
    assert "=== ipconfig /all (exit 0) ===" in text
    assert "Windows IP" in text
    assert "=== route print (skipped) ===" in text
    assert "(sem stdout)" in text
    assert "=== ping (timeout) ===" in text
    assert "=== arp -a (exit ?) ===" in text
    assert "=== netstat (exit 1) ===" in text
    assert "ipconfig /all" in text
    assert "checar" in text
