"""Video reading and writing utilities."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np


def load_video_frames(video_path: Path, max_frames: int | None = None) -> tuple[List[np.ndarray], float]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    frames: List[np.ndarray] = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
        if max_frames is not None and len(frames) >= max_frames:
            break
    cap.release()
    if not frames:
        raise ValueError("No frame could be read from the video.")
    return frames, fps


def write_video_frames(
    video_path: Path,
    frames: List[np.ndarray],
    fps: float,
    preferred_codec: str = "FFV1",
) -> None:
    if not frames:
        raise ValueError("Frame list is empty; cannot write video.")
    height, width = frames[0].shape[:2]
    codecs = [preferred_codec, "MJPG", "XVID", "mp4v"]
    writer = None
    for codec in codecs:
        candidate = cv2.VideoWriter(
            str(video_path),
            cv2.VideoWriter_fourcc(*codec),
            fps,
            (width, height),
        )
        if candidate.isOpened():
            writer = candidate
            break
        candidate.release()
    if writer is None:
        raise RuntimeError("No supported video codec found for writing stego output.")
    for frame in frames:
        writer.write(frame)
    writer.release()


def to_luma_channel(frame: np.ndarray, color_space: str = "ycrcb") -> Tuple[np.ndarray, np.ndarray]:
    if color_space.lower() == "ycrcb":
        converted = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        return converted[:, :, 0], converted
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray, gray


def from_luma_channel(luma: np.ndarray, reference: np.ndarray, color_space: str = "ycrcb") -> np.ndarray:
    if color_space.lower() == "ycrcb":
        merged = reference.copy()
        merged[:, :, 0] = luma
        return cv2.cvtColor(merged, cv2.COLOR_YCrCb2BGR)
    return cv2.cvtColor(luma, cv2.COLOR_GRAY2BGR)
