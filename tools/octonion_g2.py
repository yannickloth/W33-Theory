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
    cwd = Path('.').resolve()
    with open(cwd / 'octonion_rep_stats.json', 'w') as f:
        json.dump(stats, f)
    with open(cwd / 'octonion_derivations.json', 'w') as f:
        json.dump({'basis': basis, **deriv_info}, f)
    print('done', stats)


if __name__ == '__main__':
    main()
