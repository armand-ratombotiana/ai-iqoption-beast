"""Logging setup"""

import logging
import sys
from datetime import datetime


def setup_logger(name: str = 'trading_bot', level: int = logging.INFO) -> logging.Logger:
    """
    Set up application logger

    Args:
        name: Logger name
        level: Logging level

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


def get_logger(name: str = 'trading_bot') -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)
