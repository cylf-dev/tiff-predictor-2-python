"""TIFF horizontal differencing predictor (Predictor=2).

Encoding applies row-wise differencing; decoding undoes it via cumulative sum.
Pure Python — uses only the standard library so it can be compiled to
WebAssembly with componentize-py.
"""

import array

# bytes-per-sample -> array typecode (unsigned integers)
_TYPECODES: dict[int, str] = {1: "B", 2: "H", 4: "I"}


def decode(data: bytes, bps: int, width: int) -> bytes:
    """Undo horizontal differencing via cumulative sum per row."""
    _validate(bps, width)
    height = len(data) // (width * bps)
    mask = (1 << (bps * 8)) - 1

    arr = array.array(_TYPECODES[bps], data)
    for row in range(height):
        base = row * width
        for col in range(1, width):
            arr[base + col] = (arr[base + col] + arr[base + col - 1]) & mask

    return arr.tobytes()


def encode(data: bytes, bps: int, width: int) -> bytes:
    """Apply horizontal differencing (row-wise differences).

    Iterates backwards so each subtraction reads the original predecessor.
    """
    _validate(bps, width)
    height = len(data) // (width * bps)
    mask = (1 << (bps * 8)) - 1

    arr = array.array(_TYPECODES[bps], data)
    for row in range(height):
        base = row * width
        for col in range(width - 1, 0, -1):
            arr[base + col] = (arr[base + col] - arr[base + col - 1]) & mask

    return arr.tobytes()


def _validate(bps: int, width: int) -> None:
    """Validate parameters. Raises ValueError for invalid values."""
    if bps not in _TYPECODES:
        msg = f"unsupported bytes_per_sample: {bps}"
        raise ValueError(msg)
    if width <= 0:
        msg = f"invalid width: {width}"
        raise ValueError(msg)
