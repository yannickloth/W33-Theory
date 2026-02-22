#!/usr/bin/env python3
"""Classify geometry of nontrivial minimal UNSAT cores for global z-cells.

Focuses on `all_agl` and `hessian216` for nontrivial z-maps (all except z=(1,0)).
For these cells, the unconstrained minimal UNSAT core size is 3. We enumerate all
size-3 cores and classify whether each is exactly a full parallel class triplet
(same striation type with offsets {0,1,2}).
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.minimal_global_full_sign_cores as cores

MODES: List[str] = ["all_agl", "hessian216"]
NONTRIVIAL_Z: List[Tuple[int, int]] = [z for z in cores.Z_MAPS if z != (1, 0)]


def _is_unsat_subset(
    subset: Sequence[int], masks: Sequence[int], candidate_count: int
) -> bool:
    live = (1 << candidate_count) - 1
    for j in subset:
        live &= masks[j]
        if live == 0:
            return True
    return live == 0


def _line_sig(constraint: cores.Constraint) -> Tuple[str, int]:
    line, _ = constraint
    t, off = cores.analyze._line_equation_type(line)
    return str(t), int(off)


def _core_signature(
    core_indices: Sequence[int], constraints: Sequence[cores.Constraint]
) -> Tuple[Tuple[str, int, int], ...]:
    triples: List[Tuple[str, int, int]] = []
    for j in core_indices:
        (t, off) = _line_sig(constraints[j])
        z = int(constraints[j][1])
        triples.append((t, off, z))
    return tuple(sorted(triples))


def _is_parallel_class_triplet(
    core_indices: Sequence[int], constraints: Sequence[cores.Constraint]
) -> bool:
    line_types = []
    offsets = []
    for j in core_indices:
        t, off = _line_sig(constraints[j])
        line_types.append(t)
        offsets.append(off)
    return len(set(line_types)) == 1 and set(offsets) == {0, 1, 2}


def _cell_payload(
    mode: str,
    z_map: Tuple[int, int],
    constraints: Sequence[cores.Constraint],
    signs: Dict[cores.Constraint, int],
) -> Dict[str, Any]:
    candidates = cores._candidate_pool(mode)
    masks = cores._sat_masks(list(constraints), candidates, z_map, signs)
    candidate_count = len(candidates)

    # We only enumerate size-3 cores here (known nontrivial minimum in these modes).
    minimal_cores: List[Tuple[int, int, int]] = []
    for comb in itertools.combinations(range(len(constraints)), 3):
        if _is_unsat_subset(comb, masks, candidate_count):
            minimal_cores.append(comb)

    by_line_type: Dict[str, int] = {}
    parallel_count = 0
    for comb in minimal_cores:
        sig = _core_signature(comb, constraints)
        types = sorted({t for (t, _, _) in sig})
        key = ",".join(types)
        by_line_type[key] = by_line_type.get(key, 0) + 1
        if _is_parallel_class_triplet(comb, constraints):
            parallel_count += 1

    return {
        "mode": mode,
        "z_map": [int(z_map[0]), int(z_map[1])],
        "candidate_count": int(candidate_count),
        "minimal_core_size": 3,
        "minimal_core_count": int(len(minimal_cores)),
        "parallel_class_triplet_count": int(parallel_count),
        "all_min_cores_are_parallel_class_triplets": parallel_count
        == len(minimal_cores),
        "line_type_profile": by_line_type,
        "sample_cores": [
            {
                "indices": [int(j) for j in comb],
                "constraints": [cores._constraint_json(constraints[j]) for j in comb],
            }
            for comb in minimal_cores[:4]
        ],
        "signature_set": sorted(
            [
                list(sig)
                for sig in {
                    _core_signature(comb, constraints) for comb in minimal_cores
                }
            ]
        ),
    }


def build_report() -> Dict[str, Any]:
    constraints = cores._constraints()
    signs = cores._sign_table(constraints)
    matrix: Dict[str, Dict[str, Dict[str, Any]]] = {m: {} for m in MODES}

    for mode in MODES:
        for z_map in NONTRIVIAL_Z:
            key = f"({z_map[0]},{z_map[1]})"
            matrix[mode][key] = _cell_payload(mode, z_map, constraints, signs)

    counts_match = True
    signatures_match = True
    for z_map in NONTRIVIAL_Z:
        key = f"({z_map[0]},{z_map[1]})"
        c0 = matrix["all_agl"][key]["minimal_core_count"]
        c1 = matrix["hessian216"][key]["minimal_core_count"]
        if c0 != c1:
            counts_match = False
        s0 = matrix["all_agl"][key]["signature_set"]
        s1 = matrix["hessian216"][key]["signature_set"]
        if s0 != s1:
            signatures_match = False

    theorem_flags = {
        "all_cells_parallel_class_triplets": all(
            matrix[mode][f"({a},{b})"]["all_min_cores_are_parallel_class_triplets"]
            for mode in MODES
            for (a, b) in NONTRIVIAL_Z
        ),
        "core_counts_match_between_agl_and_hessian": counts_match,
        "core_signatures_match_between_agl_and_hessian": signatures_match,
    }

    return {
        "status": "ok",
        "modes": MODES,
        "nontrivial_z_maps": [[int(a), int(b)] for (a, b) in NONTRIVIAL_Z],
        "matrix": matrix,
        "theorem_flags": theorem_flags,
        "notes": (
            "For nontrivial z-cells in all_agl/hessian216, minimal size-3 UNSAT cores "
            "are classified exhaustively."
        ),
    }


def render_md(payload: Dict[str, Any]) -> str:
    lines: List[str] = ["# Nontrivial UNSAT Core Geometry (Global Cells)", ""]
    lines.append(
        "- Statement: classify all minimal size-3 UNSAT cores in nontrivial global z-cells for `all_agl` and `hessian216`."
    )
    lines.append("")
    lines.append("Mode | z=(1,1) | z=(1,2) | z=(2,0) | z=(2,1) | z=(2,2)")
    lines.append("--- | --- | --- | --- | --- | ---")
    for mode in MODES:
        vals = []
        for z_map in NONTRIVIAL_Z:
            key = f"({z_map[0]},{z_map[1]})"
            cell = payload["matrix"][mode][key]
            vals.append(
                f"{cell['minimal_core_count']} (parallel={cell['parallel_class_triplet_count']})"
            )
        lines.append(f"{mode} | " + " | ".join(vals))
    lines.append("")
    lines.append(f"- Theorem flags: `{payload['theorem_flags']}`")
    lines.append("")
    lines.append("## Example (all_agl, z=(1,1))")
    lines.append("")
    ex = payload["matrix"]["all_agl"]["(1,1)"]
    lines.append(f"- line-type profile: `{ex['line_type_profile']}`")
    lines.append(f"- sample cores: `{ex['sample_cores']}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("artifacts/nontrivial_unsat_core_geometry_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/NONTRIVIAL_UNSAT_CORE_GEOMETRY_2026_02_11.md"),
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
