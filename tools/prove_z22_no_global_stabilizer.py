#!/usr/bin/env python3
"""Global exclusion of z=(2,2) full-sign stabilizers.

This script checks a stronger statement than the certificate-level exclusion:

There is no affine u-map (in all AGL(2,3), or even in the det=2/order-2
involution subset) and no global sign eps in {+1,-1} such that

  s(A*line, z_map(z)) = eps * s(line, z)

for all affine lines and z in {0,1,2}, with z_map(z)=2*z+2.

Sign values use the closed-form rule implemented in
`tools/analyze_e6_f3_trilinear_symmetry_breaking.py`.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

AffineElem = Tuple[Tuple[int, int, int, int, int], Tuple[int, int]]


def _affine_elements(mode: str) -> List[AffineElem]:
    pts = [(x, y) for x in range(3) for y in range(3)]
    if mode == "all_agl":
        mats = analyze._gl2_3()
    elif mode == "hessian216":
        mats = analyze._sl2_3()
    elif mode == "involution_det2":
        mats = analyze._gl2_3()
        mats = [
            m for m in mats if m[4] == 2 and analyze._affine_order((m, (0, 0))) == 2
        ]
    else:
        raise ValueError(f"unknown mode: {mode}")
    return [(A, b) for A in mats for b in pts]


def _sign_table() -> (
    Dict[Tuple[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]], int], int]
):
    lines = analyze._all_affine_lines()
    return {
        (line, z): int(analyze._predict_full_sign_closed_form(line, z))
        for line in lines
        for z in (0, 1, 2)
    }


def _candidate_check(
    elem: AffineElem,
    eps: int,
    z_map: Tuple[int, int],
    lines: List[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]],
    signs: Dict[
        Tuple[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]], int], int
    ],
) -> Dict[str, Any]:
    A, b = elem
    for line in lines:
        mapped_line = analyze._map_line(A, b, line)
        for z in (0, 1, 2):
            lhs = signs[(mapped_line, analyze._map_z(z_map, z))]
            rhs = eps * signs[(line, z)]
            if lhs != rhs:
                return {
                    "holds": False,
                    "first_mismatch": {
                        "line": [[int(p[0]), int(p[1])] for p in line],
                        "line_type": analyze._line_equation_type(line)[0],
                        "z": int(z),
                        "lhs": int(lhs),
                        "rhs": int(rhs),
                        "mapped_line": [[int(p[0]), int(p[1])] for p in mapped_line],
                        "mapped_line_type": analyze._line_equation_type(mapped_line)[0],
                    },
                }
    return {"holds": True, "first_mismatch": None}


def analyze_no_global_stabilizer(mode: str, z_map: Tuple[int, int]) -> Dict[str, Any]:
    lines = analyze._all_affine_lines()
    signs = _sign_table()
    elems = _affine_elements(mode)

    matches: List[Dict[str, Any]] = []
    mismatch_line_type_hist: Counter[str] = Counter()
    mismatch_z_hist: Counter[str] = Counter()

    for elem in elems:
        for eps in (1, -1):
            check = _candidate_check(elem, eps, z_map, lines, signs)
            if check["holds"]:
                A, b = elem
                matches.append(
                    {
                        "A": [int(A[0]), int(A[1]), int(A[2]), int(A[3])],
                        "det": int(A[4]),
                        "shift": [int(b[0]), int(b[1])],
                        "eps": int(eps),
                    }
                )
            else:
                first = check["first_mismatch"]
                mismatch_line_type_hist[str(first["line_type"])] += 1
                mismatch_z_hist[str(first["z"])] += 1

    return {
        "status": "ok",
        "mode": mode,
        "z_map": [int(z_map[0]), int(z_map[1])],
        "checked_candidates": int(len(elems) * 2),
        "match_count": int(len(matches)),
        "matches": matches,
        "no_global_stabilizer": len(matches) == 0,
        "first_mismatch_histograms": {
            "line_type": dict(mismatch_line_type_hist),
            "z": dict(mismatch_z_hist),
        },
        "notes": (
            "Closed-form full-sign law is used on all 12 affine lines and all 3 z-layers. "
            "A zero match count certifies global exclusion for the chosen z-map."
        ),
    }


def render_md(payload_all: Dict[str, Any], payload_inv: Dict[str, Any]) -> str:
    lines = ["# Global z=(2,2) Stabilizer Exclusion", ""]
    lines.append(
        "- Statement: no global full-sign stabilizer exists for z-map `(2,2)` "
        "in either all `AGL(2,3)` candidates or the det=2/order-2 involution subset."
    )
    lines.append("")
    lines.append("## All AGL(2,3)")
    lines.append("")
    lines.append(
        f"- checked candidates (including eps): `{payload_all['checked_candidates']}`"
    )
    lines.append(f"- match count: `{payload_all['match_count']}`")
    lines.append(f"- no global stabilizer: `{payload_all['no_global_stabilizer']}`")
    lines.append(
        f"- first-mismatch histograms: `{payload_all['first_mismatch_histograms']}`"
    )
    lines.append("")
    lines.append("## det=2/order-2 Involution Subset")
    lines.append("")
    lines.append(
        f"- checked candidates (including eps): `{payload_inv['checked_candidates']}`"
    )
    lines.append(f"- match count: `{payload_inv['match_count']}`")
    lines.append(f"- no global stabilizer: `{payload_inv['no_global_stabilizer']}`")
    lines.append(
        f"- first-mismatch histograms: `{payload_inv['first_mismatch_histograms']}`"
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--z-a", type=int, default=2)
    parser.add_argument("--z-b", type=int, default=2)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("artifacts/z22_global_stabilizer_exclusion_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/Z22_GLOBAL_STABILIZER_EXCLUSION_2026_02_11.md"),
    )
    args = parser.parse_args()

    z_map = (int(args.z_a) % 3, int(args.z_b) % 3)
    payload_all = analyze_no_global_stabilizer("all_agl", z_map)
    payload_inv = analyze_no_global_stabilizer("involution_det2", z_map)

    payload = {
        "status": "ok",
        "z_map": [int(z_map[0]), int(z_map[1])],
        "all_agl": payload_all,
        "involution_det2": payload_inv,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(payload_all, payload_inv), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
