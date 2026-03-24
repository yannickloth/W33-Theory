"""
Phase CLXIII: Metric Geometry and Resistance Distance of W(3,3)

W(3,3) = SRG(40,12,2,4) has diameter 2 (any non-adjacent pair has μ=4>0 common
neighbors). All metric and resistance-distance quantities are exact rationals.

Key discoveries:
  - Average distance = 2(K-1)/(K+1) = 22/13 (numerator=2×11th superprime, denom=13th!)
  - Mean-square distance = V/(K+1) = 40/13 (exactly V over next superprime!)
  - Distance std. dev. = (K/2)/(K+1) = 6/13 (half-valency over next superprime!)
  - Wiener index W = θ(W33)×K×(K-1) = 10×12×11 = 1320
  - Effective resistance adj R_adj = (K+1)/(2V) = 13/80 (num = 13th superprime!)
  - Effective resistance non-adj R_non = (K+2)/(2V) = 14/80 = 7/40 (num = η(0)!)
  - Kirchhoff index Kf = 267/2 = 133.5
  - Pseudoinverse diagonal L+(i,i) = Kf/V² = 267/3200
"""
from fractions import Fraction

# === W(3,3) parameters ===
Q = 3    # field order / fermion generations
V = 40   # vertices
K = 12   # valency
LAM = 2  # lambda
MU = 4   # mu

# SRG eigenvalues
EIG_K = K   # = 12
EIG_R = 2   # = Q-1
EIG_S = -4  # = -(Q+1) = -MU

# Multiplicities
MUL_K = 1
MUL_R = 24   # = MU × 2Q
MUL_S = 15   # = Q × (Q²-4)

# Lovász theta number
LOVÁSZ_THETA = 10   # = Q²+1 = dim(Sp(4)) = dim(SO(5))

# === Metric quantities ===
DIAMETER = 2     # max graph distance (since μ>0, every non-adj pair has a common neighbor)

# Distance distribution from any vertex i (by vertex-transitivity):
N_DIST_0 = 1              # only i itself at distance 0
N_DIST_1 = K              # K neighbors at distance 1
N_DIST_2 = V - K - 1      # remaining vertices at distance 2 = 27

# Average (mean) distance over all other vertices
# d_avg = (K×1 + (V-K-1)×2) / (V-1)
D_AVG = Fraction(K * 1 + N_DIST_2 * 2, V - 1)   # = 66/39 = 22/13

# Mean-square distance
D_SQ_AVG = Fraction(K * 1**2 + N_DIST_2 * 2**2, V - 1)  # = 120/39 = 40/13

# Distance variance = E[d²] - E[d]²
D_VAR = D_SQ_AVG - D_AVG**2    # = 40/13 - (22/13)² = 36/169

# Wiener index W = sum_{i<j} d(i,j)
N_EDGES = V * K // 2     # = 240 (number of adjacent pairs)
N_NON_ADJ = V * (V - 1) // 2 - N_EDGES   # = 540 (non-adjacent pairs i<j)
WIENER = N_EDGES * 1 + N_NON_ADJ * 2      # = 1320

# Laplacian eigenvalues (μ_k = K - eig_k):
MU_R = K - EIG_R    # = 10 = K - r
MU_S = K - EIG_S    # = 16 = K + |s|

# Kirchhoff index Kf = V × (MUL_R/μ_R + MUL_S/μ_S)
KF = V * (Fraction(MUL_R, MU_R) + Fraction(MUL_S, MU_S))   # = 267/2

# Pseudoinverse diagonal L+(i,i) = Kf / V²
LP_DIAG = KF / V**2   # = 267/3200

# === Spectral idempotent entries (Bose-Mesner algebra) ===
# E_R and E_S are projection matrices.
# Diagonal: E_k(i,i) = MUL_k/V
ER_DIAG = Fraction(MUL_R, V)   # = 3/5
ES_DIAG = Fraction(MUL_S, V)   # = 3/8

# Adjacent pair i~j: solve system from A_{ij}=1 and (A²)_{ij}=LAM
# EIG_R×ER_adj + EIG_S×ES_adj = 1 - K/V = 7/10
# EIG_R²×ER_adj + EIG_S²×ES_adj = LAM - K²/V = -8/5
ER_ADJ = Fraction(1, 10)    # solved analytically
ES_ADJ = Fraction(-1, 8)    # solved analytically

# Non-adjacent pair i≁j: solve from A_{ij}=0 and (A²)_{ij}=MU
# EIG_R×ER_non + EIG_S×ES_non = -K/V = -3/10
# EIG_R²×ER_non + EIG_S²×ES_non = MU - K²/V = 2/5
ER_NON = Fraction(-1, 15)   # solved analytically
ES_NON = Fraction(1, 24)    # solved analytically

# Pseudoinverse off-diagonal entries: L+(i,j) = (1/μ_R)×ER_adj + (1/μ_S)×ES_adj
LP_ADJ = Fraction(1, MU_R) * ER_ADJ + Fraction(1, MU_S) * ES_ADJ   # = 7/3200
LP_NON = Fraction(1, MU_R) * ER_NON + Fraction(1, MU_S) * ES_NON   # = -13/3200

# === Effective resistance ===
# R(i,j) = L+(i,i) + L+(j,j) - 2×L+(i,j) = 2(L+(i,i) - L+(i,j))
R_ADJ = 2 * (LP_DIAG - LP_ADJ)   # = (K+1)/(2V) = 13/80
R_NON = 2 * (LP_DIAG - LP_NON)   # = (K+2)/(2V) = 14/80 = 7/40


# ============================================================
class TestT1_MetricBasics:
    """Diameter, eccentricity, and distance distribution from vertex-transitivity."""

    def test_diameter_is_2(self):
        # Every non-adjacent pair has MU=4>0 common neighbors → d≤2
        assert DIAMETER == 2

    def test_diameter_from_mu(self):
        assert MU > 0   # μ>0 forces diameter ≤ 2

    def test_distance_distribution(self):
        assert N_DIST_0 == 1
        assert N_DIST_1 == K
        assert N_DIST_2 == V - K - 1

    def test_distance_distribution_sums_to_V(self):
        assert N_DIST_0 + N_DIST_1 + N_DIST_2 == V

    def test_N_DIST_2_value(self):
        assert N_DIST_2 == 27   # = Q³

    def test_N_DIST_2_equals_Q_cubed(self):
        assert N_DIST_2 == Q**3   # 27 = q³ = dim(Albert algebra J₃(O))

    def test_N_DIST_1_equals_K(self):
        assert N_DIST_1 == K

    def test_ratio_dist1_to_dist2(self):
        # K/(V-K-1) = 12/27 = 4/9 = MU/Q² (exact!)
        assert Fraction(N_DIST_1, N_DIST_2) == Fraction(MU, Q**2)


class TestT2_AverageDistance:
    """Average and mean-square distance — exact rational formulas."""

    def test_avg_distance_exact(self):
        assert D_AVG == Fraction(22, 13)

    def test_avg_distance_formula(self):
        # d_avg = 2(K-1)/(K+1): numerator = 2×(K-1) = 22, denominator = K+1 = 13
        assert D_AVG == Fraction(2 * (K - 1), K + 1)

    def test_avg_distance_numerator_is_twice_supersingular_11(self):
        # 22 = 2×11 = 2×(K-1); and K-1=11 is the 5th supersingular prime
        assert D_AVG.numerator == 2 * (K - 1)   # 22

    def test_avg_distance_denominator_is_supersingular_13(self):
        # 13 = K+1: the 6th supersingular prime (also N_integ from Phase CLXI!)
        assert D_AVG.denominator == K + 1   # 13

    def test_mean_square_distance(self):
        assert D_SQ_AVG == Fraction(40, 13)
        assert D_SQ_AVG == Fraction(V, K + 1)   # V/(K+1): exact!

    def test_mean_square_denominator(self):
        # Mean-square distance = V/(K+1): denominator = K+1 = 13
        assert D_SQ_AVG.denominator == K + 1  # 13

    def test_distance_variance_exact(self):
        # Var = E[d²] - E[d]² = 40/13 - 484/169 = 36/169
        assert D_VAR == Fraction(36, 169)

    def test_distance_std_dev_numerator(self):
        # σ_d² = 36/169: σ_d = 6/13 = (K/2)/(K+1)
        assert D_VAR.numerator == (K // 2)**2   # 36 = 6²

    def test_distance_std_dev_denominator(self):
        assert D_VAR.denominator == (K + 1)**2   # 169 = 13²

    def test_distance_std_dev_formula(self):
        # σ_d = √(36/169) = 6/13 = (K/2)/(K+1) — half-valency over next superprime
        import math
        sigma = math.sqrt(float(D_VAR))
        assert abs(sigma - 6/13) < 1e-12


class TestT3_WienerIndex:
    """Wiener index W = sum_{i<j} d(i,j) — exact integer with beautiful factorization."""

    def test_wiener_index_value(self):
        assert WIENER == 1320

    def test_wiener_index_from_pairs(self):
        # W = |adj. pairs|×1 + |non-adj. pairs|×2
        assert WIENER == N_EDGES + 2 * N_NON_ADJ

    def test_N_edges(self):
        assert N_EDGES == 240   # = Q×V = Q×(Q+1)(Q²+1) / ... hmm or K×V/2

    def test_N_edges_formula(self):
        # |E| = V×K/2 = 40×12/2 = 240 = K×V/2
        assert N_EDGES == K * V // 2
        assert N_EDGES == 240

    def test_N_non_adjacent_pairs(self):
        assert N_NON_ADJ == 540   # = C(V,2) - |E| = 780 - 240

    def test_N_non_adjacent_is_Q_cubed_times_20(self):
        # 540 = 20×27 = 20×Q³ = (V/2)×Q³ = V×Q³/2
        assert N_NON_ADJ == V * Q**3 // 2   # 40×27/2 = 540

    def test_wiener_formula_theta_K_K_minus_1(self):
        # W = θ(W33) × K × (K-1) = 10×12×11 = 1320 — EXACT!
        assert WIENER == LOVÁSZ_THETA * K * (K - 1)

    def test_wiener_times_2_divided_by_V(self):
        # 2W/V = 2×1320/40 = 66 = K + 2(V-K-1) = sum of degrees in distance graph
        assert 2 * WIENER // V == K + 2 * N_DIST_2

    def test_wiener_equals_avg_dist_times_pairs(self):
        # W = d_avg × C(V,2) = (22/13) × 780 = 22×60 = 1320
        assert D_AVG * (V * (V - 1) // 2) == WIENER


class TestT4_KirchhoffIndex:
    """Kirchhoff index Kf = sum_{i<j} R(i,j) via Laplacian eigenvalues."""

    def test_kirchhoff_index_exact(self):
        assert KF == Fraction(267, 2)

    def test_kirchhoff_index_value(self):
        assert float(KF) == 133.5

    def test_kirchhoff_via_laplacian_eigenvalues(self):
        # Kf = V × (MUL_R/μ_R + MUL_S/μ_S) = 40×(24/10 + 15/16)
        assert KF == V * (Fraction(MUL_R, MU_R) + Fraction(MUL_S, MU_S))

    def test_laplacian_eigenvalue_mu_R(self):
        # μ_R = K - r = 12 - 2 = 10 = θ(W33)
        assert MU_R == 10
        assert MU_R == LOVÁSZ_THETA

    def test_laplacian_eigenvalue_mu_S(self):
        # μ_S = K - s = K + |s| = 12 + 4 = 16 = MU²
        assert MU_S == 16
        assert MU_S == MU**2

    def test_kirchhoff_numerator(self):
        assert KF.numerator == 267   # = 3×89

    def test_kirchhoff_denominator(self):
        assert KF.denominator == 2

    def test_kirchhoff_via_edge_sums(self):
        # Kf = N_EDGES×R_adj + N_NON_ADJ×R_non
        assert KF == N_EDGES * R_ADJ + N_NON_ADJ * R_NON

    def test_pseudoinverse_diagonal(self):
        # L+(i,i) = Kf/V² = 267/3200
        assert LP_DIAG == Fraction(267, 3200)

    def test_pseudoinverse_diagonal_from_kirchhoff(self):
        # By vertex-transitivity: V²×L+(i,i) = Kf
        assert V**2 * LP_DIAG == KF


class TestT5_SpectralIdempotents:
    """Entries of spectral projection matrices E_R, E_S (Bose-Mesner algebra)."""

    def test_ER_diagonal(self):
        # E_R(i,i) = MUL_R/V = 24/40 = 3/5
        assert ER_DIAG == Fraction(3, 5)
        assert ER_DIAG == Fraction(MUL_R, V)

    def test_ES_diagonal(self):
        # E_S(i,i) = MUL_S/V = 15/40 = 3/8
        assert ES_DIAG == Fraction(3, 8)
        assert ES_DIAG == Fraction(MUL_S, V)

    def test_idempotent_diagonals_sum(self):
        # (1/V) + ER_diag + ES_diag = 1 (partition of identity)
        assert Fraction(1, V) + ER_DIAG + ES_DIAG == 1

    def test_ER_adj_exact(self):
        assert ER_ADJ == Fraction(1, 10)

    def test_ES_adj_exact(self):
        assert ES_ADJ == Fraction(-1, 8)

    def test_ER_non_exact(self):
        assert ER_NON == Fraction(-1, 15)

    def test_ES_non_exact(self):
        assert ES_NON == Fraction(1, 24)

    def test_idempotent_consistency_adjacent(self):
        # EIG_R×ER_adj + EIG_S×ES_adj = A_{adj} - K/V = 1 - 3/10 = 7/10
        lhs = EIG_R * ER_ADJ + EIG_S * ES_ADJ
        assert lhs == 1 - Fraction(K, V)

    def test_idempotent_consistency_non_adjacent(self):
        # EIG_R×ER_non + EIG_S×ES_non = A_{non} - K/V = 0 - 3/10 = -3/10
        lhs = EIG_R * ER_NON + EIG_S * ES_NON
        assert lhs == -Fraction(K, V)

    def test_quadratic_consistency_adjacent(self):
        # EIG_R²×ER_adj + EIG_S²×ES_adj = (A²)_{adj} - K²/V = LAM - K²/V
        lhs = EIG_R**2 * ER_ADJ + EIG_S**2 * ES_ADJ
        rhs = LAM - Fraction(K**2, V)
        assert lhs == rhs

    def test_quadratic_consistency_non_adjacent(self):
        # EIG_R²×ER_non + EIG_S²×ES_non = (A²)_{non} - K²/V = MU - K²/V
        lhs = EIG_R**2 * ER_NON + EIG_S**2 * ES_NON
        rhs = MU - Fraction(K**2, V)
        assert lhs == rhs


class TestT6_EffectiveResistance:
    """Effective resistance R(i,j): only two distinct values for SRG."""

    def test_R_adj_exact(self):
        assert R_ADJ == Fraction(13, 80)

    def test_R_non_exact(self):
        assert R_NON == Fraction(7, 40)

    def test_R_adj_formula(self):
        # R_adj = (K+1)/(2V) = 13/80: numerator = K+1 = 13 (supersingular prime!)
        assert R_ADJ == Fraction(K + 1, 2 * V)

    def test_R_non_formula(self):
        # R_non = (K+2)/(2V) = 14/80 = 7/40: numerator = K+2 = 14 = η(0) = 4q+2!
        assert R_NON == Fraction(K + 2, 2 * V)

    def test_R_adj_numerator_is_supersingular_prime(self):
        # 13 = K+1 = Q²+Q+1 — supersingular prime, N_integ from Phase CLXI
        assert R_ADJ.numerator == K + 1
        assert R_ADJ.numerator == Q**2 + Q + 1   # 13

    def test_R_non_numerator_is_eta_invariant(self):
        # K+2 = 14 = 4q+2 = η(0) (eta invariant from Phase CLV!)
        # But R_non = 7/40, so numerator = 7 = (K+2)/2 = LAM+MU+1
        assert R_NON.numerator == LAM + MU + 1   # 7

    def test_R_non_denominator(self):
        # 40 = V: resistance to non-neighbor is 7/V = 7/40
        assert R_NON.denominator == V

    def test_R_adj_less_than_R_non(self):
        # Adjacent vertices are "closer" in resistance metric
        assert R_ADJ < R_NON

    def test_R_difference_exact(self):
        # R_non - R_adj = 1/(2V) = 1/80 (exactly one unit of 1/(2V)!)
        diff = R_NON - R_ADJ
        assert diff == Fraction(1, 2 * V)

    def test_R_sum_from_kirchhoff(self):
        # Kf = N_EDGES×R_adj + N_NON_ADJ×R_non
        total = N_EDGES * R_ADJ + N_NON_ADJ * R_NON
        assert total == KF

    def test_R_adj_from_pseudoinverse(self):
        # R_adj = 2(L+(i,i) - L+(i,j)_adj) = 2(267/3200 - 7/3200) = 2×260/3200 = 13/80
        assert LP_ADJ == Fraction(7, 3200)
        assert 2 * (LP_DIAG - LP_ADJ) == R_ADJ

    def test_R_non_from_pseudoinverse(self):
        # R_non = 2(L+(i,i) - L+(i,j)_non) = 2(267/3200 - (-13/3200)) = 2×280/3200 = 7/40
        assert LP_NON == Fraction(-13, 3200)
        assert 2 * (LP_DIAG - LP_NON) == R_NON


class TestT7_DistancePolynomial:
    """Distance polynomial D(x) = 1 + K×x + (V-K-1)×x² and its evaluations."""

    def dist_poly(self, x):
        return 1 + K * x + N_DIST_2 * x**2

    def test_D_at_1(self):
        # D(1) = V (total vertices)
        assert self.dist_poly(1) == V

    def test_D_at_0(self):
        # D(0) = 1 (only the vertex itself at distance 0)
        assert self.dist_poly(0) == 1

    def test_D_at_minus_1(self):
        # D(-1) = 1 - K + (V-K-1) = V - 2K = 40 - 24 = 16 = MU²
        val = self.dist_poly(-1)
        assert val == MU**2
        assert val == 16

    def test_D_at_minus_1_equals_MU_squared(self):
        assert self.dist_poly(-1) == MU**2

    def test_D_derivative_at_1(self):
        # D'(x) = K + 2(V-K-1)x; D'(1) = K + 2(V-K-1) = 12+54 = 66 = 2W/V
        dprime = K + 2 * N_DIST_2 * 1
        assert dprime == 2 * WIENER // V

    def test_D_sum_equals_wiener_via_derivative(self):
        # V × D'(1) / 2 = Wiener index
        dprime_at_1 = K + 2 * N_DIST_2
        assert V * dprime_at_1 // 2 == WIENER

    def test_D_at_Q(self):
        # D(q) = 1 + 12×3 + 27×9 = 1 + 36 + 243 = 280 = V×7 = V×(LAM+MU+1)
        val = self.dist_poly(Q)
        assert val == V * (LAM + MU + 1)   # 40×7 = 280

    def test_D_second_root_location(self):
        # D(x)=0 when 27x²+12x+1=0: x = (-12±√(144-108))/54 = (-12±6)/54
        # x₁ = -6/54 = -1/9 = -1/Q², x₂ = -18/54 = -1/3 = -1/Q = EV_S (walk!)
        import math
        disc = K**2 - 4 * N_DIST_2
        assert disc == 36    # = (K/2)² = 36 = 6²
        # Roots: x = (-K ± √disc) / (2×N_DIST_2) = (-12±6)/54
        x1 = Fraction(-K + 6, 2 * N_DIST_2)   # = -6/54 = -1/9
        x2 = Fraction(-K - 6, 2 * N_DIST_2)   # = -18/54 = -1/3
        assert x1 == Fraction(-1, Q**2)   # = -1/9
        assert x2 == Fraction(-1, Q)      # = -1/3 = walk eigenvalue EV_S!


class TestT8_MetricSuperprimes:
    """The supersingular primes 11 and 13 = K-1 and K+1 appear throughout."""

    def test_avg_dist_connects_two_superprimes(self):
        # d_avg = 22/13 = 2×(K-1)/(K+1) = 2×11/13
        assert K - 1 == 11   # 5th supersingular prime
        assert K + 1 == 13   # 6th supersingular prime
        assert D_AVG == Fraction(2 * (K - 1), K + 1)

    def test_R_adj_numerator_is_K_plus_1(self):
        assert R_ADJ.numerator == K + 1   # 13

    def test_wiener_contains_K_minus_1(self):
        # W = 1320 = 10×12×11 = θ×K×(K-1); K-1=11 factor
        assert WIENER % (K - 1) == 0
        assert WIENER // (K - 1) == LOVÁSZ_THETA * K   # 10×12=120

    def test_mean_sq_distance_denominator(self):
        # E[d²] = V/(K+1) = 40/13
        assert D_SQ_AVG.denominator == K + 1   # 13

    def test_N_dist2_equals_Q_cubed(self):
        # Q³=27 non-adjacent vertices: connects to dim(Albert algebra) from Phase CLIX
        assert N_DIST_2 == Q**3

    def test_laplacian_gap_equals_lovász(self):
        # μ_R = K-r = 10 = θ(W33) — smallest non-zero Laplacian eigenvalue = Lovász theta!
        assert MU_R == LOVÁSZ_THETA

    def test_laplacian_mu_S_equals_MU_squared(self):
        # μ_S = K+|s| = 16 = MU² = 4² (second non-zero Laplacian eigenvalue = μ²)
        assert MU_S == MU**2

    def test_kirchhoff_connects_avg_and_resistance(self):
        # Kf/W = (267/2)/1320 = 267/2640 = 89/880 — ratio of resistance to distance
        ratio = KF / WIENER
        assert ratio == Fraction(267, 2640)

    def test_distance_poly_discriminant_is_K_half_squared(self):
        # disc(D) = K² - 4×N_DIST_2 = 144 - 108 = 36 = (K/2)² = 6²
        disc = K**2 - 4 * N_DIST_2
        assert disc == (K // 2)**2
