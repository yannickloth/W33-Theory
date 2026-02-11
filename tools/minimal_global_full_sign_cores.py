#!/usr/bin/env python3
"""Compute minimal contradiction cores for global full-sign stabilizer cells.

For a fixed affine mode and z-map, consider candidates in:
  (u_affine) x {eps in {+1,-1}}
and constraints indexed by (line, z) over all 12 affine lines and z in {0,1,2}.

Each constraint requires:
  s(A*line, z_map(z)) = eps * s(line, z).

If no candidate satisfies all constraints, this script finds a minimal-size
subset of constraints whose conjunction is already impossible (an UNSAT core).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

AffineElem = Tuple[Tuple[int, int, int, int, int], Tuple[int, int]]
Constraint = Tuple[
    Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]],
    int,
]

Z_MAPS: List[Tuple[int, int]] = [(1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
MODES: List[str] = ["all_agl", "hessian216", "involution_det2"]


def _candidate_pool(mode: str) -> List[Tuple[AffineElem, int]]:
    pts = [(x, y) for x in range(3) for y in range(3)]
    if mode == "all_agl":
        mats = analyze._gl2_3()
    elif mode == "hessian216":
        mats = analyze._sl2_3()
    elif mode == "involution_det2":
        mats = [
            m
            for m in analyze._gl2_3()
            if m[4] == 2 and analyze._affine_order((m, (0, 0))) == 2
        ]
    else:
        raise ValueError(f"unknown mode: {mode}")
    return [((A, b), eps) for A in mats for b in pts for eps in (1, -1)]


def _constraints() -> List[Constraint]:
    lines = analyze._all_affine_lines()
    return [(line, z) for line in lines for z in (0, 1, 2)]


def _sign_table(constraints: List[Constraint]) -> Dict[Constraint, int]:
    return {
        (line, z): int(analyze._predict_full_sign_closed_form(line, z))
        for line, z in constraints
    }


def _sat_masks(
    constraints: List[Constraint],
    candidates: List[Tuple[AffineElem, int]],
    z_map: Tuple[int, int],
    signs: Dict[Constraint, int],
) -> List[int]:
    masks: List[int] = []
    for line, z in constraints:
        mask = 0
        for i, ((A, shift), eps) in enumerate(candidates):
            mapped_line = analyze._map_line(A, shift, line)
            lhs = signs[(mapped_line, analyze._map_z(z_map, z))]
            rhs = eps * signs[(line, z)]
            if lhs == rhs:
                mask |= 1 << i
        masks.append(mask)
    return masks


def _first_candidate(mask: int) -> Optional[int]:
    if mask == 0:
        return None
    return (mask & -mask).bit_length() - 1


def _constraint_json(constraint: Constraint) -> Dict[str, Any]:
    line, z = constraint
    return {
        "line": [[int(p[0]), int(p[1])] for p in line],
        "line_type": str(analyze._line_equation_type(line)[0]),
        "abc": [int(v) for v in analyze._normalized_line_abc(line)],
        "z": int(z),
    }


def _candidate_json(candidate: Tuple[AffineElem, int]) -> Dict[str, Any]:
    (A, shift), eps = candidate
    return {
        "A": [int(A[0]), int(A[1]), int(A[2]), int(A[3])],
        "det": int(A[4]),
        "shift": [int(shift[0]), int(shift[1])],
        "eps": int(eps),
    }


def _minimal_unsat_core_indices(
    masks: List[int], candidate_count: int
) -> Optional[List[int]]:
    """Return one minimal UNSAT core as constraint indices, or None if SAT."""
    full = (1 << candidate_count) - 1

    # If all constraints are jointly satisfiable, there is no UNSAT core.
    sat_all = full
    for m in masks:
        sat_all &= m
    if sat_all:
        return None

    order = sorted(range(len(masks)), key=lambda j: masks[j].bit_count())
    best: Optional[List[int]] = None

    # Depth-first search with branch-and-bound.
    def dfs(pos: int, live_mask: int, chosen: List[int]) -> None:
        nonlocal best
        if live_mask == 0:
            if best is None or len(chosen) < len(best):
                best = chosen.copy()
            return
        if pos >= len(order):
            return
        if best is not None and len(chosen) >= len(best):
            return

        # Include current constraint.
        j = order[pos]
        dfs(pos + 1, live_mask & masks[j], chosen + [j])

        # Exclude current constraint.
        dfs(pos + 1, live_mask, chosen)

    dfs(0, full, [])
    if best is None:
        return None
    return sorted(best)


def analyze_cell(
    mode: str,
    z_map: Tuple[int, int],
    constraints: List[Constraint],
    signs: Dict[Constraint, int],
) -> Dict[str, Any]:
    candidates = _candidate_pool(mode)
    masks = _sat_masks(constraints, candidates, z_map, signs)
    core = _minimal_unsat_core_indices(masks, len(candidates))

    if core is None:
        # SAT cell: provide matching count and one witness.
        full = (1 << len(candidates)) - 1
        sat = full
        for m in masks:
            sat &= m
        match_count = sat.bit_count()
        witness_idx = _first_candidate(sat)
        witness = (
            _candidate_json(candidates[witness_idx])
            if witness_idx is not None
            else None
        )
        return {
            "mode": mode,
            "z_map": [int(z_map[0]), int(z_map[1])],
            "status": "sat",
            "candidate_count": int(len(candidates)),
            "match_count": int(match_count),
            "first_witness": witness,
            "minimal_core_size": None,
            "minimal_core": [],
        }

    return {
        "mode": mode,
        "z_map": [int(z_map[0]), int(z_map[1])],
        "status": "unsat",
        "candidate_count": int(len(candidates)),
        "match_count": 0,
        "first_witness": None,
        "minimal_core_size": int(len(core)),
        "minimal_core": [_constraint_json(constraints[j]) for j in core],
    }


def build_report() -> Dict[str, Any]:
    constraints = _constraints()
    signs = _sign_table(constraints)
    cells: List[Dict[str, Any]] = []
    matrix: Dict[str, Dict[str, Dict[str, Any]]] = {}

    for mode in MODES:
        row: Dict[str, Dict[str, Any]] = {}
        for z_map in Z_MAPS:
            cell = analyze_cell(mode, z_map, constraints, signs)
            key = f"({z_map[0]},{z_map[1]})"
            row[key] = cell
            cells.append(cell)
        matrix[mode] = row

    theorem_flags = {
        "all_agl_only_identity_at_z10": matrix["all_agl"]["(1,0)"]["status"] == "sat"
        and matrix["all_agl"]["(1,0)"]["match_count"] == 1
        and all(
            matrix["all_agl"][f"({a},{b})"]["status"] == "unsat"
            for (a, b) in Z_MAPS
            if (a, b) != (1, 0)
        ),
        "hessian_only_identity_at_z10": matrix["hessian216"]["(1,0)"]["status"] == "sat"
        and matrix["hessian216"]["(1,0)"]["match_count"] == 1
        and all(
            matrix["hessian216"][f"({a},{b})"]["status"] == "unsat"
            for (a, b) in Z_MAPS
            if (a, b) != (1, 0)
        ),
        "involution_subset_all_unsat": all(
            matrix["involution_det2"][f"({a},{b})"]["status"] == "unsat"
            for (a, b) in Z_MAPS
        ),
    }

    return {
        "status": "ok",
        "modes": MODES,
        "z_maps": [[int(a), int(b)] for a, b in Z_MAPS],
        "constraint_count": int(len(constraints)),
        "matrix": matrix,
        "cells": cells,
        "theorem_flags": theorem_flags,
        "notes": (
            "Minimal cores are exact for the finite candidate sets and 36 line/z constraints."
        ),
    }


def render_md(payload: Dict[str, Any]) -> str:
    lines: List[str] = ["# Minimal Global Full-Sign Contradiction Cores", ""]
    lines.append(
        "- Each unsat cell is annotated with a minimal contradiction-core size."
    )
    lines.append("- SAT cells list full match count (global stabilizers).")
    lines.append("")
    lines.append("Mode | z=(1,0) | z=(1,1) | z=(1,2) | z=(2,0) | z=(2,1) | z=(2,2)")
    lines.append("--- | --- | --- | --- | --- | --- | ---")

    for mode in MODES:
        vals: List[str] = []
        for z_map in Z_MAPS:
            key = f"({z_map[0]},{z_map[1]})"
            cell = payload["matrix"][mode][key]
            if cell["status"] == "sat":
                vals.append(f"sat:{cell['match_count']}")
            else:
                vals.append(f"unsat:{cell['minimal_core_size']}")
        lines.append(f"{mode} | " + " | ".join(vals))

    lines.append("")
    lines.append(f"- Theorem flags: `{payload['theorem_flags']}`")
    lines.append("")
    lines.append("## Example Minimal Core (all_agl, z=(2,2))")
    lines.append("")
    ex = payload["matrix"]["all_agl"]["(2,2)"]
    lines.append(f"- core size: `{ex['minimal_core_size']}`")
    lines.append(f"- constraints: `{ex['minimal_core']}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("artifacts/minimal_global_full_sign_cores_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/MINIMAL_GLOBAL_FULL_SIGN_CORES_2026_02_11.md"),
    )
    args = parser.parse_args()

    payload = build_report()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(payload), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
