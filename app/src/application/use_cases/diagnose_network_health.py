"""Caso de uso: diagnosticar saude de rede do host."""

from application.ports.probe_collector import ProbeCollectorPort
from domain.entities.diagnosis_report import DiagnosisReport
from domain.services.bottom_up_diagnoser import BottomUpDiagnoser


class DiagnoseNetworkHealth:
    """Coleta evidencias e aplica o diagnoser de dominio."""

    def __init__(self, collector: ProbeCollectorPort, diagnoser: BottomUpDiagnoser) -> None:
        """Injeta collector e diagnoser."""
        self._collector = collector
        self._diagnoser = diagnoser

    def execute(self) -> DiagnosisReport:
        """Executa collect e diagnostico BOTTOM-UP."""
        evidence = self._collector.collect()
        return self._diagnoser.diagnose(evidence)
