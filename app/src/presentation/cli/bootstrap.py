"""Composition root: Settings, adapters, use cases e execucao da CLI."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from application.use_cases.diagnose_network_health import DiagnoseNetworkHealth
from application.use_cases.get_app_status import GetAppStatus
from domain.constants import APP_VERSION
from domain.entities.app_identity import AppIdentity
from domain.exceptions import DomainError
from domain.services.bottom_up_diagnoser import BottomUpDiagnoser
from infrastructure.adapters.command_runner import AllowlistedCommandRunner
from infrastructure.adapters.system_clock import SystemClock
from infrastructure.adapters.windows_probe_collector import WindowsProbeCollector
from infrastructure.config.settings import Settings
from infrastructure.logging.events import log_event
from presentation.cli.arguments import parse_args
from presentation.logging.setup import configure_logging


logger = logging.getLogger(__name__)


def bootstrap(repo_root: Path) -> None:
    """Liga dependencias e executa status ou diagnostico."""
    settings = Settings.from_env(repo_root)
    configure_logging(settings.log_level)
    args = parse_args()
    try:
        if args.status:
            _run_status(settings)
            return
        _run_diagnose(settings)
    except DomainError as exc:
        event = "snh.app.failed" if args.status else "snh.diagnose.failed"
        log_event(logger, logging.ERROR, event, error=str(exc))
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        event = "snh.app.failed" if args.status else "snh.diagnose.failed"
        log_event(
            logger,
            logging.ERROR,
            event,
            error=str(exc),
            exc_info=True,
        )
        print(f"Erro inesperado: {exc}", file=sys.stderr)
        sys.exit(1)


def _run_status(settings: Settings) -> None:
    """Executa GetAppStatus e imprime o snapshot."""
    log_event(logger, logging.INFO, "snh.app.started", name=settings.app_name)
    identity = AppIdentity(name=settings.app_name, version=APP_VERSION)
    status = GetAppStatus(clock=SystemClock()).execute(identity)
    print(status.as_text())
    log_event(logger, logging.INFO, "snh.app.finished", state=status.state.value)


def _run_diagnose(settings: Settings) -> None:
    """Coleta probes, diagnostica e imprime o relatorio."""
    log_event(logger, logging.INFO, "snh.diagnose.started", name=settings.app_name)
    collector = WindowsProbeCollector(AllowlistedCommandRunner(), settings)
    report = DiagnoseNetworkHealth(collector=collector, diagnoser=BottomUpDiagnoser()).execute()
    print(report.as_text())
    log_event(
        logger,
        logging.INFO,
        "snh.diagnose.finished",
        impact=report.impact.value,
        layer=report.probable_layer.value,
    )


def main(repo_root: Path) -> None:
    """Entrypoint usado por app/run.py."""
    bootstrap(repo_root)
