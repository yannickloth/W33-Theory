#!/usr/bin/env python3
"""Build a seed assignment (edge->root) from a z3 candidate and optionally run CP‑SAT embedder.

Strategy:
 - For each edge compute nearest root index (as done by the main solver)
 - Group edges into orbits under the candidate vertex permutation
 - For each orbit pick the root index most frequently nearest across orbit members
 - Accept orbit-level seed assignments with consensus >= threshold and enforce uniqueness
 - Write checks/PART_CVII_z3_candidate_seed_<ts>.json and optionally invoke
   scripts/solve_e8_embedding_cpsat.py --seed-json <seed> --force-seed

Usage:
  python scripts/seed_from_z3_candidate.py --candidate-json committed_artifacts/PART_CVII_z3_candidate_...json --min-consensus 0.6 --time-limit 120 --run-solver --solver-time 600 --seed 212
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

# import helper functions from solver module
try:
    from scripts.solve_e8_embedding_cpsat import (
        compute_embedding_matrix,
        generate_scaled_e8_roots,
        build_edge_vectors,
    )
except Exception:
    # ensure repo root on path
    import sys as _sys

    _sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.solve_e8_embedding_cpsat import (
        compute_embedding_matrix,
        generate_scaled_e8_roots,
        build_edge_vectors,
    )


def find_latest_registered_candidate(rep_only: bool = True) -> Path | None:
    files = sorted(glob.glob("committed_artifacts/PART_CVII_z3_candidate_*.json"), key=os.path.getmtime)
    if not files:
        return None
    if rep_only:
        for f in reversed(files):
            try:
                j = json.loads(open(f, encoding="utf-8").read())
                if j.get("conj_group_rep"):
                    return Path(f)
            except Exception:
                continue
        return Path(files[-1])
    return Path(files[-1])


def edge_orbits_from_perm(edges: List[Tuple[int, int]], perm: Tuple[int, ...]) -> List[List[int]]:
    # Build mapping of edge->index for quick lookup (unordered edge canonicalized)
    edge_to_idx = {tuple(sorted(e)): i for i, e in enumerate(edges)}

    unvisited = set(range(len(edges)))
    orbits: List[List[int]] = []
    while unvisited:
        start = unvisited.pop()
        orbit = [start]
        cur = start
        while True:
            i, j = edges[cur]
            pi, pj = perm[i], perm[j]
            nxt = edge_to_idx.get(tuple(sorted((pi, pj))))
            if nxt is None or nxt in orbit:
                break
            orbit.append(nxt)
            cur = nxt
        # remove orbit members from unvisited
        for o in orbit:
            unvisited.discard(o)
        orbits.append(orbit)
    return orbits


def build_seed_from_candidate(candidate_json: Path, min_consensus: float = 0.6, max_seeds: int | None = None) -> Dict:
    meta = json.loads(open(candidate_json, encoding="utf-8").read())
    cand_perm = tuple(meta.get("vertex_perm", []))

    X, edges = compute_embedding_matrix()
    A_mat = build_edge_vectors(X, edges)
    roots = generate_scaled_e8_roots()
    roots_arr = np.array(roots, dtype=int)
    roots_unit = roots_arr.astype(float) / np.linalg.norm(roots_arr.astype(float), axis=1, keepdims=True)

    N_edges = len(A_mat)

    # for each edge find nearest root index (and distance)
    dists = np.linalg.norm(A_mat[:, None, :] - roots_unit[None, :, :], axis=2)
    nearest = np.argmin(dists, axis=1)
    nearest_d = np.min(dists, axis=1)

    # compute orbits under candidate permutation
    orbits = edge_orbits_from_perm(edges, cand_perm)

    seed_edges = []
    used_roots = set()

    # order orbits by size descending (larger orbits first) to improve coverage
    orbits_sorted = sorted(orbits, key=lambda o: len(o), reverse=True)
    for orb in orbits_sorted:
        # gather nearest roots within orbit
        votes = collections.Counter(int(nearest[e]) for e in orb)
        root_idx, count = votes.most_common(1)[0]
        cons = count / len(orb)
        if cons >= float(min_consensus):
            if root_idx in used_roots:
                # skip if root already used
                continue
            # pick representative edge in orbit with smallest nearest distance (most confident)
            best_e = min(orb, key=lambda e: float(nearest_d[e]))
            seed_edges.append({"edge_index": int(best_e), "root_index": int(root_idx)})
            used_roots.add(root_idx)
            if max_seeds is not None and len(seed_edges) >= int(max_seeds):
                break
    seed_obj = {"seed_edges": seed_edges, "rotation": None, "source_candidate": str(candidate_json)}
    return seed_obj


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-json", help="Path to committed_artifacts candidate JSON (default: latest rep)")
    parser.add_argument("--min-consensus", type=float, default=0.6, help="Min fraction of orbit agreeing on root to accept seed")
    parser.add_argument("--max-seeds", type=int, default=None, help="Max seeds to include (None = unlimited)")
    parser.add_argument("--out", help="Path to write seed JSON (default: checks/PART_CVII_z3_candidate_seed_<ts>.json)")
    parser.add_argument("--run-solver", action="store_true", help="Run scripts/solve_e8_embedding_cpsat.py with the produced seed (uses --force-seed)")
    parser.add_argument("--solver-time", type=float, default=600.0, help="Time limit for CP-SAT solver when --run-solver")
    parser.add_argument("--solver-k", type=int, default=40, help="k parameter for solver (top-K roots per edge)")
    parser.add_argument("--seed", type=int, default=212, help="random seed for solver")
    args = parser.parse_args()

    cand = Path(args.candidate_json) if args.candidate_json else find_latest_registered_candidate(rep_only=True)
    if cand is None or not cand.exists():
        raise FileNotFoundError("No candidate JSON found; register a z3 candidate first")

    print("Building seed from candidate:", cand)
    seed = build_seed_from_candidate(cand, min_consensus=args.min_consensus, max_seeds=args.max_seeds)
    ts = int(time.time())
    out_path = Path(args.out) if args.out else Path("checks") / f"PART_CVII_z3_candidate_seed_{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(seed, f, indent=2)
    print("Wrote seed JSON:", out_path, "(seed_edges=", len(seed.get('seed_edges',[])), ")")

    if args.run_solver:
        cmd = ["py", "-3", "scripts/solve_e8_embedding_cpsat.py", "--seed-json", str(out_path), "--k", str(args.solver_k), "--time-limit", str(args.solver_time), "--seed", str(int(args.seed)), "--force-seed"]
        print("Running solver with seed (cmd):", " ".join(cmd))
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Solver stdout:\n", proc.stdout)
        print("Solver stderr:\n", proc.stderr)
        # read solver output summary if present
        checks_out = Path.cwd() / "checks" / "PART_CVII_e8_embedding_cpsat.json"
        if checks_out.exists():
            j = json.loads(open(checks_out, encoding="utf-8").read())
            print("Solver summary in checks/PART_CVII_e8_embedding_cpsat.json:")
            print(json.dumps(j, indent=2))


if __name__ == "__main__":
    main()
