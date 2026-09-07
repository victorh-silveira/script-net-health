from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from clean_workspace import _dispatch, main
from config_gates import (
    _iter_json_files,
    _iter_yaml_files,
    run_config_text,
    stage_json_lint,
    stage_json_test,
    stage_json_validate,
    stage_yaml_lint,
    stage_yaml_validate,
)
from gate_runtime import AREA_STAGES
from python_gates import _module_root, stage_lint, stage_validate


@pytest.mark.unit
def test_python_lint_and_validate_exclude_yaml_json():
    assert "stage_yaml_lint" not in stage_lint.__code__.co_names
    assert "stage_json_lint" not in stage_lint.__code__.co_names
    assert "stage_yaml_validate" not in stage_validate.__code__.co_names
    assert "stage_json_validate" not in stage_validate.__code__.co_names
    with (
        patch("python_gates.subprocess.run"),
        patch("python_gates.run_tool"),
        patch("python_gates.stage_layer_dependencies"),
        patch("python_gates.stage_structure"),
    ):
        stage_lint()
        stage_validate()


@pytest.mark.unit
def test_python_area_includes_crash_first_stages():
    stages = AREA_STAGES["python"]
    assert {"lint", "validate", "security", "test", "build"}.issubset(stages)
    assert list(AREA_STAGES) == ["python"]


@pytest.mark.unit
def test_dispatch_rejects_unknown_area_and_stage():
    with pytest.raises(SystemExit) as unknown_area:
        _dispatch("yaml", "lint", 100)
    assert unknown_area.value.code == 1
    with pytest.raises(SystemExit) as unknown_stage:
        _dispatch("python", "nope", 100)
    assert unknown_stage.value.code == 1


@pytest.mark.unit
def test_dispatch_python_stages():
    calls: list[str] = []

    def mark(name: str) -> MagicMock:
        return MagicMock(side_effect=lambda *_args, **_kwargs: calls.append(name))

    with (
        patch("clean_workspace.stage_lint", mark("py_lint")),
        patch("clean_workspace.stage_validate", mark("py_validate")),
        patch("clean_workspace.stage_security", mark("py_security")),
        patch("clean_workspace.stage_test", mark("py_test")),
        patch("clean_workspace.stage_build", mark("py_build")),
        patch("clean_workspace.stage_clean", mark("clean")),
    ):
        _dispatch("python", "lint", 100)
        _dispatch("python", "security", 100)
        _dispatch("python", "test", 90)
        _dispatch("python", "pytest", 90)
        _dispatch("python", "validate", 100)
        _dispatch("python", "build", 100)
        _dispatch("python", "clean", 100)
    assert calls == [
        "py_lint",
        "py_security",
        "py_test",
        "py_test",
        "py_validate",
        "py_build",
        "clean",
    ]


@pytest.mark.unit
def test_iter_yaml_skips_templates_and_finds_workflows():
    paths = {path.as_posix() for path in _iter_yaml_files()}
    assert any("workflows/ci.yml" in item for item in paths)
    assert any("setup-python/action.yml" in item for item in paths)
    assert all("templates" not in item for item in paths)


@pytest.mark.unit
def test_iter_json_includes_vscode_settings():
    names = [path.name for path in _iter_json_files()]
    assert "settings.json" in names


@pytest.mark.unit
def test_module_root_layers():
    assert _module_root("domain.entities.app_identity") == "domain"
    assert _module_root("application.ports.clock") == "application"
    assert _module_root("json") is None


@pytest.mark.unit
def test_json_and_yaml_validate_current_repo():
    stage_json_validate()
    stage_yaml_validate()
    stage_json_test()


@pytest.mark.unit
def test_yaml_lint_fails_without_files():
    with patch("config_gates._iter_yaml_files", return_value=[]), pytest.raises(SystemExit) as exc:
        stage_yaml_lint()
    assert exc.value.code == 1


@pytest.mark.unit
def test_json_lint_fails_when_missing():
    with patch("config_gates._iter_json_files", return_value=[Path("/no/such.json")]), pytest.raises(SystemExit) as exc:
        stage_json_lint()
    assert exc.value.code == 1


@pytest.mark.unit
def test_run_config_text_unknown_kind():
    with pytest.raises(SystemExit) as exc:
        run_config_text("lint", "xml")
    assert exc.value.code == 1


@pytest.mark.unit
def test_run_config_text_routes_json_yaml():
    with (
        patch("config_gates.stage_json_lint") as json_lint,
        patch("config_gates.stage_yaml_lint") as yaml_lint,
        patch("config_gates.stage_json_validate") as json_validate,
        patch("config_gates.stage_yaml_validate") as yaml_validate,
        patch("config_gates.stage_json_test") as json_test,
    ):
        run_config_text("lint", "json")
        run_config_text("lint", "yaml")
        run_config_text("lint", "all")
        run_config_text("validate", "json")
        run_config_text("validate", "yaml")
        run_config_text("validate", "all")
        run_config_text("test", "json")
    assert json_lint.call_count == 2
    assert yaml_lint.call_count == 2
    assert json_validate.call_count == 2
    assert yaml_validate.call_count == 2
    json_test.assert_called_once()


@pytest.mark.unit
def test_run_config_text_skips_uncovered_stages(capsys: pytest.CaptureFixture[str]):
    run_config_text("security", "json")
    run_config_text("build", "yaml")
    run_config_text("test", "yaml")
    out = capsys.readouterr().out
    assert "gitleaks" in out


@pytest.mark.unit
def test_json_validate_rejects_non_object():
    with (
        patch("config_gates.stage_json_lint"),
        patch("config_gates.json.loads", return_value=["nope"]),
        pytest.raises(SystemExit) as exc,
    ):
        stage_json_validate()
    assert exc.value.code == 1


@pytest.mark.unit
def test_json_test_fails_without_extrapaths():
    payload = {"python.testing.pytestEnabled": True, "python.analysis.extraPaths": ["other"]}
    with (
        patch("config_gates.stage_json_validate"),
        patch("config_gates.json.loads", return_value=payload),
        pytest.raises(SystemExit) as exc,
    ):
        stage_json_test()
    assert exc.value.code == 1


@pytest.mark.unit
def test_json_test_fails_without_pytest_flag():
    payload = {"python.testing.pytestEnabled": False, "python.analysis.extraPaths": ["app/src"]}
    with (
        patch("config_gates.stage_json_validate"),
        patch("config_gates.json.loads", return_value=payload),
        pytest.raises(SystemExit) as exc,
    ):
        stage_json_test()
    assert exc.value.code == 1


@pytest.mark.unit
def test_json_test_fails_when_extrapaths_not_list():
    payload = {"python.testing.pytestEnabled": True, "python.analysis.extraPaths": "app/src"}
    with (
        patch("config_gates.stage_json_validate"),
        patch("config_gates.json.loads", return_value=payload),
        pytest.raises(SystemExit) as exc,
    ):
        stage_json_test()
    assert exc.value.code == 1


@pytest.mark.unit
def test_main_config_text(monkeypatch: pytest.MonkeyPatch):
    called: dict[str, str] = {}

    def fake(stage: str, kind: str) -> None:
        called["stage"] = stage
        called["kind"] = kind

    monkeypatch.setattr("clean_workspace.run_config_text", fake)
    monkeypatch.setattr("clean_workspace.use_app_cwd", lambda: None)
    monkeypatch.setattr(
        sys,
        "argv",
        ["clean_workspace.py", "--area", "python", "--stage", "lint", "--config-text", "json"],
    )
    main()
    assert called == {"stage": "lint", "kind": "json"}


@pytest.mark.unit
def test_main_config_text_all(monkeypatch: pytest.MonkeyPatch):
    called: dict[str, str] = {}

    def fake(stage: str, kind: str) -> None:
        called["stage"] = stage
        called["kind"] = kind

    monkeypatch.setattr("clean_workspace.run_config_text", fake)
    monkeypatch.setattr("clean_workspace.use_app_cwd", lambda: None)
    monkeypatch.setattr(sys, "argv", ["clean_workspace.py", "--stage", "lint", "--config-text"])
    main()
    assert called == {"stage": "lint", "kind": "all"}


@pytest.mark.unit
def test_main_config_text_rejects_unknown_area(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["clean_workspace.py", "--area", "docker", "--stage", "lint", "--config-text"],
    )
    with pytest.raises(SystemExit):
        main()


@pytest.mark.unit
def test_main_dispatches_python(monkeypatch: pytest.MonkeyPatch):
    seen: list[tuple[str, str, int]] = []

    def fake(area: str, stage: str, coverage: int) -> None:
        seen.append((area, stage, coverage))

    monkeypatch.setattr("clean_workspace._dispatch", fake)
    monkeypatch.setattr("clean_workspace.use_app_cwd", lambda: None)
    monkeypatch.setattr(sys, "argv", ["clean_workspace.py", "--stage", "build"])
    main()
    assert seen == [("python", "build", 100)]
