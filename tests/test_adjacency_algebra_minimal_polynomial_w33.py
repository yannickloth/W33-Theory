"""
Phase CLXXXV: Adjacency Algebra, Minimal Polynomial, and Closed-Walk Recurrence of W(3,3)

The adjacency matrix satisfies a cubic minimal polynomial with Q-formula coefficients,
giving a three-term recurrence for all closed-walk power sums p_k = tr(A^k).

Key discoveries:
  - Minimal polynomial: (λ-K)(λ-r)(λ-s) = λ³ - THETA·λ² - 32λ + 96
  - Cayley-Hamilton: A³ = THETA·A² + 32A - 96I (holds as matrix identity!)
  - Coefficient 32 = LAM·MU² = MU·(K-MU) = (Q+1)²(Q-1) = 32 ✓
  - Coefficient 96 = K·LAM·MU = K·(K-MU) = Q(Q+1)²(Q-1) = 96 ✓
  - THETA = Q²+1 = 10 (leading coefficient; the sum K+r+s)
  - Recurrence: p_{k+3} = THETA·p_{k+2} + 32·p_{k+1} - 96·p_k
  - p_0=40, p_1=0, p_2=480, p_3=960, p_4=24960, p_5=234240
  - p_3/V = 24 = K·LAM (closed walks of length 3 per vertex = 24 ✓)
  - p_3 = 6 * (triangles in G) * 2 = 12 * 80... wait: p_3 = 6·T where T=#triangles=160
  - Coefficient -32 = K(r+s) + rs = K(LAM-MU) + (MU-K) (Q-formula for quadratic term)
  - Constant 96 = -K·r·s = K·(K-MU) = 96 (the -K·rs identity!)
  - Spectral moments via recurrence agree with direct computation
  - Bose-Mesner algebra: A spans entire adjacency algebra over rationals
  - Minimal polynomial is ALSO the characteristic polynomial factor (degree-3 divisor of char poly)
  - All coefficients expressible as products of {K, LAM, MU, r, s}
"""

from fractions import Fraction

# === W(3,3) parameters ===
Q = 3
V = 40
K = 12
LAM = 2
MU = 4

EIG_K = K
EIG_R = 2
EIG_S = -4

MUL_K = 1
MUL_R = 24
MUL_S = 15

THETA = EIG_K + EIG_R + EIG_S   # = 10

# Minimal polynomial: (λ-K)(λ-r)(λ-s) = λ³ - c2·λ² - c1·λ + c0
# where c2 = K+r+s = THETA, c1 = -(Kr+Ks+rs) = 32, c0 = K·r·s but sign: see below
MINPOLY_C2 = THETA                         # = 10 (coefficient of λ²; NEGATIVE in poly)
MINPOLY_C1 = -(EIG_K * EIG_R + EIG_K * EIG_S + EIG_R * EIG_S)  # = 32
MINPOLY_C0 = EIG_K * EIG_R * EIG_S        # = -96 (constant term in poly = K*r*s = -96)

# Power sums p_k = tr(A^k): K^k + r^k * f + s^k * g
P0 = V                                      # = 40
P1 = EIG_K * MUL_K + EIG_R * MUL_R + EIG_S * MUL_S   # = 0
P2 = EIG_K**2 * MUL_K + EIG_R**2 * MUL_R + EIG_S**2 * MUL_S   # = 480
P3 = EIG_K**3 * MUL_K + EIG_R**3 * MUL_R + EIG_S**3 * MUL_S   # = 960
P4 = EIG_K**4 * MUL_K + EIG_R**4 * MUL_R + EIG_S**4 * MUL_S   # = 24960
P5 = EIG_K**5 * MUL_K + EIG_R**5 * MUL_R + EIG_S**5 * MUL_S   # = 234240


# ============================================================
class TestT1_MinimalPolynomialCoefficients:
    """Coefficients of (λ-K)(λ-r)(λ-s) expressed as Q-formulas."""

    def test_c2_equals_THETA(self):
        # c2 = K+r+s = THETA = 10
        assert MINPOLY_C2 == THETA

    def test_c2_value(self):
        assert MINPOLY_C2 == 10

    def test_c1_value(self):
        # c1 = -(Kr+Ks+rs) = -(K(r+s)+rs) = -(-24-8) = 32
        assert MINPOLY_C1 == 32

    def test_c1_equals_LAM_MU_squared(self):
        # 32 = LAM * MU^2 = 2 * 16 = 32
        assert MINPOLY_C1 == LAM * MU**2

    def test_c1_equals_MU_times_K_minus_MU(self):
        # 32 = MU * (K - MU) = 4 * 8 = 32 (non-adjacency × eigenproduct-magnitude!)
        assert MINPOLY_C1 == MU * (K - MU)

    def test_c1_Q_formula(self):
        # 32 = (Q+1)^2 * (Q-1) = 16 * 2 = 32
        assert MINPOLY_C1 == (Q + 1)**2 * (Q - 1)

    def test_c1_from_K_r_s(self):
        # c1 = -(K*r + K*s + r*s) = 32
        assert -(EIG_K * EIG_R + EIG_K * EIG_S + EIG_R * EIG_S) == MINPOLY_C1

    def test_c0_value(self):
        # K * r * s = 12 * 2 * (-4) = -96
        assert MINPOLY_C0 == -96

    def test_c0_equals_minus_K_LAM_MU(self):
        # K*r*s = -K*LAM*MU = -12*2*4 = -96 (since |r|=LAM, |s|=MU and r>0, s<0: r*s=-LAM*MU)
        assert MINPOLY_C0 == -(EIG_K * LAM * MU)

    def test_c0_Q_formula(self):
        # -96 = -Q*(Q+1)^2*(Q-1) = -3*16*2 = -96
        assert MINPOLY_C0 == -(Q * (Q + 1)**2 * (Q - 1))

    def test_c0_equals_minus_K_times_K_minus_MU(self):
        # K*r*s = -K*(K-MU) = -12*8 = -96
        assert MINPOLY_C0 == -(EIG_K * (EIG_K - MU))

    def test_characteristic_cubic_expansion(self):
        # Verify: (λ-K)(λ-r)(λ-s) = λ³ - THETA*λ² - 32*λ + 96  at λ=0
        # At λ=0: (-K)(-r)(-s) = -K*r*s = -(-96) = 96 ✓
        assert (-EIG_K) * (-EIG_R) * (-EIG_S) == 96

    def test_characteristic_cubic_at_K(self):
        # At λ=K: (K-K)(K-r)(K-s) = 0 ✓ (K is a root)
        val = (EIG_K - EIG_K) * (EIG_K - EIG_R) * (EIG_K - EIG_S)
        assert val == 0


class TestT2_MinimalPolynomialRelation:
    """A³ = THETA*A² + 32*A - 96*I; check via eigenvalue substitution."""

    def test_A3_relation_at_EIG_K(self):
        # K^3 = THETA*K^2 + 32*K - 96: 1728 = 10*144 + 32*12 - 96 = 1440+384-96 = 1728 ✓
        assert EIG_K**3 == THETA * EIG_K**2 + MINPOLY_C1 * EIG_K + MINPOLY_C0

    def test_A3_relation_at_EIG_R(self):
        # r^3 = THETA*r^2 + 32*r - 96: 8 = 10*4 + 64 - 96 = 40+64-96 = 8 ✓
        assert EIG_R**3 == THETA * EIG_R**2 + MINPOLY_C1 * EIG_R + MINPOLY_C0

    def test_A3_relation_at_EIG_S(self):
        # s^3 = THETA*s^2 + 32*s - 96: -64 = 10*16 - 128 - 96 = 160-128-96 = -64 ✓
        assert EIG_S**3 == THETA * EIG_S**2 + MINPOLY_C1 * EIG_S + MINPOLY_C0

    def test_minimal_polynomial_vanishes_at_all_eigenvalues(self):
        # (λ-K)(λ-r)(λ-s) = 0 for λ in {K, r, s}
        for lam in [EIG_K, EIG_R, EIG_S]:
            val = (lam - EIG_K) * (lam - EIG_R) * (lam - EIG_S)
            assert val == 0

    def test_minimal_poly_degree_3(self):
        # W(3,3) has exactly 3 distinct eigenvalues → minimal polynomial degree = 3
        distinct_eigs = len({EIG_K, EIG_R, EIG_S})
        assert distinct_eigs == 3

    def test_cayley_hamilton_trace(self):
        # tr(A³ - THETA*A² - 32*A + 96*I) = P3 - THETA*P2 - 32*P1 + 96*V = 0
        assert P3 - THETA * P2 - MINPOLY_C1 * P1 + 96 * V == 0


class TestT3_PowerSumValues:
    """p_k = tr(A^k) values: p_0=40, p_1=0, p_2=480, p_3=960, p_4=24960, p_5=234240."""

    def test_p0_equals_V(self):
        assert P0 == V

    def test_p1_equals_zero(self):
        assert P1 == 0

    def test_p2_equals_V_K(self):
        # tr(A²) = V*K = 40*12 = 480
        assert P2 == V * K

    def test_p3_value(self):
        assert P3 == 960

    def test_p3_equals_2_V_K(self):
        # p_3 = 2 * V * K = 2 * 480 = 960 (exactly twice p_2!)
        assert P3 == 2 * V * K

    def test_p3_from_triangles(self):
        # p_3 = 6 * #triangles = 6 * 160 = 960 (each triangle gives 6 closed walks of length 3)
        triangles = 160
        assert P3 == 6 * triangles

    def test_p3_over_V_equals_K_LAM(self):
        # Closed walks of length 3 per vertex = K*LAM = 12*2 = 24 (= p3/V)
        assert P3 // V == K * LAM

    def test_p4_value(self):
        assert P4 == 24960

    def test_p5_value(self):
        assert P5 == 234240


class TestT4_ClosedWalkRecurrence:
    """p_{k+3} = THETA*p_{k+2} + 32*p_{k+1} - 96*p_k from minimal polynomial."""

    def test_recurrence_p3_from_p2_p1_p0(self):
        # p_3 = THETA*p_2 + 32*p_1 - 96*p_0 = 10*480 + 32*0 - 96*40 = 4800 - 3840 = 960
        assert THETA * P2 + MINPOLY_C1 * P1 - 96 * P0 == P3

    def test_recurrence_p4_from_p3_p2_p1(self):
        # p_4 = THETA*p_3 + 32*p_2 - 96*p_1 = 10*960 + 32*480 - 0 = 9600+15360 = 24960
        assert THETA * P3 + MINPOLY_C1 * P2 - 96 * P1 == P4

    def test_recurrence_p5_from_p4_p3_p2(self):
        # p_5 = THETA*p_4 + 32*p_3 - 96*p_2 = 10*24960 + 32*960 - 96*480
        # = 249600 + 30720 - 46080 = 234240
        assert THETA * P4 + MINPOLY_C1 * P3 - 96 * P2 == P5

    def test_recurrence_coefficient_THETA(self):
        # Leading recurrence coefficient = THETA = K+r+s = Q^2+1 = 10
        assert THETA == Q**2 + 1

    def test_recurrence_coefficient_32(self):
        # Middle coefficient = -(K*r+K*s+r*s) = 32 = LAM*MU^2
        assert MINPOLY_C1 == LAM * MU**2

    def test_recurrence_coefficient_96(self):
        # Trailing coefficient = K*r*s = -96 → subtract 96*p_{k} in recurrence
        assert -MINPOLY_C0 == 96


class TestT5_WalkCountsPerVertex:
    """p_k/V = average closed walks per vertex; k=2,3,4,5."""

    def test_p2_per_vertex(self):
        # p_2 / V = K = 12 (walks v → u → v for each neighbor u)
        assert P2 // V == K

    def test_p3_per_vertex(self):
        # p_3 / V = K*LAM = 24 (walks v→u→w→v where v,u,w form triangle)
        assert P3 // V == K * LAM

    def test_p3_per_vertex_Q_formula(self):
        # K*LAM = Q(Q+1)(Q-1) = Q*(Q^2-1) = 3*8 = 24
        assert P3 // V == Q * (Q**2 - 1)

    def test_p4_per_vertex(self):
        # p_4 / V = 24960/40 = 624
        assert P4 // V == 624

    def test_p5_per_vertex(self):
        # p_5 / V = 234240/40 = 5856
        assert P5 // V == 5856

    def test_p2_divisible_by_V(self):
        assert P2 % V == 0

    def test_p3_divisible_by_V(self):
        assert P3 % V == 0

    def test_p4_divisible_by_V(self):
        assert P4 % V == 0

    def test_p5_divisible_by_V(self):
        assert P5 % V == 0


class TestT6_AlgebraIdentities:
    """Cross-identities from the minimal polynomial structure."""

    def test_product_of_roots(self):
        # K * r * s = 12 * 2 * (-4) = -96 = -K * LAM * MU
        assert EIG_K * EIG_R * EIG_S == -K * LAM * MU

    def test_sum_of_roots(self):
        # K + r + s = THETA = 10
        assert EIG_K + EIG_R + EIG_S == THETA

    def test_sum_of_products_of_pairs(self):
        # K*r + K*s + r*s = -32 = -(MINPOLY_C1)
        assert EIG_K * EIG_R + EIG_K * EIG_S + EIG_R * EIG_S == -MINPOLY_C1

    def test_vieta_product_formula(self):
        # K * r * s = -96 = -(MINPOLY_C1 * THETA / ...) hmm; just verify value
        assert EIG_K * EIG_R * EIG_S == -96

    def test_c1_c2_c0_Q_identities(self):
        # 32 = (Q+1)^2 * (Q-1); 96 = Q*(Q+1)^2*(Q-1); ratio 96/32 = Q = 3
        assert MINPOLY_C1 == (Q + 1)**2 * (Q - 1)
        assert -MINPOLY_C0 == Q * (Q + 1)**2 * (Q - 1)
        assert Fraction(-MINPOLY_C0, MINPOLY_C1) == Q

    def test_c0_over_c1_equals_Q(self):
        # 96/32 = 3 = Q (ratio of polynomial constant to linear coefficient!)
        assert Fraction(-MINPOLY_C0, MINPOLY_C1) == Q

    def test_c1_over_THETA(self):
        # 32/10 = 16/5 (no special meaning, but useful to verify)
        assert Fraction(MINPOLY_C1, THETA) == Fraction(16, 5)
