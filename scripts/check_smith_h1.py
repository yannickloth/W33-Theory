#!/usr/bin/env python3
"""Compute Smith normal forms for d1 and d2 and report invariant factors.
"""
from sympy import Matrix
from sympy.matrices.normalforms import smith_normal_form
import sys
from pathlib import Path
# Make the `scripts` directory importable when running this helper directly
sys.path.insert(0, str(Path(__file__).parent))
from w33_homology import build_clique_complex, boundary_matrix
from e8_embedding_group_theoretic import build_w33

n, _, adj, _ = build_w33()
simplices = build_clique_complex(n, adj)
B1 = boundary_matrix(simplices[1], simplices[0])  # C1 -> C0
B2 = boundary_matrix(simplices[2], simplices[1])  # C2 -> C1
M1 = Matrix(B1.tolist())
M2 = Matrix(B2.tolist())

print('Computing SNF of d1 (C1->C0)...')
res1 = smith_normal_form(M1)
if isinstance(res1, (tuple, list)):
    S1 = res1[0]
else:
    S1 = res1
inv1 = [int(S1[i, i]) for i in range(min(S1.rows, S1.cols)) if S1[i, i] != 0]
print('  rank(d1) via SNF =', len(inv1))
print('  nontrivial invariants >1 for d1 (first 20):', [v for v in inv1 if v > 1][:20])

print('Computing SNF of d2 (C2->C1)...')
res2 = smith_normal_form(M2)
if isinstance(res2, (tuple, list)):
    S2 = res2[0]
else:
    S2 = res2
inv2 = [int(S2[i, i]) for i in range(min(S2.rows, S2.cols)) if S2[i, i] != 0]
print('  rank(d2) via SNF =', len(inv2))
print('  nontrivial invariants >1 for d2 (first 20):', [v for v in inv2 if v > 1][:20])

# Quick inference
print('\nQuick inference:')
print('  rows C0 =', M1.rows, 'cols C1 =', M1.cols)
print('  cols C2 =', M2.cols, 'rows C1 =', M2.rows)
print('  Betti b1 = dim ker(d1) - rank(d2) =', M1.cols - len(inv1) - len(inv2))
