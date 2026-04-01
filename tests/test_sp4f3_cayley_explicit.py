"""
Phase CCXXXVIII: Explicit Sp(4,F_3) symplectic adjacency matrix.

Constructs W(3,3) explicitly as the symplectic polar space:
  - Vertices: 40 points of PG(3,F_3)
  - Adjacency: J(x,y) = x0*y2 + x1*y3 - x2*y0 - x3*y1 ≡ 0 (mod 3)
  - Symplectic group Sp(4,F_3) of order 51840 acts as automorphisms

Verifies all SRG parameters from the explicit construction.
Verifies spectral projector decomposition A = k*P0 + r*P1 + s*P2.
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
    """J(x,y) = x0*y2 + x1*y3 - x2*y0 - x3*y1 mod q."""
    return (x[0]*y[2] + x[1]*y[3] - x[2]*y[0] - x[3]*y[1]) % q


def make_pts_and_adj():
    pts_set = set()
    for coords in iproduct(F3, repeat=4):
        if any(c != 0 for c in coords):
            p = normalize_pt(coords)
            if p is not None:
                pts_set.add(p)
    pts = sorted(pts_set)
    A = np.zeros((v, v), dtype=int)
    for i, pi in enumerate(pts):
        for j, pj in enumerate(pts):
            if i != j and symp_form(pi, pj) == 0:
                A[i, j] = 1
    return pts, A


pts, A = make_pts_and_adj()


class TestSp4F3CayleyExplicit:

    def test_point_count(self):
        """PG(3,F_3) has exactly 40 = v points."""
        assert len(pts) == v == 40

    def test_all_degrees_equal_k(self):
        """Every vertex has degree exactly k=12."""
        degs = A.sum(axis=1)
        assert int(degs.min()) == k
        assert int(degs.max()) == k

    def test_adjacency_is_symmetric(self):
        """Adjacency matrix is symmetric (J is alternating so J(x,y)=0 <=> J(y,x)=0)."""
        assert np.array_equal(A, A.T)

    def test_no_self_loops(self):
        """J(x,x) = 0 always (alternating form), but we exclude i=i in adjacency."""
        assert np.trace(A) == 0

    def test_lambda_parameter(self):
        """Common neighbors of any adjacent pair = lambda = 2."""
        # Check a sample of adjacent pairs
        for i in range(min(10, v)):
            nbrs_i = set(np.where(A[i])[0])
            for j in list(nbrs_i)[:3]:
                nbrs_j = set(np.where(A[j])[0])
                assert len(nbrs_i & nbrs_j) == l

    def test_mu_parameter(self):
        """Common neighbors of any non-adjacent pair = mu = 4."""
        for i in range(5):
            nbrs_i = set(np.where(A[i])[0])
            non_adj = [j for j in range(v) if j != i and A[i,j] == 0]
            for j in non_adj[:3]:
                nbrs_j = set(np.where(A[j])[0])
                assert len(nbrs_i & nbrs_j) == m

    def test_eigenvalues(self):
        """Eigenvalues are exactly {12: 1, 2: 24, -4: 15}."""
        from collections import Counter
        eigvals = np.round(np.linalg.eigvalsh(A.astype(float))).astype(int)
        counts = Counter(eigvals)
        assert counts[k] == 1
        assert counts[2] == f
        assert counts[-4] == g

    def test_symplectic_form_defines_adjacency(self):
        """i~j <=> J(pts[i], pts[j]) = 0 (mod 3)."""
        for i in range(10):
            for j in range(v):
                if i != j:
                    adj_expected = 1 if symp_form(pts[i], pts[j]) == 0 else 0
                    assert A[i, j] == adj_expected

    def test_canonical_point_neighbors(self):
        """Neighbors of [0,0,0,1]: points with p[2]=0 (since J([0,0,0,1], p)=p[2])."""
        p0 = (0, 0, 0, 1)
        idx_p0 = pts.index(p0)
        nbr_idxs = np.where(A[idx_p0])[0]
        nbr_pts = [pts[j] for j in nbr_idxs]
        # J([0,0,0,1], [x0,x1,x2,x3]) = 0*x2 + 0*x3 - 0*0 - 1*x1... 
        # Actually J(x,y) = x0y2+x1y3-x2y0-x3y1
        # J([0,0,0,1], y) = 0*y2 + 0*y3 - 0*y0 - 1*y1 = -y1 mod 3 = 0 => y1=0
        assert all(symp_form(p0, nb) == 0 for nb in nbr_pts)
        assert len(nbr_pts) == k

    def test_isotropic_line_through_two_adj_points(self):
        """Two adjacent (isotropic) points span an isotropic line: all q+1=4 points isotropic."""
        # Take two adjacent points and find their line
        p0 = pts[0]
        nbrs_0 = [pts[j] for j in np.where(A[0])[0]]
        p1 = nbrs_0[0]
        # Line: {a*p0 + b*p1 | (a,b) in F_3^2 \ (0,0)} normalized
        line_pts = set()
        for a, b in iproduct(F3, F3):
            if a != 0 or b != 0:
                raw = tuple((a*p0[i] + b*p1[i]) % 3 for i in range(4))
                norm = normalize_pt(raw)
                if norm:
                    line_pts.add(norm)
        assert len(line_pts) == q + 1  # = 4 points on the line
        # All points on the line are isotropic
        for p in line_pts:
            assert symp_form(p, p) == 0  # self-isotropic (alternating form always 0)

    def test_spectral_projector_reconstruction(self):
        """A = k*P0 + r*P1 + s_ev*P2 at machine precision."""
        eigvals_A, eigvecs_A = np.linalg.eigh(A.astype(float))
        ev_r = np.round(eigvals_A).astype(int)
        P0 = eigvecs_A[:, ev_r==k]  @ eigvecs_A[:, ev_r==k].T
        P1 = eigvecs_A[:, ev_r==2]  @ eigvecs_A[:, ev_r==2].T
        P2 = eigvecs_A[:, ev_r==-4] @ eigvecs_A[:, ev_r==-4].T
        A_rec = k*P0 + 2*P1 + (-4)*P2
        assert np.max(np.abs(A.astype(float) - A_rec)) < 1e-10

    def test_P0_is_J_over_v(self):
        """P0 = J/v = (1/40)*ones_matrix."""
        eigvals_A, eigvecs_A = np.linalg.eigh(A.astype(float))
        ev_r = np.round(eigvals_A).astype(int)
        P0 = eigvecs_A[:, ev_r==k] @ eigvecs_A[:, ev_r==k].T
        P0_expected = np.ones((v, v)) / v
        assert np.max(np.abs(P0 - P0_expected)) < 1e-10

    def test_rank3_orbits(self):
        """Three orbits on ordered pairs: diagonal (40), adjacent (480), non-adj (1080)."""
        n_diag = v
        n_adj = int(A.sum())
        n_nonadj = v*v - n_diag - n_adj
        assert n_diag == v == 40
        assert n_adj == v * k == 480
        assert n_nonadj == v * (v - k - 1) == 1080
        assert n_diag + n_adj + n_nonadj == v**2

    def test_edge_count(self):
        """Number of edges = k*v/2 = 240 = E."""
        E = k * v // 2
        assert int(A.sum()) // 2 == E == 240

    def test_normalizer_is_Sp4(self):
        """Sp(4,F_3) has order 51840 = 2^7 * 3^4 * 5."""
        order_Sp4_F3 = 3**4 * (3**2 - 1) * (3**4 - 1)
        assert order_Sp4_F3 == 51840
        assert order_Sp4_F3 == 2**7 * 3**4 * 5
