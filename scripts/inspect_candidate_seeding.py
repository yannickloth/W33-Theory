#!/usr/bin/env python3
"""Inspect nearest-root confidence metrics for edges used by seed_from_z3_candidate.

Usage: python scripts/inspect_candidate_seeding.py --candidate committed_artifacts/..json --top 30
"""
from __future__ import annotations

import argparse
import glob
import json
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


def find_latest_candidate():
    files = sorted(
        glob.glob("committed_artifacts/PART_CVII_z3_candidate_*.json"),
        key=lambda p: Path(p).stat().st_mtime,
    )
    return Path(files[-1]) if files else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", help="path to candidate json (default: latest)")
    p.add_argument("--top", type=int, default=30)
    args = p.parse_args()

    cand = Path(args.candidate) if args.candidate else find_latest_candidate()
    if not cand or not cand.exists():
        raise FileNotFoundError("No candidate file found")
    print("Inspecting candidate:", cand)

    X, edges = compute_embedding_matrix()
    A_mat = build_edge_vectors(X, edges)
    roots = generate_scaled_e8_roots()
    roots_arr = np.array(roots, dtype=int)
    roots_unit = roots_arr.astype(float) / np.linalg.norm(
        roots_arr.astype(float), axis=1, keepdims=True
    )

    dists = np.linalg.norm(A_mat[:, None, :] - roots_unit[None, :, :], axis=2)
    nearest = dists.argmin(axis=1)
    nearest_d = dists.min(axis=1)
    # second nearest distances
    sorted_idx = np.argsort(dists, axis=1)
    second_d = dists[np.arange(dists.shape[0]), sorted_idx[:, 1]]

    metrics = []
    for ei in range(dists.shape[0]):
        metrics.append(
            (
                ei,
                int(nearest[ei]),
                float(nearest_d[ei]),
                float(second_d[ei]),
                float(second_d[ei] - nearest_d[ei]),
            )
        )

    metrics.sort(key=lambda t: (t[2], -t[4]))
    print("Top by smallest nearest distance (best match):")
    for t in metrics[: args.top]:
        print(
            f"edge {t[0]:4d}: root {t[1]:3d}, nearest {t[2]:.4f}, second {t[3]:.4f}, gap {t[4]:.4f}"
        )

    print("\nTop by gap (second-nearest - nearest):")
    metrics_gap = sorted(metrics, key=lambda t: -t[4])
    for t in metrics_gap[: args.top]:
        print(
            f"edge {t[0]:4d}: root {t[1]:3d}, nearest {t[2]:.4f}, second {t[3]:.4f}, gap {t[4]:.4f}"
        )


if __name__ == "__main__":
    main()
