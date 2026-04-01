"""
Phase CCL: f/E = 1/Phi4(q) and g/E = 1/mu^2 are UNIVERSAL W(3,q) identities.

For ALL GQ(q,q) = W(3,q) with q prime power:
  v = (q+1)(q^2+1)
  k = q(q+1)
  lambda = q-1,  mu = q+1
  f = q(q+1)^2/2  (multiplicity of r = q-1 eigenvalue)
  g = q(q^2+1)/2  (multiplicity of s = -(q+1) eigenvalue)
  E = q(q+1)^2(q^2+1)/2  (number of edges)

Universal identities:
  f/E = 1/(q^2+1) = 1/Phi4(q)    [for all q]
  g/E = 1/(q+1)^2 = 1/mu^2       [for all q]
  2f*Phi4(q) = kv = 2E            [for all q]
  2g*mu^2    = kv = 2E            [for all q]

Implication: The neutrino mu_eff^2 predictions use q=3 specifically,
giving numerical values 1/Phi4(3)=1/10 and 1/mu(3)^2=1/16.
"""

from fractions import Fraction
from sympy import symbols, simplify, factor
import pytest

v_sym, k_sym, f_sym, g_sym, E_sym = None, None, None, None, None


def W3q_params_exact(q):
    """Return exact integer W(3,q) parameters."""
    v = (q+1)*(q**2+1)
    k = q*(q+1)
    l = q - 1
    m = q + 1
    r = q - 1
    s = -(q + 1)
    # f = (-k - (v-1)*s) / (r - s)
    f = (-k - (v-1)*s) // (r - s)
    g = v - 1 - f
    E = k*v//2
    Phi4q = q**2 + 1
    return v, k, l, m, f, g, E, Phi4q


class TestUniversalGQIdentities:

    @pytest.mark.parametrize("q", [2, 3, 4, 5, 7, 8, 9])
    def test_2f_Phi4_equals_kv(self, q):
        """2f*Phi4(q) = k*v for all q."""
        v, k, l, m, f, g, E, Phi4q = W3q_params_exact(q)
        assert 2*f*Phi4q == k*v

    @pytest.mark.parametrize("q", [2, 3, 4, 5, 7, 8, 9])
    def test_2g_mu2_equals_kv(self, q):
        """2g*mu^2 = k*v for all q."""
        v, k, l, m, f, g, E, Phi4q = W3q_params_exact(q)
        assert 2*g*m**2 == k*v

    @pytest.mark.parametrize("q", [2, 3, 4, 5, 7, 8, 9])
    def test_f_over_E_equals_1_Phi4(self, q):
        """f/E = 1/Phi4(q) for all q."""
        v, k, l, m, f, g, E, Phi4q = W3q_params_exact(q)
        assert Fraction(f, E) == Fraction(1, Phi4q)

    @pytest.mark.parametrize("q", [2, 3, 4, 5, 7, 8, 9])
    def test_g_over_E_equals_1_mu2(self, q):
        """g/E = 1/mu^2 = 1/(q+1)^2 for all q."""
        v, k, l, m, f, g, E, Phi4q = W3q_params_exact(q)
        assert Fraction(g, E) == Fraction(1, m**2)

    @pytest.mark.parametrize("q", [2, 3, 4, 5, 7, 8, 9])
    def test_f_explicit_formula(self, q):
        """f = q(q+1)^2/2 for all q."""
        v, k, l, m, f, g, E, Phi4q = W3q_params_exact(q)
        assert f == q*(q+1)**2//2

    @pytest.mark.parametrize("q", [2, 3, 4, 5, 7, 8, 9])
    def test_g_explicit_formula(self, q):
        """g = q(q^2+1)/2 for all q."""
        v, k, l, m, f, g, E, Phi4q = W3q_params_exact(q)
        assert g == q*(q**2+1)//2

    @pytest.mark.parametrize("q", [2, 3, 4, 5, 7, 8, 9])
    def test_E_explicit_formula(self, q):
        """E = q(q+1)^2(q^2+1)/2 for all q."""
        v, k, l, m, f, g, E, Phi4q = W3q_params_exact(q)
        assert E == q*(q+1)**2*(q**2+1)//2

    @pytest.mark.parametrize("q", [2, 3, 4, 5, 7, 8, 9])
    def test_f_plus_g_equals_v_minus_1(self, q):
        """f + g = v - 1 (multiplicity sum)."""
        v, k, l, m, f, g, E, Phi4q = W3q_params_exact(q)
        assert f + g == v - 1

    def test_sympy_symbolic_proof_f_over_E(self):
        """Symbolic proof: f/E = 1/(q^2+1) for all q."""
        qq = symbols('q', positive=True)
        vv = (qq+1)*(qq**2+1)
        kk = qq*(qq+1)
        ss = -(qq+1)
        rr = qq-1
        ff = (-kk - (vv-1)*ss) / (rr - ss)
        EE = kk*vv/2
        ratio = simplify(ff/EE - 1/(qq**2+1))
        assert ratio == 0

    def test_sympy_symbolic_proof_g_over_E(self):
        """Symbolic proof: g/E = 1/(q+1)^2 for all q."""
        qq = symbols('q', positive=True)
        vv = (qq+1)*(qq**2+1)
        kk = qq*(qq+1)
        ss = -(qq+1)
        rr = qq-1
        ff = (-kk - (vv-1)*ss) / (rr - ss)
        gg = vv - 1 - ff
        EE = kk*vv/2
        ratio = simplify(gg/EE - 1/(qq+1)**2)
        assert ratio == 0

    def test_q3_specific_values(self):
        """At q=3: f=24, g=15, E=240, Phi4=10, mu=4."""
        v, k, l, m, f, g, E, Phi4q = W3q_params_exact(3)
        assert v == 40 and k == 12 and l == 2 and m == 4
        assert f == 24 and g == 15 and E == 240 and Phi4q == 10

    def test_two_identities_are_the_same(self):
        """2f*Phi4 = 2g*mu^2 (both equal kv): the two identities coincide."""
        for q in [2, 3, 4, 5, 7]:
            v, k, l, m, f, g, E, Phi4q = W3q_params_exact(q)
            assert 2*f*Phi4q == 2*g*m**2
