"""Extraction pipeline for adaptive DWT-DCT video steganography."""

from __future__ import annotations

import logging
from typing import List, Optional

import numpy as np

from src.block_selector import select_blocks
from src.config import AppConfig
from src.frame_analyzer import combined_score_map
from src.transform_engine import extract_bit_pairwise, forward_block
from src.utils import bits_to_text, fixed_bits_to_int
from src.video_loader import to_luma_channel


def extract_message(
    stego_frames: List[np.ndarray],
    config: AppConfig,
    logger: logging.Logger,
    reference_frames: Optional[List[np.ndarray]] = None,
) -> str:
    extracted_bits = ""
    header_value = None
    expected_total = None
    prev_luma = None

    if reference_frames is None:
        reference_frames = stego_frames

    prev_ref_luma = None
    for frame_idx, stego_frame in enumerate(stego_frames):
        ref_frame = reference_frames[frame_idx] if frame_idx < len(reference_frames) else stego_frame
        ref_luma, _ = to_luma_channel(ref_frame, config.raw["video"]["color_space"])
        luma, _ = to_luma_channel(stego_frame, config.raw["video"]["color_space"])
        score_map = combined_score_map(
            prev_luma=prev_ref_luma,
            curr_luma=ref_luma,
            motion_weight=config.motion_weight,
            texture_weight=config.texture_weight,
            canny_low=config.canny_thresholds[0],
            canny_high=config.canny_thresholds[1],
        )
        blocks = select_blocks(score_map, config.block_size, config.top_block_ratio)

        for block in blocks:
            patch = luma[block.y : block.y + config.block_size, block.x : block.x + config.block_size]
            bundle = forward_block(patch, config.raw["transform"]["wavelet"])
            bit = extract_bit_pairwise(
                bundle.dct_hh,
                idx_a=config.dct_pair_indices[0],
                idx_b=config.dct_pair_indices[1],
            )
            extracted_bits += bit

            if header_value is None and len(extracted_bits) >= config.header_bits:
                header_value = fixed_bits_to_int(extracted_bits[: config.header_bits])
                expected_total = config.header_bits + header_value
                logger.info("Header decoded. Payload bit length: %s", header_value)

            if expected_total is not None and len(extracted_bits) >= expected_total:
                msg_bits = extracted_bits[config.header_bits : expected_total]
                text = bits_to_text(msg_bits, config.text_encoding)
                logger.info("Extraction completed at frame %s.", frame_idx)
                return text

        prev_ref_luma = ref_luma

    raise ValueError("Failed to extract complete payload. Video may not contain full message.")
