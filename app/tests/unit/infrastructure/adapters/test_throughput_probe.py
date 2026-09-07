"""Testes da medicao de throughput via urllib."""

from urllib.error import URLError
from urllib.request import Request

import pytest

from infrastructure.adapters import throughput_probe


class _Resp:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> "_Resp":
        return self

    def __exit__(self, *args: object) -> bool:
        return False


@pytest.mark.unit
@pytest.mark.infrastructure
def test_measure_throughput_rejects_non_http():
    assert throughput_probe.measure_throughput("ftp://x", "ftp://y", 10, 1) is None


@pytest.mark.unit
@pytest.mark.infrastructure
def test_measure_throughput_success(monkeypatch):
    def fake_urlopen(request: Request, timeout: float = 0) -> _Resp:
        if request.get_method() == "GET":
            return _Resp(b"x" * 1000)
        return _Resp(b"ok")

    times = iter([0.0, 1.0, 1.05, 2.0, 2.10, 3.0])
    monkeypatch.setattr(throughput_probe.time, "perf_counter", lambda: next(times))
    monkeypatch.setattr(throughput_probe, "urlopen", fake_urlopen)
    measured = throughput_probe.measure_throughput("", "", 1000, 1)
    assert measured is not None
    assert measured.download_mbps is not None
    assert measured.upload_mbps is not None
    assert measured.bytes_transferred == 1000
    times_zero = iter([0.0, 1.0, 1.05, 2.0, 2.10, 3.0])
    monkeypatch.setattr(throughput_probe.time, "perf_counter", lambda: next(times_zero))
    tiny = throughput_probe.measure_throughput("https://example.com/d", "https://example.com/u", 0, 1)
    assert tiny is not None
    assert tiny.bytes_transferred == 0


@pytest.mark.unit
@pytest.mark.infrastructure
def test_measure_throughput_partial_and_failures(monkeypatch):
    def down_only(request: Request, timeout: float = 0) -> _Resp:
        if request.get_method() == "GET":
            return _Resp(b"x" * 100)
        raise URLError("up-down")

    times = iter([0.0, 0.0, 0.1, 0.1, 0.2, 0.3])
    monkeypatch.setattr(throughput_probe.time, "perf_counter", lambda: next(times))
    monkeypatch.setattr(throughput_probe, "urlopen", down_only)
    partial = throughput_probe.measure_throughput("https://example.com/down", "https://example.com/up", 100, 1)
    assert partial is not None
    assert partial.download_mbps is not None
    assert partial.upload_mbps is None

    def up_only(request: Request, timeout: float = 0) -> _Resp:
        if request.get_method() == "POST":
            return _Resp(b"ok")
        raise URLError("down")

    times_up = iter([0.0, 0.0, 0.1, 0.2, 0.3, 0.4])
    monkeypatch.setattr(throughput_probe.time, "perf_counter", lambda: next(times_up))
    monkeypatch.setattr(throughput_probe, "urlopen", up_only)
    uploaded = throughput_probe.measure_throughput("https://example.com/down", "https://example.com/up", 100, 1)
    assert uploaded is not None
    assert uploaded.download_mbps is None
    assert uploaded.upload_mbps is not None

    def boom(*args, **kwargs):
        raise OSError("fail")

    monkeypatch.setattr(throughput_probe.time, "perf_counter", lambda: 1.0)
    monkeypatch.setattr(throughput_probe, "urlopen", boom)
    assert throughput_probe.measure_throughput("https://example.com/d", "https://example.com/u", 10, 1) is None


@pytest.mark.unit
@pytest.mark.infrastructure
def test_measure_throughput_empty_and_zero_elapsed(monkeypatch):
    monkeypatch.setattr(throughput_probe, "urlopen", lambda *a, **k: _Resp(b""))
    times = iter([0.0, 0.0, 0.1, 0.2, 0.2, 0.5])
    monkeypatch.setattr(throughput_probe.time, "perf_counter", lambda: next(times))
    assert throughput_probe.measure_throughput("https://example.com/d", "https://example.com/u", 10, 1) is None

    monkeypatch.setattr(throughput_probe, "urlopen", lambda *a, **k: _Resp(b"x"))
    monkeypatch.setattr(throughput_probe.time, "perf_counter", lambda: 1.0)
    assert throughput_probe.measure_throughput("https://example.com/d", "https://example.com/u", 10, 1) is None


@pytest.mark.unit
@pytest.mark.infrastructure
def test_measure_throughput_value_error(monkeypatch):
    def boom(*args, **kwargs):
        raise ValueError("bad")

    monkeypatch.setattr(throughput_probe, "urlopen", boom)
    assert throughput_probe.measure_throughput("https://example.com/d", "https://example.com/u", 10, 1) is None
