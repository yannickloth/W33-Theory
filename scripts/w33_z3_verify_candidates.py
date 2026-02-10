#!/usr/bin/env python3
"""Verify Z3 candidates by computing projection matrices and checking properties.

Reads latest PART_CVII_z3_candidates_*.json and for the top N candidates computes
- restricted action R on harmonic subspace
- projections P0, P1, P2 onto eigenclusters (1, w, w^2)
- norms: ||R^3 - I||, ||P^2 - P||, ||P_i P_j|| for i != j, rank(P_i)

Writes JSON summary to checks/ and prints a short diagnostic.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import time
from pathlib import Path

import numpy as np
from w33_full_decomposition import build_psp43_group, compute_full_hodge_eigenbasis
from w33_homology import build_clique_complex, build_w33

try:
    from utils.json_safe import dump_json
except Exception:
    import sys
    from pathlib import Path as _Path

    sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
    from utils.json_safe import dump_json


def restricted_action_on_subspace(V_sub: np.ndarray, ep, es):
    m, d = V_sub.shape
    ep = np.asarray(ep, dtype=int)
    es = np.asarray(es, dtype=float)
    temp = V_sub * es[:, None]
    Y = np.zeros_like(V_sub, dtype=float)
    Y[ep, :] = temp
    R = V_sub.T.conj() @ Y
    return R


def find_latest_candidate_file():
    files = sorted(
        glob.glob("checks/PART_CVII_z3_candidates_*.json"), key=os.path.getmtime
    )
    if not files:
        raise FileNotFoundError("No PART_CVII_z3_candidates_*.json found in checks/")
    return files[-1]


def proj_for_root(R, root):
    # P_root = (1/3) * sum_{t=0}^2 (root^{-t}) * R^t
    I = np.eye(R.shape[0], dtype=complex)
    R2 = R @ R
    inv1 = 1.0 / root
    inv2 = 1.0 / (root * root)
    P = (I + inv1 * R + inv2 * R2) / 3.0
    return P


def numeric_rank(A, tol=1e-9):
    s = np.linalg.svd(A, compute_uv=False)
    return int((s > tol).sum())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--n", type=int, default=5, help="Number of top candidates to verify"
    )
    args = parser.parse_args()

    path = find_latest_candidate_file()
    print(f"Loading candidates: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    hodge = compute_full_hodge_eigenbasis(n, adj, edges, simplices)
    V_harm = hodge["harmonic"]

    group = build_psp43_group(vertices, edges)

    results = []
    roots = [
        1.0 + 0j,
        complex(-0.5, math.sqrt(3) / 2),
        complex(-0.5, -math.sqrt(3) / 2),
    ]

    for i, cand in enumerate(data.get("candidates", [])[: args.n], start=1):
        vperm = tuple(cand["vertex_perm"])
        if vperm not in group:
            print(f"Candidate vertex_perm {vperm} not found in group; skipping")
            continue
        ep, es = group[vperm]
        R = restricted_action_on_subspace(V_harm, ep, es)
        R3_err = float(np.linalg.norm(R @ R @ R - np.eye(R.shape[0], dtype=complex)))

        Pmats = [proj_for_root(R, r) for r in roots]
        P_iderrs = [float(np.linalg.norm(P @ P - P)) for P in Pmats]
        P_ranks = [int(np.round(np.linalg.matrix_rank(P, tol=1e-8))) for P in Pmats]
        P_cross = [
            float(np.linalg.norm(Pmats[i] @ Pmats[j]))
            for i in range(3)
            for j in range(3)
            if i != j
        ]
        P_sum_err = float(
            np.linalg.norm(sum(Pmats) - np.eye(R.shape[0], dtype=complex))
        )

        meta = {
            "index": i,
            "vertex_perm": vperm,
            "R3_norm": R3_err,
            "P_iderrs": P_iderrs,
            "P_ranks": P_ranks,
            "P_cross_norms": P_cross,
            "P_sum_err": P_sum_err,
        }
        results.append(meta)

        print(
            f"Candidate {i}: R3={R3_err:.2e}, ranks={P_ranks}, iderrs={[f'{x:.2e}' for x in P_iderrs]}"
        )

    out = Path("checks") / f"PART_CVII_z3_verify_{int(time.time())}.json"
    dump_json({"file": path, "results": results}, out, indent=2)

    print(f"Wrote verification summary to: {out}")


if __name__ == "__main__":
    main()
