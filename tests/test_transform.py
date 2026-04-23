import numpy as np

from src.transform_engine import embed_bit_pairwise, extract_bit_pairwise, forward_block


def test_pairwise_embed_extract():
    block = np.full((8, 8), 120, dtype=np.uint8)
    bundle = forward_block(block, "haar")
    modified = embed_bit_pairwise(bundle.dct_hh.copy(), "1", 2, 5, 5.0)
    bit = extract_bit_pairwise(modified, 2, 5)
    assert bit == "1"
