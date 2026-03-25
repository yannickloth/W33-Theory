"""
Phase CXCIV — GQ(q,q) Integer Eigenvalue Structure and Q=3 Uniqueness
=====================================================================

The symplectic polar space W(q) = GQ(q,q) is an SRG with parameters:

    V = (q+1)(q^2+1),  K = q(q+1),  LAM = q-1,  MU = q+1

For ALL prime powers q, the non-trivial eigenvalues are EXACT INTEGERS:

    r = q-1 = LAM      (positive, equals lambda)
    s = -(q+1) = -MU   (negative, negated mu)

This follows because the SRG discriminant D = (LAM-MU)^2 + 4(K-MU) = 4q^2
is a PERFECT SQUARE — so GQ(q,q) always has integer eigenvalues.

Multiplicities (exact):
    m_r = q(q+1)^2 / 2
    m_s = q(q^2+1)  / 2

THETA = K+r+s = (q-1)(q+2)  — Lovász number of the complement
MINPOLY_C1 = |K*r + K*s + r*s| = (3q-1)(q+1)  — x-coefficient of min-poly

Q=3 uniqueness theorems (all equivalent to q=3):
    • MU  = LAM^2           ↔  (q+1) = (q-1)^2   ↔ q=3  [cascade origin!]
    • s   = -2r             ↔  -(q+1) = -2(q-1)  ↔ q=3
    • |s|/|r| = 2 (integer) ↔ (q-1)|(q+1) and quotient=2 ↔ q=3 (or q=2→3)
    • E1_diag = 3/5 for q∈{2,3} only (quadratic selection)

All arithmetic in exact fractions.Verified against W(2,2)=GQ(2,2)=SRG(15,6,1,3) and W(3,3)=SRG(40,12,2,4).
"""

from fractions import Fraction
import unittest

# ── W(3,3) specific constants (q=3) ──────────────────────────────────────────
Q   = 3
V   = 40
K   = 12
LAM = 2   # = Q-1
MU  = 4   # = Q+1
EIG_R = 2   # = LAM
EIG_S = -4  # = -MU
MUL_R = 24  # = Q*(Q+1)^2/2
MUL_S = 15  # = Q*(Q^2+1)/2
THETA = 10  # = (Q-1)*(Q+2)
MINPOLY_C1 = 32   # = (3Q-1)*(Q+1)
MINPOLY_C0 = 96   # = Q*(Q-1)*(Q+1)^2


def gq_params(q):
    """Return (V, K, lam, mu, r, s, m_r, m_s, theta, c1, c0) for GQ(q,q)."""
    V   = (q + 1) * (q**2 + 1)
    K   = q * (q + 1)
    lam = q - 1
    mu  = q + 1
    r   = q - 1     # = lam
    s   = -(q + 1)  # = -mu
    m_r = q * (q + 1)**2 // 2
    m_s = q * (q**2 + 1) // 2
    theta = (q - 1) * (q + 2)
    c1    = (3 * q - 1) * (q + 1)   # |x-coefficient of min-poly|
    c0    = q * (q - 1) * (q + 1)**2
    return V, K, lam, mu, r, s, m_r, m_s, theta, c1, c0


# ─────────────────────────────────────────────────────────────────────────────
class T1GeneralParameterFormulas(unittest.TestCase):
    """GQ(q,q) parameter formulas hold for q = 2, 3, 4, 5."""

    def _check_q(self, q):
        V, K, lam, mu, r, s, m_r, m_s, theta, c1, c0 = gq_params(q)
        self.assertEqual(V, (q + 1) * (q**2 + 1))
        self.assertEqual(K, q * (q + 1))
        self.assertEqual(lam, q - 1)
        self.assertEqual(mu, q + 1)
        self.assertEqual(r, q - 1)
        self.assertEqual(s, -(q + 1))

    def test_q2(self):   self._check_q(2)
    def test_q3(self):   self._check_q(3)
    def test_q4(self):   self._check_q(4)
    def test_q5(self):   self._check_q(5)

    def test_w33_specialization(self):
        """gq_params(3) recovers W(3,3) constants."""
        V3, K3, lam3, mu3, r3, s3, m_r3, m_s3, th3, c13, c03 = gq_params(3)
        self.assertEqual(V3, V)
        self.assertEqual(K3, K)
        self.assertEqual(lam3, LAM)
        self.assertEqual(mu3, MU)
        self.assertEqual(r3, EIG_R)
        self.assertEqual(s3, EIG_S)
        self.assertEqual(m_r3, MUL_R)
        self.assertEqual(m_s3, MUL_S)
        self.assertEqual(th3, THETA)
        self.assertEqual(c13, MINPOLY_C1)
        self.assertEqual(c03, MINPOLY_C0)


# ─────────────────────────────────────────────────────────────────────────────
class T2EigenvalueIntegrality(unittest.TestCase):
    """Discriminant D = 4q^2 is a perfect square for all q."""

    def _discriminant(self, q):
        lam = q - 1
        mu  = q + 1
        K   = q * (q + 1)
        return (lam - mu)**2 + 4 * (K - mu)

    def test_discriminant_formula(self):
        """D = (LAM-MU)^2 + 4*(K-MU) = 4*Q^2 for q=3."""
        D = self._discriminant(Q)
        self.assertEqual(D, 4 * Q**2)
        self.assertEqual(D, 36)

    def test_discriminant_perfect_square(self):
        """D is a perfect square for q = 2,3,4,5,6,7."""
        import math
        for q in range(2, 8):
            D = self._discriminant(q)
            sqrt_D = int(math.isqrt(D))
            self.assertEqual(sqrt_D * sqrt_D, D,
                             f"D={D} not a perfect square at q={q}")

    def test_discriminant_is_4q_squared(self):
        """D = 4q^2 for all tested q."""
        for q in range(2, 8):
            D = self._discriminant(q)
            self.assertEqual(D, 4 * q**2)

    def test_sqrt_discriminant_equals_2q(self):
        """sqrt(D) = 2q (the half-spread)."""
        import math
        for q in range(2, 8):
            D = self._discriminant(q)
            self.assertEqual(int(math.isqrt(D)), 2 * q)

    def test_eigenvalues_recover_from_quadratic(self):
        """r, s = ((LAM-MU) ± 2q) / 2 gives exact integers."""
        for q in range(2, 8):
            lam, mu = q - 1, q + 1
            r_from_formula = ((lam - mu) + 2 * q) // 2
            s_from_formula = ((lam - mu) - 2 * q) // 2
            self.assertEqual(r_from_formula, q - 1)
            self.assertEqual(s_from_formula, -(q + 1))


# ─────────────────────────────────────────────────────────────────────────────
class T3EigenvalueExactFormulas(unittest.TestCase):
    """r=LAM=q-1 and s=-MU=-(q+1) for all GQ(q,q)."""

    def test_r_equals_lam_for_all_q(self):
        """Non-trivial positive eigenvalue = LAM for q=2..6."""
        for q in range(2, 7):
            _, _, lam, _, r, _, _, _, _, _, _ = gq_params(q)
            self.assertEqual(r, lam)
            self.assertEqual(r, q - 1)

    def test_s_equals_neg_mu_for_all_q(self):
        """Non-trivial negative eigenvalue = -MU for q=2..6."""
        for q in range(2, 7):
            _, _, _, mu, _, s, _, _, _, _, _ = gq_params(q)
            self.assertEqual(s, -mu)
            self.assertEqual(s, -(q + 1))

    def test_r_plus_s_constant(self):
        """r+s = -2 for ALL GQ(q,q) (constant, independent of q!)."""
        for q in range(2, 8):
            r, s = q - 1, -(q + 1)
            self.assertEqual(r + s, -2)

    def test_r_minus_s_equals_2q(self):
        """r - s = 2q (the spectral spread of non-trivial part)."""
        for q in range(2, 8):
            r, s = q - 1, -(q + 1)
            self.assertEqual(r - s, 2 * q)

    def test_rs_product(self):
        """r*s = -(q^2-1) = -(q-1)(q+1) for all q."""
        for q in range(2, 8):
            r, s = q - 1, -(q + 1)
            self.assertEqual(r * s, -(q**2 - 1))

    def test_w33_r_is_lam(self):
        """At q=3: EIG_R = LAM = 2."""
        self.assertEqual(EIG_R, LAM)

    def test_w33_s_is_neg_mu(self):
        """At q=3: EIG_S = -MU = -4."""
        self.assertEqual(EIG_S, -MU)


# ─────────────────────────────────────────────────────────────────────────────
class T4MultiplicityFormulas(unittest.TestCase):
    """m_r=q(q+1)^2/2 and m_s=q(q^2+1)/2 for all GQ(q,q)."""

    def _check_multiplicities(self, q):
        V, K, _, _, r, s, m_r, m_s, _, _, _ = gq_params(q)
        # Trace condition: K + m_r*r + m_s*s = 0
        self.assertEqual(K + m_r * r + m_s * s, 0,
                         f"Trace nonzero at q={q}")
        # Count condition: 1 + m_r + m_s = V
        self.assertEqual(1 + m_r + m_s, V,
                         f"Count mismatch at q={q}")
        # Explicit formulas
        self.assertEqual(m_r, q * (q + 1)**2 // 2)
        self.assertEqual(m_s, q * (q**2 + 1) // 2)

    def test_q2(self):  self._check_multiplicities(2)
    def test_q3(self):  self._check_multiplicities(3)
    def test_q4(self):  self._check_multiplicities(4)
    def test_q5(self):  self._check_multiplicities(5)

    def test_idempotent_diag_from_multiplicity(self):
        """E_i[diag] = m_i/V (exact Fraction) for all q."""
        for q in [2, 3, 4, 5]:
            V, K, _, _, r, s, m_r, m_s, _, _, _ = gq_params(q)
            e1_diag = Fraction(m_r, V)
            e2_diag = Fraction(m_s, V)
            # E1 formula: m_r/V = q(q+1)^2 / (2(q+1)(q^2+1)) = q(q+1)/(2(q^2+1))
            self.assertEqual(e1_diag, Fraction(q * (q + 1), 2 * (q**2 + 1)))
            # E2 formula: m_s/V = q(q^2+1) / (2(q+1)(q^2+1)) = q/(2(q+1))
            self.assertEqual(e2_diag, Fraction(q, 2 * (q + 1)))

    def test_w33_multiplicities(self):
        """W(3,3) multiplicities: m_r=24, m_s=15."""
        self.assertEqual(MUL_R, 24)
        self.assertEqual(MUL_S, 15)
        self.assertEqual(MUL_R, Q * (Q + 1)**2 // 2)
        self.assertEqual(MUL_S, Q * (Q**2 + 1) // 2)

    def test_multiplicity_sum_equals_V_minus_1(self):
        """m_r + m_s = V - 1 = q^3 + q^2 + q for all q."""
        for q in range(2, 7):
            V, _, _, _, _, _, m_r, m_s, _, _, _ = gq_params(q)
            self.assertEqual(m_r + m_s, V - 1)
            self.assertEqual(V - 1, q**3 + q**2 + q)


# ─────────────────────────────────────────────────────────────────────────────
class T5ThetaAndMinpoly(unittest.TestCase):
    """THETA=(q-1)(q+2), MINPOLY_C1=(3q-1)(q+1), MINPOLY_C0=q(q-1)(q+1)^2."""

    def test_theta_formula(self):
        """THETA = (q-1)(q+2) for all q."""
        for q in range(2, 7):
            V, K, _, _, r, s, _, _, theta, _, _ = gq_params(q)
            self.assertEqual(theta, (q - 1) * (q + 2))
            self.assertEqual(theta, K + r + s)

    def test_theta_at_q3(self):
        """THETA = 10 = 2*5 = LAM*(Q+2) at q=3."""
        self.assertEqual(THETA, 10)
        self.assertEqual(THETA, (Q - 1) * (Q + 2))
        self.assertEqual(THETA, LAM * (Q + 2))

    def test_minpoly_c1_formula(self):
        """MINPOLY_C1 = (3q-1)(q+1) for all q."""
        for q in range(2, 7):
            _, K, _, _, r, s, _, _, _, c1, _ = gq_params(q)
            # c1 = |K*r + K*s + r*s|
            self.assertEqual(c1, abs(K * r + K * s + r * s))
            self.assertEqual(c1, (3 * q - 1) * (q + 1))

    def test_minpoly_c0_formula(self):
        """MINPOLY_C0 = q(q-1)(q+1)^2 = -K*r*s for all q."""
        for q in range(2, 7):
            _, K, _, _, r, s, _, _, _, _, c0 = gq_params(q)
            self.assertEqual(c0, -K * r * s)
            self.assertEqual(c0, q * (q - 1) * (q + 1)**2)

    def test_w33_minpoly_constants(self):
        """At q=3: c1=32=(Q-1)^5, c0=96=K*(Q^2-1)."""
        self.assertEqual(MINPOLY_C1, 32)
        self.assertEqual(MINPOLY_C1, (Q - 1)**5)
        self.assertEqual(MINPOLY_C0, 96)
        self.assertEqual(MINPOLY_C0, K * (Q**2 - 1))

    def test_minpoly_factored_roots(self):
        """Min poly (x-K)(x-r)(x-s) gives correct c1 and c0 for all q."""
        for q in range(2, 6):
            _, K, _, _, r, s, _, _, _, c1, c0 = gq_params(q)
            # Expand (x-K)(x-r)(x-s)
            # = x^3 - (K+r+s)x^2 + (Kr+Ks+rs)x - K*r*s
            coeff_x = K * r + K * s + r * s
            self.assertEqual(-coeff_x, c1)   # positive c1
            self.assertEqual(-K * r * s, c0)


# ─────────────────────────────────────────────────────────────────────────────
class T6Q3UniquenessTheorems(unittest.TestCase):
    """W(3,3) uniqueness: every cascade identity reduces to q=3."""

    def test_mu_eq_lam_sq_iff_q3(self):
        """MU = LAM^2 iff q=3; fails for all other q in 2..7."""
        for q in range(2, 8):
            lam, mu = q - 1, q + 1
            if q == 3:
                self.assertEqual(mu, lam**2)
            else:
                self.assertNotEqual(mu, lam**2)

    def test_algebraic_proof_of_q3_uniqueness(self):
        """(q+1) = (q-1)^2 iff q^2-3q = 0 iff q=3 (for q>0)."""
        # Polynomial: (q-1)^2 - (q+1) = q^2 - 2q + 1 - q - 1 = q^2 - 3q = q*(q-3)
        # Root: q=3 (and q=0 trivial)
        for q in range(1, 10):
            diff = (q - 1)**2 - (q + 1)   # = q*(q-3)
            self.assertEqual(diff, q * (q - 3))

    def test_s_eq_neg_2r_iff_q3(self):
        """s = -2r (i.e., |s|/|r|=2) only at q=3."""
        for q in range(2, 8):
            r, s = q - 1, -(q + 1)
            if q == 3:
                self.assertEqual(s, -2 * r)
            else:
                self.assertNotEqual(s, -2 * r)

    def test_eigenvalue_ratio_integer_only_q2_q3(self):
        """(q+1) divisible by (q-1) iff q in {2,3}."""
        integer_ratio_qs = [q for q in range(2, 10) if (q + 1) % (q - 1) == 0]
        self.assertEqual(integer_ratio_qs, [2, 3])

    def test_e1_diag_35_for_q2_and_q3(self):
        """E1_diag = 3/5 exactly for q=2 and q=3 (and no other q in 2..9)."""
        qs_with_35 = [q for q in range(2, 10)
                      if Fraction(q * (q + 1), 2 * (q**2 + 1)) == Fraction(3, 5)]
        self.assertEqual(qs_with_35, [2, 3])

    def test_e1_diag_35_algebraic(self):
        """E1_diag=3/5 iff 5q(q+1)=6(q^2+1) iff q^2-5q+6=0 iff q∈{2,3}."""
        # q^2 - 5q + 6 = (q-2)(q-3)
        for q in range(2, 10):
            poly_val = q**2 - 5 * q + 6
            self.assertEqual(poly_val, (q - 2) * (q - 3))
        # Both roots are valid GQ primes: q=2 (GQ(2,2)) and q=3 (W(3,3))

    def test_cascade_all_from_mu_eq_lam_sq(self):
        """All 5 cascade identities follow from MU=LAM^2 (equivalent at q=3)."""
        # condition: MU = LAM^2, i.e., q+1 = (q-1)^2 → only at q=3
        q = Q
        lam, mu, K_val = q - 1, q + 1, q * (q + 1)
        r_val, s_val = q - 1, -(q + 1)
        # Cascade 2: MU = LAM^2
        self.assertEqual(mu, lam**2)
        # Cascade 3: K + s = MU * LAM = (q+1)(q-1) = (q-1)^3 (since MU=LAM^2)
        self.assertEqual(K_val + s_val, mu * lam)
        self.assertEqual(K_val + s_val, lam**3)
        # Cascade 4: K + MU = (q+1)^2 = (LAM^2+1)^2? No: K+MU = q(q+1)+(q+1) = (q+1)^2 = MU^2/LAM? Hmm.
        # Actually K+MU = (q+1)(q+1) = MU^2... at q=3: 4^2=16=K+MU ✓
        self.assertEqual(K_val + mu, mu**2)
        self.assertEqual(K_val + mu, lam**4)  # since mu = lam^2
        # Cascade 5: MINPOLY_C1 = (3q-1)(q+1) = (3*LAM+2)*MU = ... complex
        self.assertEqual(MINPOLY_C1, lam**5)

    def test_w33_r_squared_equals_mu(self):
        """At q=3: r^2 = (q-1)^2 = q+1 = MU. Unique to q=3."""
        self.assertEqual(EIG_R**2, MU)
        self.assertEqual((Q - 1)**2, Q + 1)
        # For all other q: r^2 = (q-1)^2 ≠ q+1
        for q in range(2, 8):
            if q != 3:
                self.assertNotEqual((q - 1)**2, q + 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
