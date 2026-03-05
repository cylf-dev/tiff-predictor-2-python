"""componentize-py entry point.

Bridges the WIT-generated Codec protocol to the pure-Python implementation
in tiff_predictor_2.py.
"""

import tiff_predictor_2
from componentize_py_types import Err


class Codec:
    def encode(self, data: bytes, config: str) -> bytes:
        try:
            return tiff_predictor_2.encode(data, config)
        except ValueError as e:
            raise Err(str(e)) from e

    def decode(self, data: bytes, config: str) -> bytes:
        try:
            return tiff_predictor_2.decode(data, config)
        except ValueError as e:
            raise Err(str(e)) from e
