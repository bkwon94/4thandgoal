"""
Tests for the log setup of the app: an INFO line of the analyzer reaches stderr, one time.
uvicorn sets only its own loggers, so the app sets the root logger.
"""
import logging
import logging.config

import pytest
from uvicorn.config import LOGGING_CONFIG

from cornerstone_api.app import configure_logging


@pytest.fixture
def root_logger():
    """The root logger, put back as it was after the test, so the next test sees no extra handler."""
    names = ("", "uvicorn", "uvicorn.error", "uvicorn.access")
    saved = {name: (list(logging.getLogger(name).handlers), logging.getLogger(name).level,
                    logging.getLogger(name).propagate) for name in names}
    yield logging.getLogger()
    for name, (handlers, level, propagate) in saved.items():
        logger = logging.getLogger(name)
        logger.handlers[:] = handlers
        logger.setLevel(level)
        logger.propagate = propagate


def test_an_info_line_of_the_analyzer_reaches_a_handler_on_stderr(root_logger, capsys):
    configure_logging()

    logging.getLogger("analyzer.routes").info("Press of analyze for cpc: time=1.0s")

    assert "Press of analyze for cpc: time=1.0s" in capsys.readouterr().err


def test_a_second_setup_gives_no_second_copy_of_a_line(root_logger, capsys):
    configure_logging()
    configure_logging()

    logging.getLogger("analyzer.routes").info("one line")

    assert capsys.readouterr().err.count("one line") == 1


def test_the_uvicorn_access_log_keeps_its_one_line_on_stdout(root_logger, capsys):
    # uvicorn applies its own log config before it calls the factory, so the test does the same.
    logging.config.dictConfig(LOGGING_CONFIG)
    configure_logging()

    logging.getLogger("uvicorn.access").info('%s - "%s %s HTTP/%s" %d', "1.2.3.4", "GET", "/health", "1.1", 200)

    captured = capsys.readouterr()
    assert captured.out.count("GET /health") == 1
    assert "GET /health" not in captured.err
