#!/usr/bin/env python3
"""Generate the W33-side axis-fixed 192 torsor from pocket-completion data.

This script reproduces the core enumeration from the hammer pocket-lift
bundle, then filters the 2,688 embedding solutions to those whose local
"silent" index (6) is mapped to a fixed octonion axis and whose sign-bit for
that position is +1.  The resulting 192 (phi,sign) pairs form the torsor we
need on the W33 side.

Outputs JSON with the 192 solutions and a small summary.  The same script
could be adapted to produce the full 2,688 records or to vary the fixed axis.

Usage:
    python scripts/compute_w33_axis192_torsor.py [axis]

The optional axis argument (1-7) selects which octonion unit is held fixed;
default is 7.
"""
from __future__ import annotations
import itertools
import json
import sys

# octonion multiplication table for standard basis 1..7
# use the same helper from hammer_g2_pocketlift
OCTONION_TABLE = [
    # 1  2  3  4  5  6  7
    (0, 0, 0, 0, 0, 0, 0),  # placeholder for 0
]
# use the same octonion multiplication used by hammer_g2_pocketlift
# positive/negative triples define the multiplication table
pos_triples=[(1,2,7),(3,4,7),(5,6,7),(1,3,5)]
neg_triples=[(1,4,6),(2,3,6),(2,4,5)]
mul2={}
def add_triple(a,b,c,sgn=1):
    mul2[(a,b)]=(sgn,c); mul2[(b,c)]=(sgn,a); mul2[(c,a)]=(sgn,b)
    mul2[(b,a)]=(-sgn,c); mul2[(c,b)]=(-sgn,a); mul2[(a,c)]=(-sgn,b)
for t in pos_triples: add_triple(*t,sgn=1)
for t in neg_triples: add_triple(*t,sgn=-1)

def oct_mul(i,j):
    if i==0: return (1,j)
    if j==0: return (1,i)
    if i==j: return (-1,0)
    return mul2[(i,j)]

# geometric constraints for one pocket (copied from hammer script)
# constraint tuples: (x, y, spock, z) meaning phi[x]*phi[y] = spock*phi[z]
# where spock = +1 for positive triple, -1 for negative triple
constraints = [
    (0, 1, 1, 6),
    (2, 3, 1, 6),
    (4, 5, 1, 6),
    (0, 2, 1, 4),
    (1, 3, -1, 4),
    (1, 4, -1, 5),
    (2, 5, -1, 5),
]

# helper routines from hammer script

def solve_sign_eqs(eqs, n):
    """Solve linear equations over GF(2) defined by (mask,val) pairs.
    Returns (solution_vector,num_free) or (None,None) if inconsistent.
    """
    sol = [0] * n
    free = set(range(n))
    for mask, rhs in eqs:
        pivot = None
        for i in range(n):
            if mask >> i & 1:
                if i in free:
                    pivot = i
                    break
        if pivot is None:
            if rhs != 0:
                return None, None
            continue
        # eliminate pivot
        free.remove(pivot)
        sol[pivot] = rhs
        # subtract pivot from subsequent equations
        new_eqs = []
        for m, r in eqs:
            if (m >> pivot) & 1:
                new_eqs.append((m ^ (1 << pivot), r ^ rhs))
            else:
                new_eqs.append((m, r))
        eqs = new_eqs
    return sol, len(free)


def canon_table(tab):
    enc = []
    for i in range(7):
        for j in range(7):
            s, out = tab[i][j]
            enc.append(int(s))
            enc.append(-1 if out is None else int(out))
    return tuple(enc)

# enumeration of all embedding solutions (phi,bits,tab) copied from hammer;
# we don't need to record unique table here, just filter combinations

def enumerate_solutions():
    unique_sol = []
    for phi in itertools.permutations(range(1, 8), 7):
        ok = True
        eqs = []
        for x, y, spock, z in constraints:
            so, k = oct_mul(phi[x], phi[y])
            if k == 0 or k != phi[z]:
                ok = False
                break
            o = 0 if so == 1 else 1
            p = 0 if spock == 1 else 1
            mask = (1 << z) | (1 << x) | (1 << y)
            eqs.append((mask, o ^ p))
        if not ok:
            continue
        sol, nfree = solve_sign_eqs(eqs, 7)
        if sol is None:
            continue
        for bits in itertools.product([0, 1], repeat=7):
            good = True
            for mask, rhs in eqs:
                s = rhs
                m = mask
                for j in range(7):
                    if (m >> j) & 1:
                        s ^= bits[j]
                if s != 0:
                    good = False
                    break
            if not good:
                continue
            # store solution tuple for later filtering
            unique_sol.append((phi, bits))
    return unique_sol


def main():
    axis = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    solutions = enumerate_solutions()
    # filter by phi mapping and bits
    axis_sols = []
    for phi, bits in solutions:
        if phi[6] != axis:
            continue
        if bits[6] != 0:
            continue
        axis_sols.append((phi, bits))
    print(f"total embeddings = {len(solutions)}")
    print(f"axis={axis} fixed solutions = {len(axis_sols)}")
    assert len(axis_sols) == 192, "unexpected axis count"
    # save to json
    out = [{"phi": list(phi), "bits": list(bits)} for phi, bits in axis_sols]
    with open(f"w33_axis{axis}_torsor.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote w33_axis{axis}_torsor.json with 192 elements")

if __name__ == "__main__":
    main()
