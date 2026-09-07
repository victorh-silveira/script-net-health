"""Testes do probe TCP."""

import pytest

from infrastructure.adapters import tcp_probe


@pytest.mark.unit
@pytest.mark.infrastructure
def test_probe_tcp_rejects_unsafe_host_and_port():
    assert tcp_probe.probe_tcp("bad host", 443, 1) is None
    assert tcp_probe.probe_tcp("1.1.1.1", 0, 1) is None
    assert tcp_probe.probe_tcp("1.1.1.1", 70000, 1) is None


@pytest.mark.unit
@pytest.mark.infrastructure
def test_probe_tcp_success(monkeypatch):
    class _Sock:
        def __enter__(self) -> "_Sock":
            return self

        def __exit__(self, *args: object) -> bool:
            return False

    monkeypatch.setattr(tcp_probe.socket, "create_connection", lambda *a, **k: _Sock())
    assert tcp_probe.probe_tcp("1.1.1.1", 443, 1) is True


@pytest.mark.unit
@pytest.mark.infrastructure
def test_probe_tcp_oserror(monkeypatch):
    def boom(*args, **kwargs):
        raise OSError("refused")

    monkeypatch.setattr(tcp_probe.socket, "create_connection", boom)
    assert tcp_probe.probe_tcp("1.1.1.1", 443, 1) is False
