"""Diagnostico BOTTOM-UP da pilha TCP/IP de 4 camadas."""

from __future__ import annotations

from domain.entities.diagnosis_report import DiagnosisReport, FindingStatus, Impact, LayerFinding, Severity, TcpIpLayer
from domain.entities.network_evidence import NetworkEvidence, PingEvidence
from domain.services.tcp_layer_findings import (
    access_finding,
    application_finding,
    internet_finding,
    transport_finding,
)


class BottomUpDiagnoser:
    """Aplica regras deterministicas sem IO e sem log."""

    def diagnose(self, evidence: NetworkEvidence) -> DiagnosisReport:
        """Avalia evidencias de baixo para cima e monta o relatorio."""
        findings = (
            access_finding(evidence),
            internet_finding(evidence),
            transport_finding(evidence),
            application_finding(evidence),
        )
        impact, layer, severity, preliminary, cause, mitigation = self._primary(evidence, findings)
        return DiagnosisReport(
            impact=impact,
            probable_layer=layer,
            severity=severity,
            preliminary=preliminary,
            findings=findings,
            root_cause=cause,
            validation_commands=self._commands(evidence),
            mitigation_steps=mitigation,
            transcripts=evidence.transcripts,
        )

    def _primary(
        self,
        evidence: NetworkEvidence,
        findings: tuple[LayerFinding, LayerFinding, LayerFinding, LayerFinding],
    ) -> tuple[Impact, TcpIpLayer, Severity, str, str, tuple[str, ...]]:
        """Escolhe impacto e causa pela primeira falha de baixo para cima."""
        access, internet, application = findings[0], findings[1], findings[3]
        if access.status is FindingStatus.FAILED:
            return (
                Impact.LAN,
                TcpIpLayer.ACCESS,
                Severity.CRITICAL,
                "Falha de acesso a rede no host. Nenhuma interface de dados UP com endereco.",
                "Camada de acesso: interface DOWN ou sem endereco IP. Isolado a LAN local.",
                (
                    "Verificar cabo/AP e ativar o adaptador no ncpa.cpl.",
                    "Renovar DHCP (`ipconfig /renew`) apos o enlace subir.",
                ),
            )
        if evidence.default_gateway is None and internet.status is FindingStatus.FAILED:
            return (
                Impact.LAN,
                TcpIpLayer.INTERNET,
                Severity.HIGH,
                "Host sem rota default. Trafego para fora da LAN nao tem gateway.",
                "Tabela de rotas sem default via. Falha de enderecamento/DHCP na borda LAN.",
                (
                    "Checar DHCP e `route print`.",
                    "Configurar gateway estatico ou renovar o lease.",
                ),
            )
        if self._total_loss(evidence.gateway_ping):
            return (
                Impact.LAN,
                TcpIpLayer.INTERNET,
                Severity.HIGH,
                "Gateway default nao responde ICMP. Isolamento na LAN ou no gateway de borda.",
                f"Ping 100% perda para {evidence.default_gateway}. WAN nao e avaliavel enquanto o gateway falha.",
                (
                    "Validar ARP (`arp -a`) e L2 ate o gateway.",
                    "Checar ACL/ICMP no gateway e IP/mascara do host.",
                ),
            )
        if self._has_reply(evidence.gateway_ping) and self._total_loss(evidence.wan_ping):
            return (
                Impact.WAN,
                TcpIpLayer.INTERNET,
                Severity.HIGH,
                "LAN e gateway OK; destino WAN nao responde. Falha apos a borda (ISP/peering/filtro).",
                f"Ping gateway ok; perda total para {evidence.wan_target}. Isolado a WAN.",
                (
                    "Confirmar com tracert quando habilitado.",
                    "Testar outro alvo WAN e abrir chamado no ISP se persistir.",
                ),
            )
        if application.status is FindingStatus.FAILED and evidence.dns_ok is False:
            return (
                Impact.SERVICE,
                TcpIpLayer.APPLICATION,
                Severity.MEDIUM,
                "Conectividade IP aparentemente ok, mas a resolucao DNS falhou.",
                f"nslookup/DNS nao resolveu {evidence.dns_name}. Servico de aplicacao (resolvedor), nao enlace.",
                (
                    f"Rodar `nslookup {evidence.dns_name}` e checar os DNS da NIC.",
                    "Testar resolvedor publico so se a politica permitir.",
                ),
            )
        if application.status is FindingStatus.FAILED and evidence.http_ok is False:
            return (
                Impact.SERVICE,
                TcpIpLayer.APPLICATION,
                Severity.MEDIUM,
                "DNS ou IP ok, mas o probe HTTP falhou. Impacto especifico de servico.",
                f"HTTP HEAD/GET para {evidence.http_url} nao obteve sucesso.",
                (
                    "Validar URL, proxy e certificado TLS no cliente.",
                    "Repetir o probe com curl -v se precisar do handshake.",
                ),
            )
        if findings[2].status is FindingStatus.FAILED and evidence.tcp_ok is False:
            return (
                Impact.SERVICE,
                TcpIpLayer.TRANSPORT,
                Severity.MEDIUM,
                "ICMP WAN ok, mas TCP na porta de probe falhou. Possivel filtro/L4.",
                f"TCP {evidence.tcp_endpoint} recusou ou expirou.",
                (
                    "Checar firewall local e ACL no caminho ate o alvo.",
                    "Repetir com outra porta se a politica exigir.",
                ),
            )
        return (
            Impact.NONE,
            TcpIpLayer.NONE,
            Severity.LOW,
            "Nenhuma quebra de conectividade nas probes. Stack observada operacional.",
            "Evidencias nao mostram quebra de enlace, rota, ICMP WAN nem DNS.",
            ("Manter monitoramento; ampliar probes se o sintoma for de aplicacao especifica.",),
        )

    def _commands(self, evidence: NetworkEvidence) -> tuple[str, ...]:
        """Monta a lista de validacao imediata."""
        gw = evidence.default_gateway or "<gateway>"
        commands = [
            "ipconfig /all",
            "route print",
            "arp -a",
            f"ping -n 3 {gw}",
            f"ping -n 3 {evidence.wan_target}",
            "netstat -ano",
            f"nslookup {evidence.dns_name}",
        ]
        extra = [item for item in evidence.missing_probes if item not in commands]
        return tuple(commands + extra)

    def _total_loss(self, ping: PingEvidence | None) -> bool:
        """True se a probe ICMP teve 100% de perda."""
        return ping is not None and ping.is_total_loss() is True

    def _has_reply(self, ping: PingEvidence | None) -> bool:
        """True se a probe ICMP teve ao menos uma resposta."""
        return ping is not None and ping.has_reply() is True
