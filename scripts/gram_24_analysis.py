#!/usr/bin/env python3
"""Compute Gram matrix and eigenvalue ratios for the 24-dimensional eigenspace.

This script reads the basis vectors stored in `data/24_basis.npz` (produced by
`scripts/dump_24_vectors.py`) and calculates the Gram matrix G = B^T B where
columns of B are the basis vectors in H1 coordinates.  We then diagonalize G
and report the eigenvalue spectrum and the max/min ratio, analogous to the
Yukawa-analysis routine used for 27-dimensional subspaces.
"""
from __future__ import annotations

import numpy as np
import sys
import os

path = "data/24_basis.npz"
if not os.path.isfile(path):
    print(f"basis file {path} not found; run scripts/dump_24_vectors.py first")
    sys.exit(1)

basis = np.load(path)["arr_0"]  # shape (81,24)
print(f"loaded basis matrix shape {basis.shape}")

# compute Gram = B^T B
G = basis.T @ basis
print(f"Gram matrix shape {G.shape}")

eigs = np.linalg.eigvalsh(G)
eigs.sort()
sqrt_eigs = np.sqrt(np.abs(eigs))
ratio = sqrt_eigs[-1] / sqrt_eigs[0] if sqrt_eigs[0] > 0 else float('inf')

print("Eigenvalues of Gram (sorted):")
print(eigs)
print(f"sqrt eigenvalues, ratio max/min = {ratio:.6f}")

# we also output the orbit sizes from the earlier inspection if available
try:
    from scripts.inspect_aut_24 import H1_basis  # may not import
except Exception:
    H1_basis = None

if H1_basis is not None:
    # compute action matrix for the automorphism 1410 as in dump script
    from scripts.dump_24_vectors import action_matrix_on_H1
    n, verts, adj, edges = __import__('e8_embedding_group_theoretic').build_w33()
    autos = __import__('tools.cycle_space_analysis').compute_automorphisms(n, adj, limit=1411)
    perm = autos[1410]
    M_sym = action_matrix_on_H1(perm, H1_basis, edges)
    mats = np.array(M_sym.tolist(), dtype=int)
    # compute column nonzero counts to show orbit membership
    print('H1 action column nonzero counts (should equal orbit sizes):', np.count_nonzero(mats, axis=0))

print("Done.")
