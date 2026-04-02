"""Tests for tiff_predictor_2.py

Ported from tiff-predictor-2-c/test_tiff_predictor_2.c.  The Python tests
call encode()/decode() with bytes + parameters (the public API), rather
than testing internal helpers directly.
"""

import array

import pytest

from tiff_predictor_2 import decode, encode


def _to_bytes(typecode: str, values: list[int]) -> bytes:
    """Convert a list of integers to bytes via array.array (native byte order)."""
    return array.array(typecode, values).tobytes()


# ---- decode tests -----------------------------------------------------------


class TestDecode:
    def test_bps1(self) -> None:
        """[10, 5, 3, 1] -> [10, 15, 18, 19]"""
        data = _to_bytes("B", [10, 5, 3, 1])
        expected = _to_bytes("B", [10, 15, 18, 19])
        assert decode(data, 1, 4) == expected

    def test_bps1_wrapping(self) -> None:
        """200 + 100 = 300, mod 256 = 44."""
        data = _to_bytes("B", [200, 100])
        result = array.array("B", decode(data, 1, 2))
        assert result[0] == 200
        assert result[1] == (200 + 100) % 256

    def test_bps2(self) -> None:
        """[1000, 500, 200] -> [1000, 1500, 1700]"""
        data = _to_bytes("H", [1000, 500, 200])
        expected = _to_bytes("H", [1000, 1500, 1700])
        assert decode(data, 2, 3) == expected

    def test_bps4(self) -> None:
        """[100000, 50000, 25000] -> [100000, 150000, 175000]"""
        data = _to_bytes("I", [100000, 50000, 25000])
        expected = _to_bytes("I", [100000, 150000, 175000])
        assert decode(data, 4, 3) == expected

    def test_multirow(self) -> None:
        """2 rows, width=3, bps=1 — rows decoded independently."""
        data = _to_bytes("B", [10, 5, 3, 20, 2, 1])
        expected = _to_bytes("B", [10, 15, 18, 20, 22, 23])
        assert decode(data, 1, 3) == expected

    def test_single_column(self) -> None:
        """width=1: nothing to accumulate, buffer unchanged."""
        data = _to_bytes("B", [42, 99])
        assert decode(data, 1, 1) == data


# ---- encode tests -----------------------------------------------------------


class TestEncode:
    def test_bps1(self) -> None:
        """[10, 15, 18, 19] -> [10, 5, 3, 1]"""
        data = _to_bytes("B", [10, 15, 18, 19])
        expected = _to_bytes("B", [10, 5, 3, 1])
        assert encode(data, 1, 4) == expected

    def test_bps1_wrapping(self) -> None:
        """44 - 200 = -156, mod 256 = 100."""
        data = _to_bytes("B", [200, 44])
        result = array.array("B", encode(data, 1, 2))
        assert result[0] == 200
        assert result[1] == (44 - 200) % 256

    def test_bps2(self) -> None:
        """[1000, 1500, 1700] -> [1000, 500, 200]"""
        data = _to_bytes("H", [1000, 1500, 1700])
        expected = _to_bytes("H", [1000, 500, 200])
        assert encode(data, 2, 3) == expected

    def test_bps4(self) -> None:
        """[100000, 150000, 175000] -> [100000, 50000, 25000]"""
        data = _to_bytes("I", [100000, 150000, 175000])
        expected = _to_bytes("I", [100000, 50000, 25000])
        assert encode(data, 4, 3) == expected

    def test_multirow(self) -> None:
        """2 rows, width=3, bps=1 — rows encoded independently."""
        data = _to_bytes("B", [10, 15, 18, 20, 22, 23])
        expected = _to_bytes("B", [10, 5, 3, 20, 2, 1])
        assert encode(data, 1, 3) == expected

    def test_single_column(self) -> None:
        """width=1: nothing to difference, buffer unchanged."""
        data = _to_bytes("B", [42, 99])
        assert encode(data, 1, 1) == data


# ---- roundtrip tests --------------------------------------------------------


class TestRoundtrip:
    def test_encode_then_decode(self) -> None:
        original = _to_bytes("H", [1000, 1500, 1700, 2000, 2100, 2300])
        assert decode(encode(original, 2, 3), 2, 3) == original

    def test_decode_then_encode(self) -> None:
        original = _to_bytes("H", [1000, 1500, 1700, 2000, 2100, 2300])
        assert encode(decode(original, 2, 3), 2, 3) == original


# ---- invalid config tests ---------------------------------------------------


class TestInvalidConfig:
    def test_decode_bps_zero(self) -> None:
        with pytest.raises(ValueError, match="bytes_per_sample"):
            decode(b"\x01\x02\x03\x04", 0, 4)

    def test_decode_width_zero(self) -> None:
        with pytest.raises(ValueError, match="width"):
            decode(b"\x01\x02\x03\x04", 1, 0)

    def test_encode_bps_zero(self) -> None:
        with pytest.raises(ValueError, match="bytes_per_sample"):
            encode(b"\x01\x02\x03\x04", 0, 4)

    def test_encode_width_zero(self) -> None:
        with pytest.raises(ValueError, match="width"):
            encode(b"\x01\x02\x03\x04", 1, 0)
