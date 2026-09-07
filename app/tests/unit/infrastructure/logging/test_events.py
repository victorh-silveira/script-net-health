"""Testes unitarios de logging semantico."""

import logging

import pytest

from infrastructure.logging.events import log_event, redact_url


@pytest.mark.unit
@pytest.mark.infrastructure
def test_redact_url_with_query():
    assert redact_url("https://h.example/path?token=secret") == "https://h.example/path?***"


@pytest.mark.unit
@pytest.mark.infrastructure
def test_redact_url_without_query():
    assert redact_url("https://h.example/path") == "https://h.example/path"


@pytest.mark.unit
@pytest.mark.infrastructure
def test_log_event_without_fields(caplog):
    logger = logging.getLogger("test.events.empty")
    with caplog.at_level(logging.INFO, logger="test.events.empty"):
        log_event(logger, logging.INFO, "snh.app.started")
    assert "event=snh.app.started" in caplog.text


@pytest.mark.unit
@pytest.mark.infrastructure
def test_log_event_redacts_secrets_and_urls(caplog):
    logger = logging.getLogger("test.events.redact")
    with caplog.at_level(logging.INFO, logger="test.events.redact"):
        log_event(
            logger,
            logging.INFO,
            "snh.test.event",
            url="https://h.example/x?a=1",
            request_url="https://h.example/y?b=2",
            target_url=123,
            token="super-secret",
            password="pw",
            authorization="Bearer x",
            secret="s",
            anon_key="k",
            count=1,
        )
    assert "event=snh.test.event" in caplog.text
    assert "url=https://h.example/x?***" in caplog.text
    assert "request_url=https://h.example/y?***" in caplog.text
    assert "target_url=123" in caplog.text
    assert "token=***" in caplog.text
    assert "super-secret" not in caplog.text
    assert "count=1" in caplog.text


@pytest.mark.unit
@pytest.mark.infrastructure
def test_log_event_exc_info_only_on_debug(caplog):
    logger = logging.getLogger("test.events.exc")
    logger.setLevel(logging.INFO)
    with caplog.at_level(logging.ERROR, logger="test.events.exc"):
        try:
            raise RuntimeError("boom")
        except RuntimeError:
            log_event(logger, logging.ERROR, "snh.app.failed", exc_info=True)
    assert "RuntimeError" not in caplog.text

    logger.setLevel(logging.DEBUG)
    with caplog.at_level(logging.DEBUG, logger="test.events.exc"):
        try:
            raise RuntimeError("boom-debug")
        except RuntimeError:
            log_event(logger, logging.ERROR, "snh.app.failed", exc_info=True)
    assert "boom-debug" in caplog.text
