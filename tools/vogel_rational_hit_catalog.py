#!/usr/bin/env python3
"""Catalog dimensions with non-degenerate rational exceptional-line roots.

For Vogel exceptional-line gauge
alpha=-2, beta=m+4, gamma=2m+4, the equation dim=D reduces to

  30*m^2 + (118-D)*m + (112-4D) = 0

for non-degenerate roots (m != -2). This script catalogs integer D values in
a range where roots are rational.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Dict, List


def nondeg_rational_roots_for_dim(dim: int) -> Dict[str, object]:
    """Return discriminant and non-degenerate rational roots for a target dim."""
    discriminant = dim * dim + 244 * dim + 484
    root = isqrt(discriminant) if discriminant >= 0 else -1
    is_square = discriminant >= 0 and root * root == discriminant
    hits: List[Fraction] = []
    if is_square:
        candidates = [
            Fraction(dim - 118 + root, 60),
            Fraction(dim - 118 - root, 60),
        ]
        for value in candidates:
            if value in (Fraction(-2, 1), Fraction(-4, 1)):
                continue
            hits.append(value)
    hits = sorted(set(hits))
    return {
        "target_dim": int(dim),
        "discriminant": int(discriminant),
        "discriminant_is_square": bool(is_square),
        "hits": [
            (
                f"{value.numerator}/{value.denominator}"
                if value.denominator != 1
                else str(value.numerator)
            )
            for value in hits
        ],
    }


def catalog_dims(start: int, end: int, step: int) -> Dict[str, Dict[str, object]]:
    out: Dict[str, Dict[str, object]] = {}
    for dim in range(start, end + 1, step):
        out[str(dim)] = nondeg_rational_roots_for_dim(dim)
    return out


def _hit_dims(catalog: Dict[str, Dict[str, object]]) -> List[int]:
    return sorted(int(dim) for dim, rec in catalog.items() if rec.get("hits"))


def render_md(catalog: Dict[str, Dict[str, object]], targets: List[int]) -> str:
    hits = _hit_dims(catalog)
    lines: List[str] = ["# Vogel Rational Hit Catalog", ""]
    lines.append(f"- Dimensions scanned: `{len(catalog)}`")
    lines.append(f"- Hit dimensions: `{hits}`")
    lines.append(f"- Target dimensions: `{targets}`")
    lines.append("")
    lines.append("Dimension | Discriminant square | Rational non-degenerate roots")
    lines.append("--- | --- | ---")
    for dim in sorted(catalog.keys(), key=lambda x: int(x)):
        rec = catalog[dim]
        roots = rec["hits"]
        lines.append(
            f"{dim} | {rec['discriminant_is_square']} | {', '.join(roots) if roots else '-'}"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=200)
    parser.add_argument("--end", type=int, default=1000)
    parser.add_argument("--step", type=int, default=1)
    parser.add_argument("--target-dims", nargs="+", type=int, default=[728, 486, 242])
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("artifacts/vogel_rational_hit_catalog_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/VOGEL_RATIONAL_HIT_CATALOG_2026_02_11.md"),
    )
    args = parser.parse_args()

    catalog = catalog_dims(int(args.start), int(args.end), int(args.step))
    target_rows = {
        str(dim): nondeg_rational_roots_for_dim(int(dim)) for dim in args.target_dims
    }
    payload = {
        "status": "ok",
        "range": {
            "start": int(args.start),
            "end": int(args.end),
            "step": int(args.step),
        },
        "hit_dims": _hit_dims(catalog),
        "catalog": catalog,
        "targets": target_rows,
        "notes": (
            "Non-degenerate roots are characterized by a quadratic discriminant "
            "condition; s12 dimensions are expected to remain outside rational hits."
        ),
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(
        render_md(catalog, [int(dim) for dim in args.target_dims]), encoding="utf-8"
    )
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
