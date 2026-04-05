"""
logging/logger.py — Dual stdout + file logging with color support.
"""

import logging
import sys
from typing import Optional


RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
DIM    = "\033[2m"

LEVEL_COLORS = {
    logging.DEBUG:    DIM,
    logging.INFO:     RESET,
    logging.WARNING:  YELLOW,
    logging.ERROR:    RED,
    logging.CRITICAL: RED + BOLD,
}


class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        color = LEVEL_COLORS.get(record.levelno, RESET)
        msg = super().format(record)
        return f"{color}{msg}{RESET}"


def setup_logger(
    name: str = "dreamos",
    log_file: Optional[str] = None,
    verbose: bool = False,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    if logger.handlers:
        return logger  # already configured

    fmt = "%(asctime)s [%(levelname)s] %(message)s"
    datefmt = "%H:%M:%S"

    # Console handler (colored)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(ColorFormatter(fmt=fmt, datefmt=datefmt))
    console.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.addHandler(console)

    # File handler (plain text)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    return logger


# Module-level convenience
log = setup_logger()
