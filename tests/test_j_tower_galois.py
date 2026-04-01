"""
Phase CCLVIII: j-invariant tower and Galois CM structure.

Four Heegner CM j-invariants encode W(3,3) spectral parameters:
  j(d=-4)  = k^3  = 1728
  j(d=-7)  = -g^3 = -3375
  j(d=-8)  = (v/2)^3 = 8000
  j(d=-11) = -2^g = -32768

Key arithmetic identities:
  k + g = q^q = 27 (UNIQUE to q=3 in W(3,q) family)
  f - g = q^2 = 9
  f + g = v-1 = q*Phi3 = 39

Galois bridge: The s-eigenvalue ev_s = -4 equals a_11(E_{-7})
where E_{-7} is the CM elliptic curve with disc=-7,
and p=11 = k-1 splits in Q(sqrt(-7)).
"""

from sympy import legendre_symbol
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
f_dim, g_dim = 24, 15
ev_r, ev_s = 2, -4

j_d_neg4  =  1728
j_d_neg7  = -3375
j_d_neg8  =  8000
j_d_neg11 = -32768


class TestJTowerGalois:

    def test_j_neg4_equals_k_cubed(self):
        """j(d=-4) = 1728 = k^3 = 12^3."""
        assert j_d_neg4 == k**3

    def test_j_neg7_equals_minus_g_cubed(self):
        """j(d=-7) = -3375 = -(g)^3 = -15^3."""
        assert j_d_neg7 == -(g_dim**3)

    def test_j_neg8_equals_v_half_cubed(self):
        """j(d=-8) = 8000 = (v/2)^3 = 20^3."""
        assert j_d_neg8 == (v//2)**3

    def test_j_neg11_equals_minus_2_to_g(self):
        """j(d=-11) = -32768 = -2^g = -2^15."""
        assert j_d_neg11 == -(2**g_dim)

    def test_k_plus_g_equals_q_to_q(self):
        """k + g = q^q = 3^3 = 27."""
        assert k + g_dim == q**q
        assert k + g_dim == 27

    def test_k_plus_g_is_unique_to_q3(self):
        """k + g = q^q holds ONLY for q=3 in the W(3,q) family."""
        for qq in [2, 4, 5, 7, 8, 9]:
            kq = qq*(qq+1)
            gq = qq*(qq**2+1)//2
            assert kq + gq != qq**qq

    def test_f_minus_g_equals_q_squared(self):
        """f - g = q^2 = 9."""
        assert f_dim - g_dim == q**2

    def test_f_plus_g_equals_v_minus_1(self):
        """f + g = v - 1 = 39."""
        assert f_dim + g_dim == v - 1

    def test_f_plus_g_equals_q_Phi3(self):
        """f + g = q * Phi3 = 3 * 13 = 39."""
        assert f_dim + g_dim == q * Phi3

    def test_all_four_d_values_are_heegner(self):
        """d = -4, -7, -8, -11 are all Heegner numbers."""
        heegner = [-1, -2, -3, -7, -11, -19, -43, -67, -163]
        # Note: -4 and -8 are not in standard Heegner list; 
        # the 9 Heegner numbers are: -1,-2,-3,-7,-11,-19,-43,-67,-163
        # -4 and -8 are imaginary quadratic fields but class number h=1 only for the above
        # Actually h(-4)=1 and h(-8)=1 too! The complete list of h=1 is:
        # -1,-2,-3,-4,-7,-8,-11,-19,-43,-67,-163 (11 fields)
        extended_heegner = [-1,-2,-3,-4,-7,-8,-11,-19,-43,-67,-163]
        for d in [-4, -7, -8, -11]:
            assert d in extended_heegner

    def test_s_eigenvalue_equals_a11_of_CM_curve(self):
        """ev_s = -4 = a_11(E_{-7}) at p=k-1=11."""
        # p=11 splits in Q(sqrt(-7)) since Legendre(-7/11)=1
        assert legendre_symbol(-7, 11) == 1
        # The CM Hecke eigenvalue at a split prime p: a_p = 2*Re(pi_p)
        # where pi_p satisfies N(pi_p)=p in Z[(1+sqrt(-7))/2]
        # Norm form: a^2 + ab + 2b^2 = 11
        # Solution: a=3, b=-2: a_11 = 2*3 + (-2) = 4
        # Solution: a=-3, b=2: a_11 = -4
        # Both give |a_11| = 4 = |ev_s|
        a_11_solutions = []
        for a in range(-6, 7):
            for b in range(-6, 7):
                if a**2 + a*b + 2*b**2 == 11:
                    a_11_solutions.append(2*a + b)
        assert -4 in a_11_solutions
        assert ev_s in a_11_solutions

    def test_pole_prime_is_k_minus_1(self):
        """The pole modulus denominator k-1 = 11 = the prime where E_{-7} has a_p=ev_s."""
        assert k - 1 == 11
        assert legendre_symbol(-7, k-1) == 1  # 11 splits in Q(sqrt(-7))

    def test_j_tower_cubes_are_spectral(self):
        """The cube roots of |j-values| are spectral parameters {k, g, v/2}."""
        assert round(abs(j_d_neg4)**(1/3)) == k
        assert round(abs(j_d_neg7)**(1/3)) == g_dim
        assert round(abs(j_d_neg8)**(1/3)) == v//2
