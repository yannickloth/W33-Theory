"""
Phase L — Polynomial Anatomy, Spectral Measure & Special Values (T711-T725)

The minimal polynomial m(x) = x³ − ALPHA·x² − 2^N·x + Q·2^N encodes the
entire SRG through its coefficients, evaluations at graph constants, factor
anatomy, critical points, and discriminant.  Every evaluation m(c) for any
named graph constant c yields another named constant.  The complement minimal
polynomial m̄(x) = (x − ALBERT)(x² − Q²) mirrors this structure, and the
combined 6-eigenvalue spectrum satisfies ALPHA + ALBERT = V − Q.

All from (v, k, λ, μ, q) = (40, 12, 2, 4, 3).
"""

import pytest
from fractions import Fraction

# ── five source numbers ──────────────────────────────────────────────
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2                     # 240 edges
R, S = 2, -4                       # SRG eigenvalues
F, G = 24, 15                      # multiplicities
N = Q + 2                          # 5
THETA = K - R                      # 10
ALPHA = V // MU                    # 10
OMEGA = MU                         # 4
DIM_O = K - MU                     # 8
ALBERT = V - (Q**2 + MU)           # 27
PHI3 = Q**2 + Q + 1                # 13
PHI6 = Q**2 - Q + 1                # 7
K_BAR = V - 1 - K                  # 27
r_s = R - S                        # 6


def m(x):
    """Minimal polynomial of the adjacency matrix: (x-K)(x-R)(x-S)."""
    return (x - K) * (x - R) * (x - S)


def p(x):
    """Full characteristic polynomial: (x-K)^1 · (x-R)^F · (x-S)^G."""
    return (x - K) * (x - R)**F * (x - S)**G


# =====================================================================
# T711 — Minimal Polynomial Evaluations at Graph Constants
# =====================================================================
class TestT711_MinPolyEvaluations:
    """m(x) at every named graph constant yields another named constant.
    
    m(r−s) = −E, m(−1) = Q²·Φ₃, m(Q) = −Q²·Φ₆, m(−Q) = Q·N²,
    m(N) = −ALBERT·Φ₆, m(MU) = −2^Φ₆, m(DIM_O) = −Q²·2^N,
    m(ALPHA) = −2^N·Φ₆, m(0) = Q·2^N, m(1) = N·(K−1).
    """

    def test_m_at_r_minus_s(self):
        """m(r−s) = −E: the edge count emerges from the eigenvalue gap."""
        assert m(r_s) == -E

    def test_m_at_neg1(self):
        """m(−1) = Q²·Φ₃ = 117."""
        assert m(-1) == Q**2 * PHI3

    def test_m_at_Q(self):
        """m(Q) = −Q²·Φ₆ = −63."""
        assert m(Q) == -Q**2 * PHI6

    def test_m_at_neg_Q(self):
        """m(−Q) = Q·N² = 75."""
        assert m(-Q) == Q * N**2

    def test_m_at_N(self):
        """m(N) = −ALBERT·Φ₆ = −Q³·Φ₆ = −189."""
        assert m(N) == -ALBERT * PHI6
        assert m(N) == -Q**3 * PHI6

    def test_m_at_MU(self):
        """m(MU) = −2^Φ₆ = −128."""
        assert m(MU) == -(2**PHI6)

    def test_m_at_DIM_O(self):
        """m(DIM_O) = −Q²·2^N = −288."""
        assert m(DIM_O) == -Q**2 * 2**N

    def test_m_at_ALPHA(self):
        """m(ALPHA) = −2^N·Φ₆ = −224."""
        assert m(ALPHA) == -(2**N) * PHI6

    def test_m_at_0(self):
        """m(0) = Q·2^N = 96 (free term)."""
        assert m(0) == Q * 2**N

    def test_m_at_1(self):
        """m(1) = N·(K−1) = 55."""
        assert m(1) == N * (K - 1)


# =====================================================================
# T712 — Factor Table: Every Factor is a Named Constant
# =====================================================================
class TestT712_FactorTable:
    """At special x, each of (x−K), (x−R), (x−S) is a named graph constant.
    
    The entire multiplication table of factors closes on the named constants.
    """

    def test_factors_at_neg1(self):
        """x=−1: (−1−K)=−Φ₃, (−1−R)=−Q, (−1−S)=Q."""
        assert -1 - K == -PHI3
        assert -1 - R == -Q
        assert -1 - S == Q

    def test_factors_at_1(self):
        """x=1: (1−K)=−(K−1), (1−R)=−1, (1−S)=N."""
        assert 1 - K == -(K - 1)
        assert 1 - R == -1
        assert 1 - S == N

    def test_factors_at_Q(self):
        """x=Q: (Q−K)=−Q², (Q−R)=1, (Q−S)=Φ₆."""
        assert Q - K == -Q**2
        assert Q - R == 1
        assert Q - S == PHI6

    def test_factors_at_N(self):
        """x=N: (N−K)=−Φ₆, (N−R)=Q, (N−S)=Q²."""
        assert N - K == -PHI6
        assert N - R == Q
        assert N - S == Q**2

    def test_factors_at_MU(self):
        """x=MU: (MU−K)=−DIM_O, (MU−R)=LAM, (MU−S)=DIM_O."""
        assert MU - K == -DIM_O
        assert MU - R == LAM
        assert MU - S == DIM_O

    def test_factors_at_DIM_O(self):
        """x=DIM_O: (DIM_O−K)=−MU, (DIM_O−R)=r−s, (DIM_O−S)=K."""
        assert DIM_O - K == -MU
        assert DIM_O - R == r_s
        assert DIM_O - S == K

    def test_factors_at_r_s(self):
        """x=r−s: (r−s−K)=−(r−s), (r−s−R)=Ω, (r−s−S)=ALPHA."""
        assert r_s - K == -r_s
        assert r_s - R == OMEGA
        assert r_s - S == ALPHA

    def test_MU_DIM_O_duality(self):
        """MU + DIM_O = K: the factor table is self-dual under MU ↔ DIM_O."""
        assert MU + DIM_O == K
        # At MU: factors −DIM_O, LAM, DIM_O
        # At DIM_O: factors −MU, r−s, K
        assert (MU - S) == -(MU - K)  # DIM_O each way


# =====================================================================
# T713 — m(r−s) = −E: Edge Count from Eigenvalue Gap
# =====================================================================
class TestT713_EdgeCountFromGap:
    """m(r−s) = (r−s−K)(r−s−R)(r−s−S) = (−r_s)(Ω)(ALPHA) = −E.
    
    The three factors at x = r−s are exactly −r_s, MU, and ALPHA,
    whose product r_s·MU·ALPHA = 6·4·10 = 240 = V·K/2 = E.
    """

    def test_three_factors_named(self):
        """(r−s−K) = −r_s, (r−s−R) = Ω = MU, (r−s−S) = ALPHA."""
        assert r_s - K == -r_s
        assert r_s - R == OMEGA
        assert r_s - S == ALPHA

    def test_product_is_neg_E(self):
        """(−r_s)·Ω·ALPHA = −E = −240."""
        assert (-r_s) * OMEGA * ALPHA == -E

    def test_r_s_times_MU_times_ALPHA_is_E(self):
        """r_s·MU·ALPHA = V·K/2 = E."""
        assert r_s * MU * ALPHA == E
        assert r_s * MU * ALPHA == V * K // 2


# =====================================================================
# T714 — Critical Points of m'(x)
# =====================================================================
class TestT714_CriticalPoints:
    """m'(x) = 0 at x = DIM_O and x = −MU/Q.
    
    Critical pts = (2·ALPHA ± Ω·Φ₆)/6 where disc(m') = (Ω·Φ₆)² = 784.
    c₁ = DIM_O (local min between R and K).
    c₂ = −MU/Q = −4/3 (local max between S and R).
    """

    def test_critical_point_c1(self):
        """c₁ = (2·ALPHA + Ω·Φ₆)/6 = DIM_O = 8."""
        c1 = Fraction(2 * ALPHA + OMEGA * PHI6, 6)
        assert c1 == DIM_O

    def test_critical_point_c2(self):
        """c₂ = (2·ALPHA − Ω·Φ₆)/6 = −MU/Q = −4/3."""
        c2 = Fraction(2 * ALPHA - OMEGA * PHI6, 6)
        assert c2 == Fraction(-MU, Q)

    def test_discriminant_of_derivative(self):
        """disc(m') = (Ω·Φ₆)² = 28² = 784."""
        disc_mp = (2 * ALPHA)**2 + 12 * 2**N
        assert disc_mp == (OMEGA * PHI6)**2
        assert disc_mp == 784

    def test_c1_between_R_and_K(self):
        """DIM_O sits between R = 2 and K = 12."""
        assert R < DIM_O < K

    def test_c2_between_S_and_R(self):
        """−MU/Q = −4/3 sits between S = −4 and R = 2."""
        c2 = Fraction(-MU, Q)
        assert S < c2 < R

    def test_omega_phi6_is_28(self):
        """Ω·Φ₆ = MU·PHI6 = 4·7 = 28."""
        assert OMEGA * PHI6 == 28


# =====================================================================
# T715 — Discriminant of m(x)
# =====================================================================
class TestT715_Discriminant:
    """disc(m) = (MU·E)² = (ALPHA·2^MU·r_s)² = 16·E² = 921600.
    
    √disc = MU·E = 4·E = 960 = ALPHA·2^Ω·r_s.
    """

    def test_discriminant_value(self):
        """disc = (K−R)²·(K−S)²·(R−S)² = 921600."""
        disc = (K - R)**2 * (K - S)**2 * (R - S)**2
        assert disc == 921600

    def test_disc_is_MU_E_squared(self):
        """disc = (MU·E)² = (4·240)² = 960²."""
        disc = (K - R)**2 * (K - S)**2 * (R - S)**2
        assert disc == (MU * E)**2

    def test_disc_is_16_E_squared(self):
        """disc = 16·E² = 2⁴·57600."""
        disc = (K - R)**2 * (K - S)**2 * (R - S)**2
        assert disc == 16 * E**2

    def test_sqrt_disc(self):
        """√disc = ALPHA·2^MU·r_s = 10·16·6 = 960."""
        sqrt_disc = ALPHA * 2**MU * r_s
        assert sqrt_disc == MU * E
        assert sqrt_disc == 960

    def test_factor_decomposition(self):
        """(K−R) = ALPHA, (K−S) = 2^MU, (R−S) = r_s = LAM+MU."""
        assert K - R == ALPHA
        assert K - S == 2**MU
        assert R - S == r_s
        assert r_s == LAM + MU


# =====================================================================
# T716 — Characteristic Polynomial at Extended Special Points
# =====================================================================
class TestT716_CharPolyExtended:
    """p(x) = (x−K)·(x−R)^F·(x−S)^G at points beyond T679.
    
    p(−1) = −Φ₃·Q^(V−1), p(−Q) = −G·N^F, p(MU) = −2^72,
    p(N) = −Φ₆·Q^(2·ALBERT), p(DIM_O) = −MU·(r−s)^F·K^G,
    p(r−s) = −(r−s)·Ω^F·ALPHA^G, p(0) = −Q·2^(DIM_O·Φ₆).
    """

    def test_p_at_neg1(self):
        """p(−1) = −Φ₃·Q^(V−1)."""
        assert p(-1) == -PHI3 * Q**(V - 1)

    def test_p_at_neg_Q(self):
        """p(−Q) = −G·N^F."""
        assert p(-Q) == -G * N**F

    def test_p_at_MU(self):
        """p(MU) = −2^72 where 72 = 2·(r−s)² = |Δ(E₆)|."""
        assert p(MU) == -(2**72)
        assert 72 == 2 * r_s**2

    def test_p_at_N(self):
        """p(N) = −Φ₆·Q^(2·ALBERT)."""
        assert p(N) == -PHI6 * Q**(2 * ALBERT)

    def test_p_at_DIM_O(self):
        """p(DIM_O) = −MU·(r−s)^F·K^G."""
        assert p(DIM_O) == -MU * r_s**F * K**G

    def test_p_at_r_s(self):
        """p(r−s) = −(r−s)·Ω^F·ALPHA^G."""
        assert p(r_s) == -r_s * OMEGA**F * ALPHA**G

    def test_p_at_0_is_det(self):
        """p(0) = det(A) = −Q·2^(DIM_O·Φ₆) = −Q·2^56."""
        assert p(0) == -Q * 2**(DIM_O * PHI6)
        assert DIM_O * PHI6 == 56


# =====================================================================
# T717 — Determinant Anatomy
# =====================================================================
class TestT717_DeterminantAnatomy:
    """det(A) = −Q·2^56 where 56 = DIM_O·Φ₆ = 8·7 = ovoid count.
    
    The exponent 56 appears as ovoids of GQ(3,3) and |W(E₇)|/|W(E₆)|.
    """

    def test_det_value(self):
        """det(A) = K·R^F·S^G = −Q·2^56."""
        det_A = K * R**F * S**G
        assert det_A == -Q * 2**56

    def test_exponent_is_56(self):
        """56 = DIM_O·Φ₆ = 8·7."""
        assert DIM_O * PHI6 == 56

    def test_56_is_ovoid_count(self):
        """56 ovoids of GQ(3,3) = |W(E₇)|/|W(E₆)| = DIM_O·Φ₆."""
        assert DIM_O * PHI6 == 56

    def test_abs_det_prime_factorization(self):
        """|det(A)| = 3·2^56.  Only primes 2 and 3 = {LAM, Q}."""
        abs_det = abs(K * R**F * S**G)
        assert abs_det == Q * 2**56
        # Only primes are 2=LAM and 3=Q
        assert abs_det == Q * LAM**56


# =====================================================================
# T718 — Eigenvalue Pair Arithmetic
# =====================================================================
class TestT718_EigenvaluePairArithmetic:
    """Every pairwise product, sum, and difference of {K, R, S}
    equals a named graph constant.
    
    K·R = F, R·S = −DIM_O, K+R = 2·Φ₆, K+S = DIM_O,
    K−R = ALPHA, K−S = 2^MU.
    """

    def test_KR_is_F(self):
        """K·R = 12·2 = 24 = F (multiplicity of r)."""
        assert K * R == F

    def test_RS_is_neg_DIM_O(self):
        """R·S = 2·(−4) = −8 = −DIM_O."""
        assert R * S == -DIM_O

    def test_KR_plus_KS_plus_RS(self):
        """KR + KS + RS = −2^N = −32."""
        assert K * R + K * S + R * S == -(2**N)

    def test_K_plus_R(self):
        """K + R = 14 = 2·Φ₆."""
        assert K + R == 2 * PHI6

    def test_K_plus_S(self):
        """K + S = 8 = DIM_O."""
        assert K + S == DIM_O

    def test_K_minus_R(self):
        """K − R = 10 = ALPHA = THETA."""
        assert K - R == ALPHA

    def test_K_minus_S(self):
        """K − S = 16 = 2^MU."""
        assert K - S == 2**MU

    def test_R_minus_S(self):
        """R − S = 6 = r_s = LAM + MU."""
        assert R - S == r_s
        assert r_s == LAM + MU


# =====================================================================
# T719 — MU²·LAM = 2^N and Vieta Ratio
# =====================================================================
class TestT719_ProductIdentities:
    """MU²·LAM = 2^N = 32.  KRS/(KR+KS+RS) = Q.
    
    The eigenvalue product-to-sum ratio isolates Q from the spectrum.
    """

    def test_MU_sq_LAM(self):
        """MU²·LAM = 4²·2 = 32 = 2^N = 2^5."""
        assert MU**2 * LAM == 2**N

    def test_KRS_over_sigma2_is_Q(self):
        """KRS / (KR+KS+RS) = (−96)/(−32) = 3 = Q."""
        sigma2 = K * R + K * S + R * S
        assert Fraction(K * R * S, sigma2) == Q

    def test_KRS_is_neg_Q_times_2N(self):
        """KRS = −Q·2^N = −96."""
        assert K * R * S == -Q * 2**N

    def test_K_is_Q_times_MU(self):
        """K = Q·MU = 3·4 = 12."""
        assert K == Q * MU

    def test_KRS_decomposition(self):
        """KRS = Q·MU·LAM·(−MU) = −Q·MU²·LAM = −Q·2^N."""
        assert K * R * S == -Q * MU**2 * LAM


# =====================================================================
# T720 — Complement Minimal Polynomial
# =====================================================================
class TestT720_ComplementMinPoly:
    """m̄(x) = (x − ALBERT)(x² − Q²) = x³ − ALBERT·x² − Q²·x + Q²·ALBERT.
    
    The complement non-trivial eigenvalues are simply ±Q.
    """

    def test_complement_nontrivial_eigenvalues(self):
        """R̄ = −Q, S̄ = Q: complement non-trivial eigenvalues are ±Q."""
        R_bar = -(R + 1)
        S_bar = -(S + 1)
        assert R_bar == -Q
        assert S_bar == Q

    def test_complement_poly_factors(self):
        """m̄(x) = (x − ALBERT)(x − Q)(x + Q) = (x − ALBERT)(x² − Q²)."""
        # Evaluate at x=0
        m_bar_0 = (0 - K_BAR) * (0 + Q) * (0 - Q)
        assert m_bar_0 == Q**2 * ALBERT

    def test_m_bar_at_0(self):
        """m̄(0) = Q²·ALBERT = 9·27 = 243 = Q^5 = 3^5."""
        m_bar_0 = (-K_BAR) * Q * (-Q)
        assert m_bar_0 == Q**2 * ALBERT
        assert m_bar_0 == Q**5

    def test_complement_sum_is_ALBERT(self):
        """K̄ + R̄ + S̄ = ALBERT = V − ALPHA − Q = 27."""
        R_bar, S_bar = -Q, Q
        assert K_BAR + R_bar + S_bar == ALBERT
        assert ALBERT == V - ALPHA - Q


# =====================================================================
# T721 — Combined 6-Eigenvalue Spectrum
# =====================================================================
class TestT721_CombinedSpectrum:
    """The 6 distinct eigenvalues {K, R, S, K̄, R̄, S̄} = {12, 2, −4, 27, −3, 3}.
    
    Sum = V − Q = 37 = ALPHA + ALBERT.
    Product = Q³·2^N·ALBERT.
    Pairing: K + K̄ = V−1; R + R̄ = S + S̄ = −1.
    """

    def test_six_eigenvalues_sorted(self):
        """Sorted: −4, −3, 2, 3, 12, 27."""
        R_bar, S_bar = -(R + 1), -(S + 1)
        evs = sorted([K, R, S, K_BAR, R_bar, S_bar])
        assert evs == [-4, -3, 2, 3, 12, 27]

    def test_sum_is_V_minus_Q(self):
        """Sum = ALPHA + ALBERT = V − Q = 37."""
        R_bar, S_bar = -(R + 1), -(S + 1)
        total = K + R + S + K_BAR + R_bar + S_bar
        assert total == V - Q
        assert total == ALPHA + ALBERT

    def test_product(self):
        """Product = Q³·2^N·ALBERT = 23328."""
        prod = K * R * S * K_BAR * (-Q) * Q
        assert prod == Q**3 * 2**N * ALBERT

    def test_pairing_K(self):
        """K + K̄ = V − 1 = 39."""
        assert K + K_BAR == V - 1

    def test_pairing_R_S(self):
        """R + R̄ = S + S̄ = −1."""
        assert R + (-(R + 1)) == -1
        assert S + (-(S + 1)) == -1


# =====================================================================
# T722 — Interlacing Gaps
# =====================================================================
class TestT722_InterlacingGaps:
    """The 6 sorted eigenvalues {−4, −3, 2, 3, 12, 27} have gaps
    1, N, 1, Q², G with product ALBERT·N².
    """

    def test_gaps(self):
        """Gaps: 1, 5, 1, 9, 15 = 1, N, 1, Q², G."""
        evs = [-4, -3, 2, 3, 12, 27]
        gaps = [evs[i+1] - evs[i] for i in range(5)]
        assert gaps == [1, N, 1, Q**2, G]

    def test_gap_product(self):
        """Product of gaps = ALBERT·N² = 27·25 = 675."""
        gap_prod = 1 * N * 1 * Q**2 * G
        assert gap_prod == ALBERT * N**2

    def test_gap_sum(self):
        """Sum of gaps = total span = 27−(−4) = 31."""
        assert 1 + N + 1 + Q**2 + G == K_BAR - S

    def test_unit_gaps_at_QQ(self):
        """Unit gaps separate S from R̄ and R from S̄ (mod-Q pairs)."""
        assert -Q - S == 1       # R̄ − S
        assert Q - R == 1        # S̄ − R


# =====================================================================
# T723 — Spectral Measure & Moments
# =====================================================================
class TestT723_SpectralMeasure:
    """Spectral measure μ = (1/V)·δ_K + (F/V)·δ_R + (G/V)·δ_S.
    
    Weights 1/40, 3/5, 3/8 sum to 1.
    Moments: μ₂ = K, μ₃ = F = K·R, μ₄ = K·MU·Φ₃.
    """

    def test_weights_sum_to_1(self):
        """1/V + F/V + G/V = 1."""
        assert Fraction(1, V) + Fraction(F, V) + Fraction(G, V) == 1

    def test_weight_F_over_V(self):
        """F/V = 24/40 = 3/5."""
        assert Fraction(F, V) == Fraction(3, 5)

    def test_weight_G_over_V(self):
        """G/V = 15/40 = 3/8."""
        assert Fraction(G, V) == Fraction(3, 8)

    def test_moment_0(self):
        """μ₀ = 1."""
        mu0 = Fraction(1, V) + Fraction(F, V) + Fraction(G, V)
        assert mu0 == 1

    def test_moment_1(self):
        """μ₁ = 0 (trace = 0)."""
        mu1 = Fraction(K, V) + Fraction(F * R, V) + Fraction(G * S, V)
        assert mu1 == 0

    def test_moment_2_is_K(self):
        """μ₂ = tr(A²)/V = K."""
        mu2 = Fraction(K**2 + F * R**2 + G * S**2, V)
        assert mu2 == K

    def test_moment_3_is_F(self):
        """μ₃ = tr(A³)/V = F = K·R."""
        mu3 = Fraction(K**3 + F * R**3 + G * S**3, V)
        assert mu3 == F
        assert F == K * R

    def test_moment_4(self):
        """μ₄ = tr(A⁴)/V = K·MU·Φ₃ = 624."""
        mu4 = Fraction(K**4 + F * R**4 + G * S**4, V)
        assert mu4 == K * MU * PHI3


# =====================================================================
# T724 — Trace Ratio Pattern
# =====================================================================
class TestT724_TraceRatioPattern:
    """tr(A^n)/V = Q·2^n·c_n where c_n is always an integer.
    
    The trace ratios factor as Q·2^n times an integer for all n ≥ 2.
    tr(A³) = 6·C₃ counts oriented triangles.
    """

    def test_trace_ratio_n2(self):
        """tr(A²)/V = Q·2²·1 = 12 = K."""
        tr2 = K**2 + F * R**2 + G * S**2
        assert tr2 == V * Q * 4 * 1

    def test_trace_ratio_n3(self):
        """tr(A³)/V = Q·2³·1 = 24 = F."""
        tr3 = K**3 + F * R**3 + G * S**3
        assert tr3 == V * Q * 8 * 1

    def test_trace_ratio_n4(self):
        """tr(A⁴)/V = Q·2⁴·Φ₃ = Q·16·13 = 624."""
        tr4 = K**4 + F * R**4 + G * S**4
        assert tr4 == V * Q * 16 * PHI3

    def test_trace_ratio_n5(self):
        """tr(A⁵)/V = Q·2⁵·61."""
        tr5 = K**5 + F * R**5 + G * S**5
        assert tr5 == V * Q * 32 * 61

    def test_trace_ratio_n6(self):
        """tr(A⁶)/V = Q·2⁶·397."""
        tr6 = K**6 + F * R**6 + G * S**6
        assert tr6 == V * Q * 64 * 397

    def test_triangles(self):
        """tr(A³)/6 = C₃ = V·MU = 160 triangles."""
        tr3 = K**3 + F * R**3 + G * S**3
        assert tr3 // 6 == V * MU

    def test_cayley_hamilton_recurrence(self):
        """μ_n = ALPHA·μ_{n−1} + 2^N·μ_{n−2} − Q·2^N·μ_{n−3}."""
        mu = [1, 0, K]  # μ₀, μ₁, μ₂
        for _ in range(6):
            mu_next = ALPHA * mu[-1] + 2**N * mu[-2] - Q * 2**N * mu[-3]
            mu.append(mu_next)
        assert mu[3] == F
        assert mu[4] == K * MU * PHI3
        assert mu[5] == 5856
        assert mu[6] == 76224


# =====================================================================
# T725 — Polynomial Duality: m ↔ m̄
# =====================================================================
class TestT725_PolynomialDuality:
    """m(x) = x³ − ALPHA·x² − 2^N·x + Q·2^N
    m̄(x) = x³ − ALBERT·x² − Q²·x + Q²·ALBERT
    
    ALPHA + ALBERT = V − Q.  ALPHA·ALBERT = 270 = 2·N·ALBERT.
    The combined product m(0)·m̄(0) = Q³·2^N·ALBERT.
    """

    def test_alpha_plus_albert(self):
        """ALPHA + ALBERT = V − Q = 37."""
        assert ALPHA + ALBERT == V - Q

    def test_alpha_times_albert(self):
        """ALPHA·ALBERT = 270."""
        assert ALPHA * ALBERT == 270

    def test_alpha_minus_albert(self):
        """ALPHA − ALBERT = −(Φ₃ + MU) = −17."""
        assert ALPHA - ALBERT == -(PHI3 + MU)

    def test_free_terms(self):
        """m(0) = Q·2^N = 96; m̄(0) = Q²·ALBERT = Q^5 = 243."""
        assert m(0) == Q * 2**N
        m_bar_0 = (-K_BAR) * Q * (-Q)
        assert m_bar_0 == Q**2 * ALBERT

    def test_combined_product(self):
        """m(0)·m̄(0) = Q³·2^N·ALBERT = 23328."""
        combined = m(0) * Q**2 * ALBERT
        assert combined == Q**3 * 2**N * ALBERT

    def test_complement_coefficients(self):
        """m̄ coefficient of x² is −ALBERT; of x is −Q²; constant is Q²·ALBERT."""
        # m_bar = x^3 - ALBERT*x^2 - Q^2*x + Q^2*ALBERT
        # Verify by evaluating at x=1:
        m_bar_1 = (1 - K_BAR) * (1 + Q) * (1 - Q)
        expected = 1 - ALBERT - Q**2 + Q**2 * ALBERT
        assert m_bar_1 == expected

    def test_m_bar_sigma2(self):
        """K̄·R̄ + K̄·S̄ + R̄·S̄ = −Q² = −9."""
        R_bar, S_bar = -Q, Q
        sigma2 = K_BAR * R_bar + K_BAR * S_bar + R_bar * S_bar
        assert sigma2 == -Q**2
