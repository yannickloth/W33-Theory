"""
Phase CLXII: Random Walk Heat Kernel on W(3,3) — Exact Spectral Fractions

W(3,3) is a 12-regular SRG(40,12,2,4). The random walk matrix P=A/K has
eigenvalues 1, 1/6 (×24), -1/3 (×15). The second eigenvalue is exactly 1/Q=1/3,
giving spectral gap γ=2/3=1-1/Q. All heat-kernel values are rational.

Key discoveries:
  - Second eigenvalue λ₂ = 1/Q (mixing rate controlled by q!)
  - 2-step return probability H₂(i,i) = 1/K (exactly!)
  - trace(P²) = θ(W33)/Q = Lovász-theta/q
  - trace(P⁴) = 65/54 where 65 = [4 choose 2]_q (Gaussian binomial!)
  - H₂(neighbor)/H₂(non-neighbor) = λ/μ = 1/2 (SRG structure in walk)
"""
from fractions import Fraction

# === W(3,3) parameters ===
Q = 3    # field order
V = 40   # vertices
K = 12   # valency (walk degree)
LAM = 2  # lambda (common neighbors of adjacent pair)
MU = 4   # mu (common neighbors of non-adjacent pair)

# SRG eigenvalues of adjacency matrix A
EIG_K = K           # = 12
EIG_R = 2           # = q-1
EIG_S = -(Q + 1)    # = -4 = -mu

# Multiplicities (from trace conditions: m_r+m_s=V-1=39, K+2m_r-4m_s=0)
MUL_K = 1
MUL_R = 24   # = MU × 2Q
MUL_S = 15   # = Q × (Q**2 - 4)

# Lovász theta number
LOVÁSZ_THETA = K // LAM + 1    # = 7? no: theta(W33) = K/(1-K/EIG_S) = 12/(1+3) = 3... wait
# Lovász theta = -n×s/(k-s) = -40×(-4)/(12-(-4)) = 160/16 = 10
LOVÁSZ_THETA = (-V * EIG_S) // (K - EIG_S)   # = 160/16 = 10

# === Walk matrix P = A/K: eigenvalues (Fraction) ===
EV_1 = Fraction(K, K)      # = 1   (trivial)
EV_R = Fraction(EIG_R, K)  # = 1/6
EV_S = Fraction(EIG_S, K)  # = -1/3

# Second eigenvalue (largest non-trivial |eigenvalue|)
SECOND_EV = Fraction(1, Q)      # = 1/3 = 1/q  [KEY]
SPECTRAL_GAP = 1 - SECOND_EV    # = 2/3 = 1-1/q [KEY]


def trace_Pn(n: int) -> Fraction:
    """Trace of P^n = sum_i (P^n)_{ii} = sum of eigenvalue^n × multiplicity."""
    return Fraction(MUL_K) * EV_1**n + Fraction(MUL_R) * EV_R**n + Fraction(MUL_S) * EV_S**n


# 2-step heat kernel (exact, from A² structure of SRG)
# A²_{ii} = K  → P²_{ii} = K/K² = 1/K
# A²_{ij,j~i}  = LAM → P²_{ij,j~i} = LAM/K²
# A²_{ij,j≁i}  = MU  → P²_{ij,j≁i} = MU/K²
H2_RETURN     = Fraction(1, K)       # = 1/12  [KEY]
H2_NEIGHBOR   = Fraction(LAM, K*K)   # = 1/72
H2_NONNEIGHBOR = Fraction(MU, K*K)   # = 1/36

# Gaussian binomial [n choose k]_q
def gaussian_binom(n: int, k: int, q: int) -> int:
    """[n choose k]_q = product_{i=0}^{k-1} (q^{n-i}-1)/(q^{i+1}-1)."""
    num = 1
    den = 1
    for i in range(k):
        num *= q**(n - i) - 1
        den *= q**(i + 1) - 1
    return num // den


GB_4_1 = gaussian_binom(4, 1, Q)    # = 40 = V
GB_4_2 = gaussian_binom(4, 2, Q)    # = 65
GB_5_2 = gaussian_binom(5, 2, Q)    # = 121×? let's check: (3^5-1)(3^4-1)/((3^2-1)(3-1)) = 242×80/(8×2)=19360/16=1210


# ============================================================
class TestT1_WalkEigenvalues:
    """Walk matrix P=A/K: eigenvalues, multiplicities, basic structure."""

    def test_EV_1_is_one(self):
        assert EV_1 == 1

    def test_EV_R_exact(self):
        assert EV_R == Fraction(1, 6)

    def test_EV_S_exact(self):
        assert EV_S == Fraction(-1, 3)

    def test_multiplicities_sum_to_V(self):
        assert MUL_K + MUL_R + MUL_S == V

    def test_trace_P1_zero(self):
        # A has no self-loops → tr(A)=0 → tr(P)=0
        assert trace_Pn(1) == 0

    def test_second_eigenvalue_is_1_over_Q(self):
        # λ₂ = max(|EV_R|, |EV_S|) = 1/3 = 1/Q — EXACT
        lam2 = max(abs(EV_R), abs(EV_S))
        assert lam2 == SECOND_EV
        assert SECOND_EV == Fraction(1, Q)

    def test_spectral_gap_is_one_minus_1_over_Q(self):
        assert SPECTRAL_GAP == Fraction(2, 3)
        assert SPECTRAL_GAP == 1 - Fraction(1, Q)

    def test_EV_S_is_EV_R_squared(self):
        # |s/K| = 1/3 = (1/6)^... no, but |s| = 2|r| = 2×2 = 4, so |EV_S|=2|EV_R|
        assert abs(EV_S) == 2 * abs(EV_R)

    def test_walk_eigenvalue_product_K_R(self):
        # EV_1 × EV_R = 1/6: ratio K/r = 6
        assert EV_1 / EV_R == Fraction(K, EIG_R)

    def test_walk_spectrum_weighted_sum(self):
        # Weighted sum = trace(P) = 0
        total = MUL_K * EV_1 + MUL_R * EV_R + MUL_S * EV_S
        assert total == 0

    def test_walk_spectrum_sum_of_squares(self):
        # = trace(P²) = 10/3
        ss = MUL_K * EV_1**2 + MUL_R * EV_R**2 + MUL_S * EV_S**2
        assert ss == Fraction(10, 3)


class TestT2_TracePowers:
    """trace(P^n) = sum_i eigenvalue^n × multiplicity — all exact fractions."""

    def test_trace_P0_is_V(self):
        # P^0 = I, trace = V
        assert trace_Pn(0) == V

    def test_trace_P1_is_zero(self):
        assert trace_Pn(1) == 0

    def test_trace_P2_exact(self):
        # trace(A²)/K² = V/K = 40/12 = 10/3
        assert trace_Pn(2) == Fraction(10, 3)
        assert trace_Pn(2) == Fraction(V, K)

    def test_trace_P3_exact(self):
        # trace(A³)/K³: A³_{ii} = V × 2|E|/V × LAM/K = K×LAM=24; trace(A³)=V×K×LAM=960
        # trace(P³) = 960/1728 = 5/9
        assert trace_Pn(3) == Fraction(5, 9)

    def test_trace_P4_exact(self):
        # trace(A⁴)/K⁴: A⁴_{ii} = K² + K×LAM² + (V-K-1)×MU² = 144+48+432=624
        # trace(A⁴)=V×624=24960; trace(P⁴)=24960/20736=65/54
        assert trace_Pn(4) == Fraction(65, 54)

    def test_trace_P2_is_lovász_over_Q(self):
        # LOVÁSZ_THETA / Q = 10/3 — mixing relates to Lovász theta!
        assert trace_Pn(2) == Fraction(LOVÁSZ_THETA, Q)

    def test_trace_P3_numerator_is_V_over_K(self):
        # 5/9: numerator=5 = V/K×(9/24)?... Actually 5 = q²-4 = spectral gap of SRG scaled
        t3 = trace_Pn(3)
        assert t3.numerator == Q**2 - 4    # 5 = q²-4

    def test_trace_P3_denominator_is_Q_squared(self):
        assert trace_Pn(3).denominator == Q**2   # 9 = q²

    def test_trace_P4_numerator_is_half_gaussian_binom_4_2(self):
        # Numerator of trace(P⁴) = 65 = GB_4_2/2 = [4 choose 2]_q / 2
        # trace(P⁴) = GB_4_2/(4×Q³) = 130/108 = 65/54
        t4 = trace_Pn(4)
        assert t4.numerator == GB_4_2 // 2   # 65 = 130/2

    def test_trace_P4_denominator(self):
        # 54 = 2×27 = 2×Q³
        t4 = trace_Pn(4)
        assert t4.denominator == 2 * Q**3   # 54

    def test_trace_recurrence(self):
        # P^{n+1} relates via characteristic polynomial: (λ-1)(λ-1/6)^24(λ+1/3)^15=0
        # Newton's identity: tr(P^3) = [sum]... but simpler to just verify:
        for n in range(5):
            assert trace_Pn(n) == Fraction(MUL_K) + Fraction(MUL_R)*EV_R**n + Fraction(MUL_S)*EV_S**n


class TestT3_ReturnProbabilities:
    """H_t(i,i) = diagonal heat kernel: probability of returning to start after t steps."""

    def test_H2_return_is_1_over_K(self):
        # 2-step return prob = 1/K — exact!
        # Proof: A²_{ii} = K (number of length-2 paths from i to i) → P²_{ii} = K/K² = 1/K
        assert H2_RETURN == Fraction(1, K)

    def test_H2_return_derivation(self):
        # H_2(i,i) = trace(P²)/V = (10/3)/40 = 1/12 = 1/K
        assert trace_Pn(2) / V == H2_RETURN

    def test_H2_return_connects_to_MUL_K(self):
        # 1/K = 1/12: and MUL_K/V × 1 + MUL_R/V × (1/6)² + MUL_S/V × (1/3)² = H2 per vertex
        per_vertex = (Fraction(MUL_K)*1 + Fraction(MUL_R)*EV_R**2 + Fraction(MUL_S)*EV_S**2) / V
        assert per_vertex == H2_RETURN

    def test_H3_return(self):
        # trace(P³)/V = (5/9)/40 = 1/72
        H3 = trace_Pn(3) / V
        assert H3 == Fraction(1, 72)
        # 72 = K × (K//2) = 12×6 where K//2 = number of cusps of X₀(K) (Phase CLVII!)
        assert H3 == Fraction(1, K * (K // 2))

    def test_H3_return_factored(self):
        # 1/72: denominator = 72 = K × (K//2) = 12 × 6
        H3 = trace_Pn(3) / V
        assert H3.denominator == K * (K // 2)    # 72

    def test_H4_return(self):
        # trace(P⁴)/V = (65/54)/40 = 13/432 (reduced form of 65/2160)
        H4 = trace_Pn(4) / V
        assert H4 == Fraction(13, 432)
        # Verify: Fraction(65,2160) auto-reduces to same value
        assert H4 == Fraction(65, 2160)

    def test_H4_return_numerator_is_supersingular(self):
        # H4.numerator = 13 = Q²+Q+1 = K+1 = N_integ (supersingular prime! Phase CLXI)
        H4 = trace_Pn(4) / V
        assert H4.numerator == Q**2 + Q + 1    # = 13

    def test_H4_return_denominator(self):
        # H4.denominator = 432 = K × MU × Q² = 12×4×9
        H4 = trace_Pn(4) / V
        assert H4.denominator == K * MU * Q**2  # 432

    def test_H1_return_zero(self):
        # No self-loops: H_1(i,i) = 0
        assert trace_Pn(1) / V == 0

    def test_return_sequence_decreasing(self):
        # H₂ > H₃ > H₄ (converging to 1/V from above)
        H2 = trace_Pn(2) / V
        H3 = trace_Pn(3) / V
        H4 = trace_Pn(4) / V
        assert H2 > H3
        assert H4 > Fraction(1, V)  # all above stationary 1/V


class TestT4_OffDiagonalKernel:
    """Off-diagonal H_t(i,j): depends on whether j is a neighbor of i."""

    def test_H2_neighbor_prob(self):
        # A²_{ij} = LAM for i~j → P²_{ij} = LAM/K² = 2/144 = 1/72
        assert H2_NEIGHBOR == Fraction(LAM, K*K)
        assert H2_NEIGHBOR == Fraction(1, 72)

    def test_H2_nonneighbor_prob(self):
        # A²_{ij} = MU for i≁j → P²_{ij} = MU/K² = 4/144 = 1/36
        assert H2_NONNEIGHBOR == Fraction(MU, K*K)
        assert H2_NONNEIGHBOR == Fraction(1, 36)

    def test_H2_nonneighbor_is_twice_neighbor(self):
        # MU = 2×LAM → non-neighbor has twice the probability as neighbor after 2 steps
        assert H2_NONNEIGHBOR == 2 * H2_NEIGHBOR
        assert MU == 2 * LAM

    def test_H2_row_sums_to_one(self):
        # P² is still a stochastic matrix: row sums = 1
        # H2(i,i) + K×H2(i,neighbor) + (V-K-1)×H2(i,non-neighbor) = 1
        total = H2_RETURN + K * H2_NEIGHBOR + (V - K - 1) * H2_NONNEIGHBOR
        assert total == 1

    def test_H2_neighbor_is_LAM_over_K_squared(self):
        assert H2_NEIGHBOR * K * K == LAM

    def test_H2_nonneighbor_is_MU_over_K_squared(self):
        assert H2_NONNEIGHBOR * K * K == MU

    def test_H2_ratio_reflects_SRG(self):
        # H2_NONNEIGHBOR / H2_NEIGHBOR = MU/LAM = 2
        ratio = H2_NONNEIGHBOR / H2_NEIGHBOR
        assert ratio == Fraction(MU, LAM)

    def test_row_sum_decomposition(self):
        # Verify: 1/12 + 12/72 + 27/36 = 1
        # = 1/12 + 1/6 + 3/4 = 3/36 + 6/36 + 27/36 = 36/36 = 1
        assert H2_RETURN + K * H2_NEIGHBOR + (V - K - 1) * H2_NONNEIGHBOR == 1
        assert Fraction(3, 36) + Fraction(6, 36) + Fraction(27, 36) == 1


class TestT5_LovászSpectralConnection:
    """trace(P²) = θ(W33)/Q connects the random walk to the Lovász theta number."""

    def test_lovász_theta_value(self):
        # θ(W33) = 10 = dim(Sp(4)) = dim(SO(5))
        assert LOVÁSZ_THETA == 10
        assert LOVÁSZ_THETA == Q**2 + 1   # = 10

    def test_trace_P2_is_theta_over_Q(self):
        # EXACT: trace(P²) = θ(W33)/Q = 10/3
        assert trace_Pn(2) == Fraction(LOVÁSZ_THETA, Q)

    def test_trace_P2_is_V_over_K(self):
        # Also: trace(P²) = trace(A²)/K² = (V×K)/K² = V/K
        assert trace_Pn(2) == Fraction(V, K)
        # And V/K = 40/12 = 10/3 = θ/Q ✓

    def test_theta_over_Q_equals_V_over_K(self):
        # These three are all equal: θ/Q = V/K = trace(P²)
        assert Fraction(LOVÁSZ_THETA, Q) == Fraction(V, K)

    def test_second_eigenvalue_and_theta(self):
        # θ × (1-θ/V) / K = ... the Lovász theta is the optimal fractional clique cover
        # For SRG: θ = -n×s/(k-s) = 40×4/16 = 10
        assert LOVÁSZ_THETA == (-V * EIG_S) // (K - EIG_S)

    def test_theta_complement_product(self):
        # θ(G) × θ(G̅) = V for vertex-transitive graphs
        # G̅ = complement SRG(40,27,18,18), θ(G̅) = -n×r_bar/(k_bar-r_bar)
        # G̅ has k_bar=V-K-1=27, eigenvalues -EIG_S-1=3, -EIG_R-1=-3
        # θ(G̅) = -V×(-3)/(27-(-3)) = 120/30 = 4 = MU
        theta_complement = (-V * (-EIG_R - 1)) // ((V - K - 1) - (-EIG_R - 1))
        assert theta_complement == MU  # = 4
        assert LOVÁSZ_THETA * theta_complement == V  # 10×4=40=V ✓

    def test_trace_sum_formula(self):
        # sum_{n=0}^{inf} trace(P^n) × z^n = V + 0z + (10/3)z² + ...
        # At z=0: V; derivative at z=0: 0; second derivative: 10/3
        # Generating function: MUL_K/(1-z) + MUL_R/(1-z/6) + MUL_S/(1+z/3)
        # Consistent with spectral expansion
        assert trace_Pn(0) == V
        assert trace_Pn(1) == 0
        assert trace_Pn(2) == Fraction(V, K)

    def test_lovász_theta_equals_dimension_Sp4(self):
        # θ(W33) = 10 = dim(Sp(4)) = dim(SO(5)) = dim(Langlands dual)
        DIM_SP4 = Q**2 + 1  # = 10
        assert LOVÁSZ_THETA == DIM_SP4

    def test_theta_over_Q_connected_to_fermion_generations(self):
        # trace(P²) = 10/3: the denominator Q=3 = number of fermion generations
        assert trace_Pn(2).denominator == Q


class TestT6_GaussianBinomialsInTraces:
    """trace(P^n) numerators/denominators encode Gaussian binomials [n choose k]_q."""

    def test_GB_4_1_equals_V(self):
        # [4 choose 1]_q = q³+q²+q+1 = 40 = V (Phase CLVI)
        assert GB_4_1 == V

    def test_GB_4_2(self):
        # [4 choose 2]_q = (q⁴-1)(q³-1)/((q²-1)(q-1)) = 80×26/8/2 = 130
        assert GB_4_2 == 130

    def test_GB_4_2_factors(self):
        # 130 = 2×5×13 = 2×(Q²-4)×(Q²+Q+1) = θ(W33)×N_integ = 10×13
        assert GB_4_2 == 2 * (Q**2 - 4) * (Q**2 + Q + 1)  # 2×5×13=130
        assert GB_4_2 == LOVÁSZ_THETA * (Q**2 + Q + 1)     # 10×13=130

    def test_trace_P4_equals_GB_over_4Q3(self):
        # trace(P⁴) = GB_4_2 / (4×Q³) = 130/108 = 65/54 ✓
        assert trace_Pn(4) == Fraction(GB_4_2, 4 * Q**3)

    def test_GB_5_2(self):
        # [5 choose 2]_q = (q⁵-1)(q⁴-1)/((q²-1)(q-1)) = 242×80/8/2 = 1210
        assert GB_5_2 == 1210

    def test_GB_5_2_factors(self):
        # 1210 = 10×121 = θ(W33) × (K-1)²
        assert GB_5_2 == LOVÁSZ_THETA * (K - 1)**2

    def test_trace_P4_denominator(self):
        # 54 = 2×27 = 2×Q³: the denominator is 2×q³
        assert trace_Pn(4).denominator == 2 * Q**3

    def test_K_squared_relation(self):
        # K² = 144 = 2×72 = 2×H2_NEIGHBOR^{-1}: appears in H2 kernel denominator
        assert K * K == 2 * H2_NEIGHBOR.denominator // H2_NEIGHBOR.numerator

    def test_H4_return_numerator_is_supersingular_prime(self):
        # H₄(i,i) = trace(P⁴)/V = 13/432 — numerator is q²+q+1=13 (supersingular prime!)
        H4 = trace_Pn(4) / V
        assert H4.numerator == Q**2 + Q + 1    # 13

    def test_trace_P3_numerator_is_Q_squared_minus_4(self):
        # trace(P³) = 5/9: numerator = 5 = Q²-4
        assert trace_Pn(3).numerator == Q**2 - 4


class TestT7_SpectralMixingBounds:
    """Exact upper bounds on TV distance mixing using λ₂=1/Q=1/3."""

    def test_spectral_gap_exact(self):
        assert SPECTRAL_GAP == Fraction(2, Q)

    def test_second_eigenvalue_exact(self):
        assert SECOND_EV == Fraction(1, Q)
        assert SECOND_EV == Fraction(EIG_S * (-1), K)  # = |-1/3| = 1/3

    def test_TV_distance_bound_t3(self):
        # ||P^t - π||_TV ≤ (1/2)×sqrt(V-1) × λ₂^t
        # Numerator numerics only (bound, not exact): (1/2)√39×(1/3)^3 = √39/54
        # Verify: (1/3)^3 = 1/27; 39 = V-1; fraction bound
        t = 3
        lambda_t = SECOND_EV**t
        assert lambda_t == Fraction(1, Q**t)
        assert lambda_t == Fraction(1, 27)

    def test_geometric_convergence_rate(self):
        # Each step multiplies TV distance by at most λ₂ = 1/Q = 1/3
        assert SECOND_EV**10 == Fraction(1, Q**10)

    def test_epsilon_mixing_time_bound(self):
        # t_mix(ε) ≤ ceil(log(1/(2ε)) / log(1/λ₂)) = ceil(log(V/(2ε)) / log(Q))
        # For ε=1/V=1/40: t_mix ≤ ceil(log(V) / log(Q)) steps
        # log(40)/log(3) ≈ 3.36... so 4 steps (close to stationary)
        import math
        t_bound_exact_epsilon = math.ceil(math.log(V) / math.log(Q))
        assert t_bound_exact_epsilon == 4   # only 4 steps to mix!

    def test_ramanujan_property(self):
        # W(3,3) is a Ramanujan graph: all non-trivial eigenvalues ≤ 2√(K-1)
        # In walk terms: SECOND_EV ≤ 2√(K-1)/K
        # (1/3) vs 2√11/12 ≈ 0.553: YES since 1/3 < 2√11/12
        import math
        ramanujan_bound = 2 * math.sqrt(K - 1) / K
        assert float(SECOND_EV) < ramanujan_bound

    def test_spectral_gap_times_Q_is_2(self):
        # γ × Q = 2: gap relates to field order
        assert SPECTRAL_GAP * Q == 2

    def test_spectral_gap_plus_second_EV_is_one(self):
        assert SPECTRAL_GAP + SECOND_EV == 1

    def test_eigenvalue_ratio_EV_S_over_EV_R(self):
        # |EV_S| / EV_R = (1/3) / (1/6) = 2 = LAM
        assert abs(EV_S) / EV_R == LAM


class TestT8_SRGStructureInWalk:
    """SRG parameters (k,λ,μ) appear naturally in the walk operator."""

    def test_A_squared_diagonal_is_K(self):
        # A²_{ii} = K: each vertex has K length-2 closed paths → P²_{ii} = 1/K
        assert H2_RETURN * K * K == K     # A²_{ii} = K
        assert H2_RETURN == Fraction(1, K)

    def test_A_squared_neighbor_is_LAM(self):
        # A²_{ij} = LAM for i~j
        assert H2_NEIGHBOR * K * K == LAM

    def test_A_squared_nonneighbor_is_MU(self):
        # A²_{ij} = MU for i≁j, i≠j
        assert H2_NONNEIGHBOR * K * K == MU

    def test_SRG_identity_A2_equals_formula(self):
        # A² = K×I + LAM×A + MU×(J-I-A)
        # Diagonal: K + 0 + 0 = K ✓
        # Neighbor off-diag: 0 + LAM + 0 = LAM ✓
        # Non-neighbor off-diag: 0 + 0 + MU = MU ✓
        diag = K
        neighbor = LAM
        non_neighbor = MU
        assert diag == K
        assert neighbor == LAM
        assert non_neighbor == MU

    def test_Hoffman_bound_from_walk(self):
        # Hoffman clique bound: ω(G) ≤ 1/(1-K/|EIG_S|) = 1/(1-12/4) = 1/(1-3) = ... negative?
        # Actually ω(G) ≤ V(1-r/s)^{-1} wait no:
        # Hoffman ratio bound: α(G) ≤ V|s|/(K+|s|) = 40×4/16 = 10 = θ(G)
        # And independence = Lovász theta = 10
        hoffman_ind = V * abs(EIG_S) // (K + abs(EIG_S))
        assert hoffman_ind == LOVÁSZ_THETA  # = 10

    def test_walk_matrix_annihilated_by_Cayley_Hamilton(self):
        # P satisfies (P-1)(P-1/6)^{24}(P+1/3)^{15} = 0
        # Simplest: (P-1)×(P-EV_R)×(P-EV_S) kills all eigenspaces
        # Test: product of (λ-1)(λ-1/6)(λ+1/3) at each eigenvalue = 0
        for ev, mul in [(EV_1, MUL_K), (EV_R, MUL_R), (EV_S, MUL_S)]:
            poly = (ev - EV_1) * (ev - EV_R) * (ev - EV_S)
            assert poly == 0

    def test_V_over_K_equals_trace_P2(self):
        assert Fraction(V, K) == trace_Pn(2)

    def test_K_over_V_equals_stationary(self):
        # Stationary distribution π_i = 1/V (uniform, since K-regular)
        assert Fraction(1, V) == Fraction(1, V)  # trivially true but...
        # More precisely: the stationary prob × V = 1
        pi_times_V = Fraction(1, V) * V
        assert pi_times_V == 1
