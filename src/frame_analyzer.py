"""Frame-level analysis orchestrator."""

from __future__ import annotations

from typing import Optional

import numpy as np

from src.motion_detector import motion_map
from src.texture_analyzer import edge_texture_map


def combined_score_map(
    prev_luma: Optional[np.ndarray],
    curr_luma: np.ndarray,
    motion_weight: float,
    texture_weight: float,
    canny_low: int,
    canny_high: int,
) -> np.ndarray:
    texture = edge_texture_map(curr_luma, canny_low, canny_high).astype(np.float32)
    if prev_luma is None:
        motion = np.zeros_like(texture, dtype=np.float32)
    else:
        motion = motion_map(prev_luma, curr_luma).astype(np.float32)
    combined = (motion_weight * motion) + (texture_weight * texture)
    return combined
