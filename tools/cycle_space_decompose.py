"""Decompose the 201-dim cycle-space representation of Sp(4,3).

This script focuses on analyzing a single automorphism of order 3 as a
starting point.  By computing its action matrix on the cycle-space basis we
can inspect eigenvalue multiplicities; finding 27 repeated eigenvalues
provides evidence for 27-dimensional constituents.  The same machinery
could be extended to compute a full block decomposition using two generators.

Usage::

    python tools/cycle_space_decompose.py

"""

from __future__ import annotations

import sys, os
# allow importing other scripts in tools directory
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import json
from itertools import product
from pathlib import Path
from typing import Tuple

import numpy as np
from sympy import Matrix

import cycle_space_analysis as csa
# bring selected functions into namespace
build_W33 = csa.build_W33
build_cycle_basis = csa.build_cycle_basis
compute_automorphisms = csa.compute_automorphisms
permute_cycle = csa.permute_cycle

# local versions of clique-complex and boundary_matrix taken from w33_homology

def build_clique_complex(n: int, adj: list[list[int]]) -> dict:
    adj_set = [set(adj[i]) for i in range(n)]
    simplices = {0: [tuple([v]) for v in range(n)]}
    edges = []
    for i in range(n):
        for j in adj[i]:
            if j > i:
                edges.append((i, j))
    simplices[1] = sorted(edges)
    triangles = []
    for i in range(n):
        for j in adj[i]:
            if j <= i:
                continue
            for k in adj[j]:
                if k <= j:
                    continue
                if k in adj_set[i]:
                    triangles.append((i, j, k))
    simplices[2] = sorted(triangles)
    tetrahedra = []
    for i in range(n):
        for j in adj[i]:
            if j <= i:
                continue
            common_ij = adj_set[i] & adj_set[j]
            for k in common_ij:
                if k <= j:
                    continue
                common_ijk = common_ij & adj_set[k]
                for l in common_ijk:
                    if l <= k:
                        continue
                    tetrahedra.append((i, j, k, l))
    simplices[3] = sorted(tetrahedra)
    pentatopes = []
    for tet in simplices[3]:
        common = adj_set[tet[0]] & adj_set[tet[1]] & adj_set[tet[2]] & adj_set[tet[3]]
        for v in common:
            if v > tet[3]:
                pentatopes.append(tuple(sorted(list(tet) + [v])))
    simplices[4] = sorted(set(pentatopes))
    return simplices


def boundary_matrix(simplices_k: list, simplices_km1: list) -> np.ndarray:
    if not simplices_k or not simplices_km1:
        return np.zeros((len(simplices_km1), len(simplices_k)), dtype=np.int64)
    km1_index = {s: i for i, s in enumerate(simplices_km1)}
    m = len(simplices_km1)
    n = len(simplices_k)
    B = np.zeros((m, n), dtype=np.int64)
    for j, sigma in enumerate(simplices_k):
        k_plus_1 = len(sigma)
        for face_idx in range(k_plus_1):
            face = tuple(sigma[l] for l in range(k_plus_1) if l != face_idx)
            row = km1_index.get(face)
            if row is not None:
                sign = (-1) ** face_idx
                B[row, j] = sign
    return B


def permutation_order(perm: dict[int, int]) -> int:
    visited = set()
    order = 1
    for i in perm:
        if i in visited:
            continue
        # follow cycle
        length = 0
        v = i
        while v not in visited:
            visited.add(v)
            v = perm[v]
            length += 1
        if length > 0:
            order = np.lcm(order, length)
    return order


def find_element_of_order(autos: list[dict[int, int]], target: int) -> dict[int, int] | None:
    for perm in autos:
        if permutation_order(perm) == target:
            return perm
    return None


# we'll later replace express_in_basis with a numpy pseudoinverse
# precompute outside the function for speed

# placeholder; real function assigned in main()

def express_in_basis(vec: np.ndarray, basis: list[np.ndarray]) -> np.ndarray:
    raise RuntimeError("express_in_basis must be replaced by precomputed pinv")


def action_matrix(perm: dict[int, int], basis: list[np.ndarray], edges: list[tuple[int, int]]) -> Matrix:
    """Return sympy matrix of representation of perm on the given basis."""
    dim = len(basis)
    M = Matrix.zeros(dim, dim)
    for i, b in enumerate(basis):
        b_permuted = permute_cycle(b, perm, edges)
        coeffs = express_in_basis(b_permuted, basis)
        for j, c in enumerate(coeffs):
            M[j, i] = c
    return M


def main():
    n, verts, adj, edges = build_W33()
    # full graph-cycle basis (201-dim)
    full_basis = build_cycle_basis(n, adj, edges)

    # compute simplicial boundary matrices so we can isolate H1
    simplices = build_clique_complex(n, adj)
    B1 = boundary_matrix(simplices[1], simplices[0])  # 40x240
    B2 = boundary_matrix(simplices[2], simplices[1])  # 240x? triangles

    # find basis for image(B2) via column space
    M2 = Matrix(B2.tolist())
    im_basis = M2.columnspace()  # list of sympy vectors length = rank(B2)=120
    im_basis = [np.array([int(x) for x in v], dtype=int).flatten() for v in im_basis]

    # select 81 vectors from full_basis that are independent modulo im_basis
    H1_basis = []
    def in_span_list(v, vecs):
        if not vecs:
            return False
        Mmat = Matrix(np.column_stack(vecs + [v]))
        return Mmat.rank() <= Matrix(np.column_stack(vecs)).rank()
    for v in full_basis:
        if not in_span_list(v, H1_basis + im_basis):
            H1_basis.append(v.copy())
        if len(H1_basis) == 81:
            break
    if len(H1_basis) != 81:
        raise RuntimeError(f"expected 81 H1 vectors, got {len(H1_basis)}")
    basis = H1_basis
    print("constructed 81-dim H1 basis")

    autos = compute_automorphisms(n, adj)
    print(f"loaded {len(autos)} automorphisms")

    g = find_element_of_order(autos, 3)
    if g is None:
        raise RuntimeError("no element of order 3 found")
    print("found element of order 3")

    # prepare pseudoinverse for H1 basis
    Bmat = np.column_stack(basis)  # 240x81
    pinv = np.linalg.pinv(Bmat)

    def express_in_basis(vec: np.ndarray, basis_list: list[np.ndarray] = basis) -> np.ndarray:
        coeff = pinv @ vec
        coeff = np.rint(coeff).astype(int)
        return coeff

    # build representation matrix on H1
    dim = len(basis)
    M = Matrix.zeros(dim, dim)
    for i, b in enumerate(basis):
        b_permuted = permute_cycle(b, g, edges)
        coeffs = express_in_basis(b_permuted)
        for j, c in enumerate(coeffs):
            M[j, i] = int(c)
    print("computed action matrix on H1")

    # eigenvalue analysis
    print("computing eigenvalues (numpy) ...")
    Mnum = np.array(M.tolist(), dtype=complex)
    eigs = np.linalg.eigvals(Mnum)
    w1 = 1.0 + 0j
    w2 = np.exp(2j * np.pi / 3)
    w3 = np.exp(4j * np.pi / 3)
    tol = 1e-3
    counts = {w1:0, w2:0, w3:0, 'other':0}
    dists = []
    for lam in eigs:
        # classify by nearest root
        dist1 = abs(lam - w1)
        dist2 = abs(lam - w2)
        dist3 = abs(lam - w3)
        dmin = min(dist1, dist2, dist3)
        dists.append(dmin)
        if dmin < tol:
            if dmin == dist1:
                counts[w1] += 1
            elif dmin == dist2:
                counts[w2] += 1
            else:
                counts[w3] += 1
        else:
            counts['other'] += 1
    print("eigenvalue counts (approx, tol=%.1e):" % tol)
    for k,v in counts.items():
        print(k, v)
    print("max distance to nearest root", max(dists))
    print("histogram of distances (first 10):", sorted(dists)[:10])

    eig1_space = (M - Matrix.eye(dim)).nullspace()
    dim1 = len(eig1_space)
    print(f"dimension of eigenspace(1) = {dim1}")

    # check closures of each fixed vector under full group to see subspace dims
    def to_240(coords: Matrix) -> np.ndarray:
        # convert H1 coord vector to 240-dim edge vector via basis matrix
        c = np.array([int(x) for x in coords], dtype=int)
        return Bmat @ c

    def to_h1(v240: np.ndarray) -> np.ndarray:
        coeff = express_in_basis(v240)
        return coeff

    def closure_H1(vec_h1: np.ndarray) -> list[np.ndarray]:
        # compute linear span of orbit under autos within H1 coordinates
        S: list[np.ndarray] = []
        def in_span(w):
            if not S:
                return False
            Mmat = np.column_stack(S + [w])
            r0 = np.linalg.matrix_rank(Mmat.astype(float))
            r1 = np.linalg.matrix_rank(np.column_stack(S).astype(float))
            return r0 == r1
        if not in_span(vec_h1):
            S.append(vec_h1.copy())
        changed = True
        # expect ~27-dim irreducible pieces; stop when dim >=27
        while changed and len(S) < 27:
            changed = False
            for perm in autos:
                if len(S) >= 27:
                    break
                v240 = to_240(vec_h1)
                v240p = permute_cycle(v240, perm, edges)
                v_h1 = to_h1(v240p)
                if not in_span(v_h1):
                    S.append(v_h1.copy())
                    changed = True
        return S

    print("computing closures of fixed eigenvectors:")
    subspaces = []
    for idx, eig in enumerate(eig1_space):
        v240 = to_240(eig)
        v_h1 = to_h1(v240)
        S = closure_H1(v_h1)
        print(f" fixed vector {idx} closure dim: {len(S)}")
        subspaces.append(S)

    # compute Gram matrices of intersection form on each 27-subspace
    Bfull = np.column_stack(basis)  # 240x81
    gram_matrices = []
    for S in subspaces:
        # S is list of 27 coordinate vectors in H1 basis
        mat = np.column_stack(S)  # 81x27
        # map to 240-dim
        E = Bfull @ mat  # 240x27
        G = (E.T @ E)  # 27x27 integer Gram
        gram_matrices.append(G.tolist())

    Path("data").mkdir(exist_ok=True)
    with open("data/cycle_space_order3_matrix.json", "w") as f:
        json.dump({"matrix": [[int(x) for x in row] for row in M.tolist()]}, f)
    with open("data/h1_subspaces.json", "w") as f:
        json.dump({
            "subspace_dims": [len(S) for S in subspaces],
            "gram_matrices": gram_matrices,
        }, f)
    print("saved action matrix and h1_subspaces data")

    # save matrix for later
    Path("data").mkdir(exist_ok=True)
    with open("data/cycle_space_order3_matrix.json", "w") as f:
        json.dump({"matrix": [[int(x) for x in row] for row in M.tolist()]}, f)
    print("saved action matrix json")

if __name__ == "__main__":
    main()
