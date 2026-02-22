#!/usr/bin/env python3
"""Compute Dirac operator on 0- and 1-forms for W33 and analyze spectrum.

D_big = [[0, D],[D.T, 0]] where D is the oriented vertex-edge incidence (n x m).
D_big^2 = block_diag(L0, L1) where L0 = D D^T and L1 = D^T D + B2 B2^T.

Writes results to checks/PART_CVII_w33_dirac_<ts>.json
"""
from __future__ import annotations

import json

# sibling import pattern
import sys
import time
from pathlib import Path
from pathlib import Path as _Path

import numpy as np

sys.path.insert(0, str(_Path(__file__).parent))

from w33_hodge import compute_hodge_laplacians, eigen_decomp_sorted, multiplicity_dict


def build_dirac(D: np.ndarray):
    n, m = D.shape
    top = np.hstack([np.zeros((n, n), dtype=float), D])
    bottom = np.hstack([D.T, np.zeros((m, m), dtype=float)])
    return np.vstack([top, bottom])


def analyze_dirac():
    Ls = compute_hodge_laplacians()
    D = Ls["D"]
    L0 = Ls["L0"]
    L1 = Ls["L1"]

    Dir = build_dirac(D)

    # eigen-decomp of Dirac (symmetric)
    w_dir, v_dir = np.linalg.eigh(Dir)
    # sort
    idx = np.argsort(w_dir)
    w_dir = w_dir[idx]
    v_dir = v_dir[:, idx]

    # multiplicities (rounded)
    mult_dir = multiplicity_dict(w_dir)

    # compare sqrt of positive Laplacian eigenvalues
    w0, _ = eigen_decomp_sorted(L0)
    w1, _ = eigen_decomp_sorted(L1)
    # take nonzero parts
    pos_l0 = np.sqrt(np.clip(w0, 0.0, None))
    pos_l1 = np.sqrt(np.clip(w1, 0.0, None))

    # Count zeros in Dirac
    zero_mult = int(np.sum(np.isclose(w_dir, 0.0, atol=1e-8)))

    out = {
        "timestamp": int(time.time()),
        "n_vertices": L0.shape[0],
        "n_edges": L1.shape[0],
        "dirac_zero_multiplicity": zero_mult,
        "dirac_eigen_multiplicity": mult_dir,
        "sqrt_vertex_laplacian_sample": [float(x) for x in pos_l0[:10]],
        "sqrt_edge_laplacian_sample": [float(x) for x in pos_l1[:20]],
    }

    ts = int(time.time())
    out_path = Path.cwd() / "checks" / f"PART_CVII_w33_dirac_{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote dirac results to", out_path)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    analyze_dirac()
