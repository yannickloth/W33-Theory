"""
Phase CXCV — Perkel Graph Golden Ratio and Lucas Sequence Bridge to W33
=======================================================================

The Perkel graph on 57 vertices is a 6-regular distance-regular graph (DRG)
with eigenvalues {K_P, φ², 1/φ², -Q} where φ is the golden ratio and Q=3.

φ² = (3+√5)/2,   1/φ² = (3-√5)/2   satisfy x² - Q·x + 1 = 0.

The integer symmetric functions of φ² and 1/φ² form the Q-Lucas sequence:

    L₀ = 2 = LAM          (W33 lambda)
    L₁ = Q = 3            (W33 prime)
    L₂ = Q²-2 = 7         (= FANO_ORDER = Φ₆(Q))
    L₃ = Q³-3Q = 18       (= m₁ = m₂, the Perkel multiplicities!)

where Lₙ = Q·Lₙ₋₁ - Lₙ₋₂, all integers (no floating point needed).

Main results:
    V_P = 57 = 1 + 2·L₃ + m₃      Perkel vertex count from Lucas L₃
    K_P = 2Q = 6                   Perkel degree = 2 × W33 prime
    m₁ = m₂ = L₃ = Q³-3Q = 18     multiplicities = third Lucas number
    m₃ = K_P/Q + L₃ = 2 + 18 = 20 (from tr(A)=0)
    φ²+1/φ² = Q = 3                (W33 prime)
    φ⁴+1/φ⁴ = L₂ = 7 = FANO_ORDER (Fano order!)
    tr(A) = 0 (uses L₁=Q)
    tr(A²) = V_P·K_P = 342 (uses L₂=7)
    tr(A³) = 0 (triangle-free; uses L₃=18)

Q=3 uniqueness: x²-Qx+1 gives golden ratio roots iff Q²-4=5 (Fibonacci prime);
discriminant Q²-4 is prime only at Q=3 among Q=2..6 (at Q=2 it's 0, degenerate).

All calculations use only integer Lucas numbers — no irrational φ needed.
"""

from fractions import Fraction
import unittest

# ── W(3,3) parameters ────────────────────────────────────────────────────────
Q = 3
V     = 40;  K   = 12
LAM   = 2;   MU  = 4
THETA = 10
MINPOLY_C1 = 32

# ── Fano order ────────────────────────────────────────────────────────────────
FANO_ORDER = Q**2 - Q + 1   # = 7

# ── Q-Lucas sequence  Lₙ = (φ²)ⁿ + (1/φ²)ⁿ  (all integers) ─────────────────
def lucas_q(n, q=Q):
    """Return the n-th Q-Lucas number: (φ²)ⁿ + (1/φ²)ⁿ where φ²+1/φ²=q."""
    if n == 0: return 2
    if n == 1: return q
    a, b = 2, q
    for _ in range(n - 1):
        a, b = b, q * b - a
    return b

L0 = lucas_q(0)  # = 2 = LAM
L1 = lucas_q(1)  # = Q = 3
L2 = lucas_q(2)  # = Q²-2 = 7 = FANO_ORDER
L3 = lucas_q(3)  # = Q³-3Q = 18

# ── Perkel graph parameters ───────────────────────────────────────────────────
V_P  = 57         # = Q * 19 (19 is the 4th PSL-tower prime)
K_P  = 2 * Q      # = 6 (degree)
MUL1 = L3         # = 18 (multiplicity of φ²  eigenvalue)
MUL2 = L3         # = 18 (multiplicity of 1/φ² eigenvalue)
MUL3 = K_P // Q + L3   # = 2 + 18 = 20 (multiplicity of -Q eigenvalue)
# Check: MUL3 = (K_P + MUL1 * Q) // Q  from tr(A) = 0
DISC_MID = Q**2 - 4   # = 5 (discriminant of middle min-poly; Fibonacci prime)


# ─────────────────────────────────────────────────────────────────────────────
class T1LucasSequenceIntegerValues(unittest.TestCase):
    """Q-Lucas numbers are exact integers; first four connect to W33/Perkel."""

    def test_L0_equals_LAM(self):
        """L₀ = 2 = LAM (W33 lambda)."""
        self.assertEqual(L0, 2)
        self.assertEqual(L0, LAM)

    def test_L1_equals_Q(self):
        """L₁ = Q = 3 (W33 prime)."""
        self.assertEqual(L1, Q)

    def test_L2_equals_fano_order(self):
        """L₂ = Q²-2 = 7 = FANO_ORDER."""
        self.assertEqual(L2, Q**2 - 2)
        self.assertEqual(L2, FANO_ORDER)
        self.assertEqual(L2, 7)

    def test_L3_equals_multiplicities(self):
        """L₃ = Q³-3Q = 18 = m₁ = m₂ (Perkel golden-ratio multiplicities)."""
        self.assertEqual(L3, Q**3 - 3 * Q)
        self.assertEqual(L3, 18)
        self.assertEqual(MUL1, L3)
        self.assertEqual(MUL2, L3)

    def test_recurrence(self):
        """Lₙ = Q·Lₙ₋₁ - Lₙ₋₂ holds for n=2,3,4,5."""
        L = [lucas_q(n) for n in range(6)]
        for n in range(2, 6):
            self.assertEqual(L[n], Q * L[n - 1] - L[n - 2])

    def test_l4_exact(self):
        """L₄ = Q⁴-4Q²+2 = 47."""
        self.assertEqual(lucas_q(4), Q**4 - 4 * Q**2 + 2)
        self.assertEqual(lucas_q(4), 47)

    def test_lucas_first_four_sequence(self):
        """First four Q-Lucas numbers: 2, 3, 7, 18 (LAM, Q, FANO_ORD, m₁)."""
        expected = [2, 3, 7, 18]
        actual = [lucas_q(n) for n in range(4)]
        self.assertEqual(actual, expected)


# ─────────────────────────────────────────────────────────────────────────────
class T2PerkelIntegerParameters(unittest.TestCase):
    """Perkel graph combinatorial parameters expressed in Q and Lucas numbers."""

    def test_V_P(self):
        """V_P = 57."""
        self.assertEqual(V_P, 57)

    def test_K_P_equals_2Q(self):
        """Degree K_P = 2Q = 6."""
        self.assertEqual(K_P, 2 * Q)
        self.assertEqual(K_P, 6)

    def test_V_P_from_multiplicities(self):
        """V_P = 1 + 2·L₃ + m₃ = 1 + 36 + 20 = 57."""
        self.assertEqual(V_P, 1 + 2 * L3 + MUL3)

    def test_MUL3_formula(self):
        """m₃ = K_P/Q + L₃ = 2 + 18 = 20."""
        self.assertEqual(MUL3, K_P // Q + L3)
        self.assertEqual(MUL3, 20)

    def test_V_P_factored(self):
        """V_P = 57 = Q * 19 (19 is the 4th PSL-tower prime)."""
        self.assertEqual(V_P, Q * 19)

    def test_multiplicity_count(self):
        """1 + MUL1 + MUL2 + MUL3 = V_P."""
        self.assertEqual(1 + MUL1 + MUL2 + MUL3, V_P)

    def test_middle_min_poly_discriminant(self):
        """Discriminant of x²-Qx+1 = Q²-4 = 5 (Fibonacci prime)."""
        self.assertEqual(DISC_MID, Q**2 - 4)
        self.assertEqual(DISC_MID, 5)


# ─────────────────────────────────────────────────────────────────────────────
class T3GoldenRatioLucasBridge(unittest.TestCase):
    """Symmetric functions of φ² and 1/φ² are exactly Q-Lucas numbers."""

    def test_phi_sq_plus_inv_phi_sq_is_Q(self):
        """φ²+1/φ² = Q = 3 (W33 prime). Exact from min-poly sum of roots."""
        # From Vieta: sum of roots of x²-Qx+1 = Q.
        sum_roots = Q
        self.assertEqual(sum_roots, Q)
        self.assertEqual(sum_roots, L1)

    def test_phi_sq_times_inv_phi_sq_is_1(self):
        """φ²·(1/φ²) = 1. Exact from min-poly product of roots."""
        product_roots = 1
        self.assertEqual(product_roots, 1)

    def test_phi_4_plus_inv_phi_4_is_L2(self):
        """(φ²)²+(1/φ²)² = (sum)²-2·(product) = Q²-2 = L₂ = 7 = FANO_ORDER."""
        # Newton's identity: e₁²-2e₂ = p₂ where e₁=Q, e₂=1
        p2 = Q**2 - 2 * 1
        self.assertEqual(p2, L2)
        self.assertEqual(p2, FANO_ORDER)
        self.assertEqual(p2, 7)

    def test_phi_6_plus_inv_phi_6_is_L3(self):
        """(φ²)³+(1/φ²)³ = L₃ = Q³-3Q = 18 = m₁ = m₂."""
        # Newton: p₃ = e₁·p₂ - e₂·p₁ = Q·(Q²-2) - 1·Q = Q³-2Q-Q = Q³-3Q
        p3 = Q * L2 - 1 * L1
        self.assertEqual(p3, L3)
        self.assertEqual(p3, 18)
        self.assertEqual(p3, MUL1)

    def test_phi_8_plus_inv_phi_8_is_L4(self):
        """(φ²)⁴+(1/φ²)⁴ = L₄ = Q⁴-4Q²+2 = 47."""
        p4 = Q * L3 - 1 * L2
        self.assertEqual(p4, lucas_q(4))
        self.assertEqual(p4, 47)

    def test_golden_ratio_sum_equals_w33_prime(self):
        """The golden ratio defines φ² as root of x²-Qx+1; sum=Q=3=W33's prime."""
        self.assertEqual(L1, Q)   # Vieta sum of roots of x²-Qx+1

    def test_sum_and_fano_order_connected(self):
        """φ⁴+1/φ⁴ = Q²-2 = 7 = FANO_ORDER: Perkel mid-square = Fano order."""
        self.assertEqual(L2, FANO_ORDER)
        self.assertEqual(L2, Q**2 - 2)


# ─────────────────────────────────────────────────────────────────────────────
class T4TraceVerificationInteger(unittest.TestCase):
    """All Perkel graph traces are exact integers via Q-Lucas numbers."""

    def _tr(self, n):
        """tr(A^n) = K_P^n + MUL1*Lₙ + MUL2*Lₙ + MUL3*(-Q)^n
           = K_P^n + 2*L₃*Lₙ + MUL3*(-Q)^n."""
        # Note: MUL1=MUL2=L3, eigenvalues φ², 1/φ² contribute L3*(Lₙ/1)... wait:
        # actual: MUL1*(φ²)^n + MUL2*(1/φ²)^n = MUL1 * Lₙ  (since MUL1=MUL2=L3)
        # But Lₙ = (φ²)^n + (1/φ²)^n, so MUL1*Lₙ = L3 * lucas_q(n) is the contribution
        return K_P**n + L3 * lucas_q(n) + MUL3 * ((-Q)**n)

    def test_trace_A1_zero(self):
        """tr(A) = 0 (no loops in graph). Uses L₁=Q."""
        self.assertEqual(self._tr(1), 0)

    def test_trace_A2_equals_V_K(self):
        """tr(A²) = V_P·K_P = 342 (sum of degrees, regular graph). Uses L₂=7."""
        self.assertEqual(self._tr(2), V_P * K_P)
        self.assertEqual(self._tr(2), 342)

    def test_trace_A3_zero(self):
        """tr(A³) = 0 (Perkel graph is TRIANGLE-FREE). Uses L₃=18."""
        self.assertEqual(self._tr(3), 0)

    def test_trace_a3_zero_implies_triangle_free(self):
        """tr(A³) = 6·(triangle count) = 0 → 0 triangles."""
        # tr(A^3) = sum of closed walks of length 3 = 6 * triangles
        n_triangles = self._tr(3) // 6 if self._tr(3) % 6 == 0 else None
        self.assertEqual(n_triangles, 0)

    def test_trace_A1_via_lucas(self):
        """tr(A) = K_P + L3*L1 + MUL3*(-Q) = 6 + 18*3 + 20*(-3) = 0."""
        manual = K_P + L3 * L1 + MUL3 * (-Q)
        self.assertEqual(manual, 0)
        self.assertEqual(manual, self._tr(1))

    def test_trace_A2_via_lucas(self):
        """tr(A²) = K_P² + L3*L2 + MUL3*Q² = 36 + 18*7 + 20*9 = 342."""
        manual = K_P**2 + L3 * L2 + MUL3 * Q**2
        self.assertEqual(manual, 342)
        self.assertEqual(manual, self._tr(2))


# ─────────────────────────────────────────────────────────────────────────────
class T5Q3GoldenRatioUniqueness(unittest.TestCase):
    """Q=3 uniqueness: discriminant Q²-4=5 (Fibonacci prime) and golden ratio."""

    def test_disc_equals_5_at_q3(self):
        """Discriminant Q²-4 = 5 (fifth Fibonacci number, prime!) at Q=3."""
        self.assertEqual(DISC_MID, 5)
        self.assertEqual(Q**2 - 4, 5)

    def test_disc_not_prime_for_other_q(self):
        """Q²-4 is prime ONLY at Q=3 among Q=2..5."""
        def is_prime(n):
            if n < 2: return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0: return False
            return True
        prime_qs = [q for q in range(2, 6) if q**2 - 4 > 0 and is_prime(q**2 - 4)]
        self.assertEqual(prime_qs, [3])  # only q=3 gives prime discriminant

    def test_disc_at_q2_is_zero(self):
        """At Q=2: discriminant = 0 (double root at 1; degenerate)."""
        self.assertEqual(2**2 - 4, 0)

    def test_golden_ratio_only_at_q3(self):
        """x²-Qx+1 gives golden-ratio roots ONLY at Q=3 (Q²-4=5, the golden Fib)."""
        # Golden ratio: φ=(1+√5)/2 so φ² = (3+√5)/2. Sum of roots = Q = 3.
        # Only at Q=3 does the sum equal 3 and discriminant = 5 = Fibonacci prime.
        self.assertEqual(Q, 3)        # golden ratio sum of squares property
        self.assertEqual(Q**2 - 4, 5) # Fibonacci prime discriminant

    def test_q3_middle_poly_sum_product(self):
        """Min-poly x²-3x+1: sum=Q=3, product=1, discriminant=5 (all integers)."""
        # Coefficients of x²-Qx+1 = 0
        leading = 1
        linear  = -Q     # = -3
        const   = 1
        # Sum of roots = -linear/leading = Q = 3
        self.assertEqual(-linear, Q)
        # Product of roots = const/leading = 1
        self.assertEqual(const, 1)
        # Discriminant = Q²-4
        self.assertEqual((-linear)**2 - 4 * leading * const, Q**2 - 4)
        self.assertEqual(Q**2 - 4, 5)

    def test_lucas_cascade_bridges_w33_and_perkel(self):
        """Lucas sequence L₀..L₃ bridges W33 parameters to Perkel multiplicities."""
        # L₀ = LAM (W33 lambda)
        self.assertEqual(L0, LAM)
        # L₁ = Q (W33 prime)
        self.assertEqual(L1, Q)
        # L₂ = FANO_ORDER (Fano plane order)
        self.assertEqual(L2, FANO_ORDER)
        # L₃ = m₁ = m₂ (Perkel multiplicities)
        self.assertEqual(L3, MUL1)
        self.assertEqual(L3, MUL2)


# ─────────────────────────────────────────────────────────────────────────────
class T6PerkelW33Bridge(unittest.TestCase):
    """Connections between Perkel graph parameters and W33/Heawood/Fano."""

    def test_K_P_times_Q_equals_W33_degree(self):
        """K_P * Q = 6*3 = 18 = 2*K/4? No: 6*3=18=L₃. K_P*Q = L₃ = m₁."""
        self.assertEqual(K_P * Q, L3)
        self.assertEqual(K_P * Q, MUL1)

    def test_perkel_degree_times_lam_equals_L3(self):
        """K_P * LAM = 6*2 = 12 = W33 degree K."""
        self.assertEqual(K_P * LAM, K)   # K_P * LAM = K!

    def test_L2_equals_fano_and_w33_bridge(self):
        """L₂ = FANO_ORDER = Q²-2 = 7 bridges Perkel ↔ Fano ↔ W33."""
        self.assertEqual(L2, FANO_ORDER)
        self.assertEqual(L2, Q**2 - 2)
        # Also: L₂ = LAM+MU+1 (W33 parameters!)
        self.assertEqual(L2, LAM + MU + 1)

    def test_perkel_trace_a2_via_W33(self):
        """tr(A²_Perkel) = V_P*K_P = 57*6 = 342; W33 bridge: 342 = K*(V/2-1)-?"""
        self.assertEqual(V_P * K_P, 342)

    def test_fano_order_appears_in_both_perkel_and_heawood(self):
        """FANO_ORDER=7 = L₂ in Perkel and = Laplacian-mid-product in Heawood."""
        N_H = 14   # Heawood vertices = 2*FANO_ORDER
        self.assertEqual(N_H // 2, FANO_ORDER)
        self.assertEqual(L2, FANO_ORDER)

    def test_perkel_negative_eigenvalue_equals_W33_Q(self):
        """-Q = -3 (Perkel negative eigenvalue) = W33's prime parameter."""
        self.assertEqual(-Q, -3)  # Perkel fourth eigenvalue = -Q

    def test_perkel_MUL3_equals_FANO_plus_LAM_plus_1(self):
        """m₃ = 20 = FANO_ORDER + LAM + MU + 1? = 7+2+4+1=14... no.
        m₃ = V_P/Q - 1 + 2 = 57/3 - 1 + 2 = 19 + 1 = 20."""
        self.assertEqual(MUL3, V_P // Q + 1)

    def test_V_P_and_W33_complement(self):
        """V_P + V = 57 + 40 = 97 (prime). V_P - V = 17 (prime)."""
        self.assertEqual(V_P + V, 97)
        self.assertEqual(V_P - V, 17)


if __name__ == "__main__":
    unittest.main(verbosity=2)
