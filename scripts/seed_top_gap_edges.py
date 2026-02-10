#!/usr/bin/env python3
"""Select top-N edges by gap (second_nearest - nearest) and use as seeds.

Usage:
  python scripts/seed_top_gap_edges.py --candidate committed_artifacts/...json --top 6 --run-solver --force
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np

try:
    from scripts.solve_e8_embedding_cpsat import compute_embedding_matrix, generate_scaled_e8_roots, build_edge_vectors
except Exception:
    import sys as _sys

    _sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.solve_e8_embedding_cpsat import compute_embedding_matrix, generate_scaled_e8_roots, build_edge_vectors


def find_latest_candidate():
    files = sorted(glob.glob("committed_artifacts/PART_CVII_z3_candidate_*.json"), key=lambda p: Path(p).stat().st_mtime)
    return Path(files[-1]) if files else None


def build_top_gap_seed(candidate_json: Path, top_n: int = 6):
    X, edges = compute_embedding_matrix()
    A_mat = build_edge_vectors(X, edges)
    roots = generate_scaled_e8_roots()
    roots_arr = np.array(roots, dtype=int)
    roots_unit = roots_arr.astype(float) / np.linalg.norm(roots_arr.astype(float), axis=1, keepdims=True)

    dists = np.linalg.norm(A_mat[:, None, :] - roots_unit[None, :, :], axis=2)
    sorted_idx = np.argsort(dists, axis=1)
    nearest = sorted_idx[:, 0]
    nearest_d = dists[np.arange(dists.shape[0]), sorted_idx[:, 0]]
    second_d = dists[np.arange(dists.shape[0]), sorted_idx[:, 1]]
    gaps = second_d - nearest_d

    order = np.argsort(-gaps)
    seed_edges = []
    used_roots = set()
    for e in order:
        r = int(nearest[e])
        if r in used_roots:
            continue
        seed_edges.append({"edge_index": int(e), "root_index": r})
        used_roots.add(r)
        if len(seed_edges) >= int(top_n):
            break
    return {"seed_edges": seed_edges, "rotation": None}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", help="candidate json (default: latest)")
    p.add_argument("--top", type=int, default=6)
    p.add_argument("--out", help="seed output path (default checks/PART_CVII_z3_candidate_seed_gap_<ts>.json)")
    p.add_argument("--run-solver", action='store_true')
    p.add_argument("--force", action='store_true')
    p.add_argument("--solver-time", type=float, default=300.0)
    p.add_argument("--solver-k", type=int, default=40)
    p.add_argument("--seed", type=int, default=212)
    p.add_argument("--seed-reward", type=float, default=10000.0)
    args = p.parse_args()

    cand = Path(args.candidate) if args.candidate else find_latest_candidate()
    if not cand or not cand.exists():
        raise FileNotFoundError("No candidate file found")
    seed_obj = build_top_gap_seed(cand, top_n=args.top)
    ts = int(time.time())
    outp = Path(args.out) if args.out else Path('checks') / f"PART_CVII_z3_candidate_seed_gap_{ts}.json"
    outp.parent.mkdir(parents=True, exist_ok=True)
    with open(outp, 'w', encoding='utf-8') as f:
        json.dump(seed_obj, f, indent=2)
    print('Wrote seed file:', outp, 'seed_edges=', len(seed_obj['seed_edges']))

    if args.run_solver:
        cmd = ["py", "-3", "scripts/solve_e8_embedding_cpsat.py", "--seed-json", str(outp), "--k", str(args.solver_k), "--time-limit", str(args.solver_time), "--seed", str(int(args.seed))]
        if args.force:
            cmd.append("--force-seed")
        else:
            cmd += ["--seed-reward", str(args.seed_reward)]
        print('Running solver:', ' '.join(cmd))
        import subprocess as _sp

        proc = _sp.run(cmd, stdout=_sp.PIPE, stderr=_sp.PIPE, text=True)
        print('Solver stdout:\n', proc.stdout)
        print('Solver stderr:\n', proc.stderr)
        # print checks summary if exists
        out = Path.cwd() / 'checks' / 'PART_CVII_e8_embedding_cpsat.json'
        if out.exists():
            print('Solver summary:')
            print(json.dumps(json.loads(open(out, encoding='utf-8').read()), indent=2))


if __name__ == '__main__':
    import time

    main()
