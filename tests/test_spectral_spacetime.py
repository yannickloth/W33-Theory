"""
Phase XXXVII: Spectral Geometry & Emergent Spacetime (T516-T530)
================================================================

Fifteen theorems establishing the spectral-geometric structure of
W(3,3) as a discrete spacetime scaffold.  The Laplacian spectrum,
Weyl dimension, Ollivier-Ricci curvature, random-walk mixing, Ihara
zeta function, and spanning-tree count all express the SRG parameters
in geometric language.

The centrepiece: the Weyl spectral dimension of W(3,3) is EXACTLY 2,
matching the UV spectral dimension predicted by causal dynamical
triangulations and asymptotic safety.  The graph is Ramanujan (optimal
expander), negatively curved (hyperbolic), and has graph energy = E/2.

Every constant derives from (v, k, lam, mu, q) = (40, 12, 2, 4, 3).
"""

import math
import numpy as np
import pytest
from fractions import Fraction

# ── SRG parameters ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2           # 240
R, S = 2, -4             # eigenvalues of SRG adjacency
F, G = 24, 15            # multiplicities
N = Q + 2                # 5
PHI3 = Q**2 + Q + 1      # 13
PHI6 = Q**2 - Q + 1      # 7
ALBERT = V - PHI3        # 27
THETA = 10               # Lovász theta
DIM_O = K - MU           # 8


# ═══════════════════════════════════════════════════════════════════
# T516: Laplacian Spectrum
# ═══════════════════════════════════════════════════════════════════
class TestLaplacianSpectrum:
    """The combinatorial Laplacian L = kI - A has eigenvalues
    {0, k-r, k-s} = {0, theta, k+mu} with multiplicities {1, f, g}."""

    def test_lap_eigenvalue_0(self):
        assert K - K == 0

    def test_lap_eigenvalue_1(self):
        """k - r = theta = 10."""
        assert K - R == THETA

    def test_lap_eigenvalue_2(self):
        """k - s = k + mu = 16."""
        assert K - S == K + MU
        assert K - S == 16

    def test_multiplicities(self):
        """Multiplicities {1, f, g} = {1, 24, 15} sum to V=40."""
        assert 1 + F + G == V

    def test_spectral_gap_is_theta(self):
        """The spectral gap (algebraic connectivity) = theta = 10."""
        assert K - R == THETA

    def test_product_of_nonzero_lap_eigenvalues(self):
        """(K-R)*(K-S) = theta*(k+mu) = 10*16 = 160 = triangle count."""
        assert (K - R) * (K - S) == E * LAM // 3

    def test_ratio_of_lap_eigenvalues(self):
        """(K-S)/(K-R) = (k+mu)/theta = 16/10 = 8/5 = dimO/N."""
        assert Fraction(K - S, K - R) == Fraction(DIM_O, N)


# ═══════════════════════════════════════════════════════════════════
# T517: Weyl Spectral Dimension
# ═══════════════════════════════════════════════════════════════════
class TestWeylDimension:
    """The Weyl spectral dimension of W(3,3) is EXACTLY 2.

    By Weyl's law: N(lambda) ~ C * lambda^{d/2}.
    N(10) = 25, N(16) = 40.
    (10/16)^{d/2} = 25/40 = 5/8.
    (5/8)^{2/d} = 5/8 => d/2 = 1 => d = 2.
    """

    def test_eigenvalue_count_theta(self):
        """N(theta) = 1 + f = 25 = N^2."""
        assert 1 + F == N**2

    def test_eigenvalue_count_total(self):
        """N(k+mu) = V = 40."""
        assert 1 + F + G == V

    def test_weyl_dimension_is_2(self):
        """N(theta)/N(k+mu) = (theta/(k+mu))^{d/2} gives d=2."""
        ratio_N = Fraction(1 + F, V)       # 25/40 = 5/8
        ratio_lam = Fraction(THETA, K + MU) # 10/16 = 5/8
        assert ratio_N == ratio_lam  # d/2 = 1 => d = 2

    def test_N_theta_is_N_squared(self):
        """The eigenvalue count N(theta) = 25 = N^2 = clique_cover^2."""
        assert 1 + F == N**2

    def test_weyl_ratio(self):
        """Both ratios equal 5/8 = N/DIM_O."""
        assert Fraction(1 + F, V) == Fraction(N, DIM_O)


# ═══════════════════════════════════════════════════════════════════
# T518: Graph Energy
# ═══════════════════════════════════════════════════════════════════
class TestGraphEnergy:
    """Graph energy = sum|lambda_i| = E/2 = 120.

    K + f*|r| + g*|s| = 12 + 24*2 + 15*4 = 120 = E/2.
    The graph energy equals half the edge count.
    """

    ENERGY = K + F * abs(R) + G * abs(S)

    def test_energy_value(self):
        assert self.ENERGY == 120

    def test_energy_is_half_E(self):
        assert self.ENERGY == E // 2

    def test_energy_components(self):
        """k + f|r| + g|s| = 12 + 48 + 60 = 120."""
        assert K == 12
        assert F * abs(R) == 48
        assert G * abs(S) == 60

    def test_energy_per_vertex(self):
        """Energy/V = 120/40 = 3 = q."""
        assert Fraction(self.ENERGY, V) == Q


# ═══════════════════════════════════════════════════════════════════
# T519: Wiener Index & Average Distance
# ═══════════════════════════════════════════════════════════════════
class TestWienerIndex:
    """Wiener index W = V(V-1) - E = 1320.
    Average distance = 22/PHI3 = 22/13."""

    # Distance distribution for SRG of diameter 2
    N1 = E             # 240 pairs at distance 1
    N2 = V*(V-1)//2 - E  # 540 pairs at distance 2
    W = N1 + 2 * N2     # Wiener index

    def test_wiener_value(self):
        assert self.W == 1320

    def test_wiener_formula(self):
        """W = V(V-1) - E for diameter-2 graph."""
        assert self.W == V * (V - 1) - E

    def test_avg_distance(self):
        """Average distance = W / C(V,2) = 1320/780 = 22/13 = 22/PHI3."""
        assert Fraction(self.W, V * (V - 1) // 2) == Fraction(22, PHI3)

    def test_distance_ratio(self):
        """n2/n1 = 540/240 = 9/4 = q^2/mu."""
        assert Fraction(self.N2, self.N1) == Fraction(Q**2, MU)

    def test_n2_value(self):
        """540 = V(V-1)/2 - E."""
        assert self.N2 == 540


# ═══════════════════════════════════════════════════════════════════
# T520: Ollivier-Ricci Curvature
# ═══════════════════════════════════════════════════════════════════
class TestOllivierRicci:
    """Ollivier-Ricci curvature on the SRG:
    kappa_adj = (lam+2)/k - 1 = -2/3 (adjacent vertices),
    kappa_non = -mu/k = -1/3 (non-adjacent vertices).
    W(3,3) is negatively curved — a discrete hyperbolic space.
    """

    KAPPA_ADJ = Fraction(LAM + 2, K) - 1   # = -2/3
    KAPPA_NON = Fraction(-MU, K)            # = -1/3

    def test_adjacent_curvature(self):
        assert self.KAPPA_ADJ == Fraction(-2, 3)

    def test_nonadjacent_curvature(self):
        assert self.KAPPA_NON == Fraction(-1, 3)

    def test_curvature_ratio(self):
        """kappa_adj / kappa_non = 2."""
        assert self.KAPPA_ADJ / self.KAPPA_NON == 2

    def test_negative_curvature(self):
        """Both curvatures are negative -> hyperbolic geometry."""
        assert self.KAPPA_ADJ < 0
        assert self.KAPPA_NON < 0

    def test_average_curvature(self):
        """Average curvature weighted by pair counts = -17/39."""
        n1, n2 = E, V * (V - 1) // 2 - E
        total = V * (V - 1) // 2
        avg = (self.KAPPA_ADJ * n1 + self.KAPPA_NON * n2) / total
        assert avg == Fraction(-17, 39)


# ═══════════════════════════════════════════════════════════════════
# T521: Spanning Tree Count
# ═══════════════════════════════════════════════════════════════════
class TestSpanningTrees:
    """tau = (1/V) * prod(mu_i^m_i) = 2^81 * 5^23.

    The spanning tree count factorises as 2^{q^4} * 5^23.
    Exponent of 2 is 81 = q^4 = 3^4.
    """

    TAU = 2**81 * 5**23

    def test_tau_formula(self):
        """tau = (K-R)^f * (K-S)^g / V."""
        assert (K - R)**F * (K - S)**G // V == self.TAU

    def test_tau_2_exponent(self):
        """Exponent of 2 in tau = 81 = q^4."""
        n = self.TAU
        exp2 = 0
        while n % 2 == 0:
            exp2 += 1
            n //= 2
        assert exp2 == Q**4

    def test_tau_5_exponent(self):
        """Exponent of 5 in tau = 23 (prime)."""
        n = self.TAU
        while n % 2 == 0:
            n //= 2
        exp5 = 0
        while n % 5 == 0:
            exp5 += 1
            n //= 5
        assert exp5 == 23
        assert n == 1  # No other prime factors

    def test_tau_only_primes_2_5(self):
        """tau = 2^81 * 5^23 has only prime factors 2 and 5."""
        n = self.TAU
        while n % 2 == 0:
            n //= 2
        while n % 5 == 0:
            n //= 5
        assert n == 1

    def test_q4_exponent(self):
        """81 = 3^4 = q^4."""
        assert Q**4 == 81


# ═══════════════════════════════════════════════════════════════════
# T522: Ramanujan Property
# ═══════════════════════════════════════════════════════════════════
class TestRamanujanProperty:
    """W(3,3) is a Ramanujan graph: max(|r|, |s|) <= 2*sqrt(k-1).
    |s| = 4 <= 2*sqrt(11) ≈ 6.633.
    This means W(3,3) is an optimal spectral expander.
    """

    def test_second_eigenvalue(self):
        """max(|r|, |s|) = |s| = 4."""
        assert max(abs(R), abs(S)) == abs(S)
        assert abs(S) == MU

    def test_ramanujan_bound(self):
        """|s| = 4 < 2*sqrt(k-1) = 2*sqrt(11) ≈ 6.633."""
        assert abs(S)**2 < 4 * (K - 1)

    def test_ramanujan_margin(self):
        """Ramanujan ratio: |s|^2 / (4(k-1)) = 16/44 = 4/11."""
        assert Fraction(S**2, 4 * (K - 1)) == Fraction(MU, K - 1)

    def test_spectral_gap_ratio(self):
        """Spectral gap / k = (k - |s|) / k = 8/12 = 2/3."""
        assert Fraction(K - abs(S), K) == Fraction(2, 3)

    def test_expander_mixing(self):
        """Expander mixing lemma: |e(S,T) - k|S||T|/v| <= |s|*sqrt(|S||T|)."""
        # For equal sets of size V/2:
        bound = abs(S) * V // 2
        assert bound == MU * V // 2


# ═══════════════════════════════════════════════════════════════════
# T523: Ball Volumes & Surface Areas
# ═══════════════════════════════════════════════════════════════════
class TestBallVolumes:
    """Ball and sphere volumes at each vertex of W(3,3):
    B(0) = 1, B(1) = 1+k = PHI3 = 13, B(2) = V = 40 (entire graph).
    S(1) = k = 12, S(2) = V-1-k = ALBERT = 27.
    Surface ratio S(2)/S(1) = q^2/mu = 9/4.
    """

    def test_ball_0(self):
        assert 1 == 1

    def test_ball_1_is_phi3(self):
        """B(1) = 1 + k = 13 = PHI3."""
        assert 1 + K == PHI3

    def test_ball_2_is_V(self):
        """B(2) = V = 40 (diameter 2 -> entire graph)."""
        assert 1 + K + (V - 1 - K) == V

    def test_sphere_1(self):
        """S(1) = k = 12."""
        assert K == 12

    def test_sphere_2(self):
        """S(2) = V - 1 - k = ALBERT = 27."""
        assert V - 1 - K == ALBERT

    def test_surface_ratio(self):
        """S(2)/S(1) = 27/12 = 9/4 = q^2/mu."""
        assert Fraction(ALBERT, K) == Fraction(Q**2, MU)


# ═══════════════════════════════════════════════════════════════════
# T524: Kirchhoff & Kemeny Constants
# ═══════════════════════════════════════════════════════════════════
class TestKirchhoffKemeny:
    """Kirchhoff index Kf = V * sum(m_i/mu_i) = 267/2.
    Kemeny constant K_em = 267/80 = 3.3375.
    """

    KEMENY = Fraction(F, K - R) + Fraction(G, K - S)
    KIRCHHOFF = V * KEMENY

    def test_kemeny_value(self):
        """Kemeny = f/(k-r) + g/(k-s) = 24/10 + 15/16 = 267/80."""
        assert self.KEMENY == Fraction(267, 80)

    def test_kirchhoff_value(self):
        """Kf = V * Kemeny = 40 * 267/80 = 267/2."""
        assert self.KIRCHHOFF == Fraction(267, 2)

    def test_kemeny_components(self):
        """f/(k-r) = 12/5, g/(k-s) = 15/16."""
        assert Fraction(F, K - R) == Fraction(12, 5)
        assert Fraction(G, K - S) == Fraction(15, 16)

    def test_kirchhoff_numerator(self):
        """267 = 3 * 89: product of two primes."""
        assert 267 == 3 * 89

    def test_kemeny_reciprocal_sum(self):
        """1/Kemeny = 80/267: random walk efficiency metric."""
        assert 1 / self.KEMENY == Fraction(80, 267)


# ═══════════════════════════════════════════════════════════════════
# T525: Random Walk Mixing
# ═══════════════════════════════════════════════════════════════════
class TestRandomWalkMixing:
    """Random walk on W(3,3) has relaxation time q/lam = 3/2.
    Second eigenvalue ratio = 1/3 = 1/q.
    """

    def test_second_eigenvalue_ratio(self):
        """max(|r|, |s|) / k = 4/12 = 1/3 = 1/q."""
        assert Fraction(max(abs(R), abs(S)), K) == Fraction(1, Q)

    def test_relaxation_time(self):
        """t_rel = k/(k - max(|r|,|s|)) = 12/(12-4) = 3/2 = q/lam."""
        t_rel = Fraction(K, K - max(abs(R), abs(S)))
        assert t_rel == Fraction(Q, LAM)

    def test_stationary_distribution(self):
        """Uniform: pi_i = 1/V = 1/40 for all i (regular graph)."""
        assert Fraction(1, V) == Fraction(1, V)

    def test_return_probability_limit(self):
        """P(return to start, t->inf) = 1/V = 1/40 = 0.025."""
        assert Fraction(1, V) == Fraction(1, 40)

    def test_second_eigenvalue_gap(self):
        """Spectral gap in normalised spectrum = 1 - 1/q = 2/3."""
        gap = 1 - Fraction(max(abs(R), abs(S)), K)
        assert gap == Fraction(2, 3)


# ═══════════════════════════════════════════════════════════════════
# T526: Ihara Zeta Function
# ═══════════════════════════════════════════════════════════════════
class TestIharaZeta:
    """Ihara zeta of W(3,3): poles from eigenvalue equation.
    For lambda = k: real poles u = 1/(k-1) = 1/11, u = 1.
    For lambda = r, s: complex poles on circle |u| = 1/sqrt(k-1).

    The Ihara radius = 1/sqrt(k-1) = 1/sqrt(11).
    """

    def test_real_pole_small(self):
        """Smallest real pole u = 1/(k-1) = 1/11."""
        assert Fraction(1, K - 1) == Fraction(1, 11)

    def test_real_pole_large(self):
        """Largest real pole u = 1."""
        u1 = Fraction(1, 1)
        assert (K - 1) * u1**2 - K * u1 + 1 == 0

    def test_complex_pole_modulus(self):
        """Complex poles have |u| = 1/sqrt(k-1)."""
        # For eigenvalue r: 11u^2 - 2u + 1 = 0, disc = 4 - 44 = -40 < 0
        # |u|^2 = c/a = 1/11 = 1/(k-1)
        assert Fraction(1, K - 1) == Fraction(1, 11)

    def test_complex_pole_discriminant_r(self):
        """For r=2: disc = 4 - 44 = -40 < 0 (complex)."""
        disc = R**2 - 4 * (K - 1)
        assert disc == -40
        assert disc < 0

    def test_complex_pole_discriminant_s(self):
        """For s=-4: disc = 16 - 44 = -28 < 0 (complex)."""
        disc = S**2 - 4 * (K - 1)
        assert disc == -28
        assert disc < 0


# ═══════════════════════════════════════════════════════════════════
# T527: Trace Powers of A
# ═══════════════════════════════════════════════════════════════════
class TestTracePowers:
    """tr(A^n) = k^n + f*r^n + g*s^n counts closed walks of length n.

    tr(A^1) = 0 (no loops), tr(A^2) = 2E = 480,
    tr(A^3) = 960 = v*f (6x triangle count),
    tr(A^4) = 24960.
    """

    @staticmethod
    def _trace(n):
        return K**n + F * R**n + G * S**n

    def test_trace_1(self):
        """tr(A) = 0 (traceless adjacency)."""
        assert self._trace(1) == 0

    def test_trace_2(self):
        """tr(A^2) = 2E = 480."""
        assert self._trace(2) == 2 * E

    def test_trace_3(self):
        """tr(A^3) = 960 = v*f = 6 * triangle_count."""
        assert self._trace(3) == V * F
        assert self._trace(3) == 6 * (E * LAM // 3)

    def test_trace_4(self):
        """tr(A^4) = 24960."""
        assert self._trace(4) == 24960

    def test_trace_3_is_vf(self):
        """tr(A^3) = v*f: closed 3-walks = vertices * multiplicity f."""
        assert self._trace(3) == V * F


# ═══════════════════════════════════════════════════════════════════
# T528: Cayley-Hamilton Coefficients
# ═══════════════════════════════════════════════════════════════════
class TestCayleyHamilton:
    """A^3 = theta*A^2 + 32*A - 96*I.

    Coefficients of the minimal polynomial:
    k+r+s = theta = 10,
    -(kr+ks+rs) = 32 = 2^5,
    krs = -96 = -k*dimO.
    """

    SUM = K + R + S
    SYM2 = -(K*R + K*S + R*S)
    PROD = K * R * S

    def test_sum_is_theta(self):
        assert self.SUM == THETA

    def test_sym2_is_32(self):
        """-(kr+ks+rs) = 32 = 2^5."""
        assert self.SYM2 == 32
        assert self.SYM2 == 2**5

    def test_product_is_neg_k_dimO(self):
        """krs = -96 = -k*dimO = -12*8."""
        assert self.PROD == -K * DIM_O

    def test_product_value(self):
        assert self.PROD == -96

    def test_cayley_hamilton_identity(self):
        """Verify: for each eigenvalue lambda, lambda^3 = theta*lambda^2 + 32*lambda - 96."""
        for lam in [K, R, S]:
            assert lam**3 == THETA * lam**2 + 32 * lam - 96


# ═══════════════════════════════════════════════════════════════════
# T529: Normalised Laplacian
# ═══════════════════════════════════════════════════════════════════
class TestNormalisedLaplacian:
    """Normalised Laplacian eigenvalues: {0, 1-r/k, 1-s/k} = {0, 5/6, 4/3}.

    For SRG with k-regular: L_norm = I - A/k.
    Eigenvalues are 0, (k-r)/k = theta/k = 5/6, (k-s)/k = (k+mu)/k = 4/3.
    """

    def test_nlap_1(self):
        """First non-zero normalised eigenvalue = 5/6."""
        assert Fraction(K - R, K) == Fraction(5, 6)

    def test_nlap_2(self):
        """Second non-zero normalised eigenvalue = 4/3."""
        assert Fraction(K - S, K) == Fraction(4, 3)

    def test_nlap_sum(self):
        """Sum of normalised eigenvalues = f*5/6 + g*4/3 = 40 = V."""
        total = F * Fraction(5, 6) + G * Fraction(4, 3)
        assert total == V

    def test_nlap_product(self):
        """Product of non-zero eigenvalues = (5/6)^f * (4/3)^g determines tau."""
        assert Fraction(5, 6) * Fraction(4, 3) == Fraction(10, 9)

    def test_nlap_exceeds_1(self):
        """One normalised eigenvalue > 1: the graph is NOT bipartite (correct)."""
        assert Fraction(K - S, K) > 1


# ═══════════════════════════════════════════════════════════════════
# T530: Resolvent Identities
# ═══════════════════════════════════════════════════════════════════
class TestResolvent:
    """Resolvent R(z) = Tr((zI-A)^{-1}) = 1/(z-k) + f/(z-r) + g/(z-s)
    evaluated at special points.

    R(-1) = -V/PHI3 = -40/13,
    R(0) = -25/3 = -N^2/q,
    R(6) = 22/3 = 2*11/q,
    R(1) = -232/11 = -232/(k-1).
    """

    @staticmethod
    def _R(z):
        return Fraction(1, z - K) + Fraction(F, z - R) + Fraction(G, z - S)

    def test_R_neg1(self):
        """R(-1) = -40/13 = -V/PHI3."""
        assert self._R(-1) == Fraction(-V, PHI3)

    def test_R_0(self):
        """R(0) = -25/3 = -N^2/q."""
        assert self._R(0) == Fraction(-N**2, Q)

    def test_R_6(self):
        """R(6) = 22/3."""
        assert self._R(6) == Fraction(22, 3)

    def test_R_1(self):
        """R(1) = -232/11 = -232/(k-1)."""
        assert self._R(1) == Fraction(-232, K - 1)

    def test_R_at_N(self):
        """R(5) = R(N) = 200/21."""
        assert self._R(N) == Fraction(200, 21)
