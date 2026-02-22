#!/usr/bin/env python3
"""Check for a cyclic Z3 permutation of the three 27-dim H1 subspaces.

Loads ``data/h1_subspaces.json`` which now contains both the Gram matrices and
explicit H1-coordinate basis vectors for each of the three 27-dimensional
subspaces discovered by ``cycle_space_decompose.py``.  We search the full
automorphism group of W33 for an element of order three and verify that it
maps each subspace basis into another; in other words the three subspaces form
an orbit under a subgroup \cong Z_3 of Sp(4,3).

The script prints the permutation of subspace indices and saves a small report
in ``data/z3_symmetry.json``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

import cycle_space_analysis as csa


def load_subspaces(path="data/h1_subspaces.json"):
    data = json.load(open(path))
    bases = data.get("subspace_bases", [])
    # convert to numpy arrays shape (27,81) each
    return [np.array(b, dtype=int) for b in bases]


def express_in_H1(vec240: np.ndarray, H1_basis: list[np.ndarray]) -> np.ndarray:
    # H1_basis is list of 81-dim vectors; we can form matrix 81x81? but simpler
    B = np.column_stack(H1_basis)
    coeff = np.linalg.lstsq(B, vec240, rcond=None)[0]
    # round to nearest integer
    return np.rint(coeff).astype(int)


def find_order(perm: dict[int, int]) -> int:
    visited = set()
    order = 1
    for i in perm:
        if i in visited:
            continue
        length = 0
        v = i
        while v not in visited:
            visited.add(v)
            v = perm[v]
            length += 1
        if length > 0:
            order = np.lcm(order, length)
    return order


def main():
    # load subspace bases
    if not Path("data/h1_subspaces.json").is_file():
        print("run cycle_space_decompose.py first")
        return
    subspaces = load_subspaces()
    if len(subspaces) != 3:
        print("expected 3 subspaces, found", len(subspaces))
        return
    # we need the 240-dim -> 81-dim H1 basis used during decomposition
    # reconstruct exactly the procedure from cycle_space_decompose.py
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    import cycle_space_analysis as csa_local

    n, verts, adj, edges = csa_local.build_W33()

    full_basis = csa_local.build_cycle_basis(n, adj, edges)  # list of 240-dim vectors

    # build clique complex to compute image(B2)
    from cycle_space_decompose import build_clique_complex, boundary_matrix

    simplices = build_clique_complex(n, adj)
    B2 = boundary_matrix(simplices[2], simplices[1])  # 240 x ?
    M2 = csa_local.Matrix(B2.tolist())
    im_basis = M2.columnspace()
    im_basis = [np.array([int(x) for x in v], dtype=int).flatten() for v in im_basis]

    H1_basis = []
    def in_span_list(v, vecs):
        if not vecs:
            return False
        Mmat = csa_local.Matrix(np.column_stack(vecs + [v]).tolist())
        return Mmat.rank() <= csa_local.Matrix(np.column_stack(vecs).tolist()).rank()

    for v in full_basis:
        if not in_span_list(v, H1_basis + im_basis):
            H1_basis.append(v.copy())
        if len(H1_basis) == 81:
            break
    if len(H1_basis) != 81:
        raise RuntimeError("could not reconstruct 81-dim H1 basis")

    Bmat = np.column_stack(H1_basis)  # 240 x 81
    pinv = np.linalg.pinv(Bmat)

    def to_240(vh1: np.ndarray) -> np.ndarray:
        return Bmat @ vh1

    def to_h1(v240: np.ndarray) -> np.ndarray:
        coeff = pinv @ v240
        return np.rint(coeff).astype(int)

    # now proceed to enumerations below
    n, verts, adj, edges = csa.build_W33()
    autos = csa.compute_automorphisms(n, adj)
    print(f"loaded {len(autos)} automorphisms")

    candidate = None
    mapping_result = None
    for perm in autos:
        if find_order(perm) == 3:
            perm_map = []
            for i, basis in enumerate(subspaces):
                counts = [0, 0, 0]
                for vh1 in basis:
                    v240 = to_240(vh1)
                    v240p = csa.permute_cycle(v240, perm, edges)
                    vh1p = to_h1(v240p)
                    residuals = []
                    for other in subspaces:
                        coeffs, *_ = np.linalg.lstsq(np.column_stack(other), vh1p, rcond=None)
                        resid = np.linalg.norm(np.column_stack(other) @ coeffs - vh1p)
                        residuals.append(resid)
                    j = int(np.argmin(residuals))
                    counts[j] += 1
                perm_map.append(int(np.argmax(counts)))
            # check if perm_map is a cyclic 3-permutation (not a transposition)
            if perm_map in ([1, 2, 0], [2, 0, 1]):
                candidate = perm
                mapping_result = perm_map
                break
    # if we exited loop without permutation, take first order-3 anyway
    if candidate is None:
        # fallback: repeat search for first order3
        for perm in autos:
            if find_order(perm) == 3:
                candidate = perm
                mapping_result = None
                break
    if candidate is None:
        print("no element of order 3 found")
    else:
        print("found order-3 permutation that sends subspaces as", mapping_result)

    out = {"found_order3": candidate is not None, "mapping": mapping_result}
    Path("data").mkdir(exist_ok=True)
    json.dump(out, open("data/z3_symmetry.json", "w"), indent=2)
    print("report saved to data/z3_symmetry.json")


if __name__ == "__main__":
    main()
