#!/usr/bin/env python3
"""Search PSp(4,3) for order-3 elements that split HARMONIC (81) into 3x27.

This script:
 - builds W33 and computes the Hodge harmonic basis
 - enumerates PSp(4,3) as signed edge permutations
 - for each element, computes the restricted action on harmonic subspace
 - tests whether eigenvalues cluster near 1, exp(2pi i /3), exp(4pi i /3)
 - records candidates with (27,27,27) multiplicities and small R^3 - I norm

Usage:
  python scripts/w33_find_z3_split.py

Outputs JSON to checks/PART_CVII_z3_candidates_<ts>.json
"""
from __future__ import annotations

import json
import math
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from w33_full_decomposition import build_psp43_group, compute_full_hodge_eigenbasis
from w33_homology import build_clique_complex, build_w33

from utils.json_safe import dump_json


def restricted_action_on_subspace(V_sub: np.ndarray, ep, es):
    """Compute restricted matrix R = V_sub.T @ P @ V_sub where P is signed perm.

    V_sub: m x d (columns orthonormal)
    ep: iterable length m (permutation of edge indices)
    es: iterable length m (signs +-1)
    returns: d x d complex matrix
    """
    m, d = V_sub.shape
    ep = np.asarray(ep, dtype=int)
    es = np.asarray(es, dtype=float)

    # temp[j,:] = es[j] * V_sub[j,:]
    temp = V_sub * es[:, None]
    # Y = P @ V_sub: rows are placed at ep[j]
    Y = np.zeros_like(V_sub, dtype=float)
    Y[ep, :] = temp
    R = V_sub.T.conj() @ Y  # d x d
    return R


def cluster_eigenvalues(eigs, tol=1e-6):
    """Cluster eigenvalues around the 3 roots of unity (1, w, w^2).
    Returns counts dict and residuals.
    """
    w1 = 1.0 + 0j
    w2 = complex(math.cos(2 * math.pi / 3), math.sin(2 * math.pi / 3))
    w3 = complex(math.cos(4 * math.pi / 3), math.sin(4 * math.pi / 3))
    roots = [w1, w2, w3]
    counts = [0, 0, 0]
    dists = [0.0, 0.0, 0.0]

    for lam in eigs:
        lam = complex(lam)
        dlist = [abs(lam - r) for r in roots]
        i = int(np.argmin(dlist))
        counts[i] += 1
        dists[i] += dlist[i]

    return {
        "counts": counts,
        "avg_dist": [d / c if c > 0 else None for d, c in zip(dists, counts)],
    }


def is_good_z3_candidate(R, tol_counts=2, tol_power=1e-8):
    """Return True if eigen clusters are close to (27,27,27) and R^3 ~ I.

    Fast-path: check R^3 ~ I first (cheap matrix mult) and only then do eigendecomp.
    """
    d = R.shape[0]
    I = np.eye(d, dtype=complex)
    R3 = R @ R @ R
    err = np.linalg.norm(R3 - I)
    if err >= tol_power:
        return False, {"R3_norm": err}, None

    eigs, eigvecs = np.linalg.eig(R)
    cl = cluster_eigenvalues(eigs)
    counts = cl["counts"]
    # check each count near 27 within tol_counts
    if not all(abs(c - 27) <= tol_counts for c in counts):
        return False, cl, eigs

    return True, {"counts": counts, "avg_dist": cl["avg_dist"], "R3_norm": err}, eigs


def main():
    t0 = time.time()
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    m = len(edges)

    print("Building Hodge harmonic basis...")
    hodge = compute_full_hodge_eigenbasis(n, adj, edges, simplices)
    V_harm = hodge["harmonic"]  # m x 81

    print("Enumerating PSp(4,3) group elements...")
    group = build_psp43_group(vertices, edges)
    print(f"|group| = {len(group)}")

    candidates = []
    checked = 0
    total = len(group)
    for cur_v, (ep, es) in group.items():
        checked += 1
        if checked % 2000 == 0:
            print(f"Checked {checked}/{total}...")

        R = restricted_action_on_subspace(V_harm, ep, es)
        ok, info, eigs = is_good_z3_candidate(R)
        if ok:
            candidates.append(
                {
                    "vertex_perm": cur_v,
                    "counts": info.get("counts"),
                    "avg_dist": info.get("avg_dist"),
                    "R3_norm": float(info.get("R3_norm", float("nan"))),
                }
            )

    ts = int(time.time())
    out_path = Path.cwd() / "checks" / f"PART_CVII_z3_candidates_{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    dump_json({"checked": checked, "candidates": candidates}, out_path, indent=2)

    print(f"Checked {checked} group elements; found {len(candidates)} candidates")
    print(f"Wrote: {out_path}")
    print(f"Elapsed: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
