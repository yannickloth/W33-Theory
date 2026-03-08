"""
Phase XXI: Polynomial & Figurate Identities (T276-T290)
=======================================================

From (v, k, lam, mu, q) = (40, 12, 2, 4, 3) we derive 15 theorems
connecting W(3,3) to polynomial evaluations (Hoffman, minimal polynomial,
discriminant), classical figurate numbers (pentagonal, tetrahedral,
triangular), the Euler totient, binomial coefficients, and combinatorial
number theory.

These theorems expose the SRG parameters as a nexus of polynomial
and figurate identities, with the Hoffman polynomial, Euler
totient, and Moore bound all encoding the same five source numbers.

Theorems
--------
T276: Catalan chain ratios C(N)/C(mu)=q, C(C(q))=42
T277: Lucas chain L[0,2,3,4] = (lam, q, mu, Phi6)
T278: Hoffman polynomial H(1)=-N/mu, H(theta)=v-k=28
T279: Cubic discriminant = 2^12 * 3^2 * 5^2, sqrt = v*f = 960
T280: Parameter sum v+k+lam+mu+q = 61 (prime)
T281: Frobenius norm ratio ||D2||^2_F / ||A||^2_F = q^2/mu
T282: Minimal poly evaluations m(k/lam) = -E, m(1) = 55
T283: Euler number |E_4| = N = 5
T284: Moore bound deficiency k^2+1-v = q*N*Phi6 = 105
T285: Pentagonal numbers P(2)=N, P(3)=k
T286: Euler totient phi(v)=k+mu, phi(Phi3)=k
T287: Binomial tower C(k,lam)=66, C(theta,q)=E/2, C(dimO,q)=v+k+mu
T288: Tetrahedral & triangular: Tet(2)=mu, Tet(3)=theta, Tri(4)=theta
T289: Pythagorean factorization v^2-k^2 = 16*Phi3*Phi6
T290: Stirling chain S(3,2)=q, S(4,2)=Phi6, S(N,lam)=g
"""
from __future__ import annotations

import math
from fractions import Fraction

# ═══════════════════════════════════════════════════════════════
#  SRG CONSTANTS
# ═══════════════════════════════════════════════════════════════
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2                         # 240
r, s = 2, -4                           # non-trivial eigenvalues
f, g = 24, 15                          # multiplicities
THETA = 10                             # Lovász theta
PHI3 = Q**2 + Q + 1                    # 13
PHI6 = Q**2 - Q + 1                    # 7
DIM_O = K - MU                         # 8
N = 5                                  # clique covering number
ALBERT = V - 1 - K                     # 27
AUT = 51840                            # |Sp(4,3)|


# ═══════════════════════════════════════════════════════════════
#  T276: Catalan Chain Ratios
# ═══════════════════════════════════════════════════════════════

def _catalan(n: int) -> int:
    return math.comb(2 * n, n) // (n + 1)


class TestCatalanChainRatios:
    """T276: Ratios and compositions of Catalan numbers at SRG parameters.

    C(N)/C(mu) = q, C(C(q)) = 42 = The Answer,
    C(lam) = lam (fixed point), C(mu) = 2*Phi6.
    """

    def test_catalan_ratio_N_mu_is_q(self):
        assert Fraction(_catalan(N), _catalan(MU)) == Q

    def test_catalan_composition_q(self):
        """C(C(q)) = C(5) = 42 = v + lam = The Answer."""
        assert _catalan(_catalan(Q)) == V + LAM

    def test_catalan_lam_fixed_point(self):
        """C(lam) = lam: Catalan at lambda is a fixed point."""
        assert _catalan(LAM) == LAM

    def test_catalan_mu_is_2_phi6(self):
        assert _catalan(MU) == 2 * PHI6

    def test_catalan_iterated_lam(self):
        """C(C(lam)) = C(lam) = lam: double-fixed point."""
        assert _catalan(_catalan(LAM)) == LAM


# ═══════════════════════════════════════════════════════════════
#  T277: Lucas Chain
# ═══════════════════════════════════════════════════════════════

def _lucas(n: int) -> list[int]:
    """Lucas numbers L(0)..L(n)."""
    L = [2, 1]
    for _ in range(n - 1):
        L.append(L[-1] + L[-2])
    return L


class TestLucasChain:
    """T277: Lucas numbers at indices 0,2,3,4 hit four SRG parameters.

    L(0) = lam, L(2) = q, L(3) = mu, L(4) = Phi6.
    """

    LUC = _lucas(8)

    def test_lucas_0_is_lam(self):
        assert self.LUC[0] == LAM

    def test_lucas_2_is_q(self):
        assert self.LUC[2] == Q

    def test_lucas_3_is_mu(self):
        assert self.LUC[3] == MU

    def test_lucas_4_is_phi6(self):
        assert self.LUC[4] == PHI6

    def test_lucas_product_0234(self):
        """L(0)*L(2)*L(3)*L(4) = lam*q*mu*Phi6 = 168 = DIM_O * 3*Phi6."""
        prod = self.LUC[0] * self.LUC[2] * self.LUC[3] * self.LUC[4]
        assert prod == LAM * Q * MU * PHI6
        assert prod == 168


# ═══════════════════════════════════════════════════════════════
#  T278: Hoffman Polynomial Evaluations
# ═══════════════════════════════════════════════════════════════

class TestHoffmanPoly:
    """T278: Hoffman polynomial H(x) = v(x-r)(x-s)/[(k-r)(k-s)].

    H(1) = -N/mu, H(theta) = v-k = 28, H(-1) = -q^2/mu.
    """

    @staticmethod
    def _H(x: int) -> Fraction:
        return Fraction(V * (x - r) * (x - s), (K - r) * (K - s))

    def test_H_of_1(self):
        assert self._H(1) == Fraction(-N, MU)

    def test_H_of_theta(self):
        assert self._H(THETA) == V - K

    def test_H_of_neg1(self):
        assert self._H(-1) == Fraction(-Q**2, MU)

    def test_H_of_0_is_neg_lam(self):
        """H(0) = -lambda (known from T144, included for completeness)."""
        assert self._H(0) == -LAM

    def test_hoffman_denom(self):
        """Denominator = (k-r)(k-s) = theta*(k+mu) = 160."""
        assert (K - r) * (K - s) == THETA * (K + MU)
        assert (K - r) * (K - s) == 160


# ═══════════════════════════════════════════════════════════════
#  T279: Cubic Discriminant
# ═══════════════════════════════════════════════════════════════

class TestCubicDiscriminant:
    """T279: Discriminant of the minimal polynomial = 2^12 * 3^2 * 5^2.

    disc(m) = (k-r)^2*(k-s)^2*(r-s)^2 = 921600.
    sqrt(disc) = (k-r)(k-s)(r-s) = theta*(k+mu)*(k/lam) = v*f = 960.
    """

    DISC = (K - r)**2 * (K - s)**2 * (r - s)**2

    def test_discriminant_value(self):
        assert self.DISC == 921600

    def test_discriminant_factorization(self):
        assert self.DISC == 2**12 * 3**2 * 5**2

    def test_sqrt_disc_is_vf(self):
        sqrt_d = (K - r) * (K - s) * abs(r - s)
        assert sqrt_d == V * f

    def test_sqrt_disc_value(self):
        assert (K - r) * (K - s) * abs(r - s) == 960

    def test_sqrt_factors(self):
        """sqrt(disc) = theta * (k+mu) * (k/lam) = 10 * 16 * 6 = 960."""
        assert (K - r) == THETA
        assert (K - s) == K + MU
        assert abs(r - s) == K // LAM


# ═══════════════════════════════════════════════════════════════
#  T280: Parameter Sum is Prime
# ═══════════════════════════════════════════════════════════════

class TestParameterSum:
    """T280: v + k + lam + mu + q = 61, which is prime.

    The sum of all five SRG source parameters is the 18th prime.
    Also: product v*k*lam*mu*q = 11520 = 2^8 * 3^2 * 5.
    """

    SUM = V + K + LAM + MU + Q
    PROD = V * K * LAM * MU * Q

    def test_parameter_sum_value(self):
        assert self.SUM == 61

    def test_parameter_sum_is_prime(self):
        from sympy import isprime
        assert isprime(self.SUM)

    def test_parameter_product(self):
        assert self.PROD == 11520

    def test_parameter_product_factorization(self):
        assert self.PROD == 2**8 * 3**2 * 5

    def test_sum_is_18th_prime(self):
        from sympy import prime
        assert prime(18) == 61


# ═══════════════════════════════════════════════════════════════
#  T281: Frobenius Norm Ratio
# ═══════════════════════════════════════════════════════════════

class TestFrobeniusNormRatio:
    """T281: ||D2||^2_F / ||A||^2_F = q^2/mu = 9/4.

    ||A||^2_F = tr(A^2) = 2E = 480.
    ||D2||^2_F = tr(D2^2) = v*ALBERT = 1080.
    Ratio = (v*ALBERT)/(2E) = 1080/480 = 9/4 = q^2/mu.
    """

    A_FROB_SQ = K**2 + f * r**2 + g * s**2
    D2_FROB_SQ = ALBERT**2 + f * Q**2 + g * Q**2

    def test_A_frobenius_sq(self):
        assert self.A_FROB_SQ == 2 * E

    def test_D2_frobenius_sq(self):
        assert self.D2_FROB_SQ == V * ALBERT

    def test_D2_frobenius_value(self):
        assert self.D2_FROB_SQ == 1080

    def test_ratio_is_q2_over_mu(self):
        assert Fraction(self.D2_FROB_SQ, self.A_FROB_SQ) == Fraction(Q**2, MU)

    def test_ratio_value(self):
        assert Fraction(self.D2_FROB_SQ, self.A_FROB_SQ) == Fraction(9, 4)


# ═══════════════════════════════════════════════════════════════
#  T282: Minimal Polynomial at Special Points
# ═══════════════════════════════════════════════════════════════

class TestMinPolyEvals:
    """T282: The minimal polynomial m(x) = x^3 - theta*x^2 - 32x + k*dimO
    evaluated at special points.

    m(k/lam) = m(6) = -E = -240.
    m(1) = 55 = F(10) = F(theta).
    m(-1) = 117 = 9*13 = q^2*Phi3.
    """

    @staticmethod
    def _m(x: int) -> int:
        return x**3 - THETA * x**2 - 32 * x + K * DIM_O

    def test_m_at_k_over_lam_is_neg_E(self):
        assert self._m(K // LAM) == -E

    def test_m_at_6_value(self):
        assert self._m(6) == -240

    def test_m_at_1(self):
        assert self._m(1) == 55

    def test_m_at_neg1(self):
        assert self._m(-1) == 117
        assert self._m(-1) == Q**2 * PHI3

    def test_m_at_0_is_k_dimO(self):
        """m(0) = k*dimO = 96 (constant term)."""
        assert self._m(0) == K * DIM_O


# ═══════════════════════════════════════════════════════════════
#  T283: Euler Number
# ═══════════════════════════════════════════════════════════════

class TestEulerNumber:
    """T283: |E_4| = N = 5 (Euler/tangent number).

    The Euler numbers E_0=1, E_2=-1, E_4=5, E_6=-61 are coefficients
    in the Taylor expansion of sec(x). |E_4| = N = clique covering number.
    """

    # Euler numbers (tangent numbers): E_{2n} from sec(x) expansion
    EULER = {0: 1, 2: -1, 4: 5, 6: -61, 8: 1385}

    def test_abs_E4_is_N(self):
        assert abs(self.EULER[4]) == N

    def test_E0(self):
        assert self.EULER[0] == 1

    def test_E2(self):
        assert abs(self.EULER[2]) == 1

    def test_ratio_E4_E2(self):
        """E_4/E_2 = -5: magnitude ratio is N."""
        assert abs(self.EULER[4]) // abs(self.EULER[2]) == N


# ═══════════════════════════════════════════════════════════════
#  T284: Moore Bound Deficiency
# ═══════════════════════════════════════════════════════════════

class TestMooreBound:
    """T284: Moore bound deficiency = k^2+1-v = 105 = q*N*Phi6.

    For a k-regular graph of diameter 2, the Moore bound is k^2+1.
    W(3,3) has deficiency 105 = 3*5*7 = q*N*Phi6.
    """

    MOORE = K**2 + 1
    DEFICIENCY = MOORE - V

    def test_moore_bound(self):
        assert self.MOORE == 145

    def test_deficiency_value(self):
        assert self.DEFICIENCY == 105

    def test_deficiency_factorization(self):
        assert self.DEFICIENCY == Q * N * PHI6

    def test_deficiency_is_3_5_7(self):
        assert self.DEFICIENCY == 3 * 5 * 7

    def test_moore_ratio(self):
        """v / Moore = 40/145 = 8/29."""
        assert Fraction(V, self.MOORE) == Fraction(DIM_O, 29)


# ═══════════════════════════════════════════════════════════════
#  T285: Pentagonal Numbers
# ═══════════════════════════════════════════════════════════════

def _pentagonal(n: int) -> int:
    """n-th pentagonal number: n(3n-1)/2."""
    return n * (3 * n - 1) // 2


class TestPentagonalNumbers:
    """T285: Consecutive pentagonal numbers hit N and k.

    P(2) = 5 = N, P(3) = 12 = k. Also P(4) = 22 = lam*(k-1).
    Generalized: GP(-1) = 2 = lam, GP(-2) = 7 = Phi6.
    """

    def test_P2_is_N(self):
        assert _pentagonal(2) == N

    def test_P3_is_k(self):
        assert _pentagonal(3) == K

    def test_P4_is_lam_times_k_minus_1(self):
        assert _pentagonal(4) == LAM * (K - 1)
        assert _pentagonal(4) == 22

    def test_generalized_neg1_is_lam(self):
        """GP(-1) = (-1)(3*(-1)-1)/2 = 2 = lam."""
        assert _pentagonal(-1) == LAM

    def test_generalized_neg2_is_phi6(self):
        """GP(-2) = (-2)(3*(-2)-1)/2 = 7 = Phi6."""
        assert _pentagonal(-2) == PHI6

    def test_consecutive_pair(self):
        """P(2) and P(3) are consecutive pentagonal numbers hitting N and k."""
        assert _pentagonal(2) == N
        assert _pentagonal(3) == K
        assert K - N == PHI6


# ═══════════════════════════════════════════════════════════════
#  T286: Euler Totient Chain
# ═══════════════════════════════════════════════════════════════

class TestEulerTotient:
    """T286: Euler totient at SRG parameters yields SRG parameters.

    phi(v) = k + mu = 16, phi(Phi3) = k = 12.
    The totient function maps graph invariants to graph invariants.
    """

    def test_phi_v_is_k_plus_mu(self):
        from sympy import totient
        assert int(totient(V)) == K + MU

    def test_phi_v_value(self):
        from sympy import totient
        assert int(totient(V)) == 16

    def test_phi_phi3_is_k(self):
        from sympy import totient
        assert int(totient(PHI3)) == K

    def test_phi_q_is_lam(self):
        from sympy import totient
        assert int(totient(Q)) == LAM

    def test_totient_chain(self):
        """phi(v) = k+mu, phi(Phi3) = k, phi(q) = lam: totient respects SRG."""
        from sympy import totient
        assert int(totient(V)) == K + MU
        assert int(totient(PHI3)) == K
        assert int(totient(Q)) == LAM


# ═══════════════════════════════════════════════════════════════
#  T287: Binomial Coefficient Tower
# ═══════════════════════════════════════════════════════════════

class TestBinomialTower:
    """T287: Binomial coefficients at SRG parameters form a tower.

    C(k, lam) = 66 = v+k+mu+theta = denom(B_10).
    C(theta, q) = 120 = E/2.
    C(dimO, q) = 56 = v+k+mu.
    C(theta, lam) = 45 = v+N.
    """

    def test_C_k_lam_value(self):
        assert math.comb(K, LAM) == 66

    def test_C_k_lam_identity(self):
        assert math.comb(K, LAM) == V + K + MU + THETA

    def test_C_theta_q_is_half_E(self):
        assert math.comb(THETA, Q) == E // 2

    def test_C_dimO_q(self):
        assert math.comb(DIM_O, Q) == V + K + MU
        assert math.comb(DIM_O, Q) == 56

    def test_C_theta_lam_is_v_plus_N(self):
        assert math.comb(THETA, LAM) == V + N
        assert math.comb(THETA, LAM) == 45

    def test_tower_ordering(self):
        """C(dimO,q) < C(k,lam) < C(theta,q): ascending tower."""
        assert math.comb(DIM_O, Q) < math.comb(K, LAM) < math.comb(THETA, Q)


# ═══════════════════════════════════════════════════════════════
#  T288: Tetrahedral and Triangular Numbers
# ═══════════════════════════════════════════════════════════════

class TestTetrahedralTriangular:
    """T288: Figurate numbers at SRG parameters.

    Tetrahedral: Tet(2) = mu = 4, Tet(3) = theta = 10.
    Triangular: Tri(2) = q = 3, Tri(4) = theta = 10, Tri(5) = g = 15.
    """

    @staticmethod
    def _tet(n: int) -> int:
        return n * (n + 1) * (n + 2) // 6

    @staticmethod
    def _tri(n: int) -> int:
        return n * (n + 1) // 2

    def test_tet_2_is_mu(self):
        assert self._tet(2) == MU

    def test_tet_3_is_theta(self):
        assert self._tet(3) == THETA

    def test_tri_2_is_q(self):
        assert self._tri(2) == Q

    def test_tri_4_is_theta(self):
        assert self._tri(4) == THETA

    def test_tri_5_is_g(self):
        assert self._tri(5) == g

    def test_tet_tri_shared_theta(self):
        """theta = Tet(3) = Tri(4): two figurate families converge at theta."""
        assert self._tet(3) == self._tri(4) == THETA


# ═══════════════════════════════════════════════════════════════
#  T289: Pythagorean Factorization
# ═══════════════════════════════════════════════════════════════

class TestPythagoreanFactor:
    """T289: v^2 - k^2 = mu^2 * Phi3 * Phi6 = (v-k)(v+k).

    The difference of squares factorizes through both cyclotomic
    values and yields 1456 = 2^4 * 7 * 13.
    v-k = 4*Phi6, v+k = 4*Phi3, so v^2-k^2 = 16*91 = mu^2*PHI3*PHI6.
    """

    DIFF = V**2 - K**2

    def test_diff_value(self):
        assert self.DIFF == 1456

    def test_diff_is_mu2_phi3_phi6(self):
        assert self.DIFF == MU**2 * PHI3 * PHI6

    def test_diff_of_squares(self):
        """v^2 - k^2 = (v-k)(v+k) = 28 * 52."""
        assert self.DIFF == (V - K) * (V + K)

    def test_v_minus_k(self):
        """v-k = 28 = 4*Phi6."""
        assert V - K == 4 * PHI6

    def test_v_plus_k(self):
        """v+k = 52 = 4*Phi3 = dim(F4)."""
        assert V + K == 4 * PHI3

    def test_prime_factorization(self):
        """1456 = 2^4 * 7 * 13 = 2^4 * Phi6 * Phi3."""
        assert self.DIFF == 2**4 * PHI6 * PHI3


# ═══════════════════════════════════════════════════════════════
#  T290: Stirling Chain
# ═══════════════════════════════════════════════════════════════

def _stirling2(n: int, k_val: int) -> int:
    """Stirling number of the second kind S(n,k)."""
    if n == 0 and k_val == 0:
        return 1
    if n == 0 or k_val == 0:
        return 0
    if k_val > n:
        return 0
    # Use inclusion-exclusion formula for small values
    total = 0
    for j in range(k_val + 1):
        sign = (-1) ** (k_val - j)
        total += sign * math.comb(k_val, j) * j**n
    return total // math.factorial(k_val)


class TestStirlingChain:
    """T290: Stirling numbers of the second kind at small arguments.

    S(3,2) = q = 3, S(4,2) = Phi6 = 7, S(N,2) = g = 15.
    S(N,3) = 25 = N^2, S(N,4) = theta = 10.
    """

    def test_S_3_2_is_q(self):
        assert _stirling2(3, 2) == Q

    def test_S_4_2_is_phi6(self):
        assert _stirling2(4, 2) == PHI6

    def test_S_N_2_is_g(self):
        assert _stirling2(N, 2) == g

    def test_S_N_3_is_N_squared(self):
        assert _stirling2(N, 3) == N**2

    def test_S_N_4_is_theta(self):
        assert _stirling2(N, 4) == THETA

    def test_S_2_series_formula(self):
        """S(n,2) = 2^{n-1} - 1, so S(3,2)=3=q, S(4,2)=7=Phi6."""
        assert 2**2 - 1 == Q
        assert 2**3 - 1 == PHI6
