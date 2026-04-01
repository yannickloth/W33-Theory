"""
Phase CCLX: W(3,3) Uniqueness Theorem

FOUR independent characterizations, all holding simultaneously ONLY at q=3:

C1: Im(zeta poles)^2/4 = Phi_cyc(q)  iff  q=3
    Deficit = -(q-3)^2/4  [proved symbolically]

C2: k(q) + g(q) = q^q  iff  q=3
    Equivalently: q^2 + 2q + 3 = 2q^{q-1} has unique solution q=3

C3: -f(q) = tau(2)  AND  k(q)*q*Phi6(q) = tau(3)  iff  q=3
    Both require exact coincidence of W(3,q) integers with Ramanujan tau values

C4: Q(sqrt(-Phi6(q))) is a Heegner field  (also holds q=2,7 but not q=4,5,6)
    Full conjunction C1 AND C4 holds only at q=3

THEOREM: W(3,3) is the UNIQUE member of the W(3,q) family where:
    - The zeta poles encode cyclotomic polynomial values exactly
    - The degree and co-degree eigenspace multiplicities sum to q^q
    - The spectral parameters reconstruct two values of the Ramanujan tau function
    - The s-eigenspace poles live in a Heegner quadratic field
"""

from sympy import symbols, factor, simplify
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
f_dim, g_dim = 24, 15
tau_2, tau_3 = -24, 252
heegner_discriminants = [1, 2, 3, 4, 7, 8, 11, 19, 43, 67, 163]  # |d| with h(d)=1


def W3q(qq):
    return {
        'k': qq*(qq+1), 'f': qq*(qq+1)**2//2,
        'g': qq*(qq**2+1)//2, 'Phi6': qq**2-qq+1, 'Phi4': qq**2+1
    }


class TestUniquenessTheorem:

    def test_C1_deficit_formula(self):
        """C1: deficit -(q-3)^2/4 proved symbolically."""
        q_sym = symbols('q', positive=True)
        r = q_sym-1; km1 = q_sym*(q_sym+1)-1; Phi4_s = q_sym**2+1
        disc = r**2 - 4*km1
        deficit = factor(-disc/4 - Phi4_s)
        assert deficit == -(q_sym-3)**2/4

    def test_C1_holds_at_q3(self):
        """C1 holds at q=3: deficit = 0."""
        qq = 3
        r = qq-1; km1 = qq*(qq+1)-1; Phi4q = qq**2+1
        disc = r**2 - 4*km1
        assert -disc/4 == Phi4q

    def test_C1_fails_other_q(self):
        """C1 fails for q != 3."""
        for qq in [2, 4, 5, 7]:
            r = qq-1; km1 = qq*(qq+1)-1; Phi4q = qq**2+1
            disc = r**2 - 4*km1
            assert -disc/4 != Phi4q

    def test_C2_holds_at_q3(self):
        """C2: k + g = q^q = 27 at q=3."""
        assert k + g_dim == q**q
        assert k + g_dim == 27

    def test_C2_fails_other_q(self):
        """C2 fails for q != 3."""
        for qq in [2, 4, 5, 7, 8, 9]:
            p = W3q(qq)
            assert p['k'] + p['g'] != qq**qq

    def test_C2_algebraic_equation(self):
        """C2 reduces to q^2 + 2q + 3 = 2q^{q-1}, unique soln q=3."""
        for qq in range(2, 10):
            lhs = qq**2 + 2*qq + 3
            rhs = 2 * qq**(qq-1)
            if lhs == rhs:
                assert qq == 3

    def test_C3_tau2_at_q3(self):
        """C3a: -f(3) = tau(2) = -24."""
        assert -f_dim == tau_2

    def test_C3_tau3_at_q3(self):
        """C3b: k*q*Phi6 = tau(3) = 252."""
        assert k * q * Phi6 == tau_3

    def test_C3_fails_q2(self):
        """C3 fails at q=2: -f(2)=-9 != tau(2)=-24."""
        p = W3q(2)
        assert -p['f'] != tau_2
        assert p['k']*2*p['Phi6'] != tau_3

    def test_C4_holds_at_q3(self):
        """C4: Phi6(3) = 7, Q(sqrt(-7)) is Heegner."""
        assert Phi6 in heegner_discriminants

    def test_C4_also_holds_q7(self):
        """C4 also holds at q=7: Phi6(7)=43, Q(sqrt(-43)) Heegner."""
        p = W3q(7)
        assert p['Phi6'] in heegner_discriminants

    def test_C1_and_C4_together_unique_q3(self):
        """C1 AND C4 simultaneously: only at q=3 in range q=2..9."""
        for qq in range(2, 10):
            r = qq-1; km1 = qq*(qq+1)-1; Phi4q = qq**2+1
            disc = r**2 - 4*km1
            C1 = (-disc/4 == Phi4q)
            p = W3q(qq)
            C4 = (p['Phi6'] in heegner_discriminants)
            if C1 and C4:
                assert qq == 3

    def test_all_four_simultaneously_unique_q3(self):
        """All four characterizations hold simultaneously only at q=3."""
        for qq in range(2, 10):
            r = qq-1; km1 = qq*(qq+1)-1; Phi4q = qq**2+1
            disc = r**2 - 4*km1
            C1 = (-disc/4 == Phi4q)
            p = W3q(qq)
            C2 = (p['k'] + p['g'] == qq**qq)
            C3 = (-p['f'] == tau_2 and p['k']*qq*p['Phi6'] == tau_3)
            C4 = (p['Phi6'] in heegner_discriminants)
            if C1 and C2 and C3 and C4:
                assert qq == 3
