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

    # Majority map f(c_i) -> row (per e6id of c)
    row_by_c: dict[int, Counter] = defaultdict(Counter)
    for e, row, _, _ in simple:
        row_by_c[int(e.c[0])][int(row)] += 1

    f_c_to_row: dict[int, int] = {}
    correct_f = 0
    for e, row, _, _ in simple:
        c0 = int(e.c[0])
        if c0 not in f_c_to_row:
            f_c_to_row[c0] = int(row_by_c[c0].most_common(1)[0][0])
        if int(row) == int(f_c_to_row[c0]):
            correct_f += 1

    acc = correct_f / max(1, len(simple))
    print(f"  Majority row-map accuracy: {correct_f}/{len(simple)} = {acc:.4f}")

    # Try to explain f as a z-affine map with u fixed: z' = s z + t
    e6id_to_uz, uz_to_e6id = _heis_uz_maps()
    best = None
    best_match = -1
    for s in (1, 2):
        for t in (0, 1, 2):
            ok = 0
            tot = 0
            for c0, r0 in f_c_to_row.items():
                u, z = e6id_to_uz[int(c0)]
                zp = (s * z + t) % 3
                pred = uz_to_e6id[(u[0], u[1], zp)]
                tot += 1
                if int(pred) == int(r0):
                    ok += 1
            if ok > best_match:
                best_match = ok
                best = (s, t)
    assert best is not None
    s, t = best
    print(
        f"  Best fiberwise z-affine explanation: z' = {s}*z + {t} (mod 3) matches {best_match}/{len(f_c_to_row)} c-values"
    )

    # Column rule: when exactly one of a_j,b_j equals c_j, does col equal the other i?
    col_ok = 0
    col_tot = 0
    sign_by_match_u: dict[tuple[int, int], Counter] = defaultdict(Counter)
    for e, _, col, val in simple:
        a_i, a_j = e.a
        b_i, b_j = e.b
        c_i, c_j = e.c
        # determine which g1 matches c_j (by sl3 index)
        match_i = None
        other_i = None
        if a_j == c_j and b_j != c_j:
            match_i = a_i
            other_i = b_i
        elif b_j == c_j and a_j != c_j:
            match_i = b_i
            other_i = a_i
        if other_i is None or match_i is None:
            continue
        col_tot += 1
        if int(col) == int(other_i):
            col_ok += 1
        u_match, _z = e6id_to_uz[int(match_i)]
        sign_by_match_u[u_match][1 if val > 0 else -1] += 1

    print(
        f"  Column rule (col == other g1's 27-index): {col_ok}/{col_tot} = {col_ok/max(1,col_tot):.4f}"
    )

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
    print(
        "NEXT: use the inferred f(c) row-map + sign(u) table as a cocycle ansatz"
    )  # noqa: T201
    print(
        "      and validate directly against homotopy_jacobi residuals on mixed triples."
    )  # noqa: T201


if __name__ == "__main__":
    main()
