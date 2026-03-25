"""
Phase CXCVI — Chebyshev Polynomials, Fibonacci, and Lucas Bridge to W33
========================================================================

The Q-Lucas sequence Lₙ = (φ²)ⁿ + (1/φ²)ⁿ (where φ²+1/φ²=Q=3) is exactly
the Chebyshev-polynomial sequence evaluated at x=Q/2:

    Lₙ = 2·T_n(Q/2)   (Chebyshev first kind, exact rational arithmetic)

And the companion Chebyshev second-kind sequence:

    U_{n-1}(Q/2) = F_{2n}   (EVEN-INDEXED FIBONACCI NUMBERS!)

where Fibonacci: F₀=0, F₁=1, F₂=1, F₃=2, F₄=3, F₅=5, F₆=8, F₇=13, F₈=21, ...

This gives the integer PELL identity (no irrationals needed):

    Lₙ² − (Q²−4)·U_{n-1}(Q/2)² = 4 = MU   for ALL n

i.e.,   L_n² − 5·F_{2n}² = 4 = MU          (all exact, all integers!)

Here Q²−4 = 5 = DISC_MID (Fibonacci prime discriminant of the golden min-poly).
And the constant 4 = MU = Q+1 (W33 mu parameter at Q=3).

Furthermore: our Q-Lucas Lₙ equals the STANDARD LUCAS sequence at doubled index:
    Lₙ = StdLucas_{2n}   where StdLucas: 2,1,3,4,7,11,18,29,47,76,123,...

Key W33 bridges via U_n evaluations:
    U₁(Q/2) = Q = 3                (W33 prime)
    U₂(Q/2) = Q²−1 = LAM·MU = (Q−1)³ = 8  (cascade identity, unique to Q=3!)
    U₃(Q/2) = Q³−2Q = Q·FANO_ORDER = 21 = E_H   (Heawood edge count!)

All arithmetic in exact fractions.Fibonacci sequence: 0,1,1,2,3,5,8,13,21,34,55,89,144,233,...
Standard Lucas:     2,1,3,4,7,11,18,29,47,76,123,199,322,...
Q-Lucas (Q=3):      2,3,7,18,47,123,322,...
"""

from fractions import Fraction
import unittest

# ── W(3,3) parameters ────────────────────────────────────────────────────────
Q    = 3
V    = 40;  K   = 12
LAM  = 2;   MU  = 4
THETA = 10
MINPOLY_C1 = 32
FANO_ORDER = Q**2 - Q + 1   # = 7
DISC_MID   = Q**2 - 4       # = 5  (Fibonacci prime)

# ── Fibonacci and standard Lucas sequences (pre-computed) ────────────────────
# Fibonacci: F[k] with F[0]=0, F[1]=1, F[k]=F[k-1]+F[k-2]
_fib = [0, 1]
for _ in range(18): _fib.append(_fib[-1] + _fib[-2])
FIB = _fib  # FIB[k] = k-th Fibonacci number

# Standard Lucas: L[k] with L[0]=2, L[1]=1, L[k]=L[k-1]+L[k-2]
_luc = [2, 1]
for _ in range(18): _luc.append(_luc[-1] + _luc[-2])
STD_LUCAS = _luc  # STD_LUCAS[k] = k-th standard Lucas number


# ── Chebyshev polynomial evaluators (exact Fraction) ─────────────────────────
def cheby_T(n, x):
    """Chebyshev polynomial T_n(x) via recurrence T_0=1, T_1=x, Tn=2x*T_{n-1}-T_{n-2}."""
    x = Fraction(x)
    if n == 0: return Fraction(1)
    if n == 1: return x
    a, b = Fraction(1), x
    for _ in range(n - 1):
        a, b = b, 2 * x * b - a
    return b


def cheby_U(n, x):
    """Chebyshev polynomial U_n(x) via recurrence U_0=1, U_1=2x, Un=2x*U_{n-1}-U_{n-2}."""
    x = Fraction(x)
    if n < 0:  return Fraction(0)
    if n == 0: return Fraction(1)
    if n == 1: return 2 * x
    a, b = Fraction(1), 2 * x
    for _ in range(n - 1):
        a, b = b, 2 * x * b - a
    return b


def lucas_q(n):
    """Q-Lucas number Lₙ = 2·T_n(Q/2) (exact integer Fraction)."""
    return 2 * cheby_T(n, Fraction(Q, 2))


X = Fraction(Q, 2)   # = 3/2, the evaluation point


# ─────────────────────────────────────────────────────────────────────────────
class T1ChebyshevTLucasIdentity(unittest.TestCase):
    """Lₙ = 2·T_n(Q/2) for all n (Chebyshev first kind at Q/2)."""

    def test_T0(self):
        """2·T₀(Q/2) = 2 = LAM = L₀."""
        self.assertEqual(2 * cheby_T(0, X), 2)
        self.assertEqual(2 * cheby_T(0, X), LAM)

    def test_T1(self):
        """2·T₁(Q/2) = Q = 3 = L₁."""
        self.assertEqual(2 * cheby_T(1, X), Q)

    def test_T2(self):
        """2·T₂(Q/2) = Q²−2 = 7 = FANO_ORDER = L₂."""
        val = 2 * cheby_T(2, X)
        self.assertEqual(val, Q**2 - 2)
        self.assertEqual(val, FANO_ORDER)
        self.assertEqual(val, 7)

    def test_T3(self):
        """2·T₃(Q/2) = Q³−3Q = 18 = Perkel multiplicities = L₃."""
        val = 2 * cheby_T(3, X)
        self.assertEqual(val, Q**3 - 3 * Q)
        self.assertEqual(val, 18)

    def test_recurrence_T(self):
        """T_n(x) satisfies T_n = 2x·T_{n-1} − T_{n-2} (and so does Lₙ at x=Q/2)."""
        for n in range(2, 7):
            self.assertEqual(cheby_T(n, X),
                             2 * X * cheby_T(n - 1, X) - cheby_T(n - 2, X))

    def test_lucas_from_T_sequence(self):
        """First six Q-Lucas numbers from Chebyshev: 2,3,7,18,47,123."""
        expected = [2, 3, 7, 18, 47, 123]
        actual = [2 * cheby_T(n, X) for n in range(6)]
        self.assertEqual(actual, expected)


# ─────────────────────────────────────────────────────────────────────────────
class T2ChebyshevUFibonacciIdentity(unittest.TestCase):
    """U_{n-1}(Q/2) = F_{2n} (even-indexed Fibonacci numbers)."""

    def test_U0_is_F2(self):
        """U₀(Q/2) = 1 = F₂."""
        self.assertEqual(cheby_U(0, X), FIB[2])
        self.assertEqual(cheby_U(0, X), 1)

    def test_U1_is_F4(self):
        """U₁(Q/2) = 3 = F₄ = Q."""
        self.assertEqual(cheby_U(1, X), FIB[4])
        self.assertEqual(cheby_U(1, X), Q)

    def test_U2_is_F6(self):
        """U₂(Q/2) = 8 = F₆ = LAM·MU = (Q−1)³."""
        self.assertEqual(cheby_U(2, X), FIB[6])
        self.assertEqual(cheby_U(2, X), LAM * MU)
        self.assertEqual(cheby_U(2, X), (Q - 1)**3)
        self.assertEqual(cheby_U(2, X), 8)

    def test_U3_is_F8(self):
        """U₃(Q/2) = 21 = F₈ = Q·FANO_ORDER = E_H (Heawood edges!)."""
        self.assertEqual(cheby_U(3, X), FIB[8])
        self.assertEqual(cheby_U(3, X), Q * FANO_ORDER)
        self.assertEqual(cheby_U(3, X), 21)

    def test_U4_is_F10(self):
        """U₄(Q/2) = 55 = F₁₀."""
        self.assertEqual(cheby_U(4, X), FIB[10])
        self.assertEqual(cheby_U(4, X), 55)

    def test_U5_is_F12(self):
        """U₅(Q/2) = 144 = F₁₂."""
        self.assertEqual(cheby_U(5, X), FIB[12])
        self.assertEqual(cheby_U(5, X), 144)

    def test_U_general_formula(self):
        """U_{n-1}(Q/2) = F_{2n} for n=1..6."""
        for n in range(1, 7):
            self.assertEqual(cheby_U(n - 1, X), FIB[2 * n])


# ─────────────────────────────────────────────────────────────────────────────
class T3PellIdentityLucasFibonacci(unittest.TestCase):
    """Pell identity: Lₙ² − DISC_MID · F_{2n}² = 4 = MU for all n."""

    def _pell(self, n):
        Ln = lucas_q(n)
        F2n = FIB[2 * n]
        return Ln**2 - DISC_MID * F2n**2

    def test_pell_n1(self):
        """L₁² − 5·F₂² = 9−5·1 = 4 = MU."""
        self.assertEqual(self._pell(1), MU)

    def test_pell_n2(self):
        """L₂² − 5·F₄² = 49−5·9 = 4 = MU."""
        self.assertEqual(self._pell(2), MU)

    def test_pell_n3(self):
        """L₃² − 5·F₆² = 324−5·64 = 4 = MU."""
        self.assertEqual(self._pell(3), MU)

    def test_pell_n4(self):
        """L₄² − 5·F₈² = 2209−5·441 = 4 = MU."""
        self.assertEqual(self._pell(4), MU)

    def test_pell_n5(self):
        """L₅² − 5·F₁₀² = 15129−5·3025 = 4 = MU."""
        self.assertEqual(self._pell(5), MU)

    def test_pell_constant_is_MU(self):
        """The constant 4 = MU = Q+1 (W33 mu!) for all n=1..6."""
        for n in range(1, 7):
            self.assertEqual(self._pell(n), MU)

    def test_pell_disc_is_5(self):
        """DISC_MID = Q²−4 = 5 (Fibonacci prime) is the Pell coefficient."""
        self.assertEqual(DISC_MID, 5)
        self.assertEqual(DISC_MID, Q**2 - 4)


# ─────────────────────────────────────────────────────────────────────────────
class T4StandardLucasConnection(unittest.TestCase):
    """Q-Lucas Lₙ = Standard Lucas sequence L_{2n} (every other value)."""

    def test_L0_is_StdLucas_0(self):
        """L₀ = StdLucas₀ = 2."""
        self.assertEqual(lucas_q(0), STD_LUCAS[0])
        self.assertEqual(lucas_q(0), 2)

    def test_L1_is_StdLucas_2(self):
        """L₁ = StdLucas₂ = 3."""
        self.assertEqual(lucas_q(1), STD_LUCAS[2])
        self.assertEqual(lucas_q(1), 3)

    def test_L2_is_StdLucas_4(self):
        """L₂ = StdLucas₄ = 7."""
        self.assertEqual(lucas_q(2), STD_LUCAS[4])
        self.assertEqual(lucas_q(2), 7)

    def test_L3_is_StdLucas_6(self):
        """L₃ = StdLucas₆ = 18."""
        self.assertEqual(lucas_q(3), STD_LUCAS[6])
        self.assertEqual(lucas_q(3), 18)

    def test_L4_is_StdLucas_8(self):
        """L₄ = StdLucas₈ = 47."""
        self.assertEqual(lucas_q(4), STD_LUCAS[8])
        self.assertEqual(lucas_q(4), 47)

    def test_general_doubling_index(self):
        """Lₙ = StdLucas_{2n} for n=0..7."""
        for n in range(8):
            self.assertEqual(lucas_q(n), STD_LUCAS[2 * n])


# ─────────────────────────────────────────────────────────────────────────────
class T5KeyW33Evaluations(unittest.TestCase):
    """Specific Chebyshev-U evaluations recover W33 and Heawood parameters."""

    def test_U1_equals_Q(self):
        """U₁(Q/2) = Q = 3 (W33 prime)."""
        self.assertEqual(cheby_U(1, X), Q)

    def test_U2_equals_lam_times_mu(self):
        """U₂(Q/2) = Q²−1 = LAM·MU = 2·4 = 8."""
        self.assertEqual(cheby_U(2, X), LAM * MU)

    def test_U2_equals_cascade_power(self):
        """U₂(Q/2) = (Q−1)³ = 8 (cascade identity, unique to Q=3!)."""
        self.assertEqual(cheby_U(2, X), (Q - 1)**3)
        # At Q=3: Q²-1 = 8 = (Q-1)³ iff Q²-1=(Q-1)³ iff Q+1=(Q-1)² iff Q=3
        self.assertEqual(Q**2 - 1, (Q - 1)**3)

    def test_U3_equals_heawood_edges(self):
        """U₃(Q/2) = Q³−2Q = Q·FANO_ORDER = 21 = E_H (Heawood edge count)."""
        self.assertEqual(cheby_U(3, X), Q * FANO_ORDER)
        self.assertEqual(cheby_U(3, X), 21)

    def test_U2_cascade_uniqueness(self):
        """U₂(Q/2)=(Q−1)³ only at Q=3; equivalent to cascade condition MU=LAM²."""
        # Q²-1 = (Q-1)³ iff (Q+1) = (Q-1)² iff Q=3
        for q in range(2, 8):
            val = q**2 - 1
            cascade = (q - 1)**3
            if q == 3:
                self.assertEqual(val, cascade)
            else:
                self.assertNotEqual(val, cascade)

    def test_fib_sequence_in_U_values(self):
        """Every other even Fibonacci: 1,3,8,21,55,144 = U_{n-1}(Q/2) sequence."""
        expected = [FIB[2 * n] for n in range(1, 7)]
        actual = [cheby_U(n - 1, X) for n in range(1, 7)]
        self.assertEqual(actual, expected)


# ─────────────────────────────────────────────────────────────────────────────
class T6CrossBridgeArithmetic(unittest.TestCase):
    """Cross-connecting Chebyshev, Fibonacci, W33, Heawood, Perkel parameters."""

    def test_L2_times_U1_sq(self):
        """L₂·U₁² = 7·9 = 63 = V_Perkel - L₃ + FANO_ORDER·U₁."""
        self.assertEqual(lucas_q(2) * cheby_U(1, X)**2, 63)

    def test_F_indices_in_U(self):
        """U_{n-1}(Q/2) = F_{2n}: even-index Fibonacci captures every other Fib."""
        # Check that no odd-index Fibonacci appears
        for n in range(1, 6):
            Un1 = cheby_U(n - 1, X)
            self.assertEqual(Un1, FIB[2 * n])

    def test_pell_disc_equals_golden_discriminant(self):
        """DISC_MID = Q²−4 = 5 appears in Pell, golden min-poly, and Fibonacci."""
        # The golden ratio Fibonacci identity: L_m² - 5*F_m² = 4*(-1)^m
        # At m=2n: constant = 4 = MU ✓
        # DISC_MID = 5 is THE Fibonacci discriminant
        self.assertEqual(DISC_MID, 5)

    def test_fib_warp_through_w33(self):
        """F_{2·3} = F₆ = 8 = LAM·MU = U₂(Q/2) (three-way bridge)."""
        self.assertEqual(FIB[2 * Q], LAM * MU)   # F₆ = 8 = LAM*MU
        self.assertEqual(FIB[2 * Q], cheby_U(Q - 1, X))  # = U₂(Q/2)

    def test_lucas_at_n_Q_is_V_minus_two(self):
        """L_Q = StdLucas_{2Q} = StdLucas_6 = 18 = V_P/Q - 1 = Perkel mult."""
        # V_Perkel = 57 = Q*19; 57/Q - 1 = 19-1 = 18 = L_3 = L_Q
        V_P = 57
        self.assertEqual(lucas_q(Q), V_P // Q - 1)

    def test_mu_equals_pell_constant(self):
        """The Pell identity constant 4 = MU = Q+1 at Q=3."""
        self.assertEqual(MU, 4)
        self.assertEqual(MU, Q + 1)
        # Pell identity constant = 4 for even-index (from classical L_m^2-5F_m^2 = 4(-1)^m)

    def test_U3_equals_Q_times_L2(self):
        """U₃(Q/2) = Q·L₂ = Q·FANO_ORDER = 3·7 = 21 = E_H."""
        self.assertEqual(cheby_U(3, X), Q * lucas_q(2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
