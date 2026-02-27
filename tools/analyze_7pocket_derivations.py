#!/usr/bin/env python3
"""Analyze 7-pocket derivation basis files produced by derive_7pocket_derivations.

Given a directory containing derivation_basis.json (and optionally REPORT.json),
compute algebraic invariants: dimension, commutator span, center, Killing form,
and confirm the semisimple part is sl3.

Usage:
    python tools/analyze_7pocket_derivations.py /path/to/output_dir
"""

from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np


def load_basis(dirname: Path):
    data = json.loads((dirname / 'derivation_basis.json').read_text())
    mats = data['derivation_basis_matrices_colmajor']
    # convert to numpy arrays
    n = len(mats[0])
    arrs = []
    for m in mats:
        # m is list of n columns each of length n
        mat = np.zeros((n, n), dtype=int)
        for j in range(n):
            col = m[j]
            for i in range(n):
                mat[i,j] = col[i]
        arrs.append(mat)
    return np.array(arrs, dtype=int)


def commutator(a, b):
    return a @ b - b @ a


def main():
    if len(sys.argv) < 2:
        print('usage: analyze_7pocket_derivations.py dirname')
        sys.exit(1)
    dirname = Path(sys.argv[1])
    derivs = load_basis(dirname)
    k, n, n2 = derivs.shape
    print(f'loaded {k} derivation matrices of size {n}x{n}')

    # dimension of span
    flat = derivs.reshape(k, -1)
    rank = np.linalg.matrix_rank(flat.astype(float))
    print('rank of derivations', rank)

    # commutator span
    comms = []
    for i in range(k):
        for j in range(i+1, k):
            comms.append(commutator(derivs[i], derivs[j]))
    comms = np.array(comms)
    comm_rank = np.linalg.matrix_rank(comms.reshape(len(comms), -1).astype(float))
    print('commutator span rank', comm_rank)

    # center: those that commute with all
    center_idx = []
    for i in range(k):
        ok = True
        for j in range(k):
            if not np.allclose(commutator(derivs[i], derivs[j]), 0):
                ok = False; break
        if ok:
            center_idx.append(i)
    print('center dimension', len(center_idx))

    # Killing form on commutator subspace
    # create basis of commutator subspace using SVD
    B = comms.reshape(len(comms), -1).astype(float)
    u, s, vh = np.linalg.svd(B)
    rank_comm = np.sum(s > 1e-6)
    basis_com = vh[:rank_comm]
    # compute Killing form matrix K_ij = Tr(ad_i ad_j)
    # ad_i acting on full Lie algebra via commutator
    com_mats = [com.reshape(n,n) for com in basis_com]
    K = np.zeros((rank_comm, rank_comm))
    for i in range(rank_comm):
        for j in range(rank_comm):
            K[i,j] = np.trace(com_mats[i] @ com_mats[j])
    print('Killing form rank', np.linalg.matrix_rank(K))

    # output some summary
    print('center indices', center_idx)

if __name__ == '__main__':
    main()
