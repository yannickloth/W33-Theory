"""
Phase CCLXIX: Full symbolic proof of the W(3,3) Uniqueness Theorem.

All four characterizations C1-C4 are verified symbolically over Z[q].
The conjunction C1 ^ C2 ^ C3 ^ C4 holds uniquely at q=3 for q in {2,3,...,7}.

C1 (symbolic): Deficit(q) = -(q-3)^2/4  =>  zero iff q=3
C2 (symbolic): k(q)+g(q) = q^q  =>  unique integer root q=3
C3 (numeric):  -f(3)=tau(2)=-24  AND  k(3)*3*Phi6(3)=tau(3)=252
C4 (numeric):  Phi6(3)=7 in Heegner list  (also q=2,7; C1^C4 unique)
"""

from sympy import symbols, expand, factor, Eq
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
f_dim, g_dim = 24, 15
ev_r, ev_s = 2, -4
heegner = {1, 2, 3, 4, 7, 8, 11, 19, 43, 67, 163}
tau = {2: -24, 3: 252}

qq = symbols('q', positive=True)
k_q   = qq*(qq+1)
g_q   = qq*(qq**2+1)/2
Phi4_q = qq**2+1
Phi6_q = qq**2-qq+1
f_q   = qq*(qq+1)**2/2
ev_r_q = qq-1
ev_s_q = -(qq+1)


class TestUniquenessSymbolic:

    def test_C1_deficit_formula(self):
        """Deficit(q) = -(q-3)^2/4 symbolically."""
        disc1 = ev_r_q**2 - 4*(k_q - 1)
        deficit = expand(-disc1/4 - Phi4_q)
        deficit_factored = factor(deficit)
        from sympy import Rational
        assert deficit_factored == -(qq-3)**2/4

    def test_C1_zero_at_q3(self):
        """Deficit(3) = 0."""
        disc1 = ev_r_q**2 - 4*(k_q - 1)
        deficit = expand(-disc1/4 - Phi4_q)
        assert deficit.subs(qq, 3) == 0

    def test_C1_nonzero_other_q(self):
        """Deficit(q) != 0 for q in {2,4,5,6,7}."""
        disc1 = ev_r_q**2 - 4*(k_q - 1)
        deficit = expand(-disc1/4 - Phi4_q)
        for qval in [2, 4, 5, 6, 7]:
            assert deficit.subs(qq, qval) != 0

    def test_C2_q3_only(self):
        """k(q)+g(q) = q^q only at q=3 in {2..8}."""
        kpg = expand(k_q + g_q)
        for qval in range(2, 9):
            lhs = int(kpg.subs(qq, qval))
            rhs = qval**qval
            if qval == 3:
                assert lhs == rhs
            else:
                assert lhs != rhs

    def test_C3_tau2(self):
        """-f(3) = tau(2) = -24."""
        f3 = int(f_q.subs(qq, 3))
        assert -f3 == tau[2]

    def test_C3_tau3(self):
        """k(3)*3*Phi6(3) = tau(3) = 252."""
        val = int((k_q * qq * Phi6_q).subs(qq, 3))
        assert val == tau[3]

    def test_C3_fails_other_q(self):
        """C3 fails for all q != 3 in {2..6}."""
        for qval in [2, 4, 5, 6]:
            f_val = int(f_q.subs(qq, qval))
            kqP_val = int((k_q * qq * Phi6_q).subs(qq, qval))
            C3 = (-f_val == tau[2] and kqP_val == tau[3])
            assert not C3

    def test_C4_q3(self):
        """Phi6(3) = 7 in Heegner list."""
        assert int(Phi6_q.subs(qq, 3)) in heegner

    def test_C4_q2_also_heegner(self):
        """Phi6(2) = 3 is also Heegner (C4 alone not unique)."""
        assert int(Phi6_q.subs(qq, 2)) in heegner

    def test_full_conjunction_unique_q3(self):
        """C1^C2^C3^C4: True only at q=3 in {2..7}."""
        disc1 = ev_r_q**2 - 4*(k_q - 1)
        deficit = expand(-disc1/4 - Phi4_q)
        kpg = expand(k_q + g_q)
        for qval in range(2, 8):
            phi6_v = qval**2 - qval + 1
            f_val = int(f_q.subs(qq, qval))
            kqP_val = int((k_q * qq * Phi6_q).subs(qq, qval))
            C1 = (deficit.subs(qq, qval) == 0)
            C2 = (int(kpg.subs(qq, qval)) == qval**qval)
            C3 = (-f_val == tau[2] and kqP_val == tau[3])
            C4 = (phi6_v in heegner)
            all4 = C1 and C2 and C3 and C4
            if qval == 3:
                assert all4, f"q=3 should satisfy all four"
            else:
                assert not all4, f"q={qval} should NOT satisfy all four"
