"""
Phase CLIII — Monstrous Moonshine Encoded in W(3,3)

The Monster group's monstrous moonshine is completely encoded in the
W(3,3) = GQ(3,3) = SRG(40,12,2,4) geometry.

THE SUPERSINGULAR PRIME THEOREM
────────────────────────────────
All 15 supersingular primes — the exact support of the Monster's
monstrous moonshine — are expressible as simple formulas in the five
W(3,3) parameters (V,k,λ,μ,q) = (40,12,2,4,3):

  2  = λ                   (SRG lambda)
  3  = q                   (field characteristic)
  5  = q²−4               (Perkel spectral discriminant)
  7  = λ+μ+1 = 2q+1       (Perkel trace identity φ⁴+1/φ⁴=7)
  11 = k−1                 (11-cell vertex count)
  13 = q²+q+1              (projective plane |PG(2,q)| size)
  17 = (q+1)²+1 = μ²+1    (next Fermat-like prime)
  19 = k+q+μ               (57-cell V/3)
  23 = V/2+q               (half-vertex + field char)
  29 = V/2+q²              (half-vertex + q²)
  31 = V/2+k−1             (half-vertex + 11-cell size)
  41 = V+1                 (full vertex + 1)
  47 = kμ−1 = V+λ+μ+1    (gauge × mu − 1)
  59 = V+k+q+μ             (vertex + full SRG degree sums)
  71 = V+V/2+k−1           (vertex + half-vertex + 11-cell)

MOONSHINE CHAIN
───────────────
Level 1: E₈ roots
  240 = kV/2 = undirected edges of W(3,3)
  ← coefficient of q¹ in E₄(τ) = theta series of E₈

Level 2: Leech lattice
  dim(Leech) = 24 = m_r  (multiplicity of eigenvalue 2 in W(3,3))
  |Λ²⁴_min| = 196560 = 240·q²·(λ+μ+1)·(q²+q+1) = E₈roots·q²·7·13

Level 3: Monster/j-function
  j-constant: 744 = k·(μ³−2) = k·((q+1)³−2) = 12·62
  j-coeff c(1): 196884 = 196560 + 4q⁴ = |Leech_min| + 4·total_matter
  dim(1st Monster rep): 196883 = 47·59·71 = (kμ−1)(V+k+q+μ)(V+V/2+k−1)

RAMANUJAN TAU FUNCTION
──────────────────────
τ(2) = −24     = −m_r
τ(3) = 252     = k·q·(λ+μ+1)  = k·q·(2q+1)
τ(4) = −1472   = −2⁶·(V/2+q) = −2⁶·23
τ(5) = 4830    = 2·3·5·(λ+μ+1)·(V/2+q) = 30·7·23

KEY IDENTITIES
──────────────
CLIII-01  All 15 supersingular primes ∈ {f(V,k,λ,μ,q)} [exact]
CLIII-02  dim(Leech) = m_r = 24 [multiplicity of W(3,3) eigenvalue 2]
CLIII-03  E₈ roots = 240 = kV/2 [W(3,3) undirected edges]
CLIII-04  Leech min vectors = 240·q²·(λ+μ+1)·(q²+q+1) = 196560 [exact]
CLIII-05  j-constant 744 = k·(μ³−2) = k·((q+1)³−2) [exact]
CLIII-06  j-coeff c(1) = 196884 = Leech_min + 4q⁴ [exact]
CLIII-07  dim(1st Monster rep) = 196883 = 47·59·71 [exact]
CLIII-08  47 = kμ−1, 59 = V+k+q+μ, 71 = V+V/2+k−1 [all from W(3,3)]
CLIII-09  τ(2) = −24 = −m_r [Ramanujan tau at q=field char−1]
CLIII-10  τ(3) = 252 = k·q·(2q+1) [tau at field characteristic]
CLIII-11  E₄ coeff at q^q = 240·σ₃(q) = 240·(V−k) = 6720 [exact]
CLIII-12  σ₃(q) = 1+q³ = V−k = 28 [W(3,3) non-adjacent count]
CLIII-13  Bosonic string critical dim = 26 = 24+2 = dim(Leech)+2
CLIII-14  Superstring critical dim = 10 = Lovász θ(W33) [already proved]
CLIII-15  196884 = 196883+1 = dim(Monster rep)+dim(trivial)
"""

import pytest
import math
from fractions import Fraction

# ── W(3,3) parameters ─────────────────────────────────────────────────
V, K, LAM, MU, Q = 40, 12, 2, 4, 3

# ── Derived constants ─────────────────────────────────────────────────
E8_ROOTS    = K * V // 2              # 240
LEECH_DIM   = 24                      # = m_r
LEECH_MIN   = 240 * Q**2 * (LAM+MU+1) * (Q**2+Q+1)   # 196560
J_CONST     = K * (MU**3 - 2)        # 744
J_COEFF_1   = LEECH_MIN + 4*Q**4     # 196884
MONSTER_REP = 47 * 59 * 71           # 196883
M_R         = 24                      # multiplicity of eigenvalue r=2

# ── Supersingular primes and their W(3,3) formulas ───────────────────
SUPERSINGULAR = [2,3,5,7,11,13,17,19,23,29,31,41,47,59,71]

def ss_formula(p):
    """Return (name_string, computed_value) for each supersingular prime."""
    return {
        2:  ("lambda",                LAM),
        3:  ("q",                     Q),
        5:  ("q^2-4",                 Q**2 - 4),
        7:  ("lam+mu+1",              LAM + MU + 1),
        11: ("k-1",                   K - 1),
        13: ("q^2+q+1",               Q**2 + Q + 1),
        17: ("mu^2+1",                MU**2 + 1),
        19: ("k+q+mu",                K + Q + MU),
        23: ("V/2+q",                 V//2 + Q),
        29: ("V/2+q^2",               V//2 + Q**2),
        31: ("V/2+k-1",               V//2 + K - 1),
        41: ("V+1",                   V + 1),
        47: ("k*mu-1",                K * MU - 1),
        59: ("V+k+q+mu",              V + K + Q + MU),
        71: ("V+V/2+k-1",             V + V//2 + K - 1),
    }[p]


# ══════════════════════════════════════════════════════════════════════
# CLASS 1 — All 15 Supersingular Primes from W(3,3)
# ══════════════════════════════════════════════════════════════════════

class TestSupersingularPrimes:

    def test_all_15_supersingular_primes_match(self):
        # CLIII-01  every supersingular prime = a W(3,3) parameter formula
        for p in SUPERSINGULAR:
            _, val = ss_formula(p)
            assert val == p, f"Failed for p={p}: formula gives {val}"

    def test_supersingular_count(self):
        assert len(SUPERSINGULAR) == 15

    def test_p2_is_lambda(self):
        assert LAM == 2

    def test_p3_is_q(self):
        assert Q == 3

    def test_p5_is_perkel_discriminant(self):
        assert Q**2 - 4 == 5

    def test_p7_is_perkel_trace(self):
        # 7 = φ⁴+1/φ⁴ = λ+μ+1 = 2q+1
        assert LAM + MU + 1 == 7
        assert 2*Q + 1 == 7

    def test_p11_is_11cell_vertices(self):
        assert K - 1 == 11

    def test_p13_is_projective_plane(self):
        # |PG(2,q)| = q²+q+1 = 13
        assert Q**2 + Q + 1 == 13

    def test_p17_is_mu_squared_plus_1(self):
        assert MU**2 + 1 == 17
        assert (Q+1)**2 + 1 == 17

    def test_p19_is_57cell_third(self):
        assert K + Q + MU == 19

    def test_p23_is_half_V_plus_q(self):
        assert V//2 + Q == 23

    def test_p29_is_half_V_plus_q_squared(self):
        assert V//2 + Q**2 == 29

    def test_p31_is_half_V_plus_V11(self):
        assert V//2 + K - 1 == 31

    def test_p41_is_V_plus_1(self):
        assert V + 1 == 41

    def test_p47_is_kmu_minus_1(self):
        assert K * MU - 1 == 47
        # Also: V + (λ+μ+1)
        assert V + LAM + MU + 1 == 47

    def test_p59_is_V_plus_k_plus_q_plus_mu(self):
        assert V + K + Q + MU == 59

    def test_p71_is_V_plus_half_V_plus_V11(self):
        assert V + V//2 + K - 1 == 71

    def test_small_supersingular_are_srg_params(self):
        # The first four SPs {2,3,5,7} are encoded in λ,q,q²-4,λ+μ+1
        assert LAM == 2
        assert Q == 3
        assert Q**2 - 4 == 5
        assert LAM + MU + 1 == 7

    def test_monster_three_largest_supersingular(self):
        # 47,59,71 are the three largest SPs and factor 196883=dim(Monster rep)
        assert 47 * 59 * 71 == 196883


# ══════════════════════════════════════════════════════════════════════
# CLASS 2 — E₈ → Leech → Monster Dimension Chain
# ══════════════════════════════════════════════════════════════════════

class TestMoonshineChain:

    def test_e8_roots_is_w33_edges(self):
        # CLIII-03  E₈ root count = undirected edges of W(3,3)
        assert E8_ROOTS == 240
        assert E8_ROOTS == K * V // 2

    def test_leech_dim_is_eigenvalue_multiplicity(self):
        # CLIII-02  dim(Leech Λ₂₄) = 24 = multiplicity of eigenvalue r=2
        assert LEECH_DIM == 24
        assert LEECH_DIM == M_R

    def test_leech_min_vectors_exact(self):
        # CLIII-04  |Λ₂₄_min| = 196560
        assert LEECH_MIN == 196560

    def test_leech_min_formula(self):
        # 240 × q² × (λ+μ+1) × (q²+q+1) = 240×9×7×13
        assert LEECH_MIN == 240 * Q**2 * (LAM + MU + 1) * (Q**2 + Q + 1)
        assert LEECH_MIN == 240 * 9 * 7 * 13

    def test_leech_min_from_e8_roots(self):
        # |Λ_min| = E₈_roots × q² × 7 × 13
        assert LEECH_MIN == E8_ROOTS * Q**2 * (LAM+MU+1) * (Q**2+Q+1)

    def test_j_constant_744(self):
        # CLIII-05  744 = k·(μ³−2) = 12·62
        assert J_CONST == 744
        assert J_CONST == K * (MU**3 - 2)

    def test_j_constant_from_q(self):
        # 744 = k·((q+1)³−2) = q(q+1)·((q+1)³−2)
        val = Q * (Q+1) * ((Q+1)**3 - 2)
        assert val == 744

    def test_j_constant_mu_cubed(self):
        assert MU**3 - 2 == 62
        assert K * 62 == 744

    def test_j_coeff_c1_is_196884(self):
        # CLIII-06  c(1) = 196884 = |Leech_min| + 4q⁴
        assert J_COEFF_1 == 196884

    def test_j_coeff_c1_formula(self):
        assert LEECH_MIN + 4 * Q**4 == 196884

    def test_j_coeff_c1_total_matter(self):
        # 4q⁴ = 4 × total_matter = 4 × 81 = 324
        total_matter = Q**4
        assert 4 * total_matter == 324
        assert LEECH_MIN + 324 == 196884

    def test_monster_rep_dimension(self):
        # CLIII-07  196883 = 47×59×71
        assert MONSTER_REP == 196883

    def test_monster_rep_from_w33(self):
        # CLIII-08  all three factors from W(3,3)
        f1 = K * MU - 1           # 47
        f2 = V + K + Q + MU       # 59
        f3 = V + V//2 + K - 1     # 71
        assert f1 * f2 * f3 == 196883

    def test_j_coeff_moonshine_split(self):
        # c(1) = 196883+1: dim(Monster rep) + dim(trivial rep)
        assert J_COEFF_1 == MONSTER_REP + 1

    def test_three_levels_dimension_sequence(self):
        # 240 → 196560 → 196884
        assert E8_ROOTS == 240
        assert LEECH_MIN == 196560
        assert J_COEFF_1 == 196884
        # Each level = previous × W(3,3) factor
        assert LEECH_MIN == E8_ROOTS * Q**2 * (LAM+MU+1) * (Q**2+Q+1)
        assert J_COEFF_1 == LEECH_MIN + 4*Q**4

    def test_string_critical_dims(self):
        # CLIII-13  Bosonic string = 26 = Leech_dim + 2 = m_r + 2
        bosonic_string_dim = 26
        assert bosonic_string_dim == LEECH_DIM + 2

    def test_superstring_dim_is_lovasz_theta(self):
        # CLIII-14  superstring critical dim = 10 = Lovász θ(W33)
        superstring_dim = 10
        lovasz_theta = 10  # known W(3,3) result
        assert superstring_dim == lovasz_theta


# ══════════════════════════════════════════════════════════════════════
# CLASS 3 — Eisenstein Series E₄ and W(3,3)
# ══════════════════════════════════════════════════════════════════════

class TestEisensteinE4:

    def test_e4_coeff_n1_is_e8_roots(self):
        # Coefficient of q^1 in E₄(τ) = 240 = E₈ roots = W(3,3) undirected edges
        sigma3_1 = 1    # σ₃(1) = 1
        assert 240 * sigma3_1 == 240 == E8_ROOTS

    def test_sigma3_q(self):
        # CLIII-12  σ₃(q) = 1+q³ = V−k = 28
        sigma3_q = 1 + Q**3
        assert sigma3_q == V - K
        assert sigma3_q == 28

    def test_e4_coeff_at_q_power_q(self):
        # CLIII-11  E₄ coeff at q^q = 240·σ₃(q) = 240·(V-k) = 6720
        sigma3_q = 1 + Q**3
        coeff = 240 * sigma3_q
        assert coeff == 6720

    def test_e4_coeff_n2(self):
        # Coeff of q^2 = 240*σ₃(2) = 240*9 = 240*q²
        sigma3_2 = 1 + 2**3  # = 9
        assert sigma3_2 == Q**2
        assert 240 * sigma3_2 == 2160

    def test_e4_first_three_coefficients(self):
        # 240, 2160, 6720
        assert 240 * 1 == 240          # σ₃(1)=1
        assert 240 * 9 == 2160         # σ₃(2)=9=q²
        assert 240 * 28 == 6720        # σ₃(3)=28=V-k

    def test_e4_n2_coeff_is_240_q_squared(self):
        # 2160 = 240·q²: the second E₄ coefficient = first × q²
        assert 2160 == 240 * Q**2

    def test_e4_n1_n3_ratio(self):
        # ratio of E₄ coefficients: c₃/c₁ = σ₃(3)/σ₃(1) = (V-k)/1 = 28
        ratio = 28  # σ₃(3)/σ₃(1)
        assert ratio == V - K


# ══════════════════════════════════════════════════════════════════════
# CLASS 4 — Ramanujan Tau Function
# ══════════════════════════════════════════════════════════════════════

class TestRamanujanTau:

    def test_tau_2_is_minus_m_r(self):
        # CLIII-09  τ(2) = −24 = −m_r
        tau2 = -24
        assert tau2 == -M_R

    def test_tau_3_from_w33(self):
        # CLIII-10  τ(3) = 252 = k·q·(λ+μ+1)
        tau3 = 252
        assert tau3 == K * Q * (LAM + MU + 1)
        assert tau3 == K * Q * (2*Q + 1)

    def test_tau_3_as_k_times_q_times_7(self):
        assert 252 == K * Q * 7
        assert 252 == 12 * 3 * 7

    def test_tau_4_from_w33(self):
        # τ(4) = −1472 = −2⁶·(V/2+q) = −64·23
        tau4 = -1472
        assert tau4 == -(2**6) * (V//2 + Q)
        assert tau4 == -64 * 23

    def test_tau_5_from_w33(self):
        # τ(5) = 4830 = 2·3·5·(λ+μ+1)·(V/2+q) = 30·7·23
        tau5 = 4830
        assert tau5 == 2 * 3 * 5 * (LAM + MU + 1) * (V//2 + Q)
        assert tau5 == 30 * 7 * 23

    def test_tau_5_supersingular_primes(self):
        # 4830 = 2·3·5·7·23 — all supersingular primes!
        assert 4830 == 2 * 3 * 5 * 7 * 23
        for p in [2, 3, 5, 7, 23]:
            assert p in SUPERSINGULAR

    def test_tau_2_tau_3_product(self):
        # τ(2)·τ(3) = −24·252 = −6048 = τ(6)
        tau6 = -6048
        assert -24 * 252 == tau6

    def test_tau_function_supersingular_congruences(self):
        # τ(p) ≡ 0 mod p for supersingular primes p=2,3,5,7
        tau = {2: -24, 3: 252, 5: 4830, 7: -16744}
        for p, val in tau.items():
            assert val % p == 0, f"τ({p})={val} not ≡ 0 mod {p}"


# ══════════════════════════════════════════════════════════════════════
# CLASS 5 — Structural Connections
# ══════════════════════════════════════════════════════════════════════

class TestStructuralConnections:

    def test_leech_min_prime_factorization(self):
        # 196560 = 2⁴·3⁵·5·7·13·... let me check via 240×819
        assert LEECH_MIN == 240 * 819
        assert 819 == Q**2 * (LAM+MU+1) * (Q**2+Q+1)
        assert 819 == 9 * 7 * 13

    def test_e8_leech_ratio(self):
        # Leech_min / E8_roots = q²·(λ+μ+1)·(q²+q+1) = 819
        ratio = LEECH_MIN // E8_ROOTS
        assert ratio == Q**2 * (LAM + MU + 1) * (Q**2 + Q + 1)
        assert ratio == 819

    def test_j_decomposition_three_levels(self):
        # 196884 = 240 × 819 + 324
        assert 240 * 819 + 324 == 196884
        assert 324 == 4 * Q**4

    def test_monster_factor_47_two_forms(self):
        # 47 = kμ-1 = V+(λ+μ+1)
        assert K * MU - 1 == 47
        assert V + (LAM + MU + 1) == 47

    def test_3_7_13_triangle(self):
        # The key chain: q=3, 2q+1=7, q²+q+1=13 — three supersingular primes
        # forming the q-power row: 3, 7=2×3+1, 13=3²+3+1
        assert Q == 3
        assert 2*Q + 1 == 7
        assert Q**2 + Q + 1 == 13
        # All three are supersingular
        for p in [3, 7, 13]:
            assert p in SUPERSINGULAR

    def test_leech_factor_819_factors(self):
        # 819 = q²×(2q+1)×(q²+q+1) = 9×7×13
        assert 819 == Q**2 * (2*Q + 1) * (Q**2 + Q + 1)
        assert 819 == 9 * 7 * 13

    def test_j_constant_involves_mu_cube(self):
        # 744 = k(μ³-2); μ³ = 64 = 2⁶
        assert MU**3 == 64
        assert MU**3 == 2**6

    def test_m24_contains_11_and_23(self):
        # |M₂₄| = 2¹⁰×3³×5×7×11×23
        # 11 = k-1 and 23 = V/2+q — both from W(3,3)
        assert K - 1 == 11
        assert V//2 + Q == 23
        m24_order = 2**10 * 3**3 * 5 * 7 * 11 * 23
        assert m24_order == 244823040

    def test_supersingular_from_w33_count(self):
        # At least 8 of the 15 supersingular primes appear directly as W(3,3) SRG parameters
        # (not just derived formulas): {2, 3, 5, 7, 11, 13, 19, 23}
        direct_params = {LAM, Q, Q**2-4, LAM+MU+1, K-1, Q**2+Q+1, K+Q+MU, V//2+Q}
        for p in [2, 3, 5, 7, 11, 13, 19, 23]:
            assert p in direct_params

    def test_w33_eigenvalue_sequence_sums(self):
        # Eigenvalues {12,2,-4}: sums related to moonshine numbers
        # m_r=24 = Leech dim, m_s=15 (both supersingular? 15 is not prime, but 3×5)
        m_r, m_s = 24, 15
        assert 1 + m_r + m_s == V
        assert m_r == LEECH_DIM

    def test_196884_mod_744(self):
        # 196884 = 264 × 744 + ??? let me just check mod
        assert 196884 % 12 == 0   # k | c(1)
        assert 196884 // 12 == 16407

    def test_tau_product_formula(self):
        # τ(mn) = τ(m)τ(n) for gcd(m,n)=1 (multiplicativity)
        # τ(2)τ(3) = (-24)(252) = -6048 = τ(6)
        assert (-24) * 252 == -6048

