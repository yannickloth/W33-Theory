#!/usr/bin/env python3
"""
Solve for the 9 missing tritangent planes using a CP-SAT model.

The solver uses the per-line counts constraint (each line belongs to 10 tritangent planes)
and searches for the missing planes among candidate triads (from the heisenberg model or provided partition).

Usage:
  py -3 tools/solve_missing_tritangents.py --bundle-dir artifacts/more_new_work_extracted/NewestWork2_2_2026_delta_v3p52

Outputs:
  - artifacts/bundles/<bundle>/missing_9_solutions.json
  - artifacts/bundles/<bundle>/missing_9_report.md
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Tuple

try:
    from ortools.sat.python import cp_model
except Exception:
    cp_model = None

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"


def read_triads_from_heis() -> List[Tuple[int, int, int]]:
    heis = ART / "e6_cubic_affine_heisenberg_model.json"
    if not heis.exists():
        return []
    j = json.loads(heis.read_text(encoding="utf-8"))
    triads = []
    for item in j.get("affine_u_lines", []):
        for t in item.get("triads", []):
            tri = tuple(sorted(int(x) for x in t))
            triads.append(tuple(tri))
    # unique
    triads = sorted(set(triads))
    return triads


def load_existing_planes(tri_json: Path) -> Tuple[List[Tuple[int, int, int]], int]:
    j = json.loads(tri_json.read_text(encoding="utf-8"))
    planes = j.get("planes", [])
    known = []
    missing_count = 0
    for p in planes:
        if p.get("lines"):
            lines = [int(x) for x in p["lines"]]
            if p.get("missing"):
                missing_count += 1
            else:
                known.append(tuple(sorted(lines)))
        else:
            # plane label without lines
            if p.get("missing"):
                missing_count += 1
    return sorted(set(known)), missing_count


def solve_missing(triads_candidates: List[Tuple[int, int, int]], known_triads: List[Tuple[int, int, int]], missing_count: int, time_limit_s: int = 30):
    # Build line counts from known triads
    counts = [0] * 27
    for tri in known_triads:
        for l in tri:
            counts[l] += 1
    deficits = [10 - c for c in counts]
    if sum(deficits) != missing_count * 3:
        print(f"Warning: deficits sum {sum(deficits)} != {missing_count*3}; solver may fail")

    # Filter candidate triads to those not already known and with valid lines
    candidates = [t for t in triads_candidates if t not in known_triads]
    if not candidates:
        print("No candidate triads available; aborting")
        return None

    if cp_model is None:
        print("CP-SAT not available; cannot solve missing triads automatically")
        return None

    model = cp_model.CpModel()
    n = len(candidates)
    x = [model.NewBoolVar(f"x_{i}") for i in range(n)]

    # Exactly missing_count triads selected
    model.Add(sum(x) == missing_count)

    # Per-line constraints
    for l in range(27):
        involved = [x[i] for i, t in enumerate(candidates) if l in t]
        if involved:
            model.Add(sum(involved) == deficits[l])
        else:
            if deficits[l] != 0:
                print(f"Line {l} has deficit {deficits[l]} but no candidate triad covers it; unsatisfiable")
                return None

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(time_limit_s)
    solver.parameters.num_search_workers = 8

    res = solver.Solve(model)
    if res in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        chosen = [candidates[i] for i in range(n) if solver.Value(x[i])]
        return chosen
    else:
        print("No solution found (status = ", res, ")")
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bundle-dir", type=Path, required=True)
    p.add_argument("--trihedron-dir", type=Path, default=None)
    p.add_argument("--time-limit", type=int, default=30)
    args = p.parse_args()

    bundle = args.bundle_dir
    tri_dir = args.trihedron_dir if args.trihedron_dir is not None else (ART / "bundles" / bundle.name / "trihedron")
    tri_json = tri_dir / "tritangent_planes.json"
    if not tri_json.exists():
        print("trihedron output not found; run build_trihedron_tritangent_bundle.py first")
        return

    known_triads, missing_count = load_existing_planes(tri_json)
    print(f"Known triads: {len(known_triads)}, missing_count: {missing_count}")

    candidates = read_triads_from_heis()
    print(f"Heisenberg model candidate triads: {len(candidates)}")

    chosen = solve_missing(candidates, known_triads, missing_count, time_limit_s=args.time_limit)
    out_dir = ART / "bundles" / bundle.name
    out_dir.mkdir(parents=True, exist_ok=True)

    if chosen is None:
        out = {"status": "no_solution", "known_triads": known_triads, "candidates_considered": candidates}
        (out_dir / "missing_9_solutions.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
        (out_dir / "missing_9_report.md").write_text("# Missing 9 solver: no solution found\n", encoding="utf-8")
        print("No solution written; see outputs")
        return

    out = {"status": "ok", "chosen_triads": [list(t) for t in chosen], "missing_count": missing_count}
    (out_dir / "missing_9_solutions.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    md = [f"# Missing 9 tritangent planes (bundle={bundle.name})", "", "## Chosen triads:"]
    for t in chosen:
        md.append(f"- {list(t)}")
    (out_dir / "missing_9_report.md").write_text("\n".join(md), encoding="utf-8")
    print("Wrote missing_9_solutions.json and report")


if __name__ == "__main__":
    main()
