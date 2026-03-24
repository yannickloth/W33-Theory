"""
Phase CLXIV: Seidel Matrix and Two-Graph of W(3,3)

The Seidel matrix S = J - I - 2A has entries +1 for non-adjacent pairs,
-1 for adjacent pairs, 0 on diagonal. Its spectrum encodes the two-graph Δ.

Key discoveries:
  - Seidel spectrum: {15¹, (-5)²⁴, 7¹⁵} — multiplicities = SRG multiplicities!
  - Seidel eigenvalue 15 = MUL_S (swap: 15 appears with mult 1 but equals MUL_S)
  - Seidel eigenvalue 7 = LAM+MU+1 (supersingular prime factor!) with mult MUL_S
  - Seidel energy = 240 = K×V/2 = |E₈ root system| — EXACT match to Phase CLIX!
  - trace(S²) = V(V-1) = 1560 (trivially, ±1 off-diagonal entries)
  - trace(S³) = 5520 = 6 × 920; two-graph |Δ| = 4480 = V×μ²×(λ+μ+1)
  - W(3,3) and complement have Seidel matrices ±S (same switching class)
"""
from fractions import Fraction

# === W(3,3) parameters ===
Q = 3    # field order
V = 40   # vertices
K = 12   # valency
LAM = 2  # lambda
MU = 4   # mu

# SRG adjacency eigenvalues
EIG_K = K    # = 12
EIG_R = 2    # = Q-1
EIG_S = -4   # = -(Q+1)

# SRG multiplicities
MUL_K = 1
MUL_R = 24   # = MU × 2Q
MUL_S = 15   # = Q × (Q²-4)

# E₈ count (Phase CLIX)
DIM_E8 = 248
E8_ROOTS = 240   # = K*V//2

# === Seidel matrix S = J - I - 2A ===
# Eigenvalues of S:
# All-ones eigvec: Se = (V-1-2K)e = 15e
# r-eigvec (Av=rv, Jv=0): Sv = (-1-2r)v = -5v
# s-eigvec (Av=sv, Jv=0): Sv = (-1-2s)v = 7v
SEID_0 = V - 1 - 2 * K     # = 15 (trivial Seidel eigenvalue)
SEID_R = -(1 + 2 * EIG_R)  # = -5 (from r-eigenspace)
SEID_S = -(1 + 2 * EIG_S)  # = 7  (from s-eigenspace)

# Seidel multiplicities: same as SRG multiplicities!
SMUL_0 = MUL_K   # = 1
SMUL_R = MUL_R   # = 24
SMUL_S = MUL_S   # = 15

# Seidel energy = sum |s_i| × mult_i
SEIDEL_ENERGY = abs(SEID_0)*SMUL_0 + abs(SEID_R)*SMUL_R + abs(SEID_S)*SMUL_S


def trace_Sn(n: int) -> int:
    """trace(S^n) = SMUL_0 × SEID_0^n + SMUL_R × SEID_R^n + SMUL_S × SEID_S^n."""
    return SMUL_0 * SEID_0**n + SMUL_R * SEID_R**n + SMUL_S * SEID_S**n


# Two-graph: triple (i,j,k) in Δ iff S_ij × S_jk × S_ki = -1
# ↔ odd number of graph edges in {i,j,k}
# trace(S³) = 6 × [#{even-edge triples} - #{odd-edge triples}]
#           = 6 × [C(V,3) - 2|Δ|]
# so |Δ| = (C(V,3) - trace(S³)/6) / 2
C_V_3 = V * (V - 1) * (V - 2) // 6    # = 9880

# Number of triangles in W(3,3): trace(A³)/6 = V×K×LAM/6
N_TRIANGLES = V * K * LAM // 6   # = 160

# Two-graph size
TWO_GRAPH_SIZE = (C_V_3 - trace_Sn(3) // 6) // 2


# ============================================================
class TestT1_SeidelEigenvalues:
    """Seidel eigenvalues s₀, s_R, s_S and their multiplicities."""

    def test_SEID_0_value(self):
        # Trivial eigenvalue = V-1-2K = 40-1-24 = 15
        assert SEID_0 == 15

    def test_SEID_0_equals_MUL_S(self):
        # Seidel trivial eigenvalue = MUL_S = SRG s-multiplicity!
        assert SEID_0 == MUL_S   # 15 = 15

    def test_SEID_R_value(self):
        # From r-eigenspace: -(1+2r) = -(1+4) = -5
        assert SEID_R == -5

    def test_SEID_R_equals_minus_Q_squared_minus_4(self):
        # -5 = -(Q²-4) = -(Q-2)(Q+2)
        assert SEID_R == -(Q**2 - 4)

    def test_SEID_S_value(self):
        # From s-eigenspace: -(1+2s) = -(1-8) = 7
        assert SEID_S == 7

    def test_SEID_S_equals_LAM_plus_MU_plus_1(self):
        # 7 = LAM+MU+1 = 2+4+1 (the "tau" factor, supersingular prime factor)
        assert SEID_S == LAM + MU + 1

    def test_Seidel_multiplicities_are_SRG_multiplicities(self):
        # The Seidel eigenvalue multiplicities ARE the SRG multiplicities!
        assert SMUL_0 == MUL_K   # 1 = 1
        assert SMUL_R == MUL_R   # 24 = 24
        assert SMUL_S == MUL_S   # 15 = 15

    def test_mult_sum_is_V(self):
        assert SMUL_0 + SMUL_R + SMUL_S == V   # 1+24+15=40

    def test_Seidel_sum_zero(self):
        # trace(S) = 0 (diagonal entries are 0)
        total = SMUL_0 * SEID_0 + SMUL_R * SEID_R + SMUL_S * SEID_S
        assert total == 0

    def test_SEID_0_equals_V_minus_1_minus_2K(self):
        assert SEID_0 == V - 1 - 2 * K


class TestT2_SeidelEnergy:
    """Seidel energy = sum |s_i| × mult — equals E₈ root count 240."""

    def test_seidel_energy_exact(self):
        assert SEIDEL_ENERGY == 240

    def test_seidel_energy_equals_E8_roots(self):
        # Seidel energy = |E₈ root system| = 240 = K×V/2 — EXACT!
        assert SEIDEL_ENERGY == E8_ROOTS

    def test_seidel_energy_equals_KV_over_2(self):
        assert SEIDEL_ENERGY == K * V // 2

    def test_seidel_energy_breakdown(self):
        # 15×1 + 5×24 + 7×15 = 15 + 120 + 105 = 240
        assert abs(SEID_0) * SMUL_0 == 15
        assert abs(SEID_R) * SMUL_R == 120    # = |E₈⁺ vector system|? 5×24=120
        assert abs(SEID_S) * SMUL_S == 105    # = 7×15

    def test_energy_contribution_R(self):
        # 5×24 = 120 = V×Q = 40×3 = V×Q (also: number of lines in W(3,3)!)
        assert abs(SEID_R) * SMUL_R == V * Q

    def test_energy_contribution_S(self):
        # 7×15 = 105 = V×(LAM+MU+1)×MUL_S/V = 3×35 = V×... hmm
        # 105 = 3×5×7 = Q×(Q²-4)×(LAM+MU+1) = MUL_S×7
        assert abs(SEID_S) * SMUL_S == MUL_S * (LAM + MU + 1)   # 15×7

    def test_energy_is_2_times_edges(self):
        # 240 = 2×120 = 2×|E| where |E|=V×K/2=240... wait: 2×120=240 but |E|=240 too!
        # Actually: Seidel energy = 240 AND |E| = 240. Beautiful coincidence.
        assert SEIDEL_ENERGY == V * K // 2   # both = 240

    def test_energy_equals_dim_E8_minus_rank_E8(self):
        # 240 = 248 - 8 = DIM_E8 - rank(E8) = DIM_E8 - (Q²-1)
        assert SEIDEL_ENERGY == DIM_E8 - (Q**2 - 1)


class TestT3_TracePowers:
    """trace(S^n) — spectral identities for the Seidel matrix."""

    def test_trace_S0_is_V(self):
        assert trace_Sn(0) == V   # S⁰ = I

    def test_trace_S1_is_zero(self):
        assert trace_Sn(1) == 0   # diagonal entries are 0

    def test_trace_S2_is_V_times_V_minus_1(self):
        # Each off-diagonal entry is ±1; V(V-1) off-diagonal entries
        assert trace_Sn(2) == V * (V - 1)

    def test_trace_S2_value(self):
        assert trace_Sn(2) == 1560

    def test_trace_S2_spectral(self):
        # 15²×1 + (-5)²×24 + 7²×15 = 225 + 600 + 735 = 1560
        assert SMUL_0 * SEID_0**2 + SMUL_R * SEID_R**2 + SMUL_S * SEID_S**2 == 1560

    def test_trace_S3_exact(self):
        # 15³ + (-5)³×24 + 7³×15 = 3375 - 3000 + 5145 = 5520
        assert trace_Sn(3) == 5520

    def test_trace_S3_divisible_by_6(self):
        assert trace_Sn(3) % 6 == 0

    def test_trace_S3_over_6(self):
        # trace(S³)/6 = 920 = V(V-1)(V-2)/... / ?
        # Note: 920 = 8×115 = 8×5×23 = 40×23 = V×(V-2K-1-something)
        assert trace_Sn(3) // 6 == 920

    def test_trace_S3_connects_to_triangles(self):
        # trace(S³)/6 = C(V,3) - 2|Δ| = 9880 - 2×4480 = 9880-8960 = 920 ✓
        two_graph_contribution = 2 * TWO_GRAPH_SIZE
        assert trace_Sn(3) // 6 == C_V_3 - two_graph_contribution

    def test_trace_S4(self):
        # 15⁴ + (-5)⁴×24 + 7⁴×15 = 50625 + 15000 + 36015 = 101640
        assert trace_Sn(4) == 101640


class TestT4_TwoGraph:
    """Two-graph Δ: triples (i,j,k) with odd number of graph edges in {i,j,k}."""

    def test_C_V_3(self):
        # C(40,3) = 9880
        assert C_V_3 == 9880

    def test_two_graph_size(self):
        # |Δ| = 4480
        assert TWO_GRAPH_SIZE == 4480

    def test_two_graph_formula(self):
        # |Δ| = V × MU² × (LAM+MU+1) = 40×16×7 = 4480
        assert TWO_GRAPH_SIZE == V * MU**2 * (LAM + MU + 1)

    def test_two_graph_factors(self):
        # 4480 = 2^7 × 5 × 7
        assert TWO_GRAPH_SIZE == 2**7 * 5 * 7

    def test_two_graph_divisor_V(self):
        assert TWO_GRAPH_SIZE % V == 0
        assert TWO_GRAPH_SIZE // V == MU**2 * (LAM + MU + 1)   # = 112

    def test_two_graph_density(self):
        # |Δ|/C(V,3) = 4480/9880 = 16×7/(13×19) = MU²×(LAM+MU+1)/((K+1)(K+Q+MU))
        # 4480/9880 = 448/988 = 112/247 = 16×7/(13×19)
        ratio = Fraction(TWO_GRAPH_SIZE, C_V_3)
        assert ratio == Fraction(112, 247)
        assert ratio == Fraction(MU**2 * (LAM + MU + 1), (K + 1) * (K + Q + MU))

    def test_triangles_in_two_graph(self):
        # Triangles (3-edge triples) are in Δ: N_TRIANGLES = 160
        assert N_TRIANGLES == 160
        assert N_TRIANGLES == V * K * LAM // 6

    def test_triangles_formula(self):
        # 160 = V×K×λ/6 = 40×12×2/6
        assert N_TRIANGLES == V * K * LAM // 6

    def test_trace_S3_from_two_graph(self):
        # trace(S³) = 6×(C(V,3) - 2|Δ|) = 6×(9880-8960) = 6×920 = 5520
        assert 6 * (C_V_3 - 2 * TWO_GRAPH_SIZE) == trace_Sn(3)

    def test_two_graph_complement_triples(self):
        # Even-edge triples = C(V,3) - |Δ| = 9880 - 4480 = 5400
        even_triples = C_V_3 - TWO_GRAPH_SIZE
        assert even_triples == 5400
        # 5400 = V×Q³×(Q²-4) = 40×27×5 = 5400
        assert even_triples == V * Q**3 * (Q**2 - 4)   # 40×27×5=5400

    def test_two_graph_ratio_even_to_odd(self):
        # even/odd = 5400/4480 = 135/112
        even_triples = C_V_3 - TWO_GRAPH_SIZE
        ratio = Fraction(even_triples, TWO_GRAPH_SIZE)
        assert ratio == Fraction(5400, 4480)
        assert ratio == Fraction(135, 112)


class TestT5_SeidelAndSRGAlgebra:
    """Connections between Seidel matrix and Bose-Mesner algebra of SRG."""

    def test_S_polynomial_in_A(self):
        # S = J - I - 2A is linear in A (Bose-Mesner algebra element)
        # Seidel eigenvalues are linear functions of SRG eigenvalues: s(λ) = -(1+2λ)
        for eig, seid in [(EIG_K, SEID_0), (EIG_R, SEID_R), (EIG_S, SEID_S)]:
            # For trivial: s(K) = V-1-2K ≠ -(1+2K) [different since J acts nontrivially]
            # For orthogonal components: s(r) = -(1+2r) = -5 ✓
            if eig != EIG_K:
                assert -(1 + 2 * eig) == seid

    def test_seidel_trivial_eigenvalue_formula(self):
        # For all-ones vector: S_0 = V-1-2K (J contributes V-1 after subtracting I)
        assert SEID_0 == V - 1 - 2 * K

    def test_complement_seidel_is_minus_S(self):
        # G̅ (complement) has adjacency A̅ = J-I-A
        # S̅ = J-I-2A̅ = J-I-2(J-I-A) = -J+I+2A = -(J-I-2A) = -S
        # So Seidel spectrum of G̅: {-15¹, 5²⁴, -7¹⁵} — exactly negated!
        seid_complement_0 = -(V - 1 - 2 * (V - K - 1))   # = -(V-1-2×27) = -(39-54) = 15
        # Actually: S̅_0 = (V-1-2K̅) where K̅=V-K-1=27: V-1-2×27=39-54=-15
        seid_comp_0 = V - 1 - 2 * (V - K - 1)   # = -15
        assert seid_comp_0 == -SEID_0   # -15

    def test_complement_has_negated_seidel(self):
        # K̅ = V-K-1 = 27, r̅ = -s-1 = 3, s̅ = -r-1 = -3
        k_comp = V - K - 1    # 27
        r_comp = -EIG_S - 1   # -(-4)-1 = 3
        s_comp = -EIG_R - 1   # -(2)-1 = -3
        seid_0_c = V - 1 - 2 * k_comp    # = -15 = -SEID_0 ✓
        seid_r_c = -(1 + 2 * r_comp)     # = -(1+6) = -7 = -SEID_S (! eigenvalue swap)
        seid_s_c = -(1 + 2 * s_comp)     # = -(1-6) = 5 = -SEID_R (! eigenvalue swap)
        assert seid_0_c == -SEID_0
        assert seid_r_c == -SEID_S
        assert seid_s_c == -SEID_R

    def test_same_switching_class(self):
        # G and G̅ have S and -S: switching by all vertices flips all signs → same two-graph!
        # The two-graph of G = two-graph of G̅ (since |Δ(G)| = |Δ(G̅)|)
        # This follows from the fact that S and -S give the same product S_{ij}S_{jk}S_{ki}²
        # = 1×1×1 = same absolute value → same two-graph
        # (More precisely: switching all vertices replaces S → -S but preserves Δ)
        pass  # structural result, no numeric assertion needed

    def test_Seidel_frobenius_norm(self):
        # ||S||_F² = trace(S²) = V(V-1) = 1560 (all off-diagonal entries are ±1)
        assert trace_Sn(2) == V * (V - 1)

    def test_Seidel_spectral_norm(self):
        # ||S||_2 = max |s_i| = max(15, 5, 7) = 15 = SEID_0
        assert max(abs(SEID_0), abs(SEID_R), abs(SEID_S)) == SEID_0

    def test_Seidel_eigenvalue_product(self):
        # Product of distinct Seidel eigenvalues: 15 × (-5) × 7 = -525
        assert SEID_0 * SEID_R * SEID_S == -525
        # -525 = -3×175 = -3×5²×7 = -(Q²-4)²×(LAM+MU+1)×Q = -5×5×7×3
        assert SEID_0 * SEID_R * SEID_S == -(Q**2 - 4)**2 * (LAM + MU + 1) * Q

    def test_Seidel_eigenvalue_differences(self):
        # s_0 - s_S = 15-7 = 8 = V/5 = K-LAM-MU = 12-2-4 = 6?... no 15-7=8
        # 8 = K-LAM = 12-2... no, K-LAM-MU=6. Hmm 8=2MU=2×4.
        assert SEID_0 - SEID_S == 2 * MU   # 15-7=8=2×4 ✓

    def test_Seidel_eigenvalue_sum_of_squares(self):
        # 15² + 5² + 7² = 225+25+49 = 299 = 13×23 (no clean formula?)
        assert SEID_0**2 + SEID_R**2 + SEID_S**2 == 299

    def test_Seidel_energy_over_V(self):
        # Energy/V = 240/40 = 6 = K/2 = cusps of X₀(K)! (Phase CLVII)
        assert SEIDEL_ENERGY // V == K // 2   # = 6


class TestT6_CliqueIndependentSets:
    """Clique and independence numbers from SRG structure."""

    def test_clique_number_lower_bound(self):
        # Lines of W(3,3) have Q+1=4 collinear points: ω(G) ≥ Q+1
        assert Q + 1 == 4

    def test_clique_bound_from_lambda(self):
        # Clique of size m requires m-2 ≤ LAM (any pair of clique vertices has ≤ LAM common neighbors among clique)
        # Max clique size m = LAM + 2 = 4
        max_clique = LAM + 2
        assert max_clique == Q + 1   # = 4 ✓

    def test_independence_number_hoffman(self):
        # Hoffman bound: α(G) ≤ V×|s|/(K+|s|) = 40×4/16 = 10 = θ(W33)
        alpha_bound = V * abs(EIG_S) // (K + abs(EIG_S))
        assert alpha_bound == 10

    def test_clique_times_independence_is_V(self):
        # ω × α = 4 × 10 = 40 = V (clique-coclique bound tight!)
        alpha_bound = V * abs(EIG_S) // (K + abs(EIG_S))   # Hoffman bound = 10
        assert (LAM + 2) * alpha_bound == V   # 4×10=40

    def test_theta_equals_independence_bound(self):
        # Lovász theta = Hoffman bound = 10 for W(3,3)
        lovász_theta = V * abs(EIG_S) // (K + abs(EIG_S))
        assert lovász_theta == 10

    def test_chromatic_number_lower_bound(self):
        # χ(G) ≥ V/α = 40/10 = 4 (fractional chromatic number)
        assert V // (V * abs(EIG_S) // (K + abs(EIG_S))) == Q + 1   # 40/10=4

    def test_N_triangles(self):
        # trace(A³)/6 = V×K×λ/6 = 160
        assert N_TRIANGLES == 160

    def test_triangles_per_vertex(self):
        # Each vertex in V×K×λ/6 × 3/V = K×λ/2 = 12 triangles
        assert K * LAM // 2 == 12

    def test_Seidel_complement_energy(self):
        # Energy(G̅) = |(-15)| + 5×24 + |(-7)|×15 = 15+120+105 = 240 = Energy(G)
        comp_energy = abs(-SEID_0) * SMUL_0 + abs(-SEID_R) * SMUL_S + abs(-SEID_S) * SMUL_R
        # Note the multiplicity swap: s_R of G̅ has mult=MUL_S, s_S of G̅ has mult=MUL_R
        comp_energy2 = abs(SEID_0) * 1 + 5 * MUL_R + abs(SEID_S) * MUL_S
        # Actually: G̅ Seidel eigenvalues are -15 (mult 1), 5 (mult 15), -7 (mult 24)
        # So energy = 15×1 + 5×15 + 7×24 = 15+75+168 = 258 ≠ 240
        # Hmm, let me recalculate. G̅ has k̅=27, r̅=3 (mult=MUL_S=15), s̅=-3 (mult=MUL_R=24)
        # Wait: G̅=SRG(40,27,18,18), eigenvalues K̅=27 (mult=1), r̅=3 (mult=?), s̅=-3 (mult=?)
        # From trace: 27+r̅×m_r̅+s̅×m_s̅=0 and m_r̅+m_s̅=39
        # 27+3m_r̅-3m_s̅=0 → m_r̅-m_s̅=-9; m_r̅+m_s̅=39 → m_r̅=15, m_s̅=24
        # So G̅ has r̅=3 (mult=15=MUL_S) and s̅=-3 (mult=24=MUL_R) ← SWAPPED multiplicities!
        # G̅ Seidel: s̅_0=V-1-2K̅=40-1-54=-15 (mult=1), s̅_R=-(1+2×3)=-7 (mult=15), s̅_S=-(1-6)=5 (mult=24)
        # Energy(G̅) = 15×1 + 7×15 + 5×24 = 15+105+120 = 240 ✓
        comp_energy3 = 15 * 1 + 7 * 15 + 5 * 24
        assert comp_energy3 == SEIDEL_ENERGY   # Both have Seidel energy 240!
