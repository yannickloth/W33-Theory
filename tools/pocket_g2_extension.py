#!/usr/bin/env python3
"""Extend the 7-pocket analysis to geometry and g2 axis-shift candidates.

The script performs several related computations:

* enumerate all 7-pockets (same as derive_7pocket_derivations.py)
* identify a "silent" vertex in each pocket (minimal internal degree)
* count pockets by silent vertex and verify 36x15 decomposition
* pair pockets into twins sharing the same active 6-set (270 pairs)

Optional extra work when a full 36-vertex derivation basis is available

* load full derivations basis from JSON (produced by
  compute_full_derivations.py)
* for each silent vertex compute the subspace dimension of derivations
  fixing that vertex and the complementary "axis-shift" dimension (should
  be 6)
* optionally output explicit candidate derivation matrices that move the
  silent vertex (one set per silent index)

Outputs (in cwd):
  pocket_geometry.json          # pockets, silent mapping, twin pairs
  axis_shift_summary.json       # per-silent dims (if basis provided)
  axis_shift_candidates_S.json  # for each silent S with basis, a list of 6 matrices

Usage examples:
    python tools/pocket_g2_extension.py --tri_zip path/to/triangle.zip \
         --edge_zip path/to/edge.zip \
         [--full_basis path/to/full_derivations_basis.json]

"""
from __future__ import annotations
import argparse
import json
import os
import zipfile
from itertools import combinations
from pathlib import Path

import numpy as np
import sympy as sp


# reuse some helper code from derive_7pocket_derivations

def load_json_from_zip(zip_path: str, inner_path: str):
    with zipfile.ZipFile(zip_path, "r") as z:
        return json.loads(z.read(inner_path).decode("utf-8"))


def build_36_mult(tri_zip: str, edge_zip: str):
    tri_obj = load_json_from_zip(
        tri_zip,
        "TOE_E6pair_SRG_triangle_decomp_v01_20260227/triangle_decomposition_120_blocks.json",
    )
    blocks = tri_obj["blocks"]
    # we don't actually need w33_line_map or edge_map here since orientation
    # can be taken directly from the triangle list; this avoids KeyError when the
    # trimmed edge zip lacks some keys.
    e6pairs_obj = load_json_from_zip(
        tri_zip,
        "TOE_E6pair_SRG_triangle_decomp_v01_20260227/e6_antipode_pairs_36.json",
    )
    pairs36 = e6pairs_obj["pairs"]
    pair_to_vertex = {frozenset(p): idx for idx, p in enumerate(pairs36)}
    block_oriented = {}
    for tri in blocks:
        if len(tri) != 3:
            continue
        block_oriented[frozenset(tri)] = list(tri)
    n = 36
    mult = [[None] * n for _ in range(n)]
    for ori in block_oriented.values():
        a, b, c = ori
        mult[a][b] = (1, c)
        mult[b][c] = (1, a)
        mult[c][a] = (1, b)
        mult[b][a] = (-1, c)
        mult[c][b] = (-1, a)
        mult[a][c] = (-1, b)
    return np.array(mult, dtype=object)


def compute_pockets(mult):
    n = mult.shape[0]
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
    pockets7 = set()
    for seed in combinations(range(n), 4):
        cl = closure(seed)
        if len(cl) == 7:
            pockets7.add(cl)
    return sorted(pockets7, key=lambda s: tuple(sorted(s)))


def choose_silent(pocket, mult):
    # pick vertex of minimal internal degree
    degs = {}
    for v in pocket:
        cnt = 0
        for w in pocket:
            if w == v:
                continue
            if mult[v][w] is not None or mult[w][v] is not None:
                cnt += 1
        degs[v] = cnt
    return min(degs, key=lambda k: (degs[k], k))


def analyze_axis_shifts(basis_mats, silent):
    """Given full derivation basis (list of 36x36 matrices) and a silent index,
    compute fix_dim and shift_dim as well as explicit candidate matrices.
    """
    n = 36
    K = len(basis_mats)
    if K == 0:
        return {'fix_dim': None, 'shift_dim': None}, []
    # construct matrix M of shape (n x K) where column i = basis_mats[i][:, silent]
    M = sp.Matrix([[basis_mats[i][r][silent] for i in range(K)] for r in range(n)])
    rankM = M.rank()
    fix_dim = K - rankM
    shift_dim = rankM
    # find columnspace basis vectors v
    col_basis = M.columnspace()
    candidates = []
    for v in col_basis:
        # solve M*c = v for coefficients c
        c_syms = sp.symbols(f'c0:{K}')
        eqs = []
        for r in range(n):
            eqs.append(sum(c_syms[i] * M[r, i] for i in range(K)) - v[r])
        sol = sp.solve(eqs, c_syms, dict=True)
        if sol:
            sol = sol[0]
            coeffs = [int(sol[c]) for c in c_syms]
        else:
            coeffs = [0] * K
        # build derivation matrix
        D = np.zeros((n, n), dtype=int)
        for i in range(K):
            D += coeffs[i] * np.array(basis_mats[i], dtype=int)
        candidates.append(D.tolist())
    return {'fix_dim': fix_dim, 'shift_dim': shift_dim}, candidates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tri_zip", required=True)
    ap.add_argument("--edge_zip", required=True)
    ap.add_argument("--full_basis", help="path to full_derivations_basis.json")
    args = ap.parse_args()

    mult = build_36_mult(args.tri_zip, args.edge_zip)
    pockets = compute_pockets(mult)
    silent_map = {tuple(p): choose_silent(p, mult) for p in pockets}
    by_silent = {}
    for p, s in silent_map.items():
        by_silent.setdefault(s, []).append(p)
    twin_dict = {}
    for p in pockets:
        active = tuple(sorted(set(p) - {silent_map[tuple(p)]}))
        twin_dict.setdefault(active, []).append(p)
    twin_pairs = [pair for pair in twin_dict.values() if len(pair) == 2]

    geom = {
        'total_pockets': len(pockets),
        'by_silent_counts': {str(s): len(lst) for s, lst in by_silent.items()},
        'twin_pairs_count': len(twin_pairs),
    }
    # convert silent map keys to lists for JSON
    silent_json = {json.dumps(list(p)): s for p, s in silent_map.items()}
    with open('pocket_geometry.json', 'w') as f:
        json.dump({'pockets': [list(p) for p in pockets],
                   'silent_of_pocket': silent_json,
                   'twin_pairs': [[list(a), list(b)] for a,b in twin_pairs],
                   **geom}, f)
    print('geometry', geom)

    if args.full_basis:
        # load basis
        obj = json.loads(Path(args.full_basis).read_text())
        basis_mats = obj.get('basis') or obj.get('derivation_basis_matrices_colmajor', [])
        # allow either format: basis list of matrices or colmajor list
        if not basis_mats and 'derivation_basis_matrices_colmajor' in obj:
            # convert backwards by reshaping columns
            colm = obj['derivation_basis_matrices_colmajor']
            # assume square
            m = int(math.sqrt(len(colm)))
            basis_mats = []
            for matcols in colm:
                M = np.zeros((m,m), dtype=int)
                for j, col in enumerate(matcols):
                    for i, val in enumerate(col):
                        M[i,j] = val
                basis_mats.append(M.tolist())
        axis_summary = {}
        axis_candidates = {}
        for s in range(36):
            info, cand = analyze_axis_shifts(basis_mats, s)
            axis_summary[s] = info
            if cand:
                axis_candidates[s] = cand
                with open(f'axis_shift_candidates_{s}.json', 'w') as f:
                    json.dump(cand, f)
        with open('axis_shift_summary.json', 'w') as f:
            json.dump(axis_summary, f)
        print('axis summary saved; candidates written for', list(axis_candidates.keys()))


if __name__ == '__main__':
    main()
