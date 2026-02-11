#!/usr/bin/env python3
"""Arithmetic classification of rational exceptional-line dimensions.

For exceptional-line gauge alpha=-2, beta=m+4, gamma=2m+4, fixing dimension D
gives the non-degenerate quadratic condition

    30*m^2 + (118-D)*m + (112-4D) = 0

with discriminant

    Delta(D) = D^2 + 244*D + 484 = (D+122)^2 - 120^2.

Hence rational roots are equivalent to Delta(D) being a perfect square:

    (D+122-r)(D+122+r) = 14400,  r = sqrt(Delta(D)).

This factorization yields a finite, exact integer classification.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

SHIFT = 122
RADIUS = 120
FACTOR_PRODUCT = 14400
DEGENERATE_ROOTS = {Fraction(-2, 1), Fraction(-4, 1)}


def discriminant(dim: int) -> int:
    return dim * dim + 244 * dim + 484


def discriminant_square_root_if_square(dim: int) -> Optional[int]:
    delta = discriminant(dim)
    if delta < 0:
        return None
    root = isqrt(delta)
    return root if root * root == delta else None


def nondeg_rational_roots_for_dim(dim: int) -> List[Fraction]:
    root = discriminant_square_root_if_square(dim)
    if root is None:
        return []
    candidates = [
        Fraction(dim - 118 + root, 60),
        Fraction(dim - 118 - root, 60),
    ]
    out: List[Fraction] = []
    for value in candidates:
        if value in DEGENERATE_ROOTS:
            continue
        out.append(value)
    return sorted(set(out))


def _positive_factor_pairs(n: int) -> Iterable[Tuple[int, int]]:
    top = isqrt(n)
    for a in range(1, top + 1):
        if n % a == 0:
            yield a, n // a


def all_integer_dims_with_square_discriminant() -> List[int]:
    dims = set()
    for a, b in _positive_factor_pairs(FACTOR_PRODUCT):
        if (a + b) % 2 != 0:
            continue
        half_sum = (a + b) // 2
        dims.add(half_sum - SHIFT)
        dims.add(-half_sum - SHIFT)
    return sorted(dims)


def all_integer_dims_with_nondeg_hits() -> List[int]:
    return [
        dim
        for dim in all_integer_dims_with_square_discriminant()
        if nondeg_rational_roots_for_dim(dim)
    ]


def positive_nondeg_hit_dims() -> List[int]:
    return [dim for dim in all_integer_dims_with_nondeg_hits() if dim > 0]


def window_hit_dims(start: int, end: int) -> List[int]:
    return [dim for dim in positive_nondeg_hit_dims() if start <= dim <= end]


def _fmt_fraction(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def _bruteforce_square_dims(start: int, end: int) -> List[int]:
    out: List[int] = []
    for dim in range(start, end + 1):
        if discriminant_square_root_if_square(dim) is not None:
            out.append(dim)
    return out


def build_payload(
    window_start: int, window_end: int, target_dims: List[int]
) -> Dict[str, object]:
    square_dims = all_integer_dims_with_square_discriminant()
    nondeg_dims = all_integer_dims_with_nondeg_hits()
    pos_dims = [dim for dim in nondeg_dims if dim > 0]
    window_dims = [dim for dim in pos_dims if window_start <= dim <= window_end]

    square_records = {}
    for dim in square_dims:
        root = discriminant_square_root_if_square(dim)
        assert root is not None
        square_records[str(dim)] = {
            "discriminant": discriminant(dim),
            "sqrt_discriminant": root,
            "nondeg_rational_roots": [
                _fmt_fraction(v) for v in nondeg_rational_roots_for_dim(dim)
            ],
        }

    target_rows = {}
    for dim in target_dims:
        roots = nondeg_rational_roots_for_dim(dim)
        target_rows[str(dim)] = {
            "in_positive_hit_dims": dim in pos_dims,
            "nondeg_rational_roots": [_fmt_fraction(v) for v in roots],
        }

    brute = _bruteforce_square_dims(min(square_dims), max(square_dims))
    brute_matches = brute == square_dims

    return {
        "status": "ok",
        "identity": "Delta(D)=D^2+244D+484=(D+122)^2-120^2",
        "factorization": "(D+122-r)(D+122+r)=14400 with r=sqrt(Delta(D))",
        "factor_product": FACTOR_PRODUCT,
        "all_square_discriminant_dims": square_dims,
        "all_integer_nondeg_hit_dims": nondeg_dims,
        "positive_nondeg_hit_dims": pos_dims,
        "window": {
            "start": int(window_start),
            "end": int(window_end),
            "hit_dims": window_dims,
        },
        "targets": target_rows,
        "square_records": square_records,
        "verification": {
            "bruteforce_bounds": {
                "start": int(min(square_dims)),
                "end": int(max(square_dims)),
            },
            "factorization_matches_bruteforce": bool(brute_matches),
        },
        "notes": (
            "The integer-dimensional rational-hit set is finite because it reduces to "
            "divisor pairs of 14400 with parity compatibility."
        ),
    }


def render_md(payload: Dict[str, object]) -> str:
    pos = payload["positive_nondeg_hit_dims"]
    window = payload["window"]
    targets = payload["targets"]
    square_records = payload["square_records"]

    lines: List[str] = ["# Vogel Rational Dimension Theorem (Arithmetic Form)", ""]
    lines.append(f"- Identity: `{payload['identity']}`")
    lines.append(f"- Factorization: `{payload['factorization']}`")
    lines.append(
        "- Consequence: integer dimensions with rational non-degenerate exceptional-line roots are finite."
    )
    lines.append(f"- Positive hit dimensions (`{len(pos)}` total): `{pos}`")
    lines.append(
        f"- Window hits `[${window['start']}, {window['end']}]`: `{window['hit_dims']}`".replace(
            "$", ""
        )
    )
    lines.append(f"- Target checks: `{targets}`")
    lines.append("")
    lines.append("Dimension | sqrt(Delta) | Non-degenerate rational roots")
    lines.append("--- | --- | ---")
    for dim in pos:
        rec = square_records[str(dim)]
        roots = ", ".join(rec["nondeg_rational_roots"]) or "-"
        lines.append(f"{dim} | {rec['sqrt_discriminant']} | {roots}")
    lines.append("")
    lines.append(
        f"- Verification (`factorization_matches_bruteforce`): `{payload['verification']['factorization_matches_bruteforce']}`"
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--window-start", type=int, default=200)
    parser.add_argument("--window-end", type=int, default=1000)
    parser.add_argument("--target-dims", nargs="+", type=int, default=[728, 486, 242])
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("artifacts/vogel_rational_dimension_theorem_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/VOGEL_RATIONAL_DIMENSION_THEOREM_2026_02_11.md"),
    )
    args = parser.parse_args()

    payload = build_payload(
        window_start=int(args.window_start),
        window_end=int(args.window_end),
        target_dims=[int(dim) for dim in args.target_dims],
    )

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(payload), encoding="utf-8")

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
