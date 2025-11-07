#!/usr/bin/env python3
"""
Logger module for NOVAQUOTE Trading Platform
Provides structured logging functionality
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)

    # Set level
    logger.setLevel(logging.INFO)

    # Create console handler if not exists
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
