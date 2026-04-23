"""DWT-DCT transform operations for block-level embedding."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
import pywt


@dataclass
class TransformBundle:
    ll: np.ndarray
    lh: np.ndarray
    hl: np.ndarray
    hh: np.ndarray
    dct_hh: np.ndarray


def forward_block(block: np.ndarray, wavelet: str) -> TransformBundle:
    ll, (lh, hl, hh) = pywt.dwt2(block.astype(np.float32), wavelet)
    dct_hh = cv2.dct(hh.astype(np.float32))
    return TransformBundle(ll=ll, lh=lh, hl=hl, hh=hh, dct_hh=dct_hh)


def inverse_block(bundle: TransformBundle, wavelet: str) -> np.ndarray:
    hh_idct = cv2.idct(bundle.dct_hh.astype(np.float32))
    reconstructed = pywt.idwt2((bundle.ll, (bundle.lh, bundle.hl, hh_idct)), wavelet)
    return np.clip(reconstructed, 0, 255).astype(np.uint8)


def embed_bit_pairwise(dct_block: np.ndarray, bit: str, idx_a: int, idx_b: int, margin: float) -> np.ndarray:
    flat = dct_block.flatten()
    a = float(flat[idx_a])
    b = float(flat[idx_b])
    if bit == "1" and a <= b + margin:
        a = b + margin
    elif bit == "0" and b <= a + margin:
        b = a + margin
    flat[idx_a] = a
    flat[idx_b] = b
    return flat.reshape(dct_block.shape)


def extract_bit_pairwise(dct_block: np.ndarray, idx_a: int, idx_b: int) -> str:
    flat = dct_block.flatten()
    return "1" if float(flat[idx_a]) > float(flat[idx_b]) else "0"
