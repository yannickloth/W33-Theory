#!/usr/bin/env python3
"""
Compute basic linear-code invariants of the W(3,3) incidence structure.

Motivation:
  Several writeups in this repo interpret W33 as defining a (qutrit) code.
  Before any physics interpretation, we can at least compute objective,
  reproducible invariants of the point-line incidence matrix:
    - rank over GF(2)
    - rank over GF(3)
    - code dimensions k = n - rank(H)

We construct W(3,3) as the symplectic polar space on PG(3,3):
  points = 1D subspaces of F3^4  (40)
  lines  = totally isotropic 2D subspaces (40), each with 4 points

Outputs:
  - artifacts/w33_incidence_code_ranks.json
  - artifacts/w33_incidence_code_ranks.md
"""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path
from typing import List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "artifacts" / "w33_incidence_code_ranks.json"
OUT_MD = ROOT / "artifacts" / "w33_incidence_code_ranks.md"


def _omega(x: Tuple[int, int, int, int], y: Tuple[int, int, int, int]) -> int:
    # Standard symplectic form on F3^4 with blocks (x0,x1 | x2,x3)
    # ω(x,y) = x0*y2 - x2*y0 + x1*y3 - x3*y1  (mod 3)
    return (x[0] * y[2] - x[2] * y[0] + x[1] * y[3] - x[3] * y[1]) % 3


def _proj_normalize(v: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    v = list(v)
    for i in range(4):
        if v[i] % 3 != 0:
            inv = 1 if v[i] % 3 == 1 else 2  # inverse in F3
            return tuple((inv * x) % 3 for x in v)
    raise ValueError("zero vector")


def _construct_points() -> List[Tuple[int, int, int, int]]:
    F3 = [0, 1, 2]
    points = []
    seen = set()
    for v in product(F3, repeat=4):
        if all(x == 0 for x in v):
            continue
        pv = _proj_normalize(v)
        if pv not in seen:
            seen.add(pv)
            points.append(pv)
    if len(points) != 40:
        raise RuntimeError(f"Expected 40 points, got {len(points)}")
    return points


def _line_from_pair(
    points: List[Tuple[int, int, int, int]], i: int, j: int
) -> Tuple[int, ...]:
    """
    Given two orthogonal, distinct projective points, return the 4-point line
    they span (projectivized 2D subspace).
    """
    vi = points[i]
    vj = points[j]
    if _omega(vi, vj) != 0:
        raise ValueError("pair not orthogonal")

    combos = []
    for a in [0, 1, 2]:
        for b in [0, 1, 2]:
            if a == 0 and b == 0:
                continue
            w = tuple((a * vi[k] + b * vj[k]) % 3 for k in range(4))
            combos.append(_proj_normalize(w))

    # unique projective points in the span
    uniq = sorted(set(combos))
    if len(uniq) != 4:
        raise RuntimeError(f"Expected 4 points on a line, got {len(uniq)}")

    # map back to indices
    idx = {p: t for t, p in enumerate(points)}
    return tuple(sorted(idx[p] for p in uniq))


def _construct_lines(points: List[Tuple[int, int, int, int]]) -> List[Tuple[int, ...]]:
    lines = set()
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            if _omega(points[i], points[j]) != 0:
                continue
            lines.add(_line_from_pair(points, i, j))
    lines = sorted(lines)
    if len(lines) != 40:
        raise RuntimeError(f"Expected 40 lines, got {len(lines)}")
    if any(len(L) != 4 for L in lines):
        raise RuntimeError("Line size mismatch")
    return lines


def _incidence_matrix(n_points: int, lines: List[Tuple[int, ...]]) -> np.ndarray:
    H = np.zeros((len(lines), n_points), dtype=np.int64)
    for r, L in enumerate(lines):
        for c in L:
            H[r, c] = 1
    return H


def _rank_mod_p(H: np.ndarray, p: int) -> int:
    """Row-rank over GF(p) by Gaussian elimination."""
    A = (H.copy() % p).astype(np.int64)
    m, n = A.shape
    r = 0
    c = 0
    while r < m and c < n:
        pivot = None
        for i in range(r, m):
            if A[i, c] % p != 0:
                pivot = i
                break
        if pivot is None:
            c += 1
            continue
        if pivot != r:
            A[[r, pivot]] = A[[pivot, r]]

        inv = pow(int(A[r, c] % p), -1, p)
        A[r, :] = (A[r, :] * inv) % p

        for i in range(m):
            if i == r:
                continue
            factor = A[i, c] % p
            if factor != 0:
                A[i, :] = (A[i, :] - factor * A[r, :]) % p

        r += 1
        c += 1
    return r


def _rref_mod_p(H: np.ndarray, p: int) -> tuple[np.ndarray, list[int]]:
    """Reduced row echelon form over GF(p). Returns (RREF, pivot_columns)."""
    A = (H.copy() % p).astype(np.int64)
    m, n = A.shape
    r = 0
    pivots: list[int] = []
    for c in range(n):
        if r >= m:
            break
        pivot = None
        for i in range(r, m):
            if A[i, c] % p != 0:
                pivot = i
                break
        if pivot is None:
            continue
        if pivot != r:
            A[[r, pivot]] = A[[pivot, r]]

        inv = pow(int(A[r, c] % p), -1, p)
        A[r, :] = (A[r, :] * inv) % p

        for i in range(m):
            if i == r:
                continue
            factor = A[i, c] % p
            if factor != 0:
                A[i, :] = (A[i, :] - factor * A[r, :]) % p

        pivots.append(c)
        r += 1
    return A, pivots


def _nullspace_basis_mod_p(H: np.ndarray, p: int) -> np.ndarray:
    """
    Return a k×n matrix whose rows form a basis of {x : H x = 0} over GF(p).
    Uses RREF pivot/free-variable construction.
    """
    R, pivots = _rref_mod_p(H, p)
    n = H.shape[1]
    pivot_set = set(pivots)
    free_cols = [c for c in range(n) if c not in pivot_set]

    # Map pivot column -> pivot row index in R
    pivot_row_for_col = {c: i for i, c in enumerate(pivots)}

    basis = []
    for f in free_cols:
        x = np.zeros((n,), dtype=np.int64)
        x[f] = 1
        for c in pivots:
            i = pivot_row_for_col[c]
            x[c] = (-R[i, f]) % p
        basis.append(x)
    if not basis:
        return np.zeros((0, n), dtype=np.int64)
    return np.stack(basis, axis=0)


def _gf2_weight_distribution(null_basis: np.ndarray) -> tuple[int, dict[int, int]]:
    """Exact weight distribution of the GF(2) code generated by null_basis."""
    k, n = null_basis.shape
    if k == 0:
        return 0, {}

    basis_masks: list[int] = []
    for row in null_basis:
        mask = 0
        for i, bit in enumerate(row.tolist()):
            if bit & 1:
                mask |= 1 << i
        basis_masks.append(mask)

    codeword_mask = [0] * (1 << k)
    weight_hist: dict[int, int] = {}
    min_w = n + 1
    for m in range(1, 1 << k):
        lsb = m & -m
        bit = lsb.bit_length() - 1
        prev = m ^ lsb
        codeword_mask[m] = codeword_mask[prev] ^ basis_masks[bit]
        w = codeword_mask[m].bit_count()
        weight_hist[w] = weight_hist.get(w, 0) + 1
        if w < min_w:
            min_w = w
    return min_w, dict(sorted(weight_hist.items()))


def main() -> None:
    points = _construct_points()
    lines = _construct_lines(points)
    H = _incidence_matrix(len(points), lines)

    rank2 = _rank_mod_p(H, 2)
    rank3 = _rank_mod_p(H, 3)
    n = H.shape[1]

    null2 = _nullspace_basis_mod_p(H, 2)
    d2, wh2 = _gf2_weight_distribution(null2)

    out = {
        "structure": {
            "points": len(points),
            "lines": len(lines),
            "line_size": 4,
            "point_degree_lines": 4,
        },
        "incidence_matrix": {"shape": [int(H.shape[0]), int(H.shape[1])]},
        "gf2": {"rank": rank2, "k": n - rank2, "d_min": d2, "weight_hist": wh2},
        "gf3": {"rank": rank3, "k": n - rank3},
        "verdict": "Computed incidence-matrix ranks for W(3,3)",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")

    md = []
    md.append("# W(3,3) incidence code ranks")
    md.append("")
    md.append(f"- points: `{out['structure']['points']}`")
    md.append(
        f"- lines: `{out['structure']['lines']}` (each size `{out['structure']['line_size']}`)"
    )
    md.append("")
    md.append("| field | rank(H) | k = n-rank |")
    md.append("|---|---:|---:|")
    md.append(f"| GF(2) | `{rank2}` | `{n - rank2}` |")
    md.append(f"| GF(3) | `{rank3}` | `{n - rank3}` |")
    md.append("")
    md.append(f"- GF(2) exact minimum distance (incidence parity-check code): `{d2}`")
    md.append("This is a certificate-level computation (no experimental inputs).")
    md.append("")
    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"GF(2): rank={rank2}, k={n-rank2}, d_min={d2}")
    print(f"GF(3): rank={rank3}, k={n-rank3}")


if __name__ == "__main__":
    main()
