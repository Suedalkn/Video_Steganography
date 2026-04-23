"""Evaluation metrics for stego quality and extraction accuracy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import cv2
import numpy as np
from skimage.metrics import structural_similarity


def compute_psnr_for_videos(original_frames: List[np.ndarray], stego_frames: List[np.ndarray]) -> float:
    size = min(len(original_frames), len(stego_frames))
    values = [cv2.PSNR(original_frames[i], stego_frames[i]) for i in range(size)]
    return float(np.mean(values)) if values else 0.0


def compute_ssim_for_videos(original_frames: List[np.ndarray], stego_frames: List[np.ndarray]) -> float:
    size = min(len(original_frames), len(stego_frames))
    values = []
    for i in range(size):
        gray_a = cv2.cvtColor(original_frames[i], cv2.COLOR_BGR2GRAY)
        gray_b = cv2.cvtColor(stego_frames[i], cv2.COLOR_BGR2GRAY)
        values.append(structural_similarity(gray_a, gray_b, data_range=255))
    return float(np.mean(values)) if values else 0.0


def extraction_accuracy(original_text: str, extracted_text: str) -> float:
    if not original_text:
        return 1.0 if not extracted_text else 0.0
    matches = sum(1 for a, b in zip(original_text, extracted_text) if a == b)
    return matches / len(original_text)


def write_report(path: Path, report: Dict[str, float | str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
