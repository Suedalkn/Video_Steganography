"""Texture analysis helpers."""

from __future__ import annotations

import cv2
import numpy as np


def edge_texture_map(luma: np.ndarray, canny_low: int, canny_high: int) -> np.ndarray:
    edges = cv2.Canny(luma, canny_low, canny_high)
    return cv2.GaussianBlur(edges, (3, 3), 0)
