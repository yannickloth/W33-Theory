#!/usr/bin/env python3
"""Build a top-N gap seed file (small helper for interactive runs)."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

try:
    from scripts.solve_e8_embedding_cpsat import (
        build_edge_vectors,
        compute_embedding_matrix,
        generate_scaled_e8_roots,
    )
except Exception:
    import sys as _sys

    _sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.solve_e8_embedding_cpsat import (
        build_edge_vectors,
        compute_embedding_matrix,
        generate_scaled_e8_roots,
    )


def build_top_gap_seed(top_n: int = 6):
    X, edges = compute_embedding_matrix()
    A_mat = build_edge_vectors(X, edges)
    roots = generate_scaled_e8_roots()
    roots_arr = np.array(roots, dtype=int)
    roots_unit = roots_arr.astype(float) / np.linalg.norm(
        roots_arr.astype(float), axis=1, keepdims=True
    )

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
    p.add_argument("--top", type=int, default=6)
    p.add_argument("--out", default=None)
    args = p.parse_args()

    seed_obj = build_top_gap_seed(top_n=args.top)
    ts = int(time.time())
    outp = (
        Path(args.out)
        if args.out
        else Path("checks")
        / f"PART_CVII_z3_candidate_seed_manual_top{args.top}_{ts}.json"
    )
    outp.parent.mkdir(parents=True, exist_ok=True)
    from utils.json_safe import dump_json

    dump_json(seed_obj, outp, indent=2)
    print("Wrote seed file:", outp, "seed_edges=", len(seed_obj["seed_edges"]))
    print(json.dumps(seed_obj, indent=2, default=str))


if __name__ == "__main__":
    main()
