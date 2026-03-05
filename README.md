# tiff-predictor-2-python

A WebAssembly codec that implements TIFF Horizontal Differencing (Predictor=2) encoding and decoding. Written in Python, compiled to a [Wasm Component](https://component-model.bytecodealliance.org/) via [componentize-py](https://github.com/bytecodealliance/componentize-py).

This repository demonstrates that codec authors can write and ship a Wasm codec in pure Python — no C or Rust required. The trade-off is size: componentize-py bundles the CPython interpreter into the output, producing a ~41 MB binary vs. ~9 KB for the [equivalent C implementation](https://github.com/cylf-dev/tiff-predictor-2-c).

## What it does

TIFF Predictor=2 stores pixel data as row-wise differences rather than absolute values. This codec supports both directions:

- **Encode**: applies horizontal differencing (row-wise differences)
- **Decode**: reverses it via cumulative sum, restoring the original pixel values

Supports 1, 2, and 4 bytes-per-sample data (uint8, uint16, uint32).

## Wasm Component interface

The module is built as a [Wasm Component](https://component-model.bytecodealliance.org/) and exports a `codec` interface defined in a WebAssembly Interface Type ([WIT](https://component-model.bytecodealliance.org/design/wit.html)) file:

```wit
package cylf:tiff-predictor-2-python@0.1.0;

interface codec {
    encode: func(data: list<u8>, config: string) -> result<list<u8>, string>;
    decode: func(data: list<u8>, config: string) -> result<list<u8>, string>;
}

world tiff-predictor-2-python {
    export codec;
}
```

The `package` line declares a namespace, name, and version — the Component Model's equivalent of a package identifier. It scopes the interface names so they don't collide with interfaces from other packages, and it's what tooling uses to refer to this component as a dependency.

The `world` declares what this component exposes to the outside world. `export codec` means any host that loads this component can call the functions in the `codec` interface.

Both `encode` and `decode` take a byte array of pixel data and a JSON config string with `bytes_per_sample` and `width` keys, e.g. `{"bytes_per_sample": 2, "width": 256}`. Both also return a WIT [`result`](https://component-model.bytecodealliance.org/design/wit.html#results) — WIT's typed success-or-failure type, similar to Rust's `Result` or a checked exception in other languages. The two type parameters are the success type and the error type:

- **`list<u8>`** (success) — WIT's byte array; contains the encoded or decoded bytes
- **`string`** (failure) — a human-readable error message, e.g. for an invalid or missing config key

## Prerequisites

- [uv](https://docs.astral.sh/uv/)

## Build

```sh
uv sync
uv run componentize-py \
    --wit-path wit \
    --world tiff-predictor-2-python \
    componentize -p src app \
    -o tiff-predictor-2-python.wasm
```

Output: `tiff-predictor-2-python.wasm`

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
