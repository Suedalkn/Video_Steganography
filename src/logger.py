"""Project logger and development log writer."""

from __future__ import annotations

import logging
from pathlib import Path


def setup_logger(log_file: Path, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("video_steg")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def append_development_log(dev_log_file: Path, message: str) -> None:
    dev_log_file.parent.mkdir(parents=True, exist_ok=True)
    with dev_log_file.open("a", encoding="utf-8") as file:
        file.write(message.rstrip() + "\n")
