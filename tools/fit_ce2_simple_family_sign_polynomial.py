#!/usr/bin/env python3
"""Fit an explicit GF(2) polynomial law for the CE2 simple-family sign.

Background
----------
`scripts/ce2_global_cocycle.py` currently needs a sign(c, match, other) ∈ {±1}
for the dominant "simple family" of CE2 local solutions. We already ship a
compact committed map with 864 entries:

  committed_artifacts/ce2_simple_family_sign_map.json

This tool derives a *closed form* for that sign as a degree-≤4 polynomial over
GF(2) (an algebraic normal form / Z2 phase):

  sign = (-1)^(P(bits(c), bits(match), bits(other)))

where each Heisenberg trit (u1,u2,z) ∈ F3 is encoded into two GF(2) bits:
  0 -> 00, 1 -> 10, 2 -> 01  (interpreted as [is1, is2]).

We use the fixed trit order:
  (c.u1, c.u2, c.z, match.u1, match.u2, match.z, other.u1, other.u2, other.z)

The monomial basis is all subsets of the 18 input bits of size ≤ 4, ordered by
degree then lexicographically (deg-lex). There are 4048 such monomials.

Output
------
Writes a committed artifact:
  committed_artifacts/ce2_simple_family_sign_poly_gf2_deg4.json
containing the set of monomial indices with coefficient 1.

Run:
  & .venv\\Scripts\\python.exe -X utf8 tools\\fit_ce2_simple_family_sign_polynomial.py
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
SIGN_MAP_PATH = ROOT / "committed_artifacts" / "ce2_simple_family_sign_map.json"
HEIS_MODEL_PATH = ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json"

DEFAULT_OUT = ROOT / "committed_artifacts" / "ce2_simple_family_sign_poly_gf2_deg4.json"


def _load_heisenberg_vecs() -> dict[int, tuple[int, int, int]]:
    model = json.loads(HEIS_MODEL_PATH.read_text(encoding="utf-8"))
    e6id_to_h = model.get("e6id_to_heisenberg")
    if not isinstance(e6id_to_h, dict) or len(e6id_to_h) != 27:
        raise ValueError("Unexpected e6id_to_heisenberg mapping")
    out: dict[int, tuple[int, int, int]] = {}
    for k, payload in e6id_to_h.items():
        if not isinstance(payload, dict):
            raise ValueError("Unexpected heisenberg payload type")
        u = payload.get("u")
        z = payload.get("z")
        if not (isinstance(u, list) and len(u) == 2):
            raise ValueError("Unexpected heisenberg u payload")
        vec = (int(u[0]) % 3, int(u[1]) % 3, int(z) % 3)
        out[int(k)] = vec
    if set(out.keys()) != set(range(27)):
        raise ValueError("Heisenberg mapping must cover e6 ids 0..26")
    return out


def _load_sign_map() -> dict[tuple[int, int, int], int]:
    data = json.loads(SIGN_MAP_PATH.read_text(encoding="utf-8"))
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise ValueError("Unexpected sign-map JSON format (missing entries list)")
    out: dict[tuple[int, int, int], int] = {}
    for rec in entries:
        if not isinstance(rec, dict):
            continue
        c = int(rec["c"])
        m = int(rec["match"])
        o = int(rec["other"])
        s = int(rec["sign"])
        if s not in (-1, 1):
            raise ValueError(f"Unexpected sign value {s} for key {(c,m,o)}")
        out[(c, m, o)] = s
    if len(out) != 864:
        raise ValueError(f"Expected 864 sign entries, got {len(out)}")
    return out


def _encode_trit_pair_bits(trit: int) -> tuple[int, int]:
    """Encode a trit in {0,1,2} into two GF(2) bits (is1,is2)."""
    t = int(trit) % 3
    if t == 0:
        return (0, 0)
    if t == 1:
        return (1, 0)
    return (0, 1)


def _encode_input_bits(
    e6id_to_vec: dict[int, tuple[int, int, int]],
    key: tuple[int, int, int],
) -> int:
    c, m, o = key
    vc = e6id_to_vec[int(c)]
    vm = e6id_to_vec[int(m)]
    vo = e6id_to_vec[int(o)]
    trits = (
        vc[0],
        vc[1],
        vc[2],
        vm[0],
        vm[1],
        vm[2],
        vo[0],
        vo[1],
        vo[2],
    )
    bits_mask = 0
    for i, t in enumerate(trits):
        b0, b1 = _encode_trit_pair_bits(t)
        if b0:
            bits_mask |= 1 << (2 * i + 0)
        if b1:
            bits_mask |= 1 << (2 * i + 1)
    return bits_mask


def _deg_lex_monomials_upto_degree(max_degree: int) -> list[int]:
    """Return list of monomial masks on 18 input bits, ordered by (deg, lex)."""
    if max_degree < 0:
        raise ValueError("max_degree must be >= 0")
    n_bits = 18
    out: list[int] = [0]  # constant
    for d in range(1, max_degree + 1):
        for combo in combinations(range(n_bits), d):
            m = 0
            for b in combo:
                m |= 1 << b
            out.append(m)
    return out


def _row_feature_mask(
    mask_to_feature_idx: dict[int, int],
    input_bits_mask: int,
    max_degree: int,
) -> int:
    """Return feature-mask (length n_features) for monomials satisfied by input."""
    ones = [i for i in range(18) if ((input_bits_mask >> i) & 1)]
    # constant term always 1
    feature_mask = 1 << mask_to_feature_idx[0]
    for d in range(1, min(max_degree, len(ones)) + 1):
        for combo in combinations(ones, d):
            m = 0
            for b in combo:
                m |= 1 << b
            feature_mask |= 1 << mask_to_feature_idx[m]
    return feature_mask


def _solve_rref_gf2(rows_aug: list[int], n_vars: int) -> tuple[int, list[int]]:
    """Solve A x = b over GF(2) by RREF. Return (x_bitmask, pivot_cols)."""
    rows = [int(r) for r in rows_aug]
    m = len(rows)
    pivot_row = 0
    pivots: list[int] = []
    for col in range(n_vars):
        # Find a pivot.
        pivot = None
        for r in range(pivot_row, m):
            if (rows[r] >> col) & 1:
                pivot = r
                break
        if pivot is None:
            continue
        # Bring pivot into position.
        if pivot != pivot_row:
            rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        # Eliminate this column from all other rows.
        prow = rows[pivot_row]
        for r in range(m):
            if r != pivot_row and ((rows[r] >> col) & 1):
                rows[r] ^= prow
        pivots.append(col)
        pivot_row += 1
        if pivot_row >= m:
            break

    rhs_bit = 1 << n_vars
    var_mask = rhs_bit - 1
    for r in rows:
        if (r & var_mask) == 0 and (r & rhs_bit):
            raise ValueError("Inconsistent GF(2) system (0 = 1 row found)")

    # One deterministic solution: free vars = 0, pivot vars = rhs.
    x = 0
    for i, col in enumerate(pivots):
        if rows[i] & rhs_bit:
            x |= 1 << col
    return x, pivots


def _verify_solution(rows: list[tuple[int, int]], x: int) -> int:
    """Return mismatch count for A x = b over GF(2)."""
    mism = 0
    for mask, rhs in rows:
        lhs = (int(mask) & int(x)).bit_count() & 1
        if lhs != (int(rhs) & 1):
            mism += 1
    return mism


def _degree_histogram(
    monomial_masks: list[int], coeff_idx: Iterable[int]
) -> dict[int, int]:
    hist: dict[int, int] = {}
    for idx in coeff_idx:
        deg = int(monomial_masks[int(idx)]).bit_count()
        hist[deg] = hist.get(deg, 0) + 1
    return dict(sorted(hist.items()))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--max-degree", type=int, default=4)
    args = ap.parse_args()

    max_degree = int(args.max_degree)
    if max_degree != 4:
        raise ValueError("This tool is currently standardized on degree 4 only.")

    e6id_to_vec = _load_heisenberg_vecs()
    sign_map = _load_sign_map()

    monomial_masks = _deg_lex_monomials_upto_degree(max_degree)
    n_features = len(monomial_masks)
    if n_features != 4048:
        raise RuntimeError(f"Expected 4048 monomials, got {n_features}")
    mask_to_feature_idx = {m: i for i, m in enumerate(monomial_masks)}
    if len(mask_to_feature_idx) != n_features:
        raise RuntimeError("Duplicate monomial mask detected")

    rows_aug: list[int] = []
    rows_plain: list[tuple[int, int]] = []
    for key, sgn in sorted(sign_map.items()):
        x_bits = _encode_input_bits(e6id_to_vec, key)
        feat_mask = _row_feature_mask(mask_to_feature_idx, x_bits, max_degree)
        rhs = 0 if int(sgn) == 1 else 1
        rows_plain.append((feat_mask, rhs))
        rows_aug.append(feat_mask | (rhs << n_features))

    # Solve.
    coeff_mask, pivots = _solve_rref_gf2(rows_aug, n_features)
    mism = _verify_solution(rows_plain, coeff_mask)
    if mism != 0:
        raise RuntimeError(f"Fit verification failed: mismatches={mism}")

    coeff_indices = [i for i in range(n_features) if ((coeff_mask >> i) & 1)]
    deg_hist = _degree_histogram(monomial_masks, coeff_indices)

    payload = {
        "kind": "gf2_polynomial",
        "max_degree": max_degree,
        "input_bits": 18,
        "feature_count": n_features,
        "sample_count": len(rows_plain),
        "rank": len(pivots),
        "nullity": n_features - len(pivots),
        "coeff_weight": len(coeff_indices),
        "coeff_degree_hist": deg_hist,
        "trit_order": [
            "c.u1",
            "c.u2",
            "c.z",
            "match.u1",
            "match.u2",
            "match.z",
            "other.u1",
            "other.u2",
            "other.z",
        ],
        "trit_to_bits": {"0": "00", "1": "10", "2": "01"},
        "bit_pair_semantics": ["is1", "is2"],
        "feature_order": "deg-lex subsets of the 18 input bits",
        "coeff_feature_indices": coeff_indices,
    }

    out_path: Path = args.out
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("OK: fitted GF(2) polynomial sign law")
    print(f"  samples: {len(rows_plain)}")
    print(f"  features: {n_features}")
    print(f"  rank: {len(pivots)}")
    print(f"  nullity: {n_features - len(pivots)}")
    print(f"  coeff weight: {len(coeff_indices)}")
    print(f"  degree histogram: {deg_hist}")
    print(f"  wrote: {out_path}")


if __name__ == "__main__":
    main()
