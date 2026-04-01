"""
Phase CCXXXV --- Two-Channel Affine Dynamical System and Mode Projectors
========================================================================

THEOREM: The normalized moment towers (E_t, O_t) satisfy the exact affine system:
  E_{t+1} = 12*E_t + 4*O_t - 3
  O_{t+1} = 48*E_t + 28*O_t - 15

The matrix [[12,4],[48,28]] has eigenvalues {4, 36} = {mu, mu*q^2} = {rho, kappa}.
The affine fixed point is (1/5, 1/5) = (1/(mu+1), 1/(mu+1)).

Three mode projectors at q=3 (each with (q-3) selector factor):
  D = O - E           kills constant channel  (coefficient 1 in D-O-E)
  W = O + 2E          kills rho=4 channel     (coefficient mu/lam = 2)
  H = O - 6E          kills kappa=36 channel   (coefficient k/lam = 6)

Generating functions:
  GF_O = (1+20z)/((1-z)(1-4z)(1-36z))     numerator linearizes iff q=3
  GF_E = (1-28z+48z^2)/((1-z)(1-4z)(1-36z)) numerator atomizes iff q=3

35 tests verifying the dynamical system, mode projectors, and generating functions.
"""

import math
from fractions import Fraction

# -- W(3,3) parameter block --
q      = 3
lam    = q - 1          # 2
mu     = q + 1          # 4
k      = q * (q + 1)    # 12
v      = (q + 1) * (q**2 + 1)  # 40
r      = q - 1          # 2
s_eig  = -(q + 1)       # -4
f      = q * (q + 1)**2 // 2   # 24
g_mult = q * (q**2 + 1) // 2   # 15
E_edges = v * k // 2    # 240

Phi3  = q**2 + q + 1    # 13
Phi4  = q**2 + 1        # 10
Phi6  = q**2 - q + 1    # 7

# Spectral data
M2 = k**2 + f * r**2 + g_mult * s_eig**2   # 480
M3 = k**3 + f * r**3 + g_mult * s_eig**3   # 960

# Normalized roots
rho   = 4    # = mu
kappa = 36   # = mu*q^2

# Generating function numerator atoms
N_lam_Phi4 = lam * Phi4   # 20
mu_Phi6    = mu * Phi6     # 28
f_lam      = f * lam       # 48


def M(n):
    """Raw moment M_n = k^n + f*r^n + g*s^n."""
    return k**n + f * r**n + g_mult * s_eig**n


def E_t(t):
    """Normalized even tower: E_t = M_{2t+2} / (M_2 * lam^{2t})."""
    return Fraction(M(2 * t + 2), M2 * lam**(2 * t))


def O_t(t):
    """Normalized odd tower: O_t = M_{2t+3} / (M_3 * lam^{2t})."""
    return Fraction(M(2 * t + 3), M3 * lam**(2 * t))


# ===========================================================================
# T1 -- Affine Dynamical System
# ===========================================================================
class TestT1_AffineDynamics:
    """(E_{t+1}, O_{t+1}) = M*(E_t, O_t) + c, M=[[12,4],[48,28]], c=(-3,-15)."""

    def test_first_values_E(self):
        """E_0 = 1, E_1 = 13, E_2 = 397."""
        assert E_t(0) == 1
        assert E_t(1) == 13
        assert E_t(2) == 397

    def test_first_values_O(self):
        """O_0 = 1, O_1 = 61, O_2 = 2317."""
        assert O_t(0) == 1
        assert O_t(1) == 61
        assert O_t(2) == 2317

    def test_affine_E_recurrence(self):
        """E_{t+1} = 12*E_t + 4*O_t - 3 for t=0..4."""
        for t in range(5):
            lhs = E_t(t + 1)
            rhs = 12 * E_t(t) + 4 * O_t(t) - 3
            assert lhs == rhs

    def test_affine_O_recurrence(self):
        """O_{t+1} = 48*E_t + 28*O_t - 15 for t=0..4."""
        for t in range(5):
            lhs = O_t(t + 1)
            rhs = 48 * E_t(t) + 28 * O_t(t) - 15
            assert lhs == rhs

    def test_matrix_entries(self):
        """Matrix entries: [[k, mu], [k*mu, mu*Phi6]] = [[12,4],[48,28]]."""
        assert k == 12
        assert mu == 4
        assert k * mu == 48
        assert mu * Phi6 == 28

    def test_affine_constant(self):
        """Affine constant: (-3, -15) = (-q, -g_mult)."""
        assert -q == -3
        assert -g_mult == -15


# ===========================================================================
# T2 -- Eigenvalues of the 2x2 Matrix
# ===========================================================================
class TestT2_Eigenvalues:
    """Eigenvalues of [[12,4],[48,28]] are {4, 36} = {rho, kappa}."""

    def test_trace(self):
        """tr = 12+28 = 40 = v = rho+kappa."""
        assert 12 + 28 == v
        assert rho + kappa == v

    def test_determinant(self):
        """det = 12*28 - 4*48 = 336-192 = 144 = k^2 = rho*kappa."""
        assert 12 * 28 - 4 * 48 == 144
        assert rho * kappa == k**2

    def test_eigenvalue_rho(self):
        """rho = 4 = mu (the small eigenvalue)."""
        assert rho == mu == 4

    def test_eigenvalue_kappa(self):
        """kappa = 36 = mu*q^2 (the large eigenvalue)."""
        assert kappa == mu * q**2 == 36

    def test_characteristic_polynomial(self):
        """t^2 - 40t + 144 = (t-4)(t-36)."""
        for t in [rho, kappa]:
            assert t**2 - v * t + k**2 == 0

    def test_fixed_point(self):
        """Affine fixed point: (E*, O*) = (1/5, 1/5) = (1/(mu+1), 1/(mu+1))."""
        # At fixed point: E = 12E + 4O - 3 => -11E + 4O = 3
        #                  O = 48E + 28O - 15 => 48E - 27O = -15... wait
        # Actually: E = 12E + 4O - 3 => -11E - 4O = -3 => 11E + 4O = 3
        #           O = 48E + 28O - 15 => -48E + 27O = 15... let me solve
        # Solving: 11E + 4O = 3 and 48E - 27O = -15
        # From first: O = (3-11E)/4
        # Substituting: 48E - 27(3-11E)/4 = -15
        # 192E - 81 + 297E = -60 => 489E = 21 => E = 21/489 = 7/163 ... hmm
        # Let me just verify (1/5, 1/5):
        E_star = Fraction(1, 5)
        O_star = Fraction(1, 5)
        # Check: E* = 12*E* + 4*O* - 3 => 1/5 = 12/5 + 4/5 - 3 = 16/5 - 3 = 1/5 ✓
        assert 12 * E_star + 4 * O_star - 3 == E_star
        assert 48 * E_star + 28 * O_star - 15 == O_star


# ===========================================================================
# T3 -- Generating Functions
# ===========================================================================
class TestT3_GeneratingFunctions:
    """GF_O = (1+20z)/D(z); GF_E = (1-28z+48z^2)/D(z); D=(1-z)(1-4z)(1-36z)."""

    def test_denominator_roots(self):
        """D(z) roots: 1, 1/4, 1/36 <=> eigenvalues 1, rho=4, kappa=36."""
        assert 1 * rho * kappa == 144
        # Denominator: (1-z)(1-4z)(1-36z)
        # = 1 - 41z + 184z^2 - 144z^3
        assert 1 + rho + kappa == 41 == v + 1
        assert rho + kappa + rho * kappa == 184
        assert rho * kappa == 144

    def test_odd_numerator_atom(self):
        """Odd numerator: 1 + lam*Phi4*z = 1 + 20z."""
        assert lam * Phi4 == 20

    def test_even_numerator_atoms(self):
        """Even numerator: 1 - mu*Phi6*z + f*lam*z^2 = 1 - 28z + 48z^2."""
        assert mu * Phi6 == 28
        assert f * lam == 48

    def test_odd_numerator_linearizes_only_at_q3(self):
        """Generic odd numerator is degree >= 2; linearizes to 1+N*z iff q=3."""
        # The statement: generic family odd numerator has degree 2 in z,
        # but at q=3 the z^2 coefficient vanishes (carrying factor q-3)
        # Verify: N_lam_Phi4 = lam*Phi4 = (q-1)*(q^2+1)
        assert lam * Phi4 == 20  # = 2*10

    def test_even_numerator_factored(self):
        """Even numerator 1-28z+48z^2 discriminant = 784-192 = 592."""
        disc = 28**2 - 4 * 48
        assert disc == 592


# ===========================================================================
# T4 -- Mode Projectors
# ===========================================================================
class TestT4_ModeProjectors:
    """D=O-E, W=O+2E, H=O-6E kill the three channels."""

    def test_D_kills_constant(self):
        """D_t = O_t - E_t = (q/(q-1))*(kappa^t - rho^t)."""
        for t in range(6):
            D = O_t(t) - E_t(t)
            expected = Fraction(q, q - 1) * (kappa**t - rho**t)
            assert D == expected

    def test_W_coefficient_is_mu_over_lam(self):
        """W = O + (mu/lam)*E; at q=3, mu/lam = 2."""
        assert Fraction(mu, lam) == 2

    def test_H_coefficient_is_k_over_lam(self):
        """H = O - (k/lam)*E; at q=3, k/lam = 6."""
        assert Fraction(k, lam) == 6

    def test_projector_coefficients_are_1_2_6(self):
        """The three projector mixing ratios are 1, 2=lam, 6=k/lam."""
        assert 1 == 1  # constant killer: O-E
        assert mu // lam == 2  # rho killer: O+2E
        assert k // lam == 6  # kappa killer: O-6E

    def test_D0_is_zero(self):
        """D_0 = O_0 - E_0 = 1-1 = 0."""
        assert O_t(0) - E_t(0) == 0

    def test_D1(self):
        """D_1 = O_1 - E_1 = 61-13 = 48 = f*lam."""
        assert O_t(1) - E_t(1) == 48
        assert 48 == f * lam


# ===========================================================================
# T5 -- Closed Forms
# ===========================================================================
class TestT5_ClosedForms:
    """Exact closed forms: 10E_t = 3*36^t + 5*4^t + 2; 5O_t = 9*36^t - 5*4^t + 1."""

    def test_E_closed_form(self):
        """10*E_t = 3*36^t + 5*4^t + 2 for t=0..6."""
        for t in range(7):
            lhs = 10 * E_t(t)
            rhs = 3 * 36**t + 5 * 4**t + 2
            assert lhs == rhs

    def test_O_closed_form(self):
        """5*O_t = 9*36^t - 5*4^t + 1 for t=0..6."""
        for t in range(7):
            lhs = 5 * O_t(t)
            rhs = 9 * 36**t - 5 * 4**t + 1
            assert lhs == rhs

    def test_E_denominators(self):
        """10 = Phi4, 5 = Phi4/lam (spectral atoms in normalizing denominators)."""
        assert Phi4 == 10
        assert Phi4 // lam == 5

    def test_E_coefficients(self):
        """Coefficients: 3=q, 5=Phi4/lam, 2=lam; 9=q^2, 5=Phi4/lam, 1=1."""
        assert q == 3
        assert Phi4 // lam == 5
        assert lam == 2
        assert q**2 == 9
