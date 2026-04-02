"""
Phase CCXLIII: Sp(4,F_3) transvection automorphisms -- explicit verification.

A transvection in Sp(4,F_3) is the map:
  T_{a,c}: x -> x + c * J(x,a) * a  (mod 3)
for isotropic a (J(a,a)=0) and c in F_3*.

These generate all of Sp(4,F_3) by the Steinberg presentation.

Key results:
  - All tested transvections are verified automorphisms: P_g * A * P_g^T = A.
  - Each transvection T_a fixes exactly Phi3=13 points = |perp(a) in PG(3,F_3)|.
  - chi(T_a) = Phi3 = 13: splits as 1 + 6 + 6 across irreps {1, 24, 15}.
  - |Stab(p0)| = |Sp(4,3)|/v = 51840/40 = 1296 = 2^4 * 3^4.
"""

from fractions import Fraction
from math import comb
import numpy as np
from itertools import product as iproduct
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
f_dim, g_dim = 24, 15
s_param = k // l
N = comb(s_param, q)
E = k * v // 2
Sp4_order = 51840
F3 = [0, 1, 2]


def normalize_pt(vec, q=3):
    for i, c in enumerate(vec):
        if c % q != 0:
            inv = pow(int(c), -1, q)
            return tuple((int(x)*inv) % q for x in vec)
    return None


def symp_form(x, y, q=3):
    return (x[0]*y[2] + x[1]*y[3] - x[2]*y[0] - x[3]*y[1]) % q


def build_pts_and_adj():
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


def apply_transvection(x, a, c, q=3):
    Jxa = symp_form(x, a, q)
    return tuple((x[i] + c * Jxa * a[i]) % q for i in range(4))


def make_perm_matrix(a_vec, c_val, pts, q=3):
    imgs = []
    for pt in pts:
        raw = apply_transvection(pt, a_vec, c_val, q)
        img = normalize_pt(raw, q)
        imgs.append(img)
    perm = [pts.index(p) for p in imgs]
    P = np.zeros((v, v), dtype=int)
    for i, j in enumerate(perm):
        P[j, i] = 1
    return P, perm


pts, A = build_pts_and_adj()
eigvals_A, eigvecs_A = np.linalg.eigh(A.astype(float))
ev_arr = np.round(eigvals_A).astype(int)
P0 = eigvecs_A[:, ev_arr==k]  @ eigvecs_A[:, ev_arr==k].T
P1 = eigvecs_A[:, ev_arr==2]  @ eigvecs_A[:, ev_arr==2].T
P2 = eigvecs_A[:, ev_arr==-4] @ eigvecs_A[:, ev_arr==-4].T


class TestSp4F3Transvections:

    def test_Sp4_order(self):
        """Sp(4,3) has order 2^7 * 3^4 * 5 = 51840."""
        assert Sp4_order == 2**7 * 3**4 * 5
        assert Sp4_order == 3**4 * (3**2 - 1) * (3**4 - 1)

    def test_stabilizer_order(self):
        """|Stab(p0)| = |Sp(4,3)|/v = 51840/40 = 1296 = 2^4 * 3^4."""
        stab = Sp4_order // v
        assert stab == 1296
        assert stab == 2**4 * 3**4

    def test_transvection_a1_is_isotropic(self):
        """a=(1,0,0,0) is isotropic: J(a,a) = 0."""
        a = (1, 0, 0, 0)
        assert symp_form(a, a) == 0

    def test_transvection_a1_is_automorphism(self):
        """T_{(1,0,0,0), 1} is an automorphism of W(3,3)."""
        P_g, _ = make_perm_matrix((1,0,0,0), 1, pts)
        conj = P_g @ A @ P_g.T
        assert np.array_equal(conj, A)

    def test_transvection_a2_is_automorphism(self):
        """T_{(0,1,0,0), 1} is an automorphism."""
        P_g, _ = make_perm_matrix((0,1,0,0), 1, pts)
        assert np.array_equal(P_g @ A @ P_g.T, A)

    def test_transvection_a3_is_automorphism(self):
        """T_{(0,0,1,0), 1} is an automorphism."""
        P_g, _ = make_perm_matrix((0,0,1,0), 1, pts)
        assert np.array_equal(P_g @ A @ P_g.T, A)

    def test_transvection_a4_is_automorphism(self):
        """T_{(0,0,0,1), 1} is an automorphism."""
        P_g, _ = make_perm_matrix((0,0,0,1), 1, pts)
        assert np.array_equal(P_g @ A @ P_g.T, A)

    def test_transvection_diagonal_is_automorphism(self):
        """T_{(1,1,0,0), 1} is an automorphism."""
        a = (1,1,0,0)
        assert symp_form(a, a) == 0
        P_g, _ = make_perm_matrix(a, 1, pts)
        assert np.array_equal(P_g @ A @ P_g.T, A)

    def test_transvection_c2_is_automorphism(self):
        """T_{(1,0,0,1), 2} is an automorphism (c=2=-1 in F_3)."""
        a = (1,0,0,1)
        # J((1,0,0,1),(1,0,0,1)) = 0+0-0-1 = -1 = 2 mod 3 != 0... check
        Jaa = symp_form(a, a)
        if Jaa == 0:  # only if isotropic
            P_g, _ = make_perm_matrix(a, 2, pts)
            assert np.array_equal(P_g @ A @ P_g.T, A)
        else:
            pytest.skip(f"a=(1,0,0,1) not isotropic: J(a,a)={Jaa}")

    def test_transvection_fixed_points_count(self):
        """Each transvection T_a fixes exactly Phi3=13 points."""
        for a_vec in [(1,0,0,0), (0,1,0,0), (0,0,1,0), (0,0,0,1)]:
            _, perm = make_perm_matrix(a_vec, 1, pts)
            fixed = sum(1 for i in range(v) if perm[i] == i)
            assert fixed == Phi3

    def test_fixed_points_are_perp_hyperplane(self):
        """Fixed pts of T_a = perp(a) = {x in PG(3,F_3): J(x,a)=0}."""
        a_vec = (1, 0, 0, 0)
        _, perm = make_perm_matrix(a_vec, 1, pts)
        fixed_pts = [pts[i] for i in range(v) if perm[i] == i]
        # All fixed points satisfy J(x,a)=0
        assert all(symp_form(p, a_vec) == 0 for p in fixed_pts)
        assert len(fixed_pts) == Phi3

    def test_perp_size_is_Phi3(self):
        """|perp(a) in PG(3,F_3)| = (q^3-1)/(q-1) = 13 = Phi3."""
        assert (q**3 - 1) // (q - 1) == Phi3

    def test_character_total_is_Phi3(self):
        """chi_perm(T_a) = fixed pts = Phi3 = 13."""
        P_g, perm = make_perm_matrix((1,0,0,0), 1, pts)
        chi_total = int(round(np.trace(P_g.astype(float))))
        assert chi_total == Phi3

    def test_character_trivial_rep_is_1(self):
        """chi_{P0}(T_a) = Tr(P0 * P_g) = 1 (trivial rep)."""
        P_g, _ = make_perm_matrix((1,0,0,0), 1, pts)
        chi_P0 = np.trace(P0 @ P_g.astype(float))
        assert abs(chi_P0 - 1.0) < 1e-8

    def test_character_irreps_sum_to_Phi3(self):
        """chi_P0 + chi_P1 + chi_P2 = 1+6+6 = 13 = Phi3."""
        P_g, _ = make_perm_matrix((1,0,0,0), 1, pts)
        chi_P0 = np.trace(P0 @ P_g.astype(float))
        chi_P1 = np.trace(P1 @ P_g.astype(float))
        chi_P2 = np.trace(P2 @ P_g.astype(float))
        assert abs(chi_P0 + chi_P1 + chi_P2 - Phi3) < 1e-7

    def test_character_P1_equals_6(self):
        """chi_{P1}(T_a) = 6 = s_param = k/lambda."""
        P_g, _ = make_perm_matrix((1,0,0,0), 1, pts)
        chi_P1 = np.trace(P1 @ P_g.astype(float))
        assert abs(chi_P1 - s_param) < 1e-7

    def test_character_P2_equals_6(self):
        """chi_{P2}(T_a) = 6 = s_param = k/lambda (equal to chi_P1)."""
        P_g, _ = make_perm_matrix((1,0,0,0), 1, pts)
        chi_P2 = np.trace(P2 @ P_g.astype(float))
        assert abs(chi_P2 - s_param) < 1e-7

    def test_character_formula(self):
        """chi(T_a) = 1 + 2*s_param = 1 + 2*6 = 13 = Phi3."""
        chi_formula = 1 + 2 * s_param
        assert chi_formula == Phi3

    def test_perm_matrix_is_permutation(self):
        """P_g is a 0-1 matrix with exactly one 1 per row and column."""
        P_g, _ = make_perm_matrix((1,0,0,0), 1, pts)
        assert P_g.sum(axis=0).tolist() == [1]*v
        assert P_g.sum(axis=1).tolist() == [1]*v

    def test_transvection_is_involution_over_F3(self):
        """T_{a,1}^3 = identity (order divides 3 since c in F_3*)."""
        P_g, perm = make_perm_matrix((1,0,0,0), 1, pts)
        # Apply perm 3 times
        perm3 = [perm[perm[perm[i]]] for i in range(v)]
        assert perm3 == list(range(v))  # identity

    def test_transvection_order_is_3(self):
        """T_{a,1} has order 3 (not 1 unless trivial)."""
        _, perm = make_perm_matrix((1,0,0,0), 1, pts)
        perm2 = [perm[perm[i]] for i in range(v)]
        perm3 = [perm[perm[perm[i]]] for i in range(v)]
        assert perm != list(range(v))  # not identity
        assert perm3 == list(range(v))  # order 3
