"""
Phase CCXLVIII: Krein parameters of W(3,3).

The Krein parameters q_{ij}^k are the structure constants of the
Bose-Mesner algebra in the dual (Hadamard) basis of minimal idempotents.

Key results:
  q_(1,2)^2 = q_(2,2)^1 = mu = 4  (mu appears as TWO Krein parameters!)
  q_(1,1)^2 = q_(1,2)^1 = Phi4/lambda = 5
  q_(1,1)^0 = f/v = 3/5
  q_(2,2)^0 = g/v = 3/8
  All Krein params >= 0 (Krein condition satisfied)
"""

import numpy as np
from fractions import Fraction
from math import comb
from itertools import product as iproduct
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
f_dim, g_dim = 24, 15
E_edges = k * v // 2
F3 = [0, 1, 2]


def normalize_pt(vec, q=3):
    for i, c in enumerate(vec):
        if c % q != 0:
            inv = pow(int(c), -1, q)
            return tuple((int(x)*inv) % q for x in vec)
    return None


def symp_form(x, y, q=3):
    return (x[0]*y[2]+x[1]*y[3]-x[2]*y[0]-x[3]*y[1]) % q


def build_pts_adj():
    pts_set = set()
    for coords in iproduct(F3, repeat=4):
        if any(c != 0 for c in coords):
            p = normalize_pt(coords)
            if p: pts_set.add(p)
    pts = sorted(pts_set)
    A = np.zeros((v, v), dtype=int)
    for i, pi in enumerate(pts):
        for j, pj in enumerate(pts):
            if i != j and symp_form(pi, pj) == 0:
                A[i, j] = 1
    return pts, A


pts, A = build_pts_adj()
eigvals_A, eigvecs_A = np.linalg.eigh(A.astype(float))
ev_arr = np.round(eigvals_A).astype(int)
E0 = (1/v)*np.ones((v,v))
E1 = eigvecs_A[:, ev_arr==2] @ eigvecs_A[:, ev_arr==2].T
E2 = eigvecs_A[:, ev_arr==-4] @ eigvecs_A[:, ev_arr==-4].T

# Compute Krein parameters via Hadamard products
# q_{ij}^k = v * sum_{a,b} (E_i)_{ab}*(E_j)_{ab}*(E_k)_{ab}
def krein_raw(Ei, Ej, Ek, v=40):
    return v * np.sum(Ei * Ej * Ek)

# Raw (multiplied by v) Krein parameters
q11_0 = krein_raw(E1, E1, E0)
q11_1 = krein_raw(E1, E1, E1)
q11_2 = krein_raw(E1, E1, E2)
q12_0 = krein_raw(E1, E2, E0)
q12_1 = krein_raw(E1, E2, E1)
q12_2 = krein_raw(E1, E2, E2)
q22_0 = krein_raw(E2, E2, E0)
q22_1 = krein_raw(E2, E2, E1)
q22_2 = krein_raw(E2, E2, E2)


class TestKreinParameters:

    def test_q11_0_equals_f_over_v(self):
        """q_(1,1)^0 = f/v = 24/40 = 3/5."""
        assert abs(q11_0 / v - f_dim/v) < 1e-8
        assert Fraction(f_dim, v) == Fraction(3, 5)

    def test_q22_0_equals_g_over_v(self):
        """q_(2,2)^0 = g/v = 15/40 = 3/8."""
        assert abs(q22_0 / v - g_dim/v) < 1e-8
        assert Fraction(g_dim, v) == Fraction(3, 8)

    def test_q12_0_is_zero(self):
        """q_(1,2)^0 = 0 (cross term to trivial)."""
        assert abs(q12_0) < 1e-8

    def test_q12_2_equals_mu(self):
        """q_(1,2)^2 = mu = 4."""
        assert abs(q12_2 / v - m) < 1e-8

    def test_q22_1_equals_mu(self):
        """q_(2,2)^1 = mu = 4."""
        assert abs(q22_1 / v - m) < 1e-8

    def test_q12_2_equals_q22_1(self):
        """q_(1,2)^2 = q_(2,2)^1: mu appears as TWO Krein parameters."""
        assert abs(q12_2 - q22_1) < 1e-8

    def test_q11_2_equals_Phi4_over_lambda(self):
        """q_(1,1)^2 = Phi4/lambda = 10/2 = 5."""
        assert abs(q11_2 / v - Phi4/l) < 1e-8
        assert Phi4 // l == 5

    def test_q12_1_equals_Phi4_over_lambda(self):
        """q_(1,2)^1 = Phi4/lambda = 5."""
        assert abs(q12_1 / v - Phi4/l) < 1e-8

    def test_q11_2_equals_q12_1(self):
        """q_(1,1)^2 = q_(1,2)^1 = Phi4/lambda = 5."""
        assert abs(q11_2 - q12_1) < 1e-8

    def test_all_krein_nonneg(self):
        """All Krein parameters >= 0 (Delsarte Krein condition)."""
        raw_vals = [q11_0, q11_1, q11_2, q12_0, q12_1, q12_2, q22_0, q22_1, q22_2]
        assert all(qv >= -1e-8 for qv in raw_vals)

    def test_krein_sum_11(self):
        """sum_k q_(1,1)^k = f^2/v = 72/5 (Delsarte normalization)."""
        total = (q11_0 + q11_1 + q11_2) / v
        assert abs(total - f_dim**2/v) < 1e-8

    def test_krein_sum_22(self):
        """sum_k q_(2,2)^k = g^2/v = 45/8."""
        total = (q22_0 + q22_1 + q22_2) / v
        assert abs(total - g_dim**2/v) < 1e-8

    def test_mu_double_appearance(self):
        """mu=4 is both q_(1,2)^2 and q_(2,2)^1."""
        assert abs(q12_2/v - m) < 1e-8
        assert abs(q22_1/v - m) < 1e-8
        # This encodes the SRG mu-parameter in the dual algebra

    def test_Phi4_lambda_double_appearance(self):
        """Phi4/lambda=5 is both q_(1,1)^2 and q_(1,2)^1."""
        assert abs(q11_2/v - Phi4/l) < 1e-8
        assert abs(q12_1/v - Phi4/l) < 1e-8
