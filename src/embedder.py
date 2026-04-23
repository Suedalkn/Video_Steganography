"""Embedding pipeline for adaptive DWT-DCT video steganography."""

from __future__ import annotations

import logging
from typing import List

import numpy as np

from src.block_selector import select_blocks
from src.config import AppConfig
from src.frame_analyzer import combined_score_map
from src.transform_engine import embed_bit_pairwise, forward_block, inverse_block
from src.utils import int_to_fixed_bits, text_to_bits
from src.video_loader import from_luma_channel, to_luma_channel


def embed_message(frames: List[np.ndarray], message: str, config: AppConfig, logger: logging.Logger) -> List[np.ndarray]:
    msg_bits = text_to_bits(message, config.text_encoding)
    payload = int_to_fixed_bits(len(msg_bits), config.header_bits) + msg_bits
    bit_index = 0
    stego_frames: List[np.ndarray] = []

    prev_luma = None
    for frame_idx, frame in enumerate(frames):
        luma, ref = to_luma_channel(frame, config.raw["video"]["color_space"])
        score_map = combined_score_map(
            prev_luma=prev_luma,
            curr_luma=luma,
            motion_weight=config.motion_weight,
            texture_weight=config.texture_weight,
            canny_low=config.canny_thresholds[0],
            canny_high=config.canny_thresholds[1],
        )
        blocks = select_blocks(score_map, config.block_size, config.top_block_ratio)
        working = luma.copy()

        for block in blocks:
            if bit_index >= len(payload):
                break
            patch = working[block.y : block.y + config.block_size, block.x : block.x + config.block_size]
            bundle = forward_block(patch, config.raw["transform"]["wavelet"])
            bundle.dct_hh = embed_bit_pairwise(
                bundle.dct_hh,
                payload[bit_index],
                idx_a=config.dct_pair_indices[0],
                idx_b=config.dct_pair_indices[1],
                margin=config.coefficient_margin,
            )
            patch_recon = inverse_block(bundle, config.raw["transform"]["wavelet"])
            working[block.y : block.y + config.block_size, block.x : block.x + config.block_size] = patch_recon
            bit_index += 1

        stego_frames.append(from_luma_channel(working, ref, config.raw["video"]["color_space"]))
        prev_luma = luma
        logger.info("Frame %s processed, embedded bits so far: %s", frame_idx, bit_index)
        if bit_index >= len(payload):
            stego_frames.extend(frames[frame_idx + 1 :])
            break

    if bit_index < len(payload):
        raise ValueError(
            f"Payload too large. Embedded {bit_index} bits but need {len(payload)} bits."
        )
    logger.info("Embedding completed. Total embedded bits: %s", bit_index)
    return stego_frames
