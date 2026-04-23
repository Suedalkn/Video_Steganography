from src.utils import bits_to_text, int_to_fixed_bits, text_to_bits


def test_text_bit_roundtrip():
    text = "Merhaba Proje"
    bits = text_to_bits(text)
    assert bits_to_text(bits) == text


def test_fixed_header():
    value = 123
    bits = int_to_fixed_bits(value, 16)
    assert len(bits) == 16
    assert int(bits, 2) == value
