#!/usr/bin/env python3
"""Fit a compact Heisenberg/cocycle rule to the CE2 mixed-sector repairs.

This script is an *analysis driver* for the next algebra breakthrough:

  - We already have exact/rational local CE2 solutions (per failing triple).
  - Those solutions are extremely sparse and strongly structured.
  - The goal here is to infer a low-parameter, Heisenberg-coordinate law
    (a cocycle/phase rule) that reproduces the repairs *without* per-triple
    special cases.

Inputs (preferred):
  committed_artifacts/ce2_sparse_local_solutions.json
    Produced by tools/compress_ce2_local_solutions.py from the ignored, large
    artifacts/ce2_rational_local_solutions.json.

Usage:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_fit_ce2_global_cocycle.py
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_fit_ce2_global_cocycle.py --max-entries 2000
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Iterator

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from ce2_global_cocycle import predict_ce2_uv


@dataclass(frozen=True)
class CE2Entry:
    key: str
    a: tuple[int, int]
    b: tuple[int, int]
    c: tuple[int, int]
    U: list[tuple[int, Fraction]]
    V: list[tuple[int, Fraction]]


def _decode_flat_index(idx: int) -> tuple[str, tuple[int, int] | tuple[int, int, int]]:
    """Decode a flattened E8Z3 coordinate (len=900) into (sector, indices)."""
    idx = int(idx)
    if idx < 0 or idx >= 900:
        raise ValueError("flat index out of range")

    if idx < 27 * 27:
        return ("e6", (idx // 27, idx % 27))
    idx -= 27 * 27
    if idx < 9:
        return ("sl3", (idx // 3, idx % 3))
    idx -= 9
    if idx < 81:
        return ("g1", (idx // 3, idx % 3))
    idx -= 81
    return ("g2", (idx // 3, idx % 3))


def _iter_sparse_entries(
    sparse_json: Path, *, max_entries: int | None = None
) -> Iterator[CE2Entry]:
    data = json.loads(sparse_json.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("unexpected sparse CE2 JSON format")

    for t, rec in enumerate(entries):
        if max_entries is not None and t >= int(max_entries):
            break
        if not isinstance(rec, dict):
            continue
        k = str(rec.get("k"))
        a = tuple(int(x) for x in rec.get("a", []))
        b = tuple(int(x) for x in rec.get("b", []))
        c = tuple(int(x) for x in rec.get("c", []))
        U_raw = rec.get("U", [])
        V_raw = rec.get("V", [])
        if len(a) != 2 or len(b) != 2 or len(c) != 2:
            continue
        if not isinstance(U_raw, list) or not isinstance(V_raw, list):
            continue

        def parse_sparse(lst: list) -> list[tuple[int, Fraction]]:
            out: list[tuple[int, Fraction]] = []
            for item in lst:
                if not (isinstance(item, list) and len(item) == 2):
                    continue
                idx = int(item[0])
                val = Fraction(str(item[1]))
                out.append((idx, val))
            out.sort(key=lambda kv: kv[0])
            return out

        yield CE2Entry(
            key=k,
            a=(int(a[0]), int(a[1])),
            b=(int(b[0]), int(b[1])),
            c=(int(c[0]), int(c[1])),
            U=parse_sparse(U_raw),
            V=parse_sparse(V_raw),
        )


def _load_heisenberg_model() -> dict[str, dict[int, object]]:
    model_path = ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json"
    model = json.loads(model_path.read_text(encoding="utf-8"))
    e6id_to_h = model.get("e6id_to_heisenberg", {})
    if not isinstance(e6id_to_h, dict) or len(e6id_to_h) < 27:
        raise ValueError("unexpected/missing heisenberg model mapping")
    parsed: dict[int, object] = {}
    for k, v in e6id_to_h.items():
        parsed[int(k)] = v
    return {"e6id_to_h": parsed}


def _heis_uz_maps() -> (
    tuple[dict[int, tuple[tuple[int, int], int]], dict[tuple[int, int, int], int]]
):
    model = _load_heisenberg_model()["e6id_to_h"]
    e6id_to_uz: dict[int, tuple[tuple[int, int], int]] = {}
    uz_to_e6id: dict[tuple[int, int, int], int] = {}
    for e6id, payload in model.items():
        if not isinstance(payload, dict):
            continue
        u = payload.get("u")
        z = payload.get("z")
        if not (isinstance(u, list) and len(u) == 2):
            continue
        if not isinstance(z, int):
            z = int(z)
        u2 = (int(u[0]), int(u[1]))
        z2 = int(z) % 3
        e6id_to_uz[int(e6id)] = (u2, z2)
        uz_to_e6id[(u2[0], u2[1], z2)] = int(e6id)
    if len(e6id_to_uz) != 27:
        raise ValueError("expected full 27-point heisenberg labeling")
    return e6id_to_uz, uz_to_e6id


def _inv_z(e6id: int) -> int:
    e6id_to_uz, uz_to_e6id = _heis_uz_maps()
    u, z = e6id_to_uz[int(e6id)]
    zp = (-int(z)) % 3
    return int(uz_to_e6id[(u[0], u[1], zp)])


def _legendre3(x: int) -> int:
    """Quadratic character mod 3: 0->0, 1->+1, 2->-1."""
    x = int(x) % 3
    if x == 0:
        return 0
    return 1 if x == 1 else -1


def _fit_u_sign_quadratic(u_to_sign: dict[tuple[int, int], int]) -> dict[str, object]:
    """Brute search a small quadratic form Q(u) over F3^2 whose Legendre sign matches.

    Q(u1,u2) = a u1^2 + b u2^2 + c u1 u2 + d u1 + e u2 + f  (mod 3)
    and sign(u) is taken as:
      +1 if Q in {0,1},  -1 if Q == 2
    (i.e., sign = -1 exactly when Q is a nonresidue).
    """
    points = sorted(u_to_sign.keys())
    y = [int(u_to_sign[u]) for u in points]

    best = None
    best_score = -1

    def sign_from_q(qv: int) -> int:
        return -1 if int(qv) % 3 == 2 else 1

    for a in range(3):
        for b in range(3):
            for c in range(3):
                for d in range(3):
                    for e in range(3):
                        for f in range(3):
                            score = 0
                            for (u1, u2), yi in zip(points, y):
                                qv = (
                                    a * (u1 * u1)
                                    + b * (u2 * u2)
                                    + c * (u1 * u2)
                                    + d * u1
                                    + e * u2
                                    + f
                                ) % 3
                                if sign_from_q(qv) == yi:
                                    score += 1
                            if score > best_score:
                                best_score = score
                                best = (a, b, c, d, e, f)
    assert best is not None
    a, b, c, d, e, f = best
    return {
        "best_score": int(best_score),
        "n_points": int(len(points)),
        "coeffs": {"a": a, "b": b, "c": c, "d": d, "e": e, "f": f},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sparse-json",
        type=Path,
        default=ROOT / "committed_artifacts" / "ce2_sparse_local_solutions.json",
    )
    parser.add_argument("--max-entries", type=int, default=None)
    parser.add_argument("--top-patterns", type=int, default=10)
    parser.add_argument(
        "--verify-global-laws",
        action="store_true",
        help="Verify predict_ce2_uv reproduces every sparse entry exactly.",
    )
    args = parser.parse_args()

    if not args.sparse_json.exists():
        raise SystemExit(
            f"Missing sparse CE2 file: {args.sparse_json}. "
            "Generate it with tools/compress_ce2_local_solutions.py."
        )

    entries = list(_iter_sparse_entries(args.sparse_json, max_entries=args.max_entries))

    print("=" * 78)
    print("CE2 GLOBAL COCYCLE FIT (sparse local solutions -> structural laws)")
    print("=" * 78)
    print(f"Sparse file: {args.sparse_json}")
    print(f"Entries read: {len(entries)}")

    if args.verify_global_laws:
        mismatches = 0
        for e in entries:
            pred = predict_ce2_uv(e.a, e.b, e.c)
            if pred is None:
                mismatches += 1
                continue
            if sorted(pred.U) != sorted(e.U) or sorted(pred.V) != sorted(e.V):
                mismatches += 1
        print(f"Global-law reproduction mismatches: {mismatches} (expected 0)")
        assert mismatches == 0

    # -------------------------------------------------------------------------
    # §1. Pattern census
    # -------------------------------------------------------------------------
    def pattern_sig(e: CE2Entry) -> str:
        def sector_counts(s: list[tuple[int, Fraction]]) -> str:
            ctr = Counter()
            vals = []
            for idx, val in s:
                sec, _ = _decode_flat_index(idx)
                ctr[sec] += 1
                vals.append(str(val))
            parts = ",".join(
                f"{k}:{ctr[k]}" for k in ("e6", "sl3", "g1", "g2") if ctr[k]
            )
            vpart = ",".join(sorted(vals))
            return f"[{parts or '0'}|{vpart or '0'}]"

        return f"U{sector_counts(e.U)} V{sector_counts(e.V)}"

    sig_ctr = Counter(pattern_sig(e) for e in entries)
    print()
    print("§1. Local-solution sparsity patterns (top)")
    print("-" * 50)
    for sig, n in sig_ctr.most_common(int(args.top_patterns)):
        print(f"  {n:5d}  {sig}")

    # -------------------------------------------------------------------------
    # §2. Dominant simple family: single e6 unit with denom 54
    # -------------------------------------------------------------------------
    simple: list[tuple[CE2Entry, int, int, Fraction]] = []
    for e in entries:
        nz = e.U + e.V
        if len(nz) != 1:
            continue
        idx, val = nz[0]
        sec, ij = _decode_flat_index(idx)
        if sec != "e6":
            continue
        if val == 0:
            continue
        if abs(val.denominator) != 54:
            continue
        row, col = int(ij[0]), int(ij[1])
        simple.append((e, row, col, val))

    print()
    print("§2. Simple family (|val|=1/54, exactly one e6 entry)")
    print("-" * 50)
    print(f"  Count: {len(simple)} / {len(entries)}")

    e6id_to_uz, uz_to_e6id = _heis_uz_maps()

    # Global support law (derived from the CE2 sparse data):
    #
    # Let the mixed triple be g1(a_i,a_j), g1(b_i,b_j), g2(c_i,c_j). In the simple
    # family, exactly one of {a_j,b_j} equals c_j. Define:
    #   match_i := a_i if a_j=c_j else b_i
    #   other_i := the remaining g1 index
    #
    # Then the single nonzero e6 matrix-unit lives at:
    #   col = other_i
    #   row = match + other - c   (in Heisenberg F3^3 coordinates (u1,u2,z))
    #
    # Side rule:
    #   a_j=c_j -> V is nonzero,   b_j=c_j -> U is nonzero.
    side_ok = 0
    side_tot = 0
    row_ok = 0
    sign_map: dict[tuple[int, int, int], int] = {}

    # Column rule: when exactly one of a_j,b_j equals c_j, does col equal the other i?
    col_ok = 0
    col_tot = 0
    sign_by_match_u: dict[tuple[int, int], Counter] = defaultdict(Counter)
    for e, row, col, val in simple:
        a_i, a_j = e.a
        b_i, b_j = e.b
        c_i, c_j = e.c
        # determine which g1 matches c_j (by sl3 index)
        match_i = None
        other_i = None
        expected_side = None
        if a_j == c_j and b_j != c_j:
            match_i = a_i
            other_i = b_i
            expected_side = "V"
        elif b_j == c_j and a_j != c_j:
            match_i = b_i
            other_i = a_i
            expected_side = "U"
        if other_i is None or match_i is None:
            continue

        side_tot += 1
        actual_side = "U" if e.U else "V"
        if actual_side == expected_side:
            side_ok += 1

        col_tot += 1
        if int(col) == int(other_i):
            col_ok += 1

        # Heisenberg affine row law (F3^3 on the 27-point model).
        (um0, um1), zm = e6id_to_uz[int(match_i)]
        (uo0, uo1), zo = e6id_to_uz[int(other_i)]
        (uc0, uc1), zc = e6id_to_uz[int(c_i)]
        u_row = ((um0 + uo0 - uc0) % 3, (um1 + uo1 - uc1) % 3)
        z_row = (zm + zo - zc) % 3
        row_pred = int(uz_to_e6id[(u_row[0], u_row[1], z_row)])
        if int(row_pred) == int(row):
            row_ok += 1

        u_match, _z = e6id_to_uz[int(match_i)]
        sign_by_match_u[u_match][1 if val > 0 else -1] += 1

        # Deterministic sign table on ordered triples (c, match, other).
        k = (int(c_i), int(match_i), int(other_i))
        sgn = 1 if val > 0 else -1
        if k in sign_map and int(sign_map[k]) != int(sgn):
            raise AssertionError(
                f"Non-deterministic sign for key={k}: {sign_map[k]} vs {sgn}"
            )
        sign_map[k] = int(sgn)

    print(
        f"  Side rule (a_j=c_j -> V, b_j=c_j -> U): {side_ok}/{side_tot} = {side_ok/max(1,side_tot):.4f}"
    )
    print(
        f"  Column rule (col == other g1's 27-index): {col_ok}/{col_tot} = {col_ok/max(1,col_tot):.4f}"
    )
    print(
        f"  Heisenberg row law (row = match+other-c in F3^3): {row_ok}/{len(simple)} = {row_ok/max(1,len(simple)):.4f}"
    )
    print(f"  Deterministic sign keys (c,match,other): {len(sign_map)} (expected 864)")
    assert side_ok == side_tot == len(simple)
    assert col_ok == col_tot == len(simple)
    assert row_ok == len(simple)
    assert len(sign_map) == 864

    # Build a majority sign table by Heisenberg u for the matching g1
    u_to_sign: dict[tuple[int, int], int] = {}
    for u, ctr in sorted(sign_by_match_u.items()):
        pos = int(ctr.get(1, 0))
        neg = int(ctr.get(-1, 0))
        if pos == 0 and neg == 0:
            continue
        u_to_sign[u] = 1 if pos >= neg else -1
        print(f"  sign(u={u}): pos={pos:4d} neg={neg:4d} -> {u_to_sign[u]:+d}")

    if u_to_sign:
        fit = _fit_u_sign_quadratic(u_to_sign)
        print()
        print(
            "  Best quadratic-form fit for sign(u) (Legendre of Q):"
        )  # interpretation aid
        print("   ", fit)

    print()
    from ce2_global_cocycle import (
        _simple_family_sign_poly_coeff_mask,
        predict_simple_family_sign,
    )

    coeff_mask = _simple_family_sign_poly_coeff_mask()
    if coeff_mask is None:
        print("  No committed GF(2) sign-polynomial artifact found.")  # noqa: T201
        print(  # noqa: T201
            "NEXT: turn the (row,col,side) Heisenberg law into a global alpha(cocycle) ansatz,"
        )
        print(  # noqa: T201
            "      compress the deterministic sign-table into a low-parameter phase rule,"
        )
    else:
        mism = 0
        for (c_i, match_i, other_i), s in sign_map.items():
            if predict_simple_family_sign(c_i, match_i, other_i) != int(s):
                mism += 1
        print(  # noqa: T201
            "  GF(2) sign polynomial (deg≤4): weight=%d, mismatches=%d"
            % (int(coeff_mask).bit_count(), mism)
        )
        assert mism == 0
        print(  # noqa: T201
            "NEXT: turn the (row,col,side) Heisenberg law into a global alpha(cocycle) ansatz,"
        )
        print(  # noqa: T201
            "      validate directly against homotopy_jacobi residuals on mixed triples."
        )


if __name__ == "__main__":
    main()
