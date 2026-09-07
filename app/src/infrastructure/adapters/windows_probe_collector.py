"""Coleta de evidencias via probes Windows allowlisted."""

from __future__ import annotations

import logging

from domain.entities.network_evidence import NetworkEvidence, PingEvidence, ProbeTranscript, ThroughputEvidence
from infrastructure.adapters.command_runner import AllowlistedCommandRunner, CommandResult
from infrastructure.adapters.http_probe import probe_http
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
from infrastructure.adapters.tcp_probe import probe_tcp
from infrastructure.adapters.throughput_probe import measure_throughput
from infrastructure.config.settings import Settings
from infrastructure.logging.events import log_event


logger = logging.getLogger(__name__)


class WindowsProbeCollector:
    """Implementa ProbeCollectorPort no host Windows."""

    def __init__(self, runner: AllowlistedCommandRunner, settings: Settings) -> None:
        """Recebe runner e settings de probe."""
        self._runner = runner
        self._settings = settings

    def collect(self) -> NetworkEvidence:
        """Executa probes L1-L4 e devolve NetworkEvidence."""
        missing: list[str] = []
        transcripts: list[ProbeTranscript] = []
        timeout = float(self._settings.probe_timeout_seconds)

        ipconfig_res = self._run(["ipconfig", "/all"], timeout, missing, "ipconfig /all", transcripts)
        route_res = self._run(["route", "print"], timeout, missing, "route print", transcripts)
        arp_res = self._run(["arp", "-a"], timeout, missing, "arp -a", transcripts)
        netstat_res = self._run(["netstat", "-ano"], timeout, missing, "netstat -ano", transcripts)

        links, ipv4_to_name = (
            parse_ipconfig(ipconfig_res.stdout) if not ipconfig_res.skipped and not ipconfig_res.timed_out else ((), {})
        )
        gateway, iface_ip = parse_route_print(route_res.stdout) if route_res.stdout else (None, None)
        iface = ipv4_to_name.get(iface_ip, iface_ip) if iface_ip else None
        neighbors = parse_arp(arp_res.stdout) if arp_res.stdout else ()
        sockets = parse_netstat(netstat_res.stdout) if netstat_res.stdout else ()

        gateway_ping = self._ping(gateway, timeout, missing, transcripts)
        wan_ping = self._ping(self._settings.wan_ping_target, timeout, missing, transcripts)
        dns_ok = self._dns(timeout, missing, transcripts)
        hops = self._tracert(missing, transcripts)
        http_ok = self._http()
        tcp_ok, tcp_endpoint = self._tcp()
        throughput = self._throughput()

        return NetworkEvidence(
            links=links,
            neighbors=neighbors,
            default_gateway=gateway,
            default_iface=iface,
            gateway_ping=gateway_ping,
            wan_ping=wan_ping,
            dns_ok=dns_ok,
            dns_name=self._settings.dns_probe_name,
            wan_target=self._settings.wan_ping_target,
            listening_sockets=sockets,
            missing_probes=tuple(missing),
            traceroute_hops=hops,
            http_ok=http_ok,
            http_url=self._settings.http_probe_url or None,
            transcripts=tuple(transcripts),
            throughput=throughput,
            tcp_ok=tcp_ok,
            tcp_endpoint=tcp_endpoint,
            min_download_mbps=self._settings.min_download_mbps,
            min_upload_mbps=self._settings.min_upload_mbps,
        )

    def _run(
        self,
        argv: list[str],
        timeout: float,
        missing: list[str],
        label: str,
        transcripts: list[ProbeTranscript],
    ) -> CommandResult:
        """Executa um argv allowlisted e registra skip/falha."""
        log_event(logger, logging.INFO, "snh.probe.started", probe=label)
        result = self._runner.run(argv, timeout)
        transcripts.append(
            ProbeTranscript(
                command=label,
                returncode=result.returncode,
                stdout=result.stdout,
                skipped=result.skipped,
                timed_out=result.timed_out,
            )
        )
        if result.skipped:
            log_event(logger, logging.INFO, "snh.probe.skipped_binary", probe=label)
            missing.append(label)
            return result
        if result.timed_out:
            log_event(logger, logging.INFO, "snh.probe.failed", probe=label, reason="timeout")
            missing.append(label)
            return result
        if result.returncode not in {0, None}:
            log_event(logger, logging.INFO, "snh.probe.failed", probe=label, reason="exit")
        else:
            log_event(logger, logging.INFO, "snh.probe.finished", probe=label)
        return result

    def _ping(
        self,
        target: str | None,
        timeout: float,
        missing: list[str],
        transcripts: list[ProbeTranscript],
    ) -> PingEvidence | None:
        """Corre ping Windows contra um alvo seguro."""
        if target is None or not is_safe_host(target):
            return None
        count = str(self._settings.ping_count)
        label = f"ping -n {count} {target}"
        result = self._run(["ping", "-n", count, target], timeout, missing, label, transcripts)
        if result.skipped or result.timed_out or not result.stdout:
            return PingEvidence(target=target, transmitted=None, received=None, loss_pct=None, rtt_avg_ms=None)
        return parse_ping(result.stdout, target)

    def _dns(self, timeout: float, missing: list[str], transcripts: list[ProbeTranscript]) -> bool | None:
        """Resolve o nome de probe via nslookup."""
        name = self._settings.dns_probe_name
        if not is_safe_host(name):
            return None
        label = f"nslookup {name}"
        result = self._run(["nslookup", name], timeout, missing, label, transcripts)
        if result.skipped or result.timed_out:
            return None
        return parse_nslookup(result.stdout)

    def _tracert(self, missing: list[str], transcripts: list[ProbeTranscript]) -> tuple[str, ...]:
        """Corre tracert se habilitado."""
        if not self._settings.enable_traceroute:
            log_event(logger, logging.INFO, "snh.probe.skipped_traceroute")
            return ()
        target = self._settings.wan_ping_target
        if not is_safe_host(target):
            return ()
        result = self._run(
            ["tracert", "-d", "-h", "5", "-w", "1000", target],
            float(self._settings.tracert_timeout_seconds),
            missing,
            f"tracert -d {target}",
            transcripts,
        )
        if result.skipped or result.timed_out or not result.stdout:
            return ()
        return parse_tracert_hops(result.stdout)

    def _http(self) -> bool | None:
        """GET opcional quando SNH_HTTP_PROBE_URL esta definido."""
        url = self._settings.http_probe_url
        if not url:
            return None
        log_event(logger, logging.INFO, "snh.probe.started", probe="http")
        ok = probe_http(url, float(self._settings.probe_timeout_seconds))
        if ok is False:
            log_event(logger, logging.INFO, "snh.probe.failed", probe="http")
        else:
            log_event(logger, logging.INFO, "snh.probe.finished", probe="http")
        return ok

    def _tcp(self) -> tuple[bool | None, str | None]:
        """Handshake TCP no alvo WAN."""
        host = self._settings.wan_ping_target
        port = self._settings.tcp_probe_port
        endpoint = f"{host}:{port}"
        if not is_safe_host(host):
            return None, None
        log_event(logger, logging.INFO, "snh.probe.started", probe=f"tcp {endpoint}")
        ok = probe_tcp(host, port, float(self._settings.probe_timeout_seconds))
        if ok is False:
            log_event(logger, logging.INFO, "snh.probe.failed", probe=f"tcp {endpoint}")
        elif ok is True:
            log_event(logger, logging.INFO, "snh.probe.finished", probe=f"tcp {endpoint}")
        return ok, endpoint

    def _throughput(self) -> ThroughputEvidence | None:
        """Mede download/upload se habilitado."""
        if not self._settings.enable_speedtest:
            log_event(logger, logging.INFO, "snh.probe.skipped_speedtest")
            return None
        log_event(logger, logging.INFO, "snh.probe.started", probe="speedtest")
        measured = measure_throughput(
            self._settings.speedtest_download_url,
            self._settings.speedtest_upload_url,
            self._settings.speedtest_bytes,
            float(self._settings.speedtest_timeout_seconds),
        )
        if measured is None:
            log_event(logger, logging.INFO, "snh.probe.failed", probe="speedtest")
            return None
        log_event(logger, logging.INFO, "snh.probe.finished", probe="speedtest")
        return measured
