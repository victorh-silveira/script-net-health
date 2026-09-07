"""Testes do composition root da CLI."""

import pytest

from domain.entities.diagnosis_report import (
    DiagnosisReport,
    FindingStatus,
    Impact,
    LayerFinding,
    Severity,
    TcpIpLayer,
)
from domain.exceptions import DomainError
from presentation.cli import bootstrap
from presentation.cli.arguments import parse_args


def _report() -> DiagnosisReport:
    return DiagnosisReport(
        impact=Impact.NONE,
        probable_layer=TcpIpLayer.ACCESS,
        severity=Severity.LOW,
        preliminary="Sem falha.",
        findings=(
            LayerFinding(TcpIpLayer.ACCESS, FindingStatus.OK, "up"),
            LayerFinding(TcpIpLayer.INTERNET, FindingStatus.OK, "gw"),
            LayerFinding(TcpIpLayer.TRANSPORT, FindingStatus.OK, "ss"),
            LayerFinding(TcpIpLayer.APPLICATION, FindingStatus.OK, "dns"),
        ),
        root_cause="Probes saudaveis.",
        validation_commands=("ip route",),
        mitigation_steps=("monitorar",),
    )


@pytest.mark.unit
@pytest.mark.presentation
def test_parse_args(monkeypatch):
    monkeypatch.setattr("sys.argv", ["snh"])
    args = parse_args()
    assert args.status is False


@pytest.mark.unit
@pytest.mark.presentation
def test_parse_args_status(monkeypatch):
    monkeypatch.setattr("sys.argv", ["snh", "--status"])
    args = parse_args()
    assert args.status is True


@pytest.mark.unit
@pytest.mark.presentation
def test_bootstrap_status_success(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("SNH_DISABLE_DOTENV", "1")
    monkeypatch.setenv("SNH_APP_NAME", "script-net-health")
    monkeypatch.setattr("sys.argv", ["snh", "--status"])
    bootstrap.bootstrap(tmp_path)
    output = capsys.readouterr().out
    assert "script-net-health" in output
    assert "ready" in output


@pytest.mark.unit
@pytest.mark.presentation
def test_bootstrap_diagnose_success(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("SNH_DISABLE_DOTENV", "1")
    monkeypatch.setattr("sys.argv", ["snh"])

    class FakeUseCase:
        def execute(self):
            return _report()

    monkeypatch.setattr(bootstrap, "DiagnoseNetworkHealth", lambda **kwargs: FakeUseCase())
    bootstrap.bootstrap(tmp_path)
    output = capsys.readouterr().out
    assert "#### 1. Resumo Executivo" in output


@pytest.mark.unit
@pytest.mark.presentation
def test_bootstrap_status_domain_error(monkeypatch, tmp_path):
    monkeypatch.setenv("SNH_DISABLE_DOTENV", "1")
    monkeypatch.setenv("SNH_APP_NAME", "   ")
    monkeypatch.setattr("sys.argv", ["snh", "--status"])
    with pytest.raises(SystemExit) as exc:
        bootstrap.bootstrap(tmp_path)
    assert exc.value.code == 1


@pytest.mark.unit
@pytest.mark.presentation
def test_bootstrap_diagnose_domain_error(monkeypatch, tmp_path):
    monkeypatch.setenv("SNH_DISABLE_DOTENV", "1")
    monkeypatch.setattr("sys.argv", ["snh"])

    class Boom:
        def execute(self):
            raise DomainError("falha de dominio")

    monkeypatch.setattr(bootstrap, "DiagnoseNetworkHealth", lambda **kwargs: Boom())
    with pytest.raises(SystemExit) as exc:
        bootstrap.bootstrap(tmp_path)
    assert exc.value.code == 1


@pytest.mark.unit
@pytest.mark.presentation
def test_bootstrap_diagnose_unexpected_error(monkeypatch, tmp_path):
    monkeypatch.setenv("SNH_DISABLE_DOTENV", "1")
    monkeypatch.setattr("sys.argv", ["snh"])

    class Boom:
        def execute(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(bootstrap, "DiagnoseNetworkHealth", lambda **kwargs: Boom())
    with pytest.raises(SystemExit) as exc:
        bootstrap.bootstrap(tmp_path)
    assert exc.value.code == 1


@pytest.mark.unit
@pytest.mark.presentation
def test_bootstrap_status_unexpected_error(monkeypatch, tmp_path):
    monkeypatch.setenv("SNH_DISABLE_DOTENV", "1")
    monkeypatch.setenv("SNH_APP_NAME", "script-net-health")
    monkeypatch.setattr("sys.argv", ["snh", "--status"])

    class Boom:
        def execute(self, identity):
            raise RuntimeError("boom")

    monkeypatch.setattr(bootstrap, "GetAppStatus", lambda **kwargs: Boom())
    with pytest.raises(SystemExit) as exc:
        bootstrap.bootstrap(tmp_path)
    assert exc.value.code == 1


@pytest.mark.unit
@pytest.mark.presentation
def test_main_calls_bootstrap(monkeypatch, tmp_path):
    called = {}

    def fake_bootstrap(root):
        called["root"] = root

    monkeypatch.setattr(bootstrap, "bootstrap", fake_bootstrap)
    bootstrap.main(tmp_path)
    assert called["root"] == tmp_path
