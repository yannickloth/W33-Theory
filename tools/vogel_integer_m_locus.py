#!/usr/bin/env python3
"""Integer-parameter locus on the Vogel exceptional line.

For alpha=-2, beta=m+4, gamma=2m+4, the dimension is

    D(m) = 2*(3m+7)*(5m+8)/(m+4),   m != -4.

Set n = m + 4. Then

    D = 30*n - 122 + 120/n.

Hence for integer m (equivalently integer n), D is integer iff n divides 120.
This gives an exact finite classification of integer-m integer-D points.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.vogel_rational_dimension_theorem import positive_nondeg_hit_dims


def dim_from_m(m: Fraction) -> Fraction:
    if m == Fraction(-4, 1):
        raise ZeroDivisionError("Degenerate denominator at m=-4")
    return Fraction(2 * (3 * m + 7) * (5 * m + 8), m + 4)


def _divisors_of_120_with_sign() -> List[int]:
    base = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 40, 60, 120]
    out = sorted(set(base + [-d for d in base]))
    return out


def integer_m_locus() -> List[Dict[str, int]]:
    rows = []
    for n in _divisors_of_120_with_sign():
        m = n - 4
        dim = int(30 * n - 122 + 120 // n)
        rows.append({"n": int(n), "m": int(m), "dim": dim})
    return sorted(rows, key=lambda r: (r["dim"], r["m"]))


def theorem_check_in_range(m_min: int, m_max: int) -> Dict[str, object]:
    mismatches: List[Dict[str, object]] = []
    for m in range(m_min, m_max + 1):
        if m == -4:
            continue
        lhs = dim_from_m(Fraction(m, 1))
        is_int_dim = lhs.denominator == 1
        n = m + 4
        rhs = (120 % n == 0) if n != 0 else False
        if is_int_dim != rhs:
            mismatches.append(
                {
                    "m": int(m),
                    "n": int(n),
                    "dim": f"{lhs.numerator}/{lhs.denominator}",
                    "is_integer_dim": bool(is_int_dim),
                    "n_divides_120": bool(rhs),
                }
            )
    return {
        "m_range": {"min": int(m_min), "max": int(m_max)},
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }


def build_payload(m_min: int, m_max: int, target_dims: List[int]) -> Dict[str, object]:
    rows = integer_m_locus()
    pos_rows = [row for row in rows if row["dim"] > 0]
    pos_hit_set = set(positive_nondeg_hit_dims())
    pos_dim_to_ms: Dict[str, List[int]] = {}
    for row in pos_rows:
        pos_dim_to_ms.setdefault(str(row["dim"]), []).append(int(row["m"]))

    target_rows = {}
    for dim in target_dims:
        ms = pos_dim_to_ms.get(str(dim), [])
        target_rows[str(dim)] = {
            "is_integer_m_hit": bool(ms),
            "integer_m_values": ms,
        }

    return {
        "status": "ok",
        "identity": "D=2*(3m+7)*(5m+8)/(m+4)=30*(m+4)-122+120/(m+4)",
        "criterion": "For integer m != -4, D is integer iff (m+4) divides 120",
        "integer_m_locus": rows,
        "positive_integer_m_locus": pos_rows,
        "positive_integer_m_dims": sorted({row["dim"] for row in pos_rows}),
        "positive_integer_m_dims_are_subset_of_positive_rational_hit_dims": all(
            row["dim"] in pos_hit_set for row in pos_rows
        ),
        "positive_dim_to_integer_m_values": pos_dim_to_ms,
        "targets": target_rows,
        "verification": theorem_check_in_range(m_min, m_max),
        "notes": (
            "This is an exact finite classification of integer-parameter points on "
            "the exceptional line yielding integer dimensions."
        ),
    }


def render_md(payload: Dict[str, object]) -> str:
    rows = payload["positive_integer_m_locus"]
    lines: List[str] = ["# Vogel Integer-m Locus (Exceptional Line)", ""]
    lines.append(f"- Identity: `{payload['identity']}`")
    lines.append(f"- Criterion: `{payload['criterion']}`")
    lines.append(
        "- Positive dimensions from integer m: "
        f"`{payload['positive_integer_m_dims']}`"
    )
    lines.append(f"- Target checks: `{payload['targets']}`")
    lines.append("")
    lines.append("n=m+4 | m | D(m)")
    lines.append("--- | --- | ---")
    for row in rows:
        lines.append(f"{row['n']} | {row['m']} | {row['dim']}")
    lines.append("")
    lines.append(
        "- Verification mismatch count in scan range "
        f"`[{payload['verification']['m_range']['min']}, {payload['verification']['m_range']['max']}]`: "
        f"`{payload['verification']['mismatch_count']}`"
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--m-min", type=int, default=-300)
    parser.add_argument("--m-max", type=int, default=300)
    parser.add_argument("--target-dims", nargs="+", type=int, default=[728, 486, 242])
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("artifacts/vogel_integer_m_locus_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/VOGEL_INTEGER_M_LOCUS_2026_02_11.md"),
    )
    args = parser.parse_args()

    payload = build_payload(
        m_min=int(args.m_min),
        m_max=int(args.m_max),
        target_dims=[int(v) for v in args.target_dims],
    )

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(payload), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
