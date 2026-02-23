#!/usr/bin/env python3
"""Estimate the CKM quark mixing matrix from the 27-dim H1 Yukawa Gram matrices.

The three Gram matrices computed by ``tools/cycle_space_decompose.py``
represent the intersection forms on the three 27-dimensional Sp(4,3)-invariant
subspaces of H_1(W(3,3)).  In a phenomenological interpretation they are
proportional to Yukawa coupling matrices for the three fermion sectors.  If we
interpret two of the matrices as the up- and down-type quark Yukawas, then
their mass-eigenvector bases will in general be misaligned.  The overlap
between the first three principal eigenvectors of each matrix gives a rough
3x3 mixing matrix that can be compared with the experimental CKM matrix.

Usage::

    python scripts/ckm_from_grams.py

The script prints both the raw 27x27 eigen-decomposition information and the
3x3 overlap matrix, and writes ``data/ckm_from_grams.json`` with the results.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# ensure repository root on sys.path so MASS_PREDICTIONS etc can be imported
import os
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)

# experimental CKM magnitudes (PDG 2024 default)
V_CKM_exp = np.array([
    [0.97373, 0.2243, 0.00382],
    [0.2210, 0.987, 0.0410],
    [0.0080, 0.0388, 1.013],
])


def fetch_experimental_ckm_from_wikipedia() -> np.ndarray | None:
    """Attempt to pull the CKM magnitude table from Wikipedia.

    Returns a 3x3 numpy array if successful, otherwise ``None``.
    """
    try:
        import urllib.request, re
        url = (
            "https://en.wikipedia.org/wiki/Cabibbo%E2%80%93Kobayashi%E2%80%93Maskawa_matrix"
        )
        html = urllib.request.urlopen(url, timeout=10).read().decode("utf-8")
        # look for pattern like |V_{ud}| = 0.97373 in the page text
        nums = re.findall(r"V_[uc,t][dsb]?\|?\s*=\s*([0]\.[0-9]+)", html)
        if len(nums) >= 9:
            vals = list(map(float, nums[:9]))
            return np.array(vals).reshape((3, 3))
    except Exception:
        pass
    return None

# try to update values live
from scripts.experimental_data import fetch_ckm_from_wikipedia
live = fetch_ckm_from_wikipedia()
if live is not None:
    print("Fetched live CKM magnitudes from Wikipedia, updating values.")
    V_CKM_exp = live

labels_up = ["u", "c", "t"]
labels_down = ["d", "s", "b"]


def load_gram_list(path: Path | str = "data/h1_subspaces.json") -> list[np.ndarray]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Gram data file {path} not found")
    data = json.load(open(path))
    return [np.array(G, dtype=float) for G in data.get("gram_matrices", [])]


def principal_ratios(G: np.ndarray) -> tuple[np.ndarray, float]:
    """Return sorted eigenvalues and ratio of largest to smallest sqrt eigen.
    """
    vals = np.linalg.eigvalsh(G)
    vals.sort()
    sqrt_vals = np.sqrt(vals)
    ratio = sqrt_vals[-1] / sqrt_vals[0]
    return sqrt_vals, ratio


def compute_ckm(G_up: np.ndarray, G_down: np.ndarray, k: int = 3) -> np.ndarray:
    # eigen-decompose
    vals_u, vecs_u = np.linalg.eigh(G_up)
    vals_d, vecs_d = np.linalg.eigh(G_down)
    idx_u = np.argsort(vals_u)[::-1]
    idx_d = np.argsort(vals_d)[::-1]
    basis_u = vecs_u[:, idx_u[:k]]
    basis_d = vecs_d[:, idx_d[:k]]
    # overlap absolute value
    overlap = np.abs(basis_u.T @ basis_d)
    # normalize rows to unit sum
    overlap = overlap / overlap.sum(axis=1, keepdims=True)
    return overlap


def main():
    grams = load_gram_list()
    if len(grams) < 2:
        print("need at least two Gram matrices to compute CKM")
        sys.exit(1)

    # we choose the two with largest principal ratio as up/down candidates
    ratios = [principal_ratios(G)[1] for G in grams]
    order = np.argsort(ratios)[::-1]
    up_idx, down_idx = order[:2]
    print(f"choosing subspace {up_idx} as up-type, {down_idx} as down-type (ratios {ratios})")

    CKM = compute_ckm(grams[up_idx], grams[down_idx])
    print("\n3x3 overlap matrix (unnormalized to experimental CKM):")
    print(CKM)
    print("\nexperimental magnitudes:")
    print(V_CKM_exp)

    # save results
    out = {
        "up_index": int(up_idx),
        "down_index": int(down_idx),
        "overlap_matrix": CKM.tolist(),
        "experimental": V_CKM_exp.tolist(),
    }
    Path("data").mkdir(exist_ok=True)
    json.dump(out, open("data/ckm_from_grams.json", "w"), indent=2)
    print("\nResults saved to data/ckm_from_grams.json")


if __name__ == "__main__":
    main()
