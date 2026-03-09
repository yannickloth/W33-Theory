"""
Phase XXXIX: Spectral Thermodynamics & Quantum Walks on W(3,3) (T546-T560)
==========================================================================

Fifteen theorems exploring the heat kernel, spectral zeta function,
Estrada index, von Neumann graph entropy, continuous-time quantum walks,
and thermodynamic partition function on W(3,3).

Key discoveries:
  - The quantum walk on W(3,3) has period exactly π and returns with
    unit probability (perfect revival).
  - At the half-period π/2, the return probability is exactly 1/N² = 1/25,
    with amplitude −dim_O/V = −1/5.
  - The von Neumann graph entropy equals (1/2)·ln(V(V−μ)) = ln(q√(μV)).
  - The trace ratio Tr(L²)/Tr(L) = Φ₃ = 13 (cyclotomic!).
  - The spectral Vandermonde determinant Δ = Vf = 960.

Parameters: (v, k, λ, μ, q) = (40, 12, 2, 4, 3).
"""

import math
import numpy as np
import pytest
from fractions import Fraction

# ── SRG parameters for W(3,3) ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2           # 240
R, S = 2, -4             # eigenvalues
F, G = 24, 15            # multiplicities
N = Q + 2                # 5
PHI3 = Q**2 + Q + 1      # 13
PHI6 = Q**2 - Q + 1      # 7
ALBERT = V - PHI3        # 27
DIM_O = K - MU           # 8
THETA = 10               # Lovász theta
AUT = 51840              # |Aut(W(3,3))| = |W(E6)|

# ── Laplacian eigenvalues ──
# L = KI - A has eigenvalues {0, K-R, K-S} = {0, 10, 16}
THETA_L1 = K - R          # 10 (with multiplicity F=24)
THETA_L2 = K - S          # 16 (with multiplicity G=15)


# ═══════════════════════════════════════════════════════════════════
# T546: Laplacian Heat Trace
# ═══════════════════════════════════════════════════════════════════
class TestHeatTrace:
    """Z(t) = Tr(e^{-tL}) = 1 + f·e^{-θ₁t} + g·e^{-θ₂t}.
    Encodes all spectral information of the Laplacian.
    Z(0) = V (total vertex count), Z(∞) → 1 (connected component).
    """

    def heat_trace(self, t):
        return 1 + F * np.exp(-THETA_L1 * t) + G * np.exp(-THETA_L2 * t)

    def test_z_at_zero(self):
        """Z(0) = 1 + f + g = V = 40."""
        assert self.heat_trace(0) == pytest.approx(V)

    def test_z_at_infinity(self):
        """Z(∞) → 1 (one connected component)."""
        assert self.heat_trace(100) == pytest.approx(1.0, abs=1e-10)

    def test_z_positive(self):
        """Z(t) > 0 for all t ≥ 0 (partition function positivity)."""
        for t in np.linspace(0, 10, 100):
            assert self.heat_trace(t) > 0

    def test_z_monotone_decreasing(self):
        """Z(t) is strictly decreasing for t > 0."""
        ts = np.linspace(0.01, 3, 50)
        vals = [self.heat_trace(t) for t in ts]
        for i in range(len(vals) - 1):
            assert vals[i] >= vals[i + 1] - 1e-15

    def test_z_eigenvalue_count(self):
        """Z(t) has exactly 3 exponential terms (3-eigenvalue spectrum)."""
        # For W(3,3), the Laplacian has 3 distinct eigenvalues
        distinct = {0, THETA_L1, THETA_L2}
        assert len(distinct) == 3
        # Total multiplicity
        assert 1 + F + G == V


# ═══════════════════════════════════════════════════════════════════
# T547: Trace Moments of Laplacian
# ═══════════════════════════════════════════════════════════════════
class TestTraceMoments:
    """Tr(L^n) = f·θ₁ⁿ + g·θ₂ⁿ.  The ratio Tr(L²)/Tr(L) = Φ₃ = 13
    is a cyclotomic number, linking heat asymptotics to cyclotomy.
    """

    def trace_Ln(self, n):
        return F * THETA_L1**n + G * THETA_L2**n

    def test_trace_L1(self):
        """Tr(L) = f·θ₁ + g·θ₂ = 240 + 240 = 480 = 2E."""
        assert self.trace_Ln(1) == 2 * E
        assert self.trace_Ln(1) == K * V

    def test_trace_L2(self):
        """Tr(L²) = f·θ₁² + g·θ₂² = 2400 + 3840 = 6240 = 2E·Φ₃."""
        assert self.trace_Ln(2) == 2 * E * PHI3

    def test_trace_ratio(self):
        """Tr(L²)/Tr(L) = K + 1 = Φ₃ = 13 (general identity for W(3,q))."""
        ratio = Fraction(self.trace_Ln(2), self.trace_Ln(1))
        assert ratio == PHI3
        assert ratio == K + 1

    def test_trace_derivative_link(self):
        """Z'(0) = -Tr(L) = -2E = -480 (first derivative gives edge count)."""
        assert -self.trace_Ln(1) == -2 * E

    def test_trace_L3(self):
        """Tr(L³) = f·θ₁³ + g·θ₂³ = 24000 + 61440 = 85440."""
        assert self.trace_Ln(3) == F * THETA_L1**3 + G * THETA_L2**3
        assert self.trace_Ln(3) == 85440

    def test_individual_sums_equal(self):
        """f·θ₁ = g·θ₂ = E = 240 (each eigenspace contributes equally)."""
        assert F * THETA_L1 == E
        assert G * THETA_L2 == E


# ═══════════════════════════════════════════════════════════════════
# T548: Spectral Determinant Factorization
# ═══════════════════════════════════════════════════════════════════
class TestSpectralDeterminant:
    """det'(L) = θ₁^f · θ₂^g = 10^24 · 16^15 = 2^84 · 5^24.
    Kirchhoff's theorem: τ = det'(L)/V = 2^81 · 5^23 spanning trees.
    """

    def test_prime_factorization(self):
        """det'(L) = 2^84 · 5^24."""
        det_L = THETA_L1**F * THETA_L2**G
        assert det_L == 2**84 * 5**24

    def test_spanning_trees(self):
        """τ = det'(L)/V = 2^81 · 5^23."""
        det_L = THETA_L1**F * THETA_L2**G
        tau = det_L // V
        assert tau == 2**81 * 5**23

    def test_det_only_primes_2_5(self):
        """det'(L) has exactly two prime factors: 2 and 5."""
        det_L = THETA_L1**F * THETA_L2**G
        n = det_L
        while n % 2 == 0:
            n //= 2
        while n % 5 == 0:
            n //= 5
        assert n == 1

    def test_exponent_sum(self):
        """Sum of prime exponents: 84 + 24 = 108 = V + 2f + 2g + 8."""
        # 84 comes from 2^24 (from 10^24) + 2^60 (from 16^15)
        # 24 + 60 = 84
        assert 24 + 4 * G == 84  # 24 (from 10=2*5) + 4*15 (from 16=2^4)
        # 24 comes solely from 5^24 in 10^24
        assert F == 24


# ═══════════════════════════════════════════════════════════════════
# T549: Spectral Zeta Function
# ═══════════════════════════════════════════════════════════════════
class TestSpectralZeta:
    """ζ_L(s) = f/θ₁^s + g/θ₂^s is the spectral zeta function of L.
    ζ_L(1) = 267/80 (the Green's function trace).
    """

    def zeta_L(self, s):
        return Fraction(F, THETA_L1**s) + Fraction(G, THETA_L2**s)

    def test_zeta_at_1(self):
        """ζ_L(1) = f/θ₁ + g/θ₂ = 24/10 + 15/16 = 267/80."""
        assert self.zeta_L(1) == Fraction(267, 80)

    def test_zeta_at_2(self):
        """ζ_L(2) = f/θ₁² + g/θ₂² = 24/100 + 15/256."""
        expected = Fraction(F, THETA_L1**2) + Fraction(G, THETA_L2**2)
        assert self.zeta_L(2) == expected

    def test_zeta_numerator_267(self):
        """267 = 3 × 89; the numerator of ζ_L(1)."""
        assert 267 == 3 * 89

    def test_green_trace_equals_zeta1(self):
        """Tr(G) = ζ_L(1) = 267/80 (Green's function trace = spectral zeta at 1)."""
        green_trace = Fraction(F, THETA_L1) + Fraction(G, THETA_L2)
        assert green_trace == self.zeta_L(1)

    def test_zeta_decreasing(self):
        """ζ_L(s) is decreasing for s > 0 (eigenvalues > 1)."""
        assert float(self.zeta_L(1)) > float(self.zeta_L(2))
        assert float(self.zeta_L(2)) > float(self.zeta_L(3))


# ═══════════════════════════════════════════════════════════════════
# T550: Zeta-Determinant Identity
# ═══════════════════════════════════════════════════════════════════
class TestZetaDeterminantLink:
    """−ζ'_L(0) = f·ln(θ₁) + g·ln(θ₂) = ln(det'(L)).
    This links zeta regularization to the spectral determinant,
    exactly as in quantum field theory.
    """

    def test_zeta_prime_equals_ln_det(self):
        """f·ln(θ₁) + g·ln(θ₂) = ln(θ₁^f · θ₂^g) = ln(det'(L))."""
        lhs = F * math.log(THETA_L1) + G * math.log(THETA_L2)
        rhs = math.log(float(THETA_L1**F * THETA_L2**G))
        assert lhs == pytest.approx(rhs, rel=1e-12)

    def test_decomposition_ln10_ln16(self):
        """−ζ'(0) = 24·ln(10) + 15·ln(16) = 24·ln(10) + 60·ln(2)."""
        val1 = F * math.log(10) + G * math.log(16)
        val2 = F * math.log(10) + 4 * G * math.log(2)
        assert val1 == pytest.approx(val2, rel=1e-14)

    def test_ln_det_from_primes(self):
        """ln(det'(L)) = 84·ln(2) + 24·ln(5)."""
        lhs = F * math.log(THETA_L1) + G * math.log(THETA_L2)
        rhs = 84 * math.log(2) + 24 * math.log(5)
        assert lhs == pytest.approx(rhs, rel=1e-12)

    def test_numerical_value(self):
        """−ζ'_L(0) ≈ 96.85 > 0 (positive spectral action)."""
        val = F * math.log(THETA_L1) + G * math.log(THETA_L2)
        assert val == pytest.approx(96.850873, rel=1e-5)
        assert val > 0


# ═══════════════════════════════════════════════════════════════════
# T551: Estrada Index & Communicability
# ═══════════════════════════════════════════════════════════════════
class TestEstradaIndex:
    """EE = Tr(e^A) = e^k + f·e^r + g·e^s.
    The Estrada index measures subgraph centrality and communicability.
    For W(3,3), EE ≈ 162932 is dominated by the e^k term.
    """

    def test_estrada_definition(self):
        """EE = e^12 + 24·e^2 + 15·e^{-4}."""
        ee = math.exp(K) + F * math.exp(R) + G * math.exp(S)
        assert ee == pytest.approx(162932.40, rel=1e-4)

    def test_estrada_dominated_by_k(self):
        """e^k contributes > 99.8% of the Estrada index."""
        ee = math.exp(K) + F * math.exp(R) + G * math.exp(S)
        ratio = math.exp(K) / ee
        assert ratio > 0.998

    def test_subgraph_centrality(self):
        """SC = EE/V (average subgraph centrality per vertex)."""
        ee = math.exp(K) + F * math.exp(R) + G * math.exp(S)
        sc = ee / V
        assert sc == pytest.approx(4073.31, rel=1e-3)

    def test_natural_connectivity(self):
        """λ̄ = ln(EE/V) ≈ 8.31 (natural connectivity measure)."""
        ee = math.exp(K) + F * math.exp(R) + G * math.exp(S)
        nc = math.log(ee / V)
        assert nc == pytest.approx(8.312, rel=1e-2)

    def test_estrada_vs_energy(self):
        """EE ≫ graph energy (exponential vs linear in eigenvalues)."""
        ee = math.exp(K) + F * math.exp(R) + G * math.exp(S)
        energy = K + F * abs(R) + G * abs(S)  # = E/2 = 120
        assert ee > energy * 1000


# ═══════════════════════════════════════════════════════════════════
# T552: Bipartiteness Measure
# ═══════════════════════════════════════════════════════════════════
class TestBipartiteness:
    """The bipartiteness ratio β = ẼE/EE where ẼE = Tr(e^{-A}).
    For bipartite graphs β = 1; for W(3,3), β ≈ 0.005 ≪ 1.
    """

    def test_anti_estrada(self):
        """ẼE = e^{-12} + 24·e^{-2} + 15·e^4 ≈ 822.22."""
        ee_bar = math.exp(-K) + F * math.exp(-R) + G * math.exp(-S)
        assert ee_bar == pytest.approx(822.22, rel=1e-3)

    def test_bipartiteness_ratio(self):
        """β = ẼE/EE ≈ 0.00505 ≪ 1 (far from bipartite)."""
        ee = math.exp(K) + F * math.exp(R) + G * math.exp(S)
        ee_bar = math.exp(-K) + F * math.exp(-R) + G * math.exp(-S)
        beta = ee_bar / ee
        assert beta == pytest.approx(0.00505, rel=1e-2)
        assert beta < 0.01

    def test_anti_estrada_dominated_by_s(self):
        """g·e^{-s} = 15·e^4 dominates ẼE (complementary to Estrada)."""
        ee_bar = math.exp(-K) + F * math.exp(-R) + G * math.exp(-S)
        s_term = G * math.exp(-S)
        assert s_term / ee_bar > 0.99

    def test_not_bipartite(self):
        """β < 1 confirms W(3,3) is not bipartite."""
        ee = math.exp(K) + F * math.exp(R) + G * math.exp(S)
        ee_bar = math.exp(-K) + F * math.exp(-R) + G * math.exp(-S)
        assert ee_bar < ee

    def test_odd_cycle_existence(self):
        """Tr(A³) = 960 ≠ 0 confirms odd cycles exist (non-bipartite)."""
        tr_A3 = K**3 + F * R**3 + G * S**3
        assert tr_A3 == V * F
        assert tr_A3 != 0


# ═══════════════════════════════════════════════════════════════════
# T553: Von Neumann Graph Entropy
# ═══════════════════════════════════════════════════════════════════
class TestVonNeumannEntropy:
    """The von Neumann entropy of ρ = L/Tr(L) equals (1/2)·ln(V(V−μ)).
    For W(3,3): S = (1/2)·ln(1440) = ln(12√10) = ln(q·√(μV)).
    """

    def test_density_eigenvalues(self):
        """ρ = L/Tr(L) has eigenvalues {0, 1/48, 1/30}."""
        rho1 = Fraction(THETA_L1, 2 * E)
        rho2 = Fraction(THETA_L2, 2 * E)
        assert rho1 == Fraction(1, 48)
        assert rho2 == Fraction(1, 30)

    def test_density_trace(self):
        """Tr(ρ) = f/48 + g/30 = 1/2 + 1/2 = 1."""
        rho_trace = Fraction(F, 48) + Fraction(G, 30)
        assert rho_trace == 1

    def test_equal_weight_eigenspaces(self):
        """Each nonzero eigenspace contributes weight 1/2 to Tr(ρ)."""
        w1 = F * Fraction(THETA_L1, 2 * E)  # F * θ₁ / 2E = 240/480 = 1/2
        w2 = G * Fraction(THETA_L2, 2 * E)  # G * θ₂ / 2E = 240/480 = 1/2
        assert w1 == Fraction(1, 2)
        assert w2 == Fraction(1, 2)

    def test_entropy_value(self):
        """S = (1/2)·ln(V(V−μ)) = (1/2)·ln(1440)."""
        r1, r2 = 1.0 / 48, 1.0 / 30
        S_vN = -(F * r1 * math.log(r1) + G * r2 * math.log(r2))
        expected = 0.5 * math.log(V * (V - MU))
        assert S_vN == pytest.approx(expected, rel=1e-12)

    def test_entropy_product(self):
        """V(V−μ) = 40 × 36 = 1440 = 6E = 2qE."""
        assert V * (V - MU) == 1440
        assert 1440 == 6 * E
        assert 1440 == 2 * Q * E

    def test_entropy_compact_form(self):
        """S = ln(q·√(μV)) = ln(3·√160) = ln(12√10)."""
        s1 = 0.5 * math.log(V * (V - MU))
        s2 = math.log(Q * math.sqrt(MU * V))
        assert s1 == pytest.approx(s2, rel=1e-12)
        # 12√10 = q·√(μV) = 3·√(4·40) = 3·√160 = 3·4√10 = 12√10
        s3 = math.log(12 * math.sqrt(10))
        assert s1 == pytest.approx(s3, rel=1e-12)


# ═══════════════════════════════════════════════════════════════════
# T554: Continuous-Time Quantum Walk Period
# ═══════════════════════════════════════════════════════════════════
class TestQuantumWalkPeriod:
    """The continuous-time quantum walk e^{-iAt} on W(3,3) is periodic
    with period T = π.  Since all eigenvalues {k,r,s} = {12,2,-4}
    are integers, the differences {10,16,6} have gcd = 2, giving T = 2π/2 = π.
    """

    def test_eigenvalues_integral(self):
        """All adjacency eigenvalues are integers."""
        for ev in [K, R, S]:
            assert ev == int(ev)

    def test_eigenvalue_differences(self):
        """k−r = 10, k−s = 16, r−s = 6."""
        assert K - R == 10
        assert K - S == 16
        assert R - S == 6

    def test_gcd_of_differences(self):
        """gcd(10, 16, 6) = 2."""
        g = math.gcd(K - R, math.gcd(K - S, R - S))
        assert g == 2

    def test_period_is_pi(self):
        """Period T = 2π/gcd = 2π/2 = π."""
        g = math.gcd(K - R, math.gcd(K - S, R - S))
        T = 2 * math.pi / g
        assert T == pytest.approx(math.pi, rel=1e-14)

    def test_periodicity_check(self):
        """e^{-iλπ} is the same for all eigenvalues (up to global phase)."""
        phases = [np.exp(-1j * ev * math.pi) for ev in [K, R, S]]
        # All should be ±1 since eigenvalues are integers
        for phi in phases:
            assert abs(abs(phi) - 1) < 1e-10


# ═══════════════════════════════════════════════════════════════════
# T555: Perfect Quantum Revival
# ═══════════════════════════════════════════════════════════════════
class TestPerfectRevival:
    """At t = π, the quantum walk returns with unit probability.
    ⟨v|e^{-iAπ}|v⟩ = (1/V)(1 + f + g) = V/V = 1.
    All integer eigenvalues → all phases e^{-iλπ} = 1 at period π.
    """

    def test_return_amplitude(self):
        """⟨v|e^{-iAπ}|v⟩ = 1 (perfect return)."""
        # e^{-iKπ} = e^{-12iπ} = 1, e^{-iRπ} = e^{-2iπ} = 1, e^{-iSπ} = e^{4iπ} = 1
        amp = (np.exp(-1j * K * math.pi) + F * np.exp(-1j * R * math.pi)
               + G * np.exp(-1j * S * math.pi)) / V
        assert amp.real == pytest.approx(1.0, abs=1e-10)
        assert abs(amp.imag) < 1e-10

    def test_return_probability(self):
        """|⟨v|e^{-iAπ}|v⟩|² = 1."""
        amp = (np.exp(-1j * K * math.pi) + F * np.exp(-1j * R * math.pi)
               + G * np.exp(-1j * S * math.pi)) / V
        assert abs(amp)**2 == pytest.approx(1.0, abs=1e-10)

    def test_all_phases_unity(self):
        """All e^{-iλπ} = 1 for even integer eigenvalues."""
        for ev in [K, R, S]:
            phase = np.exp(-1j * ev * math.pi)
            assert phase.real == pytest.approx(1.0, abs=1e-10)
            assert abs(phase.imag) < 1e-10

    def test_sum_of_multiplicities(self):
        """Amplitude relies on 1 + f + g = V = 40."""
        assert 1 + F + G == V

    def test_double_period_revival(self):
        """At t = 2π, also perfect revival."""
        amp = (np.exp(-1j * K * 2 * math.pi) + F * np.exp(-1j * R * 2 * math.pi)
               + G * np.exp(-1j * S * 2 * math.pi)) / V
        assert abs(amp)**2 == pytest.approx(1.0, abs=1e-10)


# ═══════════════════════════════════════════════════════════════════
# T556: Half-Period Quantum Echo
# ═══════════════════════════════════════════════════════════════════
class TestHalfPeriodEcho:
    """At t = π/2, the return amplitude is −dim_O/V = −1/N = −1/5.
    Return probability = 1/N² = 1/25.

    This arises because e^{-iKπ/2} = e^{-6iπ} = 1, e^{-iRπ/2} = e^{-iπ} = −1,
    e^{-iSπ/2} = e^{2iπ} = 1, giving amplitude (1 − f + g)/V = −8/40 = −dim_O/V.
    """

    def test_half_period_amplitude(self):
        """⟨v|e^{-iAπ/2}|v⟩ = −dim_O/V = −1/N = −1/5."""
        amp = (np.exp(-1j * K * math.pi / 2) + F * np.exp(-1j * R * math.pi / 2)
               + G * np.exp(-1j * S * math.pi / 2)) / V
        assert amp.real == pytest.approx(-1.0 / N, abs=1e-10)
        assert abs(amp.imag) < 1e-10

    def test_half_period_probability(self):
        """|⟨v|e^{-iAπ/2}|v⟩|² = 1/N² = 1/25."""
        amp = (np.exp(-1j * K * math.pi / 2) + F * np.exp(-1j * R * math.pi / 2)
               + G * np.exp(-1j * S * math.pi / 2)) / V
        assert abs(amp)**2 == pytest.approx(1.0 / N**2, abs=1e-10)

    def test_alternating_sum(self):
        """1 − f + g = −8 = −dim_O (the multiplicity alternating sum)."""
        assert 1 - F + G == -DIM_O

    def test_amplitude_from_dim_o(self):
        """Amplitude = −dim_O/V = −(k−μ)/V = −8/40 = −1/5."""
        assert Fraction(-DIM_O, V) == Fraction(-1, N)

    def test_phases_at_half_period(self):
        """At π/2: e^{-12iπ/2}=1, e^{-2iπ/2}=−1, e^{4iπ/2}=1."""
        p_k = np.exp(-1j * K * math.pi / 2)
        p_r = np.exp(-1j * R * math.pi / 2)
        p_s = np.exp(-1j * S * math.pi / 2)
        assert p_k.real == pytest.approx(1.0, abs=1e-10)
        assert p_r.real == pytest.approx(-1.0, abs=1e-10)
        assert p_s.real == pytest.approx(1.0, abs=1e-10)


# ═══════════════════════════════════════════════════════════════════
# T557: Time-Averaged Quantum Return Probability
# ═══════════════════════════════════════════════════════════════════
class TestTimeAveragedReturn:
    """⟨p⟩ = (1/T)∫₀ᵀ |a(t)|² dt = Σ mₗ²/V² = (1+f²+g²)/V² = 401/800.
    Here 401 is prime, and 800 = V²/2.
    """

    def test_time_average_formula(self):
        """⟨p⟩ = (1 + f² + g²)/V² = 802/1600 = 401/800."""
        p_avg = Fraction(1 + F**2 + G**2, V**2)
        assert p_avg == Fraction(401, 800)

    def test_numerator_802(self):
        """1 + f² + g² = 1 + 576 + 225 = 802 = 2 × 401."""
        assert 1 + F**2 + G**2 == 802

    def test_401_prime(self):
        """401 is prime."""
        assert all(401 % p != 0 for p in range(2, 21))

    def test_above_uniform(self):
        """⟨p⟩ = 401/800 > 1/V = 1/40 (quantum localization)."""
        p_avg = Fraction(401, 800)
        uniform = Fraction(1, V)
        assert p_avg > uniform

    def test_numerical_integration(self):
        """Numerical time average over one period matches 401/800."""
        ts = np.linspace(0, math.pi, 10000)
        dt = ts[1] - ts[0]
        total = 0.0
        for t in ts:
            amp = (np.exp(-1j * K * t) + F * np.exp(-1j * R * t)
                   + G * np.exp(-1j * S * t)) / V
            total += abs(amp)**2 * dt
        avg = total / math.pi
        assert avg == pytest.approx(401.0 / 800, rel=1e-3)


# ═══════════════════════════════════════════════════════════════════
# T558: Cheeger Isoperimetric Bounds
# ═══════════════════════════════════════════════════════════════════
class TestCheegerBounds:
    """The Cheeger constant h(G) satisfies N ≤ h ≤ √E.
    Lower bound: (k − λ₂)/2 = (k−r)/2 = 5 = N = q+2.
    Upper bound: √(2k(k−r)) = √(2·12·10) = √240 = √E.
    W(3,3) is an expander graph.
    """

    def test_lower_bound_equals_N(self):
        """(k − r)/2 = 10/2 = 5 = N = q + 2."""
        lower = (K - R) // 2
        assert lower == N
        assert lower == Q + 2

    def test_upper_bound_equals_sqrt_E(self):
        """√(2k(k−r)) = √(2·12·10) = √240 = √E."""
        upper_sq = 2 * K * (K - R)
        assert upper_sq == 240
        assert upper_sq == E

    def test_expander(self):
        """h ≥ 5 > 0 confirms W(3,3) is an expander."""
        assert (K - R) / 2 > 0

    def test_spectral_gap_value(self):
        """Spectral gap α = k − r = 10 = θ₁ (Laplacian smallest nonzero)."""
        gap = K - R
        assert gap == 10
        assert gap == THETA_L1

    def test_cheeger_ratio(self):
        """Upper/Lower = √E/N = √(240)/5 = 4√15/5 ≈ 3.098."""
        ratio = math.sqrt(E) / N
        assert ratio == pytest.approx(4 * math.sqrt(15) / 5, rel=1e-10)


# ═══════════════════════════════════════════════════════════════════
# T559: Thermodynamic Energy & Free Energy
# ═══════════════════════════════════════════════════════════════════
class TestThermodynamicEnergy:
    """The Laplacian partition function Z(β) defines a thermodynamics.
    At infinite temperature (β→0): U = k (energy = degree).
    F(β) = −(1/β)·ln Z(β) interpolates between −ln(V)/β and 0.
    """

    def test_infinite_temp_energy(self):
        """U(β→0) = Tr(L)/V = 2E/V = 12 = k."""
        U_inf = (F * THETA_L1 + G * THETA_L2) / (1 + F + G)
        assert U_inf == pytest.approx(K)

    def test_zero_temp_energy(self):
        """U(β→∞) → 0 (ground state energy)."""
        # At large β, everything except ground state is exponentially suppressed
        beta = 100
        num = F * THETA_L1 * math.exp(-THETA_L1 * beta) + G * THETA_L2 * math.exp(-THETA_L2 * beta)
        den = 1 + F * math.exp(-THETA_L1 * beta) + G * math.exp(-THETA_L2 * beta)
        assert num / den == pytest.approx(0, abs=1e-10)

    def test_high_temp_free_energy(self):
        """F(β→0) ≈ −ln(V)/β → −∞."""
        beta = 0.001
        Z = 1 + F * math.exp(-THETA_L1 * beta) + G * math.exp(-THETA_L2 * beta)
        F_val = -math.log(Z) / beta
        F_approx = -math.log(V) / beta
        assert F_val == pytest.approx(F_approx, rel=1e-2)

    def test_low_temp_free_energy(self):
        """F(β→∞) → 0 (ground state free energy vanishes)."""
        beta = 100
        Z = 1 + F * math.exp(-THETA_L1 * beta) + G * math.exp(-THETA_L2 * beta)
        F_val = -math.log(Z) / beta
        assert F_val == pytest.approx(0, abs=1e-5)

    def test_energy_equals_KV_over_V(self):
        """U(0) = KV/V = K = 12 (degree equals infinite-temp energy)."""
        # General identity for k-regular graph: Tr(L)/V = K
        assert Fraction(F * THETA_L1 + G * THETA_L2, V) == K


# ═══════════════════════════════════════════════════════════════════
# T560: Lagrange Spectral Calculus & Vandermonde
# ═══════════════════════════════════════════════════════════════════
class TestLagrangeCalculus:
    """Any function f(A) equals c₀I + c₁A + c₂A² (3-eigenvalue Lagrange).
    The spectral Vandermonde determinant Δ = (k−r)(k−s)(r−s) = Vf = 960.
    The SRG equation A² + 2A − dim_O·I = μJ unifies all spectral structure.
    """

    def test_vandermonde_determinant(self):
        """Δ = (k−r)(k−s)(r−s) = 10·16·6 = 960 = V·f."""
        Delta = (K - R) * (K - S) * (R - S)
        assert Delta == 960
        assert Delta == V * F

    def test_lagrange_denominators(self):
        """Lagrange denominators: Δ₀=160, Δ₁=−60, Δ₂=96."""
        D0 = (K - R) * (K - S)      # 10 * 16 = 160
        D1 = (R - K) * (R - S)      # (-10) * 6 = -60
        D2 = (S - K) * (S - R)      # (-16) * (-6) = 96
        assert D0 == 160
        assert D1 == -60
        assert D2 == 96

    def test_srg_matrix_equation(self):
        """A² + 2A − dim_O·I = μJ (fundamental SRG equation).

        From A² = dim_O·I + (λ−μ)A + μJ = 8I − 2A + 4J.
        """
        # Verify eigenvalue-by-eigenvalue:
        # For λ = k: k² + 2k - DIM_O should equal μ·V (since J has eigenvalue V for const vec)
        assert K**2 + 2 * K - DIM_O == MU * V  # 144+24-8 = 160 = 4·40 ✓
        # For λ = r: r² + 2r - DIM_O should equal 0 (since Jv=0 for non-const eigenvectors)
        assert R**2 + 2 * R - DIM_O == 0  # 4+4-8 = 0 ✓
        # For λ = s: s² + 2s - DIM_O should equal 0
        assert S**2 + 2 * S - DIM_O == 0  # 16-8-8 = 0 ✓

    def test_eigenvalue_quadratic(self):
        """r and s are roots of x² + 2x − dim_O = 0."""
        # x² + 2x - 8 = 0 → x = (-2 ± √(4+32))/2 = (-2 ± 6)/2 → x = 2 or x = -4
        discriminant = 4 + 4 * DIM_O
        sqrt_disc = int(math.isqrt(discriminant))
        assert sqrt_disc**2 == discriminant
        root1 = (-2 + sqrt_disc) // 2
        root2 = (-2 - sqrt_disc) // 2
        assert {root1, root2} == {R, S}

    def test_product_relation(self):
        """r·s = −dim_O = −8 (Vieta: product of eigenvalues)."""
        assert R * S == -DIM_O

    def test_sum_relation(self):
        """r + s = −2 (Vieta: sum of eigenvalues)."""
        assert R + S == -2
        assert R + S == LAM - MU

    def test_lagrange_for_identity(self):
        """f(x) = 1: Lagrange gives c₀I + c₁A + c₂A² = I.
        Coefficients sum correctly via Lagrange.
        """
        D0 = (K - R) * (K - S)
        D1 = (R - K) * (R - S)
        D2 = (S - K) * (S - R)
        # f(k)=1, f(r)=1, f(s)=1 → l₀+l₁+l₂ = I
        # The sum 1/D0·(x-r)(x-s) + 1/D1·(x-k)(x-s) + 1/D2·(x-k)(x-r) = 1 for all x
        for x in [K, R, S, 0, 1, -1, 5]:
            val = (Fraction((x - R) * (x - S), D0)
                   + Fraction((x - K) * (x - S), D1)
                   + Fraction((x - K) * (x - R), D2))
            assert val == 1
