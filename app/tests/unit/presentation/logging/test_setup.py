"""Testes do setup de logging da apresentacao."""

import logging

import pytest

from presentation.logging.setup import configure_logging


@pytest.mark.unit
@pytest.mark.presentation
def test_configure_logging_sets_level_and_quiets_http():
    configure_logging("WARNING")
    assert logging.getLogger().level == logging.WARNING
    assert logging.getLogger("urllib3").level == logging.WARNING
    assert logging.getLogger("requests").level == logging.WARNING
    assert logging.getLogger("httpx").level == logging.WARNING
    assert logging.getLogger("httpcore").level == logging.WARNING


@pytest.mark.unit
@pytest.mark.presentation
def test_configure_logging_unknown_level_falls_back_to_info():
    configure_logging("FOO")
    assert logging.getLogger().level == logging.INFO


@pytest.mark.unit
@pytest.mark.presentation
def test_configure_logging_non_int_attribute_falls_back_to_info():
    configure_logging("BASIC_FORMAT")
    assert logging.getLogger().level == logging.INFO
