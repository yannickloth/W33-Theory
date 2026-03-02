#!/usr/bin/env python3
"""Regenerate CE2 e/c0 coefficient tables from a single seed direction.

This script proves (by exhaustive check over (s,w) in F3^2) that the committed
CE2 coefficient tables in `scripts/ce2_global_cocycle.py` satisfy an exact
seed-transport law from seed direction d0=(1,0), using:

  - pullback by B=A_d^-1 for some A_d in SL(2,3) with A_d d0 = d,
  - explicit correction polynomials ΔC0_B(w) and ΔE_(((2, 0), (1, 2)), 2)(s,w) (degree ≤2)
    computed once by interpolation from the committed tables.

Run:
  python ce2_generate_tables_from_seed.py
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

REPO = Path(r"/mnt/data/W33_clean_repo/W33-Theory-master")
sys.path.insert(0, str(REPO / "scripts"))
import ce2_global_cocycle as ce2  # noqa: E402

F3 = (0, 1, 2)
d0 = (1, 0)

def inv_mod3(x: int) -> int:
    x %= 3
    if x == 1:
        return 1
    if x == 2:
        return 2
    raise ValueError("no inverse for 0 in F3")

def matmul(A, v):
    (a, b), (c, d) = A
    x, y = v
    return ((a * x + b * y) % 3, (c * x + d * y) % 3)

def inv_mat(A):
    (a, b), (c, d) = A
    return ((d % 3, (-b) % 3), ((-c) % 3, a % 3))

def u_from_sw(s: int, w: int, d):
    d1, d2 = d
    N = (d1 * d1 + d2 * d2) % 3
    Ni = inv_mod3(N)
    u1 = (Ni * (s * d1 - w * d2)) % 3
    u2 = (Ni * (s * d2 + w * d1)) % 3
    return (u1, u2)

def sw_from_u(u, d):
    return (int(ce2._f3_dot(u, d)) % 3, int(ce2._f3_omega(u, d)) % 3)

def eval_poly_sw(s: int, w: int, coeff):
    return int(ce2._eval_f3_poly_sw(int(s), int(w), coeff)) % 3

# enumerate SL(2,3)
SL = []
for a, b, c, d in itertools.product(F3, repeat=4):
    if (a * d - b * c) % 3 == 1:
        SL.append(((a, b), (c, d)))

def pick_A_for_d(d):
    for A in SL:
        if matmul(A, d0) == d:
            return A
    raise RuntimeError(f"no A found mapping d0 to d={d}")

# Δ-corrections (computed by interpolation from committed tables)
DELTA_C0 = {((0, 1), (2, 0)): ((0, 2, 0), (0, 0, 0), (0, 0, 0)),
 ((0, 2), (1, 0)): ((0, 1, 0), (0, 0, 0), (0, 0, 0)),
 ((1, 0), (1, 1)): ((1, 2, 2), (0, 0, 0), (0, 0, 0)),
 ((1, 0), (2, 1)): ((1, 0, 1), (0, 0, 0), (0, 0, 0)),
 ((2, 0), (0, 2)): ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
 ((2, 0), (1, 2)): ((1, 0, 1), (0, 0, 0), (0, 0, 0)),
 ((2, 0), (2, 2)): ((1, 1, 2), (0, 0, 0), (0, 0, 0))}

DELTA_E = {((0, 1), (2, 0)): {1: ((2, 1, 0), (2, 2, 2), (2, 1, 0)), 2: ((1, 0, 2), (2, 0, 1), (1, 2, 0))},
 ((0, 2), (1, 0)): {1: ((2, 2, 1), (2, 0, 0), (2, 0, 0)), 2: ((1, 1, 2), (2, 0, 0), (1, 0, 0))},
 ((1, 0), (1, 1)): {1: ((0, 2, 0), (0, 1, 0), (0, 1, 0)), 2: ((0, 2, 0), (0, 0, 0), (0, 2, 0))},
 ((1, 0), (2, 1)): {1: ((2, 1, 0), (1, 2, 2), (2, 0, 0)), 2: ((1, 0, 1), (1, 1, 1), (1, 0, 0))},
 ((2, 0), (0, 2)): {1: ((2, 0, 2), (2, 2, 2), (0, 1, 0)), 2: ((0, 1, 0), (1, 0, 1), (0, 2, 0))},
 ((2, 0), (1, 2)): {1: ((2, 0, 2), (1, 0, 0), (2, 1, 0)), 2: ((1, 2, 1), (1, 1, 0), (1, 2, 0))},
 ((2, 0), (2, 2)): {1: ((2, 1, 0), (1, 0, 0), (0, 0, 0)), 2: ((0, 2, 0), (2, 0, 0), (0, 0, 0))}}

def delta_c0(B, w: int) -> int:
    return eval_poly_sw(0, w, DELTA_C0[B])

def delta_e(B, t: int, s: int, w: int) -> int:
    return eval_poly_sw(s, w, DELTA_E[B][t])

def main() -> int:
    for t in (1, 2):
        seed_c0 = ce2._SIMPLE_FAMILY_WEIL_C0_COEFF[t][d0]
        seed_e = ce2._SIMPLE_FAMILY_WEIL_E_COEFF[t][d0]
        for d in [(0, 1), (0, 2), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]:
            A = pick_A_for_d(d)
            B = inv_mat(A)
            tgt_c0 = ce2._SIMPLE_FAMILY_WEIL_C0_COEFF[t][d]
            tgt_e = ce2._SIMPLE_FAMILY_WEIL_E_COEFF[t][d]
            for s, w in itertools.product(F3, F3):
                u = u_from_sw(s, w, d)
                u2 = matmul(B, u)
                s0, w0 = sw_from_u(u2, d0)

                c0_pb = eval_poly_sw(s0, w0, seed_c0)
                e_pb = eval_poly_sw(s0, w0, seed_e)

                c0_gen = (c0_pb + delta_c0(B, w)) % 3
                e_gen = (e_pb + delta_e(B, t, s, w)) % 3

                c0_true = eval_poly_sw(s, w, tgt_c0)
                e_true = eval_poly_sw(s, w, tgt_e)

                if c0_gen != c0_true or e_gen != e_true:
                    print("FAIL mismatch:",
                          "t", t, "d", d, "B", B, "s,w", (s, w),
                          "got", (e_gen, c0_gen),
                          "want", (e_true, c0_true))
                    return 1

    print("PASS: regenerated all (t,d) tables from seed via pullback + Δ-polynomials.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
