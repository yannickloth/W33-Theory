"""Search for an Sp(4,3) automorphism of W33 whose H1 action has a 24-dim eigenspace.

This could explain the mysterious appearance of 24 (and hence 72=3*24) in RG
running: if the geometry admits a natural 24-dimensional invariant subspace
in the 81-dimensional H1 representation, that subspace could define a
GUT-scale top-bottom splitting.
"""
from __future__ import annotations

import sys
from collections import defaultdict
import numpy as np
from sympy import Matrix

# add scripts dir to import path
sys.path.append('.')
from e8_embedding_group_theoretic import build_w33
from tools.cycle_space_analysis import (
    build_cycle_basis,
)
from tools.cycle_space_decompose import (
    build_clique_complex,
    boundary_matrix,
    permute_cycle,
    compute_automorphisms,
)


def construct_H1_basis(n, adj, edges):
    # build full cycle basis (240x201) then extract 81 independent mod im(B2)
    full_basis = build_cycle_basis(n, adj, edges)
    simplices = build_clique_complex(n, adj)
    B2 = boundary_matrix(simplices[2], simplices[1])
    # compute image basis of B2 via sympy
    M2 = Matrix(B2.tolist())
    im_basis_sym = M2.columnspace()
    im_basis = [np.array([int(x) for x in v], dtype=int).flatten() for v in im_basis_sym]

    H1_basis = []
    def in_span(v, vecs):
        if not vecs:
            return False
        M = Matrix(np.column_stack(vecs + [v]))
        return M.rank() <= Matrix(np.column_stack(vecs)).rank()

    for v in full_basis:
        if not in_span(v, H1_basis + im_basis):
            H1_basis.append(v.copy())
        if len(H1_basis) == 81:
            break
    if len(H1_basis) != 81:
        raise RuntimeError(f"expected 81 H1 vectors, got {len(H1_basis)}")
    return H1_basis


def action_matrix_on_H1(perm, basis, edges):
    dim = len(basis)
    Bmat = np.column_stack(basis)  # 240x81
    pinv = np.linalg.pinv(Bmat)
    M = Matrix.zeros(dim, dim)
    for i, b in enumerate(basis):
        b_permuted = permute_cycle(b, perm, edges)
        coeffs = pinv @ b_permuted
        coeffs = np.rint(coeffs).astype(int)
        for j, c in enumerate(coeffs):
            M[j, i] = c
    return M


import argparse

def main():
    parser = argparse.ArgumentParser(description='Search for 24-dim eigenspace in automorphisms')
    parser.add_argument('--limit', type=int, default=None,
                        help='only examine first N automorphisms (default all)')
    args = parser.parse_args()

    n, verts, adj, edges = build_w33()
    print(f"building H1 basis for n={n}")
    H1_basis = construct_H1_basis(n, adj, edges)
    # cache automorphisms to avoid repeated expensive enumeration
    import os, pickle
    autos_cache = 'data/automorphisms.pkl'
    if os.path.exists(autos_cache):
        print('loading cached automorphisms')
        with open(autos_cache, 'rb') as f:
            autos = pickle.load(f)
    else:
        autos = compute_automorphisms(n, adj)
        os.makedirs('data', exist_ok=True)
        with open(autos_cache, 'wb') as f:
            pickle.dump(autos, f)
    print(f"loaded {len(autos)} automorphisms (cached={os.path.exists(autos_cache)})")

    from collections import Counter
    found = []
    total = len(autos) if args.limit is None else min(len(autos), args.limit)
    print(f"searching up to {total} automorphisms")
    for idx, perm in enumerate(autos[:total]):
        if idx and idx % 1000 == 0:
            print(f"checked {idx} automorphisms...")
        M = action_matrix_on_H1(perm, H1_basis, edges)
        # quick numeric eigenvalue test
        Mnum = np.array(M.tolist(), dtype=float)
        eigvals, _ = np.linalg.eig(Mnum)
        rounded = [round(v.real, 6) for v in eigvals]
        cnt = Counter(rounded)
        if any(c == 24 for c in cnt.values()):
            # compute symbolic eigenvectors for exact basis
            evlist = M.eigenvects()
            for val, mult, space in evlist:
                if int(mult) == 24:
                    print(f"automorphism {idx} has eigenspace size 24 for eigenvalue {val}")
                    np.set_printoptions(threshold=20, edgeitems=3)
                    print("sample invariant vectors (H1 coords):")
                    for v in space[:3]:
                        print(np.array(v, dtype=int).flatten())
                    found.append((idx, val))
                    break
        if found:
            break
    if not found:
        print("no 24-dimensional eigenspace found among automorphisms")
    else:
        print("candidates:", found)

if __name__ == '__main__':
    main()
