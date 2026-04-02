# tiff-predictor-2-python

A WebAssembly codec that implements TIFF Horizontal Differencing (Predictor=2) encoding and decoding. Written in Python, compiled to a [Wasm Component](https://component-model.bytecodealliance.org/) via [componentize-py](https://github.com/bytecodealliance/componentize-py).

This repository demonstrates that codec authors can write and ship a Wasm codec in pure Python — no C or Rust required. The trade-off is size: componentize-py bundles the CPython interpreter into the output, producing a ~41 MB binary vs. ~9 KB for the [equivalent C implementation](https://github.com/cylf-dev/tiff-predictor-2-c).

## What it does

TIFF Predictor=2 stores pixel data as row-wise differences rather than absolute values. This codec supports both directions:

- **Encode**: applies horizontal differencing (row-wise differences)
- **Decode**: reverses it via cumulative sum, restoring the original pixel values

Supports 1, 2, and 4 bytes-per-sample data (uint8, uint16, uint32).

## Wasm Component interface

The module is built as a [Wasm Component](https://component-model.bytecodealliance.org/) and exports a `transform` interface defined in a WebAssembly Interface Type ([WIT](https://component-model.bytecodealliance.org/design/wit.html)) file:

```wit
package chonkle:codec@0.1.0;

interface transform {
    type port-name = string;
    type port-map = list<tuple<port-name, list<u8>>>;

    encode: func(inputs: port-map) -> result<port-map, string>;
    decode: func(inputs: port-map) -> result<port-map, string>;
}

world codec {
    export transform;
}
```

Both `encode` and `decode` take a `port-map` — a list of named byte buffers — and return a `port-map` on success or a human-readable error string on failure.

This codec expects three input ports:

- **`bytes`** — the raw pixel data
- **`bytes_per_sample`** — UTF-8 digit string (`"1"`, `"2"`, or `"4"`)
- **`width`** — UTF-8 digit string (e.g. `"256"`)

It returns one output port:

- **`bytes`** — the encoded or decoded pixel data

## Prerequisites

- [uv](https://docs.astral.sh/uv/)

## Build

```sh
uv sync
uv run componentize-py \
    --wit-path wit \
    --world codec \
    componentize -p src app \
    -o tiff-predictor-2-python.wasm
```

Output: `tiff-predictor-2-python.wasm`

## Codec signature

The `.wasm` binary includes an embedded `chonkle:signature` custom section declaring the codec's identifier, implementation name, and input/output ports. The signature is defined in [`signature.json`](signature.json) and embedded automatically by the release workflow.

To embed locally after building:

```sh
python3 embed_signature.py tiff-predictor-2-python.wasm signature.json
```

## Development

```sh
uv run pytest -v
```

This project uses [pre-commit](https://pre-commit.com/) to run checks before each commit. Enable the hooks:

```sh
pre-commit install
```

To run all checks manually:

```sh
pre-commit run --all-files
```
