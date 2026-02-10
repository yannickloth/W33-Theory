#!/usr/bin/env python3
"""Analyze Z3-splitting candidates and export eigen-subspaces.

Reads the most recent PART_CVII_z3_candidates_*.json and for the top N
candidates computes R, eigendecomposition on harmonic subspace, and
writes .npz artifacts containing basis vectors for each eigen-cluster.

Usage:
  python scripts/w33_z3_analyze_candidates.py --n 5
"""
from __future__ import annotations

import argparse
import glob
import json
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


def cluster_indices(eigs, roots=None):
    if roots is None:
        roots = [
            1.0 + 0j,
            complex(-0.5, math.sqrt(3) / 2),
            complex(-0.5, -math.sqrt(3) / 2),
        ]
    inds = {0: [], 1: [], 2: []}
    for i, lam in enumerate(eigs):
        dlist = [abs(lam - r) for r in roots]
        j = int(np.argmin(dlist))
        inds[j].append(i)
    return inds


def find_latest_candidate_file():
    files = sorted(
        glob.glob("checks/PART_CVII_z3_candidates_*.json"), key=os.path.getmtime
    )
    if not files:
        raise FileNotFoundError("No PART_CVII_z3_candidates_*.json found in checks/")
    return files[-1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--n", type=int, default=5, help="Number of top candidates to analyze"
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

    outdir = Path("checks") / f"z3_analysis_{int(time.time())}"
    outdir.mkdir(parents=True, exist_ok=True)

    candidates = data.get("candidates", [])[: args.n]
    results = []

    for i, cand in enumerate(candidates, start=1):
        vperm = tuple(cand["vertex_perm"])
        if vperm not in group:
            print(f"Candidate vertex_perm {vperm} not found in group; skipping")
            continue
        ep, es = group[vperm]
        R = restricted_action_on_subspace(V_harm, ep, es)
        w, vecs = np.linalg.eig(R)
        # cluster by closeness to roots of unity
        roots = [
            1.0 + 0j,
            complex(-0.5, math.sqrt(3) / 2),
            complex(-0.5, -math.sqrt(3) / 2),
        ]
        inds = {0: [], 1: [], 2: []}
        for idx, lam in enumerate(w):
            dvals = [abs(lam - r) for r in roots]
            j = int(np.argmin(dvals))
            inds[j].append(idx)

        # Extract the basis vectors (columns of vecs) for each cluster and save them
        cluster_bases = {}
        for k in inds:
            if not inds[k]:
                cluster_bases[f"cluster_{k}"] = np.zeros(
                    (V_harm.shape[0], 0), dtype=complex
                )
            else:
                cluster_bases[f"cluster_{k}"] = vecs[:, inds[k]]

        out_npz = outdir / f"z3_candidate_{i:02d}.npz"
        np.savez_compressed(out_npz, **cluster_bases)

        meta = {
            "index": i,
            "vertex_perm": vperm,
            "counts": [len(inds[0]), len(inds[1]), len(inds[2])],
            "R3_norm": float(np.linalg.norm(R @ R @ R - np.eye(R.shape[0]))),
            "artifact": str(out_npz),
        }
        results.append(meta)
        print(f"Wrote candidate {i:02d}: counts={meta['counts']} -> {out_npz}")

    summary_path = outdir / "summary.json"
    dump_json({"file": path, "results": results}, summary_path, indent=2)

    print(f"Analysis written to: {outdir}")


if __name__ == "__main__":
    import math

    main()
