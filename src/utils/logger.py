"""Structured logging utility for SkillVector Engine."""

import logging
import os
import sys


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger with structured output.

    Args:
        name: Logger name, typically __name__ from the calling module.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(f"skillvector.{name}")

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        handler.setLevel(getattr(logging, log_level, logging.INFO))
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, log_level, logging.INFO))

    return logger
