#!/usr/bin/env python3
"""Construct a symmetric 57x57 matrix with Perkel-like spectrum and save eigendata.

This is a spectral surrogate (not the true combinatorial Perkel adjacency).
It produces a symmetric real matrix A = Q D Q^T with eigenvalues matching the
Perkel nontrivial spectrum multiplicities: 6 (1), φ² (18), 1/φ² (18), -3 (20).
"""
from __future__ import annotations

import math
from pathlib import Path
import numpy as np
import json
import matplotlib.pyplot as plt


def perkel_spectral_matrix(seed: int = 42):
    rng = np.random.default_rng(seed)
    n = 57
    # eigenvalues
    q = 3
    phi = (1 + math.sqrt(5)) / 2
    phi2 = phi ** 2
    inv_phi2 = 1.0 / phi2

    vals = [6.0] + [phi2] * 18 + [inv_phi2] * 18 + [-3.0] * 20
    assert len(vals) == n

    # random orthogonal matrix via QR
    X = rng.normal(size=(n, n))
    Q, _ = np.linalg.qr(X)
    D = np.diag(vals)
    A = Q @ D @ Q.T
    # Symmetrize to avoid numerical drift
    A = (A + A.T) / 2
    return A, np.array(vals)


def main():
    out_dir = Path("checks")
    out_dir.mkdir(exist_ok=True)
    A, vals = perkel_spectral_matrix()

    # eigendecomposition (sanity)
    w, V = np.linalg.eigh(A)
    idx = np.argsort(-np.abs(w))
    w_sorted = w[idx]

    metadata = {
        "constructed": True,
        "note": "Spectral surrogate with Perkel eigenvalue multiplicities (not true adjacency)",
        "requested_multiplicities": {"6": 1, "phi2": 18, "inv_phi2": 18, "-3": 20},
        "eigenvalues_sorted_sample": w_sorted[:10].tolist(),
    }

    np.savez(out_dir / "perkel_spectral_surrogate.npz", A=A, eigenvalues=w, eigenvectors=V)
    with open(out_dir / "perkel_spectral_surrogate_meta.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Plot eigenvalue histogram
    plt.figure(figsize=(6, 3))
    plt.hist(w, bins=40)
    plt.title("Surrogate Perkel eigenvalue histogram")
    plt.tight_layout()
    plt.savefig(out_dir / "perkel_eigen_hist.png")
    print(f"Wrote surrogate spectral data to {out_dir}")


if __name__ == "__main__":
    main()
