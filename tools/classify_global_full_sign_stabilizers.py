#!/usr/bin/env python3
"""Classify global full-sign stabilizers across all affine z-maps.

Builds a mode x z-map census using the closed-form sign law:
- mode `all_agl`: all affine u-maps (432 elements)
- mode `hessian216`: SL(2,3)-based affine subset (216 elements)
- mode `involution_det2`: det=2/order-2 affine involutions (108 elements)

Each cell counts candidate matches in
  (u_affine) x {eps in +/-1}
for fixed z-map.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.prove_z22_no_global_stabilizer import analyze_no_global_stabilizer

Z_MAPS: List[Tuple[int, int]] = [(1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
MODES: List[str] = ["all_agl", "hessian216", "involution_det2"]


def build_census() -> Dict[str, Any]:
    rows: Dict[str, Dict[str, Any]] = {}
    nonzero: List[Dict[str, Any]] = []

    for mode in MODES:
        mode_row: Dict[str, Any] = {}
        for z_map in Z_MAPS:
            payload = analyze_no_global_stabilizer(mode, z_map)
            key = f"({z_map[0]},{z_map[1]})"
            mode_row[key] = {
                "checked_candidates": int(payload["checked_candidates"]),
                "match_count": int(payload["match_count"]),
                "matches": payload["matches"],
            }
            if payload["match_count"] > 0:
                nonzero.append(
                    {
                        "mode": mode,
                        "z_map": [int(z_map[0]), int(z_map[1])],
                        "match_count": int(payload["match_count"]),
                        "matches": payload["matches"],
                    }
                )
        rows[mode] = mode_row

    theorem = {
        "all_agl_trivial_only": rows["all_agl"]["(1,0)"]["match_count"] == 1
        and all(
            rows["all_agl"][f"({a},{b})"]["match_count"] == 0
            for a, b in Z_MAPS
            if (a, b) != (1, 0)
        ),
        "hessian216_trivial_only": rows["hessian216"]["(1,0)"]["match_count"] == 1
        and all(
            rows["hessian216"][f"({a},{b})"]["match_count"] == 0
            for a, b in Z_MAPS
            if (a, b) != (1, 0)
        ),
        "involution_subset_none": all(
            rows["involution_det2"][f"({a},{b})"]["match_count"] == 0 for a, b in Z_MAPS
        ),
    }

    return {
        "status": "ok",
        "z_maps": [[int(a), int(b)] for a, b in Z_MAPS],
        "modes": MODES,
        "matrix": rows,
        "nonzero_cells": nonzero,
        "theorem_flags": theorem,
        "notes": (
            "Global full-sign stabilizers are classified by z-map and affine mode; "
            "nonzero cells isolate surviving exact symmetries."
        ),
    }


def render_md(payload: Dict[str, Any]) -> str:
    lines: List[str] = ["# Global Full-Sign Stabilizer Census", ""]
    lines.append(
        "- Statement: classify global full-sign stabilizers by `z`-map in three affine modes."
    )
    lines.append("")
    lines.append("Mode | z=(1,0) | z=(1,1) | z=(1,2) | z=(2,0) | z=(2,1) | z=(2,2)")
    lines.append("--- | --- | --- | --- | --- | --- | ---")

    for mode in MODES:
        row = payload["matrix"][mode]
        vals = [
            str(row["(1,0)"]["match_count"]),
            str(row["(1,1)"]["match_count"]),
            str(row["(1,2)"]["match_count"]),
            str(row["(2,0)"]["match_count"]),
            str(row["(2,1)"]["match_count"]),
            str(row["(2,2)"]["match_count"]),
        ]
        lines.append(f"{mode} | " + " | ".join(vals))

    lines.append("")
    lines.append(f"- Nonzero cells: `{payload['nonzero_cells']}`")
    lines.append(f"- Theorem flags: `{payload['theorem_flags']}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("artifacts/global_full_sign_stabilizer_census_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/GLOBAL_FULL_SIGN_STABILIZER_CENSUS_2026_02_11.md"),
    )
    args = parser.parse_args()

    payload = build_census()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(payload), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
