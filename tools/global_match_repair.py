#!/usr/bin/env python3
"""
Global matching repair for bundles: assign output_root vectors to root indices
via a global linear-assignment (Hungarian) solver to avoid local nearest-neighbor
mismatches.

Usage:
  py -3 tools/global_match_repair.py --couplings <coupling.json> --out <fixed_couplings.json>

Outputs:
  - writes `--out` coupling JSON with `output_root_index` filled where missing
  - prints mean rel before/after if passed through `toe_backbone_coset_coupling_map.py`
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Tuple

import numpy as np

try:
    from scipy.optimize import linear_sum_assignment
except Exception:  # pragma: no cover - fallback
    linear_sum_assignment = None


def measure_mean_rel(out_json_path: Path):
    j = json.loads(out_json_path.read_text(encoding="utf-8"))
    vals = [
        c.get("backbone_coset", {}).get("rel_resid")
        for c in j.get("couplings", [])
        if c.get("backbone_coset")
    ]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)


def collect_unique_output_vectors(couplings: List[dict]) -> Tuple[List[Tuple[float, ...]], List[int]]:
    uniq = []
    idx_map = []  # maps coupling index -> uniq index or -1
    for c in couplings:
        ov = c.get("output_root")
        if ov is None:
            idx_map.append(-1)
            continue
        tup = tuple(float(x) for x in ov)
        if tup in uniq:
            idx_map.append(uniq.index(tup))
        else:
            idx_map.append(len(uniq))
            uniq.append(tup)
    return uniq, idx_map


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--couplings", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--root-npy", type=Path, default=Path("artifacts/toe_root_operator_dictionary.npy"))
    args = p.parse_args()

    couplings = json.loads(args.couplings.read_text(encoding="utf-8"))
    cs = couplings.get("couplings", [])

    uniq, idx_map = collect_unique_output_vectors(cs)
    if not uniq:
        print("No output_root vectors found; nothing to do")
        args.out.write_text(json.dumps(couplings, indent=2), encoding="utf-8")
        return

    # Load root weights
    if not args.root_npy.exists():
        raise FileNotFoundError(args.root_npy)
    rd = np.load(args.root_npy, allow_pickle=True).item()
    weights = rd.get("weights")
    # Use real part for matching
    weights_re = np.real(weights)

    X = np.array(uniq, dtype=float)  # (m, k)
    if X.ndim == 1:
        X = X.reshape(1, -1)

    # Build cost matrix: squared Euclidean distances between X and weights_re
    m = X.shape[0]
    n = weights_re.shape[0]
    C = np.zeros((m, n), dtype=float)
    for i in range(m):
        dif = weights_re - X[i:i+1, :]
        C[i, :] = np.sum(dif.real ** 2, axis=1)

    if linear_sum_assignment is None:
        print("Warning: scipy not available; performing greedy assignment")
        # Greedy: assign each row to nearest available column
        assigned = [-1] * m
        used = set()
        for i in range(m):
            order = list(np.argsort(C[i, :]))
            for j in order:
                if j not in used:
                    assigned[i] = j
                    used.add(j)
                    break
    else:
        # Use Hungarian algorithm (works with rectangular m x n)
        row_ind, col_ind = linear_sum_assignment(C)
        assigned = [-1] * m
        for r, c in zip(row_ind, col_ind):
            assigned[r] = int(c)

    # Apply assignments back to couplings
    changed = 0
    for idx, c in enumerate(cs):
        umap = idx_map[idx]
        if umap == -1:
            continue
        if c.get("output_root_index") is None and assigned[umap] != -1:
            c["output_root_index"] = int(assigned[umap])
            c["output_root_match_dist"] = float(C[umap, assigned[umap]])
            changed += 1

    json_out = args.out
    json_out.write_text(json.dumps(couplings, indent=2), encoding="utf-8")
    print(f"Wrote fixed couplings to {json_out} (assigned {changed} output indices)")


if __name__ == "__main__":
    main()
