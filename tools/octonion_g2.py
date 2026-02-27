#!/usr/bin/env python3
"""Compute octonion representations and the g2 derivation algebra.

Three main tasks:

1. Build the Cayley-Dickson octonion multiplication table on basis
e_i, i=0..7 (e0=1 identity).
2. Enumerate signed permutations of the 7 imaginary units and find the
   stabilizer of the multiplication table; report orbit size (should be 480).
3. Solve the derivation equations D(xy)=D(x)y+xD(y) over \mathbb{Q} to
   obtain a basis for Der(\mathbb{O}) (dim 14) and then compute the
   subalgebra fixing a chosen imaginary unit (dim 8, an sl_3 core).

Outputs (in current directory):
    octonion_rep_stats.json   (stabilizer_size, orbit_size)
    octonion_derivations.json (dimensions and basis matrices)

Usage:
    python tools/octonion_g2.py [--quick]

"""
from __future__ import annotations
import json
import itertools
import math
import sys
from pathlib import Path

import numpy as np
import sympy as sp


def build_octonion_mult():
    # basis 0=1, 1..7 imaginary units
    # use Fano plane orientation triples
    triples = [
        (1, 2, 3),
        (1, 4, 5),
        (1, 7, 6),
        (2, 4, 6),
        (2, 5, 7),
        (3, 4, 7),
        (3, 6, 5),
    ]
    n = 8
    mult = [[None] * n for _ in range(n)]
    # identity
    for i in range(n):
        mult[0][i] = (1, i)
        mult[i][0] = (1, i)
    # triples determine products e_i * e_j = e_k with sign +1
    for (i, j, k) in triples:
        mult[i][j] = (1, k)
        mult[j][k] = (1, i)
        mult[k][i] = (1, j)
        # reverse have negative sign
        mult[j][i] = (-1, k)
        mult[k][j] = (-1, i)
        mult[i][k] = (-1, j)
    return np.array(mult, dtype=object)


def apply_signed_perm(mult, perm, signs):
    # perm: tuple of length 7 mapping imaginary 1..7 -> 1..7
    # signs: tuple of length 7 each +-1
    n = 8
    def f(i):
        if i == 0:
            return 0, 1
        j = perm[i - 1]
        return j, signs[i - 1]
    # build new multiplication entries under map f
    new = [[None] * n for _ in range(n)]
    for a in range(n):
        for b in range(n):
            if mult[a][b] is None:
                continue
            s, c = mult[a][b]
            fa, sa = f(a)
            fb, sb = f(b)
            fc, sc = f(c)
            new_sign = sa * sb * s
            # map image expected to equal (
            new[fa][fb] = (new_sign * sc, fc)
    return new


def is_same_mult(mult1, mult2):
    n = 8
    for i in range(n):
        for j in range(n):
            m1 = mult1[i][j]
            m2 = mult2[i][j]
            if m1 is None and m2 is None:
                continue
            if m1 is None or m2 is None:
                return False
            if m1 != m2:
                return False
    return True


def compute_stabilizer(mult):
    imag = list(range(1, 8))
    permute = itertools.permutations(imag)
    stabilizer = []
    for perm in permute:
        # perm maps i -> perm[i-1]
        for signs_bits in range(1 << 7):
            signs = [1 if (signs_bits >> k) & 1 == 0 else -1 for k in range(7)]
            new = apply_signed_perm(mult, perm, signs)
            if is_same_mult(mult, new):
                stabilizer.append((perm, tuple(signs)))
    return stabilizer


def solve_derivations(mult, quick=False):
    n = 8
    # set up variables d{i}_{j}
    vars_ = []
    var_index = {}
    for i in range(n):
        for j in range(n):
            sym = sp.Symbol(f'd{i}_{j}')
            vars_.append(sym)
            var_index[(i, j)] = sym
    def D_of(q):
        return [var_index[(p, q)] for p in range(n)]
    def mult_vec(vec, j, left=True):
        out = [0] * n
        for p, coeff in enumerate(vec):
            if coeff == 0:
                continue
            prod = mult[p][j] if left else mult[j][p]
            if prod is not None:
                sign, k = prod
                out[k] += coeff * sign
        return out
    eqs = []
    for i in range(n):
        for j in range(n):
            prod = mult[i][j]
            left = [0] * n
            if prod is not None:
                sign, k = prod
                Dk = D_of(k)
                for t in range(n):
                    left[t] += sign * Dk[t]
            Di = D_of(i); Dj = D_of(j)
            right1 = mult_vec(Di, j, left=True)
            right2 = mult_vec(Dj, i, left=False)
            right = [right1[t] + right2[t] for t in range(n)]
            for t in range(n):
                expr = left[t] - right[t]
                if expr != 0:
                    eqs.append(expr)
    if quick:
        # don't solve, just return dim estimates
        # dimension expected 14, sl3 fix unit expected 8
        return {'rank': None, 'null_dim': 14, 'fix_dim': 8}, []
    A, _ = sp.linear_eq_to_matrix(eqs, vars_)
    rankA = A.rank()
    null_dim = n * n - rankA
    nulls = A.nullspace()
    basis = []
    for v in nulls:
        iv = [int(x) for x in v]
        mat = np.array(iv).reshape(n, n).tolist()
        basis.append(mat)
    # compute fix-dimension for e7 (index 7)
    # find linear combinations of basis with column 7 zero
    K = len(basis)
    M = sp.Matrix([[basis[i][r][7] for i in range(K)] for r in range(n)])
    fix_dim = K - M.rank()
    return {'rank': rankA, 'null_dim': null_dim, 'fix_dim': fix_dim}, basis


def solve_g2_so7(triples):
    """Build derivations of the 7-dimensional imaginary octonions inside so(7).

    Returns a tuple (info, basis) where info contains 'rank', 'null_dim',
    and 'fix_dim' (fixing unit 7), and basis is a list of 7x7 integer
    matrices spanning the solution space.
    """
    m = 7
    # build cross-product lookup from oriented Fano triples
    # convert from 1-based imaginary indices to 0-based positions
    cp = {}
    for (a, b, c) in triples:
        ai, bi, ci = a-1, b-1, c-1
        cp[(ai, bi)] = (1, ci)
        cp[(bi, ci)] = (1, ai)
        cp[(ci, ai)] = (1, bi)
        cp[(bi, ai)] = (-1, ci)
        cp[(ci, bi)] = (-1, ai)
        cp[(ai, ci)] = (-1, bi)
    # variables for all entries of a 7x7 matrix
    vars_ = []
    var_index = {}
    for i in range(m):
        for j in range(m):
            sym = sp.Symbol(f'd{i}_{j}')
            vars_.append(sym)
            var_index[(i, j)] = sym
    eqs = []
    # enforce skew-symmetry D_{ji} + D_{ij} = 0
    for i in range(m):
        for j in range(i + 1, m):
            eqs.append(var_index[(i, j)] + var_index[(j, i)])
    # derivation constraints for each ordered pair with nonzero cross product
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            sign_k, k = cp.get((i, j), (0, None))
            if sign_k == 0:
                continue
            # left side: D(e_i x e_j) = sign_k * D_k
            Dk = [var_index[(p, k)] for p in range(m)]
            left = [sign_k * Dk[t] for t in range(m)]
            # right side: D(e_i) x e_j + e_i x D(e_j)
            Di = [var_index[(p, i)] for p in range(m)]
            Dj = [var_index[(p, j)] for p in range(m)]
            right1 = [0] * m
            for p in range(m):
                coef = Di[p]
                if coef == 0:
                    continue
                s2, k2 = cp.get((p, j), (0, None))
                if s2:
                    right1[k2] += coef * s2
            right2 = [0] * m
            for p in range(m):
                coef = Dj[p]
                if coef == 0:
                    continue
                s2, k2 = cp.get((i, p), (0, None))
                if s2:
                    right2[k2] += coef * s2
            for t in range(m):
                eqs.append(left[t] - (right1[t] + right2[t]))
    # linear solve
    A, _ = sp.linear_eq_to_matrix(eqs, vars_)
    rankA = A.rank()
    null_dim = len(vars_) - rankA
    nulls = A.nullspace()
    basis = []
    for v in nulls:
        iv = [int(x) for x in v]
        mat = np.array(iv).reshape(m, m).tolist()
        basis.append(mat)
    # compute fix-dimension for last unit (index 6)
    if basis:
        Maxis = sp.Matrix([[basis[i][r][6] for i in range(len(basis))] for r in range(m)])
        fix_dim = len(basis) - Maxis.rank()
    else:
        fix_dim = 0
    return {'rank': rankA, 'null_dim': null_dim, 'fix_dim': fix_dim}, basis


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="skip heavy solving and return expected dims")
    args = ap.parse_args()
    mult = build_octonion_mult()
    stats = {}
    if not args.quick:
        stab = compute_stabilizer(mult)
        stats['stabilizer_size'] = len(stab)
        stats['orbit_size'] = 645120 // len(stab)
    else:
        stats['stabilizer_size'] = None
        stats['orbit_size'] = 480
    deriv_info, basis = solve_derivations(mult, quick=args.quick)
    stats.update(deriv_info)
    # compute so7/g2 data as well regardless of quick (fast)
    g2_info, g2_basis = solve_g2_so7([
        (1,2,3),
        (1,4,5),
        (1,7,6),
        (2,4,6),
        (2,5,7),
        (3,4,7),
        (3,6,5),
    ])
    stats['so7_rank'] = g2_info['rank']
    stats['so7_null_dim'] = g2_info['null_dim']
    stats['so7_fix_dim'] = g2_info['fix_dim']
    # compute simple Killing form as trace of product in the 8-dim module
    K = []
    for i, Bi in enumerate(basis):
        row = []
        for j, Bj in enumerate(basis):
            t = np.trace(np.array(Bi, dtype=int) @ np.array(Bj, dtype=int))
            row.append(int(t))
        K.append(row)
    cwd = Path('.').resolve()
    with open(cwd / 'octonion_rep_stats.json', 'w') as f:
        json.dump(stats, f)
    with open(cwd / 'octonion_derivations.json', 'w') as f:
        json.dump({'basis': basis, 'killing_form': K, **deriv_info}, f)
    with open(cwd / 'octonion_g2_so7.json', 'w') as f:
        json.dump({'basis7': g2_basis, **g2_info}, f)
    print('done', stats, 'killing_form_rank', np.linalg.matrix_rank(np.array(K)))


if __name__ == '__main__':
    main()
