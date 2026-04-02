"""componentize-py entry point.

Bridges the WIT-generated Transform protocol to the pure-Python implementation
in tiff_predictor_2.py.
"""

from componentize_py_types import Err

import tiff_predictor_2


class Transform:
    def encode(self, inputs: list[tuple[str, bytes]]) -> list[tuple[str, bytes]]:
        try:
            data, bps, width = _unpack_inputs(inputs)
            result = tiff_predictor_2.encode(data, bps, width)
            return [("bytes", result)]
        except ValueError as e:
            raise Err(str(e)) from e

    def decode(self, inputs: list[tuple[str, bytes]]) -> list[tuple[str, bytes]]:
        try:
            data, bps, width = _unpack_inputs(inputs)
            result = tiff_predictor_2.decode(data, bps, width)
            return [("bytes", result)]
        except ValueError as e:
            raise Err(str(e)) from e


def _unpack_inputs(inputs: list[tuple[str, bytes]]) -> tuple[bytes, int, int]:
    """Extract and parse the three required ports from a port-map."""
    ports = dict(inputs)
    data = _require_port(ports, "bytes")
    bps = int(_require_port(ports, "bytes_per_sample").decode())
    width = int(_require_port(ports, "width").decode())
    return data, bps, width


def _require_port(ports: dict[str, bytes], name: str) -> bytes:
    """Look up a port by name, raising ValueError if missing."""
    if name not in ports:
        msg = f"missing required port: {name}"
        raise ValueError(msg)
    return ports[name]
