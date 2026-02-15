#!/usr/bin/env python3
"""
Quantum error-correction primitives from W(3,3)

Pillar 45 — Ternary code & stabilizer-building primitives
- Build natural ternary (GF(3)) linear codes from W33 incidence / triangle data
- Compute code dimension (row-space over GF(3)) and minimum Hamming distance
- Show existence of MUBs / Pauli commuting sets (link to w33_two_qutrit_pauli)

Usage:
    python scripts/w33_quantum_error_correction.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Tuple

import numpy as np
from w33_homology import build_clique_complex, build_w33

from w33_h1_decomposition import build_incidence_matrix


def compute_basis_rows_mod3(M: np.ndarray) -> np.ndarray:
    """Compute a basis for the row-space of integer matrix M over GF(3)."""
    A = (M % 3).astype(int).copy()
    v, b = A.shape
    used = [False] * v
    basis = []
    for c in range(b):
        pivot = None
        for i in range(v):
            if not used[i] and A[i, c] % 3 != 0:
                pivot = i
                break
        if pivot is None:
            continue
        used[pivot] = True
        pv = A[pivot] % 3
        inv = pow(int(pv[c]), -1, 3)
        pv = (pv * inv) % 3
        basis.append(pv.copy())
        for i in range(v):
            if i != pivot and A[i, c] % 3 != 0:
                A[i, :] = (A[i, :] - A[i, c] * pv) % 3
    if basis:
        return np.array(basis, dtype=int)
    return np.zeros((0, b), dtype=int)


def code_min_distance_from_basis(basis: np.ndarray) -> int:
    """Enumerate all nonzero ternary linear combinations of basis to find min Hamming weight.
    Works well when basis dimension bs is modest (bs <= 12..14 in practice here).
    """
    bs = basis.shape[0]
    if bs == 0:
        return 0
    total = 3**bs
    min_w = basis.shape[1] + 1
    # enumerate combinations
    for idx in range(1, total):
        # base-3 digits
        coeffs = []
        x = idx
        for _ in range(bs):
            coeffs.append(x % 3)
            x //= 3
        coeffs = np.array(coeffs[::-1], dtype=int)
        cw = (coeffs @ basis) % 3
        w = int(np.count_nonzero(cw))
        if 0 < w < min_w:
            min_w = w
            if min_w == 1:
                return 1
    return int(min_w) if min_w <= basis.shape[1] else 0


def analyze_w33_qec() -> dict:
    t0 = time.time()
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    # triangle-edge incidence (C2 -> C1)
    from w33_homology import boundary_matrix

    B2 = boundary_matrix(simplices[2], simplices[1]).astype(int)  # tri x edge
    M = B2.T  # edge x triangle incidence

    basis = compute_basis_rows_mod3(M)
    basis_dim = basis.shape[0]
    min_dist = code_min_distance_from_basis(basis)

    results = {
        "basis_dim": int(basis_dim),
        "code_length": int(M.shape[1]),
        "min_distance": int(min_dist),
        "elapsed_seconds": time.time() - t0,
    }

    out_dir = Path(__file__).resolve().parent.parent / "checks"
    out_dir.mkdir(exist_ok=True)
    fname = out_dir / f"PART_CXV_qec_{int(time.time())}.json"
    with open(fname, "w") as f:
        json.dump(results, f, indent=2)
    return results


if __name__ == "__main__":
    print(json.dumps(analyze_w33_qec(), indent=2))
