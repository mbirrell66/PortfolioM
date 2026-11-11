"""Log file setup.

Writes to data/portfolio_manager.log (next to the database), rotating at 1 MB
with three old files kept. In the packaged app there is no console, so
print() output and error tracebacks are sent to the log as well.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler


class _StreamToLog:
    """Stand-in for stdout/stderr that writes each line to a logger."""

    def __init__(self, logger: logging.Logger, level: int):
        self._logger = logger
        self._level = level

    def write(self, text):
        for line in str(text).rstrip().splitlines():
            if line.strip():
                self._logger.log(self._level, line)
        return len(text)

    def flush(self):
        pass

    def isatty(self):
        return False


def setup_logging():
    """Attach the log file. Safe to call more than once. Returns the log path."""
    from database.database import DATA_DIR
    log_path = DATA_DIR / "portfolio_manager.log"

    root = logging.getLogger()
    if any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        return log_path

    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")
    file_handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3,
                                       encoding="utf-8")
    file_handler.setFormatter(fmt)
    root.setLevel(logging.INFO)
    root.addHandler(file_handler)

    no_console = getattr(sys, "frozen", False) or sys.stdout is None or sys.stderr is None
    if no_console:
        sys.stdout = _StreamToLog(logging.getLogger("stdout"), logging.INFO)
        sys.stderr = _StreamToLog(logging.getLogger("stderr"), logging.ERROR)
    else:
        console = logging.StreamHandler()
        console.setFormatter(fmt)
        root.addHandler(console)

    def _log_uncaught(exc_type, exc, tb):
        logging.getLogger("uncaught").critical(
            "Uncaught exception", exc_info=(exc_type, exc, tb))

    sys.excepthook = _log_uncaught
    return log_path
