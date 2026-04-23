"""Adaptive block ranking and selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class BlockRef:
    y: int
    x: int
    score: float


def select_blocks(score_map: np.ndarray, block_size: int, top_ratio: float) -> List[BlockRef]:
    h, w = score_map.shape
    blocks: List[BlockRef] = []
    for y in range(0, h - block_size + 1, block_size):
        for x in range(0, w - block_size + 1, block_size):
            block = score_map[y : y + block_size, x : x + block_size]
            blocks.append(BlockRef(y=y, x=x, score=float(np.mean(block))))

    if not blocks:
        return []

    blocks.sort(key=lambda item: item.score, reverse=True)
    count = max(1, int(len(blocks) * top_ratio))
    return blocks[:count]
