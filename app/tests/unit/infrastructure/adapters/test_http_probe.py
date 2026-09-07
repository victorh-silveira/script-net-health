"""Testes do probe HTTP."""

from urllib.error import URLError

import pytest

from infrastructure.adapters import http_probe


class _Resp:
    def __init__(self, status: int) -> None:
        self.status = status

    def __enter__(self) -> "_Resp":
        return self

    def __exit__(self, *args: object) -> bool:
        return False


@pytest.mark.unit
@pytest.mark.infrastructure
def test_probe_http_rejects_non_http():
    assert http_probe.probe_http("ftp://x", 1) is None


@pytest.mark.unit
@pytest.mark.infrastructure
def test_probe_http_success(monkeypatch):
    monkeypatch.setattr(http_probe, "urlopen", lambda *a, **k: _Resp(200))
    assert http_probe.probe_http("https://example.com", 1) is True


@pytest.mark.unit
@pytest.mark.infrastructure
def test_probe_http_error_status(monkeypatch):
    monkeypatch.setattr(http_probe, "urlopen", lambda *a, **k: _Resp(500))
    assert http_probe.probe_http("https://example.com", 1) is False


@pytest.mark.unit
@pytest.mark.infrastructure
def test_probe_http_urlerror(monkeypatch):
    def boom(*args, **kwargs):
        raise URLError("down")

    monkeypatch.setattr(http_probe, "urlopen", boom)
    assert http_probe.probe_http("http://example.com", 1) is False


@pytest.mark.unit
@pytest.mark.infrastructure
def test_probe_http_missing_status(monkeypatch):
    class _Bare:
        def __enter__(self) -> "_Bare":
            return self

        def __exit__(self, *args: object) -> bool:
            return False

    monkeypatch.setattr(http_probe, "urlopen", lambda *a, **k: _Bare())
    assert http_probe.probe_http("https://example.com", 1) is False


@pytest.mark.unit
@pytest.mark.infrastructure
def test_probe_http_value_error(monkeypatch):
    def boom(*args, **kwargs):
        raise ValueError("bad-url")

    monkeypatch.setattr(http_probe, "urlopen", boom)
    assert http_probe.probe_http("https://example.com", 1) is False
