"""Motion estimation between adjacent frames."""

from __future__ import annotations

import cv2
import numpy as np


def motion_map(prev_luma: np.ndarray, curr_luma: np.ndarray) -> np.ndarray:
    diff = cv2.absdiff(prev_luma, curr_luma)
    return cv2.GaussianBlur(diff, (3, 3), 0)
