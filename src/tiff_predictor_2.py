"""TIFF horizontal differencing predictor (Predictor=2).

Encoding applies row-wise differencing; decoding undoes it via cumulative sum.
Pure Python — uses only the standard library so it can be compiled to
WebAssembly with componentize-py.
"""

import array
import json

# bytes-per-sample -> array typecode (unsigned integers)
_TYPECODES: dict[int, str] = {1: "B", 2: "H", 4: "I"}


def decode(data: bytes, config: str) -> bytes:
    """Undo horizontal differencing via cumulative sum per row."""
    bps, width, height = _parse_config(config, len(data))
    mask = (1 << (bps * 8)) - 1

    arr = array.array(_TYPECODES[bps], data)
    for row in range(height):
        base = row * width
        for col in range(1, width):
            arr[base + col] = (arr[base + col] + arr[base + col - 1]) & mask

    return arr.tobytes()


def encode(data: bytes, config: str) -> bytes:
    """Apply horizontal differencing (row-wise differences).

    Iterates backwards so each subtraction reads the original predecessor.
    """
    bps, width, height = _parse_config(config, len(data))
    mask = (1 << (bps * 8)) - 1

    arr = array.array(_TYPECODES[bps], data)
    for row in range(height):
        base = row * width
        for col in range(width - 1, 0, -1):
            arr[base + col] = (arr[base + col] - arr[base + col - 1]) & mask

    return arr.tobytes()


def _parse_config(config: str, data_len: int) -> tuple[int, int, int]:
    """Parse JSON config and return (bps, width, height).

    Raises ValueError for invalid or missing parameters.
    """
    cfg = json.loads(config)
    bps = cfg.get("bytes_per_sample", 0)
    width = cfg.get("width", 0)

    if bps not in _TYPECODES:
        msg = f"unsupported bytes_per_sample: {bps}"
        raise ValueError(msg)
    if width <= 0:
        msg = f"invalid width: {width}"
        raise ValueError(msg)

    height = data_len // (width * bps)
    return bps, width, height
