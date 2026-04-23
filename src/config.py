"""Configuration loader and typed access helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml


@dataclass
class ProjectPaths:
    input_video: Path
    stego_video: Path
    stego_preview_video: Path
    extracted_text: Path
    report_json: Path
    process_log: Path
    development_log: Path


@dataclass
class AppConfig:
    raw: Dict[str, Any]
    paths: ProjectPaths

    @property
    def block_size(self) -> int:
        return int(self.raw["analysis"]["block_size"])

    @property
    def top_block_ratio(self) -> float:
        return float(self.raw["analysis"]["top_block_ratio"])

    @property
    def motion_weight(self) -> float:
        return float(self.raw["analysis"]["motion_weight"])

    @property
    def texture_weight(self) -> float:
        return float(self.raw["analysis"]["texture_weight"])

    @property
    def canny_thresholds(self) -> Tuple[int, int]:
        return (
            int(self.raw["analysis"]["canny_low"]),
            int(self.raw["analysis"]["canny_high"]),
        )

    @property
    def dct_pair_indices(self) -> Tuple[int, int]:
        values = self.raw["transform"]["dct_pair_indices"]
        return int(values[0]), int(values[1])

    @property
    def coefficient_margin(self) -> float:
        return float(self.raw["transform"]["coefficient_margin"])

    @property
    def header_bits(self) -> int:
        return int(self.raw["payload"]["header_bits"])

    @property
    def text_encoding(self) -> str:
        return str(self.raw["payload"]["text_encoding"])


def load_config(config_path: Path) -> AppConfig:
    with config_path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file)

    root = config_path.parent
    paths = raw["paths"]
    app_paths = ProjectPaths(
        input_video=root / paths["input_video"],
        stego_video=root / paths["stego_video"],
        stego_preview_video=root / paths["stego_preview_video"],
        extracted_text=root / paths["extracted_text"],
        report_json=root / paths["report_json"],
        process_log=root / paths["process_log"],
        development_log=root / paths["development_log"],
    )

    for directory in [
        app_paths.stego_video.parent,
        app_paths.extracted_text.parent,
        app_paths.report_json.parent,
        app_paths.process_log.parent,
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    return AppConfig(raw=raw, paths=app_paths)
