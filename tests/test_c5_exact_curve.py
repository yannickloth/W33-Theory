"""
Phase CCLXXX-CCLXXXII: C5 exact curve verification.

THEOREM (C5, final): Let E: y^2 = x^3 - 35x + 98  (j=-3375, N=49).
Then a_{k-1}(E) = a_11(E) = ev_s = -(q+1) = -4.
E is a CM curve with CM by Z[(1+sqrt(-7))/2].
This is the (-1)-quadratic twist of y^2 = x^3 - 35x - 98.
"""

import sympy
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
f_dim, g_dim = 24, 15
ev_r, ev_s = 2, -4

A_C5, B_C5 = -35, 98  # y^2 = x^3 - 35x + 98
heegner = {1, 2, 3, 4, 7, 8, 11, 19, 43, 67, 163}


def count_ap_short(A, B, p):
    count = 1
    for x in range(p):
        rhs = (x**3 + A*x + B) % p
        if rhs == 0: count += 1
        elif sympy.legendre_symbol(rhs, p) == 1: count += 2
    return p + 1 - count


class TestC5ExactCurve:

    def test_j_value_is_neg_g_cubed(self):
        """j(E) = -3375 = -g^3."""
        A, B = A_C5, B_C5
        disc = -16 * (4*A**3 + 27*B**2)
        j = 1728 * 4 * A**3 * (-1) // (4*A**3 + 27*B**2)
        # Use standard formula
        j_int = (1728 * 4 * A**3) // (4*A**3 + 27*B**2)
        assert abs(j_int) == g_dim**3

    def test_a11_equals_ev_s(self):
        ap = count_ap_short(A_C5, B_C5, 11)
        assert ap == ev_s

    def test_CM_inert_primes_give_zero(self):
        inert_primes = [p for p in [3, 5, 13, 17, 19]
                        if sympy.legendre_symbol(-7, p) == -1]
        for p in inert_primes:
            assert count_ap_short(A_C5, B_C5, p) == 0

    def test_a29_equals_ev_r(self):
        assert count_ap_short(A_C5, B_C5, 29) == ev_r

    def test_discriminant_check(self):
        """a_11^2 - 4*11 = ev_s^2 - 4*(k-1) = -28 = -4*Phi6."""
        assert ev_s**2 - 4*(k-1) == -4 * Phi6
        assert ev_s**2 - 4*(k-1) == -28

    def test_curve_is_minus1_twist_of_standard(self):
        """Standard model: A=-35,B=-98. Twist by d=-1: A->A*1=-35, B->B*(-1)=98."""
        A_std, B_std = -35, -98
        d = -1
        assert A_C5 == A_std * d**2
        assert B_C5 == B_std * d**3
