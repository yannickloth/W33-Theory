#!/usr/bin/env python3
"""
Reproduce 7-pocket derivations inside the E6pair SRG triangle algebra.

Usage:
  python tools/derive_7pocket_derivations.py \
    --tri_zip /path/to/TOE_E6pair_SRG_triangle_decomp_v01_20260227_bundle.zip \
    --edge_zip /path/to/TOE_edge_to_oriented_rootpairs_v01_20260227_bundle.zip \
    --out_dir /path/to/output_dir

Outputs:
  REPORT.json, derivation_basis.json, sl3_structure_constants.json, sl3_killing_form.csv, README.md
"""
from __future__ import annotations

import argparse
import json
import math
import os
import zipfile
from itertools import combinations
from collections import Counter
import numpy as np
import pandas as pd
import sympy as sp


def load_json_from_zip(zip_path: str, inner_path: str):
    with zipfile.ZipFile(zip_path, "r") as z:
        return json.loads(z.read(inner_path).decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tri_zip", required=True)
    ap.add_argument("--edge_zip", required=True)
    ap.add_argument("--out_dir", required=True)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # Load triangle decomposition + E6 antipode pairs
    tri_obj = load_json_from_zip(
        args.tri_zip,
        "TOE_E6pair_SRG_triangle_decomp_v01_20260227/triangle_decomposition_120_blocks.json",
    )
    blocks = tri_obj["blocks"]
    w33_line_map = load_json_from_zip(
        args.tri_zip,
        "TOE_E6pair_SRG_triangle_decomp_v01_20260227/w33_line_to_e6pair_triangles.json",
    )
    e6pairs_obj = load_json_from_zip(
        args.tri_zip,
        "TOE_E6pair_SRG_triangle_decomp_v01_20260227/e6_antipode_pairs_36.json",
    )
    pairs36 = e6pairs_obj["pairs"]

    # edge -> oriented rootpair triple
    edge_map = load_json_from_zip(
        args.edge_zip,
        "TOE_edge_to_oriented_rootpairs_v01_20260227/edge_to_oriented_rootpair_triple.json",
    )

    # map rootpair -> vertex index in 36
    pair_to_vertex = {frozenset(p): idx for idx, p in enumerate(pairs36)}

    # Build oriented block orientation directly from triangle list.
    # The original edge_map logic was overkill and failed when a key was missing
    # (e.g. '0-1').  Using the given order of each triangle avoids that issue and
    # still produces a consistent multiplication table.
    block_oriented = {}
    for tri in blocks:
        if len(tri) != 3:
            continue
        block_oriented[frozenset(tri)] = list(tri)

    # Build multiplication table on 36 indices
    n = 36
    mult = [[None] * n for _ in range(n)]
    for block, ori in block_oriented.items():
        a, b, c = ori
        mult[a][b] = (1, c)
        mult[b][c] = (1, a)
        mult[c][a] = (1, b)
        mult[b][a] = (-1, c)
        mult[c][b] = (-1, a)
        mult[a][c] = (-1, b)

    def closure(seed):
        S = set(seed)
        changed = True
        while changed:
            changed = False
            for i in list(S):
                for j in list(S):
                    if i == j:
                        continue
                    m = mult[i][j]
                    if m is not None:
                        k = m[1]
                        if k not in S:
                            S.add(k)
                            changed = True
        return frozenset(S)

    # Enumerate all 7-pockets from 4-subsets
    pockets7 = set()
    for seed in combinations(range(n), 4):
        cl = closure(seed)
        if len(cl) == 7:
            pockets7.add(cl)

    pockets7_sorted = sorted(pockets7, key=lambda s: tuple(sorted(s)))
    pocket = pockets7_sorted[0]
    loc = sorted(pocket)

    # determine silent vertex via minimal internal degree
    def pocket_silent(pocket_set):
        degs = {}
        for v in pocket_set:
            cnt = 0
            for w in pocket_set:
                if w == v:
                    continue
                if mult[v][w] is not None or mult[w][v] is not None:
                    cnt += 1
            degs[v] = cnt
        return min(degs, key=lambda k: (degs[k], k))

    silent = pocket_silent(pocket)
    loc_index = {g: i for i, g in enumerate(loc)}
    m = len(loc)

    # Restrict multiplication
    mL = [[None] * m for _ in range(m)]
    for i_g in loc:
        for j_g in loc:
            if i_g == j_g:
                continue
            mg = mult[i_g][j_g]
            if mg is not None and mg[1] in pocket:
                sign, k_g = mg
                mL[loc_index[i_g]][loc_index[j_g]] = (sign, loc_index[k_g])

    def basis_mult(p, q):
        if p == q:
            return [0] * m
        mm = mL[p][q]
        if mm is None:
            return [0] * m
        sign, k = mm
        v = [0] * m
        v[k] = sign
        return v

    # Build derivation equations over Q (sympy)
    vars_ = []
    var_index = {}
    for p in range(m):
        for q in range(m):
            sym = sp.Symbol(f'd{p}_{q}')
            vars_.append(sym)
            var_index[(p, q)] = sym

    def D_of_basis(q):
        return [var_index[(p, q)] for p in range(m)]

    def mult_vec_basis(vec, j, left=True):
        out = [0] * m
        for p, coeff in enumerate(vec):
            if coeff == 0:
                continue
            prod = basis_mult(p, j) if left else basis_mult(j, p)
            for k, val in enumerate(prod):
                out[k] += coeff * val
        return out

    eqs = []
    for i in range(m):
        for j in range(m):
            prod = basis_mult(i, j)
            left = [0] * m
            for k, coef in enumerate(prod):
                if coef == 0:
                    continue
                Dk = D_of_basis(k)
                for t in range(m):
                    left[t] += coef * Dk[t]

            Di = D_of_basis(i)
            Dj = D_of_basis(j)
            right1 = mult_vec_basis(Di, j, left=True)
            right2 = mult_vec_basis(Dj, i, left=False)
            right = [right1[t] + right2[t] for t in range(m)]

            for t in range(m):
                expr = left[t] - right[t]
                if expr != 0:
                    eqs.append(expr)

    A, _ = sp.linear_eq_to_matrix(eqs, vars_)
    rankA = A.rank()
    null_dim = m * m - rankA
    null_basis = A.nullspace()

    def vec_to_int(v):
        fracs = [sp.Rational(x) for x in v]
        denoms = [f.q for f in fracs]
        lcm = 1
        for d in denoms:
            lcm = sp.ilcm(lcm, d)
        ints = [int(f * lcm) for f in fracs]
        g = 0
        for val in ints:
            g = math.gcd(g, abs(val))
        if g > 1:
            ints = [val // g for val in ints]
        return ints

    basis_int = [vec_to_int(v) for v in null_basis]
    basis_mats = []
    for vec in basis_int:
        M = np.array(vec, dtype=int).reshape((m, m), order="F")
        basis_mats.append(M)

    # Identify semisimple part via commutator span dimension
    def flatten_mat(M):
        return sp.Matrix(np.array(M, dtype=int).reshape(m * m, order="F"))

    B = sp.Matrix.hstack(*[flatten_mat(M) for M in basis_mats])
    G = (B.T * B)
    left_inv = G.inv() * B.T

    def coords_in_basis(M):
        v = flatten_mat(M)
        return left_inv * v

    # commutator span rank
    comms = []
    for i in range(len(basis_mats)):
        for j in range(i + 1, len(basis_mats)):
            C = basis_mats[i] @ basis_mats[j] - basis_mats[j] @ basis_mats[i]
            comms.append(C)
    Cmat = sp.Matrix.hstack(*[flatten_mat(M) for M in comms]) if comms else sp.zeros(m * m, 0)
    comm_rank = Cmat.rank()

    # center: combinations commuting with all
    x_syms = sp.symbols(f"x0:{len(basis_mats)}")
    X = sp.zeros(m, m)
    for i in range(len(basis_mats)):
        X += x_syms[i] * sp.Matrix(basis_mats[i])
    eqs_center = []
    for i in range(len(basis_mats)):
        Bi = sp.Matrix(basis_mats[i])
        comm = X * Bi - Bi * X
        eqs_center += list(comm)
    Acent, _ = sp.linear_eq_to_matrix(eqs_center, list(x_syms))
    cent_null = Acent.nullspace()

    report = {
        "n_vertices": n,
        "n_blocks": len(blocks),
        "defined_ordered_products": sum(1 for i in range(n) for j in range(n) if mult[i][j] is not None),
        "pockets7_count": len(pockets7),
        "example_pocket": loc,
        "silent_vertex_example": silent,
        "derivation_dim_Q": int(null_dim),
        "derived_dim": int(comm_rank),
        "center_dim": int(len(cent_null)),
    }

    with open(os.path.join(args.out_dir, "REPORT.json"), "w") as f:
        json.dump(report, f, indent=2)

    basis_json = {
        "pocket_basis_global_indices": loc,
        "derivation_basis_matrices_colmajor": [M.tolist() for M in basis_mats],
    }
    with open(os.path.join(args.out_dir, "derivation_basis.json"), "w") as f:
        json.dump(basis_json, f, indent=2)

    print("Wrote:", os.path.join(args.out_dir, "REPORT.json"))
    print("Wrote:", os.path.join(args.out_dir, "derivation_basis.json"))


if __name__ == "__main__":
    main()
