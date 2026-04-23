"""Common utility helpers for bit and text conversions."""

from __future__ import annotations

from typing import List


def text_to_bits(text: str, encoding: str = "utf-8") -> str:
    return "".join(f"{byte:08b}" for byte in text.encode(encoding))


def bits_to_text(bits: str, encoding: str = "utf-8") -> str:
    if len(bits) % 8 != 0:
        raise ValueError("Bit string length must be divisible by 8.")
    data = bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))
    return data.decode(encoding, errors="replace")


def int_to_fixed_bits(value: int, bit_length: int) -> str:
    if value < 0:
        raise ValueError("Value cannot be negative.")
    if value >= 2**bit_length:
        raise ValueError("Value exceeds fixed bit length capacity.")
    return format(value, f"0{bit_length}b")


def fixed_bits_to_int(bits: str) -> int:
    return int(bits, 2)


def chunk_bits(bits: str, chunk_size: int) -> List[str]:
    return [bits[i : i + chunk_size] for i in range(0, len(bits), chunk_size)]
