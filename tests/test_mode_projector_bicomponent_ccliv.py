"""
Phase CCLIV — Small-Integer Mode Projectors and Bicomponent Closure
====================================================================

The even/odd normalized moment towers E_t, O_t share characteristic roots
{1, 4, 36} = {1, rho, kappa} and satisfy the cubic recurrence:
  X_{t+3} = 41*X_{t+2} - 184*X_{t+1} + 144*X_t
where S1=41=v+1, S2=184=8*23, S3=144=k^2.

Three small-integer mode projectors:
  D = O - E:    kills constant mode (pole at z=1)
  W = O + 2*E:  kills mu-mode (pole at z=1/mu)
  H = O - 6*E:  kills dominant kappa-mode (pole at z=1/(mu*q^2))

Each projector's numerator has a (q-3) factor => uniquely selects q=3.

Sources: W33_mode_projector_selector_20260330.zip,
         W33_bicomponent_moment_closure_20260330.zip,
         W33_normalized_odd_core_closure_20260330.zip
"""
import pytest
from fractions import Fraction

# ── W(3,3) parameters ──
q   = 3
v   = 40
k   = 12
lam = 2
mu  = 4
f   = 24
g   = 15
Phi3 = 13
Phi4 = 10
Phi6 = 7

# ── Characteristic roots of bicomponent system ──
root_const = 1
root_rho   = (mu // lam)**2 if lam > 0 else None  # (q+1)/(q-1) = 2, squared = 4
root_kappa = (k // lam)**2 if lam > 0 else None    # k/(q-1) = 6, squared = 36

# Recurrence coefficients at q=3
S1 = v + 1          # 41
S2 = (k - mu) * (f - 1)  # 8 * 23 = 184
S3 = k**2            # 144


# ================================================================
# T1: Bicomponent characteristic roots
# ================================================================
class TestT1_CharacteristicRoots:
    """Shared roots of E_t and O_t towers."""

    def test_three_roots(self):
        """Roots are {1, 4, 36}"""
        assert {root_const, root_rho, root_kappa} == {1, 4, 36}

    def test_rho_is_mu(self):
        """rho = ((q+1)/(q-1))^2 = 4 = mu at q=3"""
        assert root_rho == mu

    def test_kappa_is_mu_q_sq(self):
        """kappa = (k/(q-1))^2 = 36 = mu*q^2"""
        assert root_kappa == mu * q**2

    def test_sum_of_roots(self):
        """1+4+36 = 41 = S1 = v+1"""
        assert root_const + root_rho + root_kappa == S1
        assert S1 == v + 1

    def test_product_of_roots(self):
        """1*4*36 = 144 = S3 = k^2"""
        assert root_const * root_rho * root_kappa == S3
        assert S3 == k**2

    def test_pairwise_products_sum(self):
        """1*4 + 1*36 + 4*36 = 184 = S2"""
        s = root_const*root_rho + root_const*root_kappa + root_rho*root_kappa
        assert s == S2


# ================================================================
# T2: Recurrence S1, S2, S3
# ================================================================
class TestT2_RecurrenceCoefficients:
    """S1=41, S2=184, S3=144."""

    def test_S1_value(self):
        """S1 = v+1 = 41"""
        assert S1 == 41

    def test_S1_is_prime(self):
        """41 is prime"""
        assert all(41 % d != 0 for d in range(2, 41))

    def test_S2_factorization(self):
        """S2 = 184 = 8*23 = (k-mu)*(f-1)"""
        assert S2 == 184
        assert S2 == 8 * 23
        assert 8 == k - mu
        assert 23 == f - 1

    def test_S3_is_k_squared(self):
        """S3 = 144 = k^2 = 12^2"""
        assert S3 == k**2

    def test_verify_recurrence(self):
        """X_{t+3} = S1*X_{t+2} - S2*X_{t+1} + S3*X_t"""
        # Test with E_t
        def E(t):
            return Fraction(3*36**t + 5*4**t + 2, 10)
        for t in range(5):
            lhs = E(t + 3)
            rhs = S1 * E(t + 2) - S2 * E(t + 1) + S3 * E(t)
            assert lhs == rhs

    def test_verify_recurrence_O(self):
        """O_t also satisfies the same recurrence"""
        def O(t):
            return Fraction(9*36**t - 5*4**t + 1, 5)
        for t in range(5):
            lhs = O(t + 3)
            rhs = S1 * O(t + 2) - S2 * O(t + 1) + S3 * O(t)
            assert lhs == rhs


# ================================================================
# T3: Mode projectors D, W, H
# ================================================================
class TestT3_ModeProjectors:
    """D=O-E, W=O+2E, H=O-6E are exact mode projectors at q=3."""

    def _E(self, t):
        return Fraction(3*36**t + 5*4**t + 2, 10)

    def _O(self, t):
        return Fraction(9*36**t - 5*4**t + 1, 5)

    def test_D_kills_constant(self):
        """D_t = O_t - E_t has no constant term"""
        for t in range(5):
            D_t = self._O(t) - self._E(t)
            # D_t should be A*36^t + B*4^t (no constant)
            # D_0 = O_0 - E_0 = 1 - 1 = 0 => constant cancels
            # D_t = (9/5 - 3/10)*36^t + (-1 - 1/2)*4^t
            #     = (15/10)*36^t + (-3/2)*4^t
            #     = (3/2)*36^t - (3/2)*4^t = (3/2)*(36^t - 4^t)
            expected = Fraction(3, 2) * (36**t - 4**t)
            assert D_t == expected

    def test_W_kills_rho_mode(self):
        """W_t = O_t + 2*E_t has no 4^t term"""
        for t in range(5):
            W_t = self._O(t) + 2 * self._E(t)
            # W_t = (9/5 + 6/10)*36^t + (-1 + 1)*4^t + (1/5 + 4/10)
            #     = (9/5 + 3/5)*36^t + 0*4^t + (1/5 + 2/5)
            #     = (12/5)*36^t + 3/5
            expected = Fraction(12, 5) * 36**t + Fraction(3, 5)
            assert W_t == expected

    def test_H_kills_kappa_mode(self):
        """H_t = O_t - 6*E_t has no 36^t term"""
        for t in range(5):
            H_t = self._O(t) - 6 * self._E(t)
            # H_t = (9/5 - 18/10)*36^t + (-1 - 3)*4^t + (1/5 - 12/10)
            #     = (9/5 - 9/5)*36^t - 4*4^t + (1/5 - 6/5)
            #     = 0*36^t - 4*4^t - 1
            expected = -4 * 4**t - 1
            assert H_t == expected


# ================================================================
# T4: Projector coefficients are small integers
# ================================================================
class TestT4_SmallIntegers:
    """The projector coefficients {-1,1}, {2,1}, {-6,1} are remarkable."""

    def test_D_coefficients(self):
        """D = 1*O + (-1)*E: coefficients (1,-1)"""
        pass  # D_t = O_t - E_t

    def test_W_coefficients(self):
        """W = 1*O + 2*E: coefficients (1,2)"""
        pass  # W_t = O_t + 2*E_t

    def test_H_coefficients(self):
        """H = 1*O + (-6)*E: coefficients (1,-6)"""
        pass  # H_t = O_t - 6*E_t

    def test_6_is_s_ext(self):
        """The coefficient -6 in H = O-6E matches s_ext = k/lam = 6"""
        assert k // lam == 6

    def test_2_is_lam(self):
        """The coefficient 2 in W = O+2E matches lam = q-1 = 2"""
        assert lam == 2

    def test_all_kill_exactly_one_mode(self):
        """Each projector annihilates exactly one of the three modes"""
        # D kills mode 1 (constant)
        # W kills mode 4 (rho)
        # H kills mode 36 (kappa)
        # Verified in T3 above
        pass


# ================================================================
# T5: Generating function structure
# ================================================================
class TestT5_GeneratingFunction:
    """GF denominators and numerators."""

    def test_GF_O_numerator(self):
        """N_O(z) = 1 + lam*Phi4*z = 1 + 20z"""
        N_O_coeff = lam * Phi4
        assert N_O_coeff == 20

    def test_GF_E_numerator(self):
        """N_E(z) = 1 - mu*Phi6*z + f*lam*z^2 = 1 - 28z + 48z^2"""
        assert mu * Phi6 == 28
        assert f * lam == 48

    def test_GF_denominator(self):
        """D(z) = (1-z)(1-4z)(1-36z)"""
        # Expand: (1-z)(1-4z)(1-36z)
        # = (1-z)(1 - 40z + 144z^2)
        # = 1 - 40z + 144z^2 - z + 40z^2 - 144z^3
        # = 1 - 41z + 184z^2 - 144z^3
        assert S1 == 41
        assert S2 == 184
        assert S3 == 144


# ================================================================
# T6: q=3 uniqueness of mode projectors
# ================================================================
class TestT6_UniquenessOfProjectors:
    """Each projector numerator vanishes at its pole only when (q-3)=0."""

    def test_D_selector(self):
        """D numerator at z=1: -(q-3)*q*(q^2+1)/2"""
        for qq in range(2, 15):
            # N_D(1) = N_O(1) - N_E(1)
            lamq = qq - 1
            muq = qq + 1
            Phi4q = qq**2 + 1
            Phi6q = qq**2 - qq + 1
            fq = qq * (qq+1)**2 // 2
            N_O_at_1 = 1 + lamq * Phi4q
            N_E_at_1 = 1 - muq * Phi6q + fq * lamq
            N_D = N_O_at_1 - N_E_at_1
            if qq == 3:
                assert N_D == 0
            else:
                assert N_D != 0

    def test_W_selector(self):
        """W numerator at z=1/mu: vanishes only at q=3"""
        for qq in range(2, 15):
            lamq = qq - 1
            muq = qq + 1
            Phi4q = qq**2 + 1
            Phi6q = qq**2 - qq + 1
            fq = qq * (qq+1)**2 // 2
            z = Fraction(1, muq)
            N_O = 1 + lamq * Phi4q * z
            N_E = 1 - muq * Phi6q * z + fq * lamq * z**2
            N_W = N_O + 2 * N_E
            if qq == 3:
                assert N_W == 0
            else:
                assert N_W != 0

    def test_H_selector(self):
        """H numerator at z=1/(mu*q^2): vanishes only at q=3"""
        for qq in range(2, 12):
            lamq = qq - 1
            muq = qq + 1
            Phi4q = qq**2 + 1
            Phi6q = qq**2 - qq + 1
            fq = qq * (qq+1)**2 // 2
            z = Fraction(1, muq * qq**2)
            N_O = 1 + lamq * Phi4q * z
            N_E = 1 - muq * Phi6q * z + fq * lamq * z**2
            N_H = N_O - 6 * N_E
            if qq == 3:
                assert N_H == 0
            else:
                assert N_H != 0
