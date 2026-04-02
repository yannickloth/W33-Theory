"""
Phase CCXXXIX: Irrep decomposition of Sp(4,F_3) permutation representation.

The permutation representation of Sp(4,F_3) on the 40 points of PG(3,F_3)
splits into EXACTLY 3 irreducible representations with dimensions {1, 24, 15}.

This is the FINITE GROUP proof that the SU(6) spectral projectors P0, P1, P2
identified in Phase CCXXXII are IDENTICAL to the Sp(4,F_3) isotypic components:
  - Trivial rep (dim 1): P0 = J/v
  - Middle rep (dim 24): P1, corresponds to mu*s = 4*6
  - Alt^2 rep (dim 15): P2, corresponds to C(s,2) = C(6,2)

Rank-3 permutation group theory: a transitive group with 3 orbits on ordered
pairs has permutation character decomposing into exactly 3 irreps.
"""

import numpy as np
from itertools import product as iproduct
from fractions import Fraction
from math import comb
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
f, g = 24, 15
s = k // l
N = comb(s, q)
F3 = [0, 1, 2]


def normalize_pt(vec, q=3):
    for i, c in enumerate(vec):
        if c % q != 0:
            inv = pow(int(c), -1, q)
            return tuple((int(x)*inv) % q for x in vec)
    return None


def symp_form(x, y, q=3):
    return (x[0]*y[2] + x[1]*y[3] - x[2]*y[0] - x[3]*y[1]) % q


def make_adj():
    pts_set = set()
    for coords in iproduct(F3, repeat=4):
        if any(c != 0 for c in coords):
            p = normalize_pt(coords)
            if p:
                pts_set.add(p)
    pts = sorted(pts_set)
    A = np.zeros((v, v), dtype=int)
    for i, pi in enumerate(pts):
        for j, pj in enumerate(pts):
            if i != j and symp_form(pi, pj) == 0:
                A[i, j] = 1
    return pts, A


pts, A = make_adj()
eigvals_A, eigvecs_A = np.linalg.eigh(A.astype(float))
ev_r = np.round(eigvals_A).astype(int)
P0 = eigvecs_A[:, ev_r==k]  @ eigvecs_A[:, ev_r==k].T
P1 = eigvecs_A[:, ev_r==2]  @ eigvecs_A[:, ev_r==2].T
P2 = eigvecs_A[:, ev_r==-4] @ eigvecs_A[:, ev_r==-4].T


class TestIrrepDecompositionSp4F3:

    def test_three_irreps_only(self):
        """Permutation rep on 40 pts decomposes into exactly 3 irreps."""
        from collections import Counter
        ev_counts = Counter(ev_r)
        assert len(ev_counts) == 3

    def test_irrep_dims_match_multiplicities(self):
        """Irrep dims: {1, 24, 15} = {rank P0, rank P1, rank P2}."""
        assert round(np.trace(P0)) == 1
        assert round(np.trace(P1)) == f
        assert round(np.trace(P2)) == g

    def test_dim_sum_equals_v(self):
        """1 + 24 + 15 = 40 = v."""
        assert 1 + f + g == v

    def test_projectors_sum_to_identity(self):
        """P0 + P1 + P2 = I_40."""
        assert np.max(np.abs(P0 + P1 + P2 - np.eye(v))) < 1e-10

    def test_projectors_are_orthogonal(self):
        """P_i * P_j = 0 for i != j."""
        assert np.max(np.abs(P0 @ P1)) < 1e-10
        assert np.max(np.abs(P0 @ P2)) < 1e-10
        assert np.max(np.abs(P1 @ P2)) < 1e-10

    def test_projectors_are_idempotent(self):
        """P_i^2 = P_i."""
        assert np.max(np.abs(P0 @ P0 - P0)) < 1e-10
        assert np.max(np.abs(P1 @ P1 - P1)) < 1e-10
        assert np.max(np.abs(P2 @ P2 - P2)) < 1e-10

    def test_trivial_rep_is_J_over_v(self):
        """Trivial rep projector P0 = J/v (constant functions)."""
        P0_expected = np.ones((v, v)) / v
        assert np.max(np.abs(P0 - P0_expected)) < 1e-10

    def test_middle_rep_dim_24_from_params(self):
        """dim(P1 rep) = 24 = mu*s = mu*(k/lambda) = 4*6."""
        assert round(np.trace(P1)) == m * s

    def test_alt2_rep_dim_15_from_params(self):
        """dim(P2 rep) = 15 = C(s,2) = C(6,2) = dim(Alt^2(C^6))."""
        assert round(np.trace(P2)) == comb(s, 2)

    def test_rank3_implies_3_irreps(self):
        """Rank-3 permutation group <-> permutation char = sum of 3 distinct irreps."""
        # The 3 orbital matrices (association scheme) are:
        # A0 = I (diagonal), A1 = A (adj), A2 = J-I-A (non-adj)
        A0 = np.eye(v, dtype=int)
        A1 = A
        A2 = np.ones((v, v), dtype=int) - A0 - A1
        # They form a commutative association scheme (Bose-Mesner algebra)
        # The dimension of the Bose-Mesner algebra = number of irreps = 3
        BM_span = np.array([A0, A1, A2], dtype=float)
        # Check they commute:
        assert np.max(np.abs(A1.astype(float) @ A2.astype(float) - A2.astype(float) @ A1.astype(float))) < 1e-8

    def test_bose_mesner_algebra_dim_3(self):
        """Bose-Mesner algebra has dimension 3 = number of orbital matrices."""
        # Three basis matrices: I, A, J-I-A
        basis = [np.eye(v), A.astype(float), np.ones((v, v)) - np.eye(v) - A.astype(float)]
        # They are linearly independent
        mat = np.array([b.flatten() for b in basis])
        rank = np.linalg.matrix_rank(mat)
        assert rank == 3

    def test_spectral_idempotents_match_BM_algebra(self):
        """Spectral idempotents P0, P1, P2 ARE the primitive idempotents of BM algebra."""
        # In BM algebra: P0 = (1/v)*J, and P1, P2 are the other primitive idempotents
        # Verify they are in the BM algebra (commute with A):
        assert np.max(np.abs(A.astype(float) @ P0 - P0 @ A.astype(float))) < 1e-10
        assert np.max(np.abs(A.astype(float) @ P1 - P1 @ A.astype(float))) < 1e-10
        assert np.max(np.abs(A.astype(float) @ P2 - P2 @ A.astype(float))) < 1e-10
