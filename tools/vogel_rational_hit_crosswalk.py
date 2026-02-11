#!/usr/bin/env python3
"""Crosswalk for integer-dimensional rational Vogel exceptional-line hits.

Builds a structured classification of the finite positive hit set from
`tools/vogel_rational_dimension_theorem.py` into:
- classical family dimension hits (A/B/C/D),
- direct exceptional-table hits (A2, G2, D4, F4, E6, E7, E8),
- remaining arithmetic-only hit dimensions.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.vogel_rational_dimension_theorem import (
    nondeg_rational_roots_for_dim,
    positive_nondeg_hit_dims,
)

DIRECT_TABLE_DIMS = {
    "A2": 8,
    "G2": 14,
    "D4": 28,
    "F4": 52,
    "E6": 78,
    "E7": 133,
    "E8": 248,
}


def _is_square(num: int) -> bool:
    if num < 0:
        return False
    root = isqrt(num)
    return root * root == num


def classical_hits(dim: int) -> Dict[str, List[int]]:
    """Return classical-family rank hits for a target dimension."""
    out: Dict[str, List[int]] = {"A": [], "B": [], "C": [], "D": []}

    # A_{n-1}: dim = n^2 - 1
    if _is_square(dim + 1):
        n = isqrt(dim + 1)
        if n >= 2:
            out["A"].append(n - 1)

    # B_n / C_n: dim = n(2n+1)
    disc = 1 + 8 * dim
    if _is_square(disc):
        root = isqrt(disc)
        if (root - 1) % 4 == 0:
            n = (root - 1) // 4
            if n >= 2:
                out["B"].append(n)
                out["C"].append(n)

    # D_n: dim = n(2n-1)
    if _is_square(disc):
        root = isqrt(disc)
        if (root + 1) % 4 == 0:
            n = (root + 1) // 4
            if n >= 4:
                out["D"].append(n)

    return out


def _fmt_fraction(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def _nearest_hit(dim: int, hits: List[int]) -> Dict[str, object]:
    if not hits:
        return {"nearest_dims": [], "distance": None}
    min_dist = min(abs(dim - h) for h in hits)
    nearest = [h for h in hits if abs(dim - h) == min_dist]
    return {"nearest_dims": nearest, "distance": int(min_dist)}


def build_crosswalk(target_dims: List[int]) -> Dict[str, object]:
    hits = positive_nondeg_hit_dims()
    direct_dim_to_names: Dict[int, List[str]] = {}
    for name, dim in DIRECT_TABLE_DIMS.items():
        direct_dim_to_names.setdefault(dim, []).append(name)

    rows = {}
    classical_hit_dims: List[int] = []
    direct_table_hit_dims: List[int] = []
    integral_root_hit_dims: List[int] = []
    integral_roots: Dict[str, List[str]] = {}

    for dim in hits:
        roots = nondeg_rational_roots_for_dim(dim)
        roots_s = [_fmt_fraction(v) for v in roots]
        classical = classical_hits(dim)
        direct_names = direct_dim_to_names.get(dim, [])
        int_roots = [v for v in roots if v.denominator == 1]

        if any(classical.values()):
            classical_hit_dims.append(dim)
        if direct_names:
            direct_table_hit_dims.append(dim)
        if int_roots:
            integral_root_hit_dims.append(dim)
            integral_roots[str(dim)] = [_fmt_fraction(v) for v in int_roots]

        rows[str(dim)] = {
            "roots": roots_s,
            "classical_hits": classical,
            "direct_table_hits": direct_names,
            "has_classical_hit": any(classical.values()),
            "has_direct_table_hit": bool(direct_names),
            "has_integral_root": bool(int_roots),
            "integral_roots": [_fmt_fraction(v) for v in int_roots],
        }

    classical_set = set(classical_hit_dims)
    direct_set = set(direct_table_hit_dims)
    mixed_set = classical_set | direct_set
    arithmetic_only = sorted([d for d in hits if d not in mixed_set])

    target_rows = {}
    for dim in target_dims:
        target_rows[str(dim)] = {
            "in_positive_hit_set": dim in hits,
            "nearest_hit": _nearest_hit(dim, hits),
            "roots": [_fmt_fraction(v) for v in nondeg_rational_roots_for_dim(dim)],
        }

    return {
        "status": "ok",
        "positive_hit_dims": hits,
        "rows": rows,
        "summary": {
            "total_positive_hits": len(hits),
            "classical_hit_dims": sorted(classical_hit_dims),
            "direct_table_hit_dims": sorted(direct_table_hit_dims),
            "classical_direct_overlap_dims": sorted(classical_set & direct_set),
            "arithmetic_only_hit_dims": arithmetic_only,
            "integral_root_hit_dims": sorted(integral_root_hit_dims),
            "integral_roots_by_dim": integral_roots,
        },
        "targets": target_rows,
        "direct_table_dims": DIRECT_TABLE_DIMS,
        "notes": (
            "This crosswalk isolates which finite rational-hit dimensions are accounted "
            "for by classical or direct exceptional-table families."
        ),
    }


def render_md(payload: Dict[str, object], target_dims: List[int]) -> str:
    summary = payload["summary"]
    rows = payload["rows"]
    targets = payload["targets"]
    hits = payload["positive_hit_dims"]

    lines: List[str] = ["# Vogel Rational Hit Crosswalk", ""]
    lines.append(f"- Positive hit dimensions (`{len(hits)}`): `{hits}`")
    lines.append(f"- Classical hit dimensions: `{summary['classical_hit_dims']}`")
    lines.append(f"- Direct-table hit dimensions: `{summary['direct_table_hit_dims']}`")
    lines.append(
        f"- Arithmetic-only hit dimensions: `{summary['arithmetic_only_hit_dims']}`"
    )
    lines.append(
        f"- Integral-root hit dimensions: `{summary['integral_root_hit_dims']}`"
    )
    lines.append(f"- Target dimensions checked: `{target_dims}`")
    lines.append("")
    lines.append("Dimension | Roots | Classical hits | Direct-table hits | Category")
    lines.append("--- | --- | --- | --- | ---")
    for dim in hits:
        rec = rows[str(dim)]
        roots = ", ".join(rec["roots"]) if rec["roots"] else "-"
        cls = rec["classical_hits"]
        cls_s = ", ".join(f"{fam}:{vals}" for fam, vals in cls.items() if vals) or "-"
        direct_s = (
            ", ".join(rec["direct_table_hits"]) if rec["direct_table_hits"] else "-"
        )
        if rec["has_classical_hit"] and rec["has_direct_table_hit"]:
            cat = "classical+direct"
        elif rec["has_classical_hit"]:
            cat = "classical-only"
        elif rec["has_direct_table_hit"]:
            cat = "direct-only"
        else:
            cat = "arithmetic-only"
        lines.append(f"{dim} | {roots} | {cls_s} | {direct_s} | {cat}")
    lines.append("")
    lines.append("## Target Checks")
    lines.append("")
    for dim in target_dims:
        rec = targets[str(dim)]
        lines.append(
            f"- `D={dim}` in hit set: `{rec['in_positive_hit_set']}`; nearest hit: `{rec['nearest_hit']}`"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-dims", nargs="+", type=int, default=[728, 486, 242])
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("artifacts/vogel_rational_hit_crosswalk_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/VOGEL_RATIONAL_HIT_CROSSWALK_2026_02_11.md"),
    )
    args = parser.parse_args()

    target_dims = [int(dim) for dim in args.target_dims]
    payload = build_crosswalk(target_dims)

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(payload, target_dims), encoding="utf-8")

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
