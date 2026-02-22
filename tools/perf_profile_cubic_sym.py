#!/usr/bin/env python3
"""Micro-benchmarks for `cubic_sym` and `bracket_g1_g1`.

Run from repo root with the project's Python env.
Prints average runtime per call and a simple throughput metric.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# make project root importable when running this script directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import time
from typing import Tuple

import numpy as np

from tools.toe_e8_z3graded_bracket_jacobi import (
    E8Z3,
    E6Projector,
    E8Z3Bracket,
    _load_signed_cubic_triads,
)


def cubic_sym_bincount(
    br: E8Z3Bracket, u: np.ndarray, v: np.ndarray, *, scale: float
) -> np.ndarray:
    """Alternative implementation using np.bincount on real/imag parts."""
    a = br._triad_a
    b = br._triad_b
    c = br._triad_c
    s = br._triad_sign * float(scale)
    contrib_a = s * (u[b] * v[c] + u[c] * v[b])
    contrib_b = s * (u[a] * v[c] + u[c] * v[a])
    contrib_c = s * (u[a] * v[b] + u[b] * v[a])

    # np.bincount does not support complex weights; accumulate real/imag separately
    out_real = np.bincount(a, weights=contrib_a.real, minlength=27)
    out_real += np.bincount(b, weights=contrib_b.real, minlength=27)
    out_real += np.bincount(c, weights=contrib_c.real, minlength=27)
    out_imag = np.bincount(a, weights=contrib_a.imag, minlength=27)
    out_imag += np.bincount(b, weights=contrib_b.imag, minlength=27)
    out_imag += np.bincount(c, weights=contrib_c.imag, minlength=27)
    return out_real.astype(np.complex128) + 1j * out_imag.astype(np.complex128)


# try to prepare a numba implementation if available
try:
    import numba as _numba

    def make_numba_cubic_sym(br: E8Z3Bracket):
        a = br._triad_a.copy()
        b = br._triad_b.copy()
        c = br._triad_c.copy()
        s = br._triad_sign.astype(np.complex128).copy()

        @_numba.njit
        def cubic_sym_numba(u, v, scale):
            out = np.zeros(27, dtype=np.complex128)
            for t in range(a.shape[0]):
                ai = a[t]
                bi = b[t]
                ci = c[t]
                ss = s[t] * scale
                ca = ss * (u[bi] * v[ci] + u[ci] * v[bi])
                cb = ss * (u[ai] * v[ci] + u[ci] * v[ai])
                cc = ss * (u[ai] * v[bi] + u[bi] * v[ai])
                out[ai] += ca
                out[bi] += cb
                out[ci] += cc
            return out

        return cubic_sym_numba

    _NUMBA_AVAILABLE = True
except Exception:
    _NUMBA_AVAILABLE = False


def bench_cubic_sym(iterations: int = 20000) -> Tuple[float, float]:
    triads = _load_signed_cubic_triads()
    # minimal E8Z3Bracket init (projector not needed for cubic_sym)
    proj = E6Projector(
        np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(np.complex128)
    )
    br = E8Z3Bracket(e6_projector=proj, cubic_triads=triads)

    rng = np.random.default_rng(12345)
    u = rng.standard_normal(27).astype(np.complex128)
    v = rng.standard_normal(27).astype(np.complex128)

    # warmup
    for _ in range(20):
        _ = br.cubic_sym(u, v, scale=1.0)

    t0 = time.perf_counter()
    for _ in range(iterations):
        _ = br.cubic_sym(u, v, scale=1.0)
    t1 = time.perf_counter()
    total = t1 - t0
    return total, total / iterations


def bench_alternatives(iterations: int = 6000) -> dict:
    triads = _load_signed_cubic_triads()
    proj = E6Projector(
        np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(np.complex128)
    )
    br = E8Z3Bracket(e6_projector=proj, cubic_triads=triads)
    rng = np.random.default_rng(12345)
    u = rng.standard_normal(27).astype(np.complex128)
    v = rng.standard_normal(27).astype(np.complex128)

    results = {}

    # baseline
    t0 = time.perf_counter()
    for _ in range(iterations):
        _ = br.cubic_sym(u, v, scale=1.0)
    t1 = time.perf_counter()
    results["baseline_total"] = t1 - t0
    results["baseline_avg_us"] = (t1 - t0) / iterations * 1e6

    # bincount variant
    t0 = time.perf_counter()
    for _ in range(iterations):
        _ = cubic_sym_bincount(br, u, v, scale=1.0)
    t1 = time.perf_counter()
    results["bincount_total"] = t1 - t0
    results["bincount_avg_us"] = (t1 - t0) / iterations * 1e6

    # numba variant (if available)
    if _NUMBA_AVAILABLE:
        cubic_numba = make_numba_cubic_sym(br)
        # warmup compile
        _ = cubic_numba(u, v, 1.0)
        t0 = time.perf_counter()
        for _ in range(iterations):
            _ = cubic_numba(u, v, 1.0)
        t1 = time.perf_counter()
        results["numba_total"] = t1 - t0
        results["numba_avg_us"] = (t1 - t0) / iterations * 1e6
    else:
        results["numba_total"] = None
        results["numba_avg_us"] = None

    # matrix-accumulation variant (precompute small dense indicator matrices)
    A = np.zeros((27, len(br._triad_a)), dtype=np.float64)
    B = np.zeros((27, len(br._triad_a)), dtype=np.float64)
    C = np.zeros((27, len(br._triad_a)), dtype=np.float64)
    for idx, (ai, bi, ci) in enumerate(zip(br._triad_a, br._triad_b, br._triad_c)):
        A[ai, idx] = 1.0
        B[bi, idx] = 1.0
        C[ci, idx] = 1.0

    def cubic_sym_mat(u, v, scale=1.0):
        s = br._triad_sign * float(scale)
        contrib_a = s * (
            u[br._triad_b] * v[br._triad_c] + u[br._triad_c] * v[br._triad_b]
        )
        contrib_b = s * (
            u[br._triad_a] * v[br._triad_c] + u[br._triad_c] * v[br._triad_a]
        )
        contrib_c = s * (
            u[br._triad_a] * v[br._triad_b] + u[br._triad_b] * v[br._triad_a]
        )
        # matrix multiply (BLAS-backed)
        out = A.dot(contrib_a.real) + 1j * A.dot(contrib_a.imag)
        out += B.dot(contrib_b.real) + 1j * B.dot(contrib_b.imag)
        out += C.dot(contrib_c.real) + 1j * C.dot(contrib_c.imag)
        return out

    # benchmark matrix variant
    t0 = time.perf_counter()
    for _ in range(iterations):
        _ = cubic_sym_mat(u, v, scale=1.0)
    t1 = time.perf_counter()
    results["mat_total"] = t1 - t0
    results["mat_avg_us"] = (t1 - t0) / iterations * 1e6

    return results


def bench_bracket_g1g1(iterations: int = 4000) -> Tuple[float, float]:
    triads = _load_signed_cubic_triads()
    proj = E6Projector(
        np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(np.complex128)
    )
    br = E8Z3Bracket(e6_projector=proj, cubic_triads=triads)

    rng = np.random.default_rng(54321)
    X = rng.standard_normal((27, 3)).astype(np.complex128)
    Y = rng.standard_normal((27, 3)).astype(np.complex128)

    # warmup
    for _ in range(10):
        _ = br.bracket_g1_g1(X, Y)

    t0 = time.perf_counter()
    for _ in range(iterations):
        _ = br.bracket_g1_g1(X, Y)
    t1 = time.perf_counter()
    total = t1 - t0
    return total, total / iterations


if __name__ == "__main__":
    print("Benchmarking cubic_sym and bracket_g1_g1 (this may take a few seconds)...")
    total_cubic, avg_cubic = bench_cubic_sym(6000)
    print(
        f"cubic_sym (baseline): total {total_cubic:.4f}s for 6000 calls — avg {avg_cubic*1e6:.1f} µs/call"
    )
    total_br, avg_br = bench_bracket_g1g1(1200)
    print(
        f"bracket_g1_g1: total {total_br:.4f}s for 1200 calls — avg {avg_br*1e6:.1f} µs/call"
    )

    print("\nRunning alternative implementations (bincount, numba if present) ...")
    alt = bench_alternatives(6000)
    import json

    print(json.dumps(alt, indent=2))
