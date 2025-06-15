"""Utility functions and helpers"""

import logging
from datetime import datetime
from typing import Any


def setup_logging(level: str = "INFO") -> None:
    """Setup application logging"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO string with Z suffix"""
    return dt.isoformat() + "Z"


__all__ = [
    "setup_logging",
    "format_timestamp"
]
