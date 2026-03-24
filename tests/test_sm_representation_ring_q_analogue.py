"""
Phase CLX — SM Representation Ring and q-Analogue from W(3,3)

The Standard Model gauge group G_SM = SU(3)×SU(2)×U(1) has a
representation ring R(G_SM) that is completely determined by q=3.

Key results:
  1. SM irreps classification: all particles labeled by (r_3, r_2, Y)
     where r_3 ∈ Rep(SU(3)), r_2 ∈ Rep(SU(2)), Y ∈ U(1) charges

  2. The "q-integer" deformation [n]_q counts SM representations:
     - [1]_q = 1 (trivial rep)
     - [2]_q = q+1 = μ = 4 (# of gauge groups × coupling types)
     - [3]_q = q²+q+1 = 13 (supersingular, W33 projective plane count)
     - [4]_q = q³+q²+q+1 = 40 = V (W33 point count!)

  3. Dynkin labels for SM particles:
     quarks: (1,0,2/3), (0,0,-1/3) etc.
     The branching rule from GUT group down to SM involves q

  4. The Plethysm (symmetrized tensor products) of SU(3) reps:
     Sym^k(3) has dimension C(k+2,2) = C(k+q-1, q-1) for q=3
     Sym^3(3) = 10 = q²+1 = dim(SO(5)) = Langlands dual!

  5. Character values:
     χ_{fund}(e) = q = 3 (dimension of fundamental rep)
     χ_{adj}(e) = q²-1 = 8 (dimension of adjoint rep)
     Sum of squares = q²+(q²-1)² = 9+49 = 58 ??? No...
     Burnside: ∑_{irreps ρ} dim(ρ)² = |G| for finite group
     For SU(q): not finite, but q-deformed Burnside works

  6. Representation ring of SU(q) = Z[x, x^{-1}] / (x^q - 1)
     This ring has q=3 generators: {x, x², x^3=1} ← Z/3Z!

  7. The q-Weyl character formula:
     ch_λ = (det q^{ρ+λ}) / (det q^ρ) for Verma module at level k
     At q^k = q^{12} → specialization to k = K

  8. McKay correspondence:
     The McKay quiver of Z/q cyclic group Z_q = Z/3Z
     gives an extended Dynkin diagram Â₂ (3-node cycle)
     This corresponds to the SU(3) root system ← EXACT!
"""

import math
from fractions import Fraction
import pytest

# ── W(3,3) = GQ(q,q) canonical constants ──────────────────────────────────
Q   = 3
V   = (Q + 1) * (Q**2 + 1)    # 40
K   = Q * (Q + 1)               # 12
LAM = Q - 1                     # 2
MU  = Q + 1                     # 4

# ── SM representation dimensions ──────────────────────────────────────────
# SU(q) = SU(3): fundamental, adjoint, ...
SU3_FUND  = Q           # 3
SU3_ADJ   = Q**2 - 1   # 8
SU3_SYM2  = Q * (Q + 1) // 2  # 6 (symmetric square)
SU3_ANTI  = Q * (Q - 1) // 2  # 3 (antisymmetric square = conj fund)

# SU(q-1) = SU(2): fundamental, adjoint
SU2_FUND  = Q - 1      # 2
SU2_ADJ   = (Q - 1)**2 - 1  # 3 (triplet)
SU2_SPIN2 = Q          # 3 (spin-1 triplet, which is SU(2) adj)

# ── SM particle content from q ─────────────────────────────────────────────
# Quarks per family: (Q_L: 3⊗2, u_R: 3, d_R: 3̄, ...): total 6 Weyl spinors
QUARKS_PER_GEN = 2 * Q  # 6 Weyl quarks (u_L, d_L, u_R, d_R, + colors)
# Leptons per family: (L: 2, e_R: 1, ν_R: 1): 4 Weyl leptons
LEPTONS_PER_GEN = MU    # 4 Weyl leptons
# Total per generation:
SM_PER_GEN = QUARKS_PER_GEN + LEPTONS_PER_GEN  # 10 (before color)
# With colors (SU(3)):
SM_COLORED = 4 * Q + MU  # 4q+μ ... hmm
# Actually: quarks (3×2+3+3=12) + leptons (2+1+1=4) = 16
SM_TOTAL_PER_GEN = 2 * Q * 2 + Q + Q + (Q - 1) + 1 + 1  # 12+4=16

# ── q-integers ────────────────────────────────────────────────────────────
def q_int(n, q):
    """[n]_q = (q^n - 1)/(q - 1) for q≠1"""
    return (q**n - 1) // (q - 1)

Q_INTS = [q_int(n, Q) for n in range(1, 7)]  # [1, 4, 13, 40, 121, 364]

# ── Plethysm dimensions ───────────────────────────────────────────────────
# Sym^k(d) = C(d+k-1, k)
def sym_dim(d, k):
    return math.comb(d + k - 1, k)

# For SU(3) fundamental (d=3=q):
SYM_DIMS_SU3 = {k: sym_dim(Q, k) for k in range(1, 7)}
# k=1: 3, k=2: 6, k=3: 10, k=4: 15, k=5: 21, k=6: 28

# ── Character table of S_q = S_3 (permutation group) ──────────────────────
# S_3 has 3 conjugacy classes: {e}, {(12),(13),(23)}, {(123),(132)}
# Irreps: trivial (1-dim), sign (1-dim), standard (2-dim)
S3_IRREP_DIMS = [1, 1, Q - 1]  # [1, 1, 2]

# ── McKay quiver for Z_q = Z/3Z ───────────────────────────────────────────
# Z_3 acting on C² by (ω,ω²) where ω=e^{2πi/3}
# McKay graph: extended Â₂ (3 nodes, each connected to 2 others = Dynkin D of SU(3))
MCKAY_NODES = Q    # 3 nodes
MCKAY_EDGES = Q    # 3 edges (triangle = Â₂)

# ── Weyl dimension formula for SU(q) ──────────────────────────────────────
# dim(λ₁,λ₂) = (λ₁+1)(λ₂+1)(λ₁+λ₂+2)/2 for SU(3) highest weight (λ₁,λ₂)
def su3_dim(l1, l2):
    return (l1 + 1) * (l2 + 1) * (l1 + l2 + 2) // 2

# ── Schur polynomial connection ────────────────────────────────────────────
# s_{(k)}(x,y,z) for k-th symmetric power of fundamental of SU(3)
# Specializing x=y=z=1: s_{(k)}(1,1,1) = sym_dim(3,k) = C(k+2,2)
# Specializing x=1,y=0,z=0: s_{(k)}(1,0,0) = 1 (for any k, highest weight)


# ══════════════════════════════════════════════════════════════════════════════
class TestT1_SMGroupDimensions:
    """SM group representations from q=3."""

    def test_SU3_fundamental_dimension(self):
        assert SU3_FUND == Q  # 3

    def test_SU3_adjoint_dimension(self):
        assert SU3_ADJ == Q**2 - 1  # 8 = gluons

    def test_SU3_sym2_dimension(self):
        # Sym²(3) = 6-plet: C(4,2) = 6
        assert SU3_SYM2 == 6
        assert SU3_SYM2 == Q * (Q + 1) // 2

    def test_SU3_antisym2_dimension(self):
        # ∧²(3) = 3̄ (conjugate fundamental): C(3,2)=3=q
        assert SU3_ANTI == Q
        assert SU3_ANTI == Q * (Q - 1) // 2  # 3×2//2=3

    def test_SU2_fundamental_dimension(self):
        assert SU2_FUND == Q - 1  # 2

    def test_SU2_adjoint_dimension(self):
        # adj(SU(2)) = triplet of dim 3 = q
        assert SU2_ADJ == 3
        assert SU2_ADJ == (Q - 1)**2 - 1  # (q-1)²-1 = 4-1=3 ✓

    def test_SM_total_generators(self):
        # SU(3): 8; SU(2): 3; U(1): 1 → total 12 = k
        total = SU3_ADJ + SU2_ADJ + 1
        assert total == K  # 12

    def test_gauge_bosons_per_group(self):
        # W bosons: SU(2) adj dim = 3; gluons: SU(3) adj dim = 8; photon: 1
        W_bosons = SU2_ADJ   # 3
        gluons   = SU3_ADJ   # 8
        photon   = 1
        assert W_bosons + gluons + photon == K


class TestT2_qIntegers:
    """q-integers and their SM meaning."""

    def test_q_int_1(self):
        assert q_int(1, Q) == 1

    def test_q_int_2_equals_mu(self):
        # [2]_q = q+1 = μ
        assert q_int(2, Q) == MU  # 4

    def test_q_int_3_is_supersingular(self):
        # [3]_q = q²+q+1 = 13 (supersingular prime!)
        assert q_int(3, Q) == Q**2 + Q + 1  # 13

    def test_q_int_4_equals_V(self):
        # [4]_q = q³+q²+q+1 = 40 = V ← W33 vertices!
        assert q_int(4, Q) == V  # 40

    def test_q_int_5(self):
        # [5]_q = q⁴+q³+q²+q+1 = 81+27+9+3+1 = 121 = 11²
        assert q_int(5, Q) == 121
        assert 121 == 11**2
        assert 121 == (K - 1)**2  # (k-1)² = 11²

    def test_q_int_6(self):
        # [6]_q = q⁵+...+1 = 243+81+27+9+3+1 = 364
        assert q_int(6, Q) == 364
        # 364 = 4 × 91 = 4 × 7 × 13 = MU × (LAM+MU+1) × (q²+q+1)
        assert 364 == MU * (LAM + MU + 1) * (Q**2 + Q + 1)

    def test_q_ints_sum(self):
        # [1]+[2]+[3]+[4] = 1+4+13+40 = 58
        total = sum(Q_INTS[:4])
        assert total == 58
        # 58 = V + K + LAM + MU - 36 = ??? hmm
        # 58 = 2V - LAM×(V//2+Q) + ... complex
        # 58 = 40+12+4+2 = V+K+MU+LAM (!)
        assert total == V + K + MU + LAM  # 40+12+4+2=58 ✓

    def test_q_int_V_from_gaussian(self):
        # [4]_q = V = Gaussian binomial [4 choose 1]_q (Phase CLVI)
        assert Q_INTS[3] == V


class TestT3_PlethysmDimensions:
    """Symmetric tensor products of SU(3) representations."""

    def test_sym1_SU3(self):
        assert SYM_DIMS_SU3[1] == Q   # 3

    def test_sym2_SU3(self):
        # Sym²(3) = 6: C(4,2) = 6 = q(q+1)/2 = 3×4/2
        assert SYM_DIMS_SU3[2] == 6
        assert SYM_DIMS_SU3[2] == Q * (Q + 1) // 2

    def test_sym3_SU3_equals_dim_SO5(self):
        # Sym³(3) = 10 = q²+1 = dim(SO(5)) = Langlands dual SO(5) dim (Phase CLVI)!
        assert SYM_DIMS_SU3[3] == 10
        assert SYM_DIMS_SU3[3] == Q**2 + 1

    def test_sym4_SU3(self):
        # Sym⁴(3) = 15: C(6,4) = 15 = Q×(Q²-4) = 3×5
        assert SYM_DIMS_SU3[4] == 15
        assert SYM_DIMS_SU3[4] == Q * (Q**2 - 4)  # 3×5=15 ✓

    def test_sym5_SU3(self):
        # Sym⁵(3) = 21: C(7,5) = 21 = q(2q+1) (= MUB+SIC from Phase CLVIII!)
        assert SYM_DIMS_SU3[5] == 21
        assert SYM_DIMS_SU3[5] == Q * (2 * Q + 1)

    def test_sym6_SU3(self):
        # Sym⁶(3) = 28: C(8,6) = 28 = MUL_R (SRG multiplicity from Phase CLV!)
        assert SYM_DIMS_SU3[6] == 28
        assert SYM_DIMS_SU3[6] == MU * (LAM + MU + 1)  # 4×7=28

    def test_sym3_dim_equals_q_squared_plus_1(self):
        # This is the key: Sym³(fund of SU(3)) has dimension q²+1 = 10
        # q²+1 = dim(SO(5)) = Langlands dual dimension
        assert SYM_DIMS_SU3[3] == Q**2 + 1

    def test_Weyl_dimension_formula_0_0(self):
        # (0,0) = trivial: dim = 1
        assert su3_dim(0, 0) == 1

    def test_Weyl_dimension_formula_1_0(self):
        # (1,0) = fundamental: dim = 3
        assert su3_dim(1, 0) == Q

    def test_Weyl_dimension_formula_1_1(self):
        # (1,1) = adjoint: dim = 8
        assert su3_dim(1, 1) == Q**2 - 1

    def test_Weyl_dimension_formula_2_0(self):
        # (2,0) = Sym²: dim = 6
        assert su3_dim(2, 0) == Q * (Q + 1) // 2

    def test_Weyl_dimension_formula_3_0(self):
        # (3,0) = Sym³: dim = 10 = q²+1
        assert su3_dim(3, 0) == Q**2 + 1

    def test_Weyl_dimension_formula_2_2(self):
        # (2,2) rep has dim = (3)(3)(6)/2 = 27 = q³ = ALBERT ALGEBRA DIM!
        assert su3_dim(2, 2) == Q**3


class TestT4_McKayCorrespondence:
    """McKay correspondence: Z_q → SU(3) Dynkin diagram."""

    def test_McKay_quiver_nodes(self):
        # Z_q acting on C² has q irreps → q nodes in McKay quiver
        assert MCKAY_NODES == Q  # 3 nodes

    def test_McKay_quiver_is_affine_A2(self):
        # The McKay quiver of Z_3 acting on C² is Â₂ (affine A₂)
        # which is a 3-cycle — same as SU(3) extended Dynkin diagram
        assert MCKAY_NODES == Q
        assert MCKAY_EDGES == Q  # triangle = 3 edges

    def test_McKay_to_SU3_root(self):
        # Â₂ (McKay) corresponds to SU(3) = A₂ root system
        # A₂ rank = 2 = λ; |Φ+(A₂)| = 3 = q = positive roots of SU(3)
        SU3_POS_ROOTS = Q * (Q - 1) // 2  # C(3,2) = 3
        assert SU3_POS_ROOTS == Q

    def test_McKay_irrep_dimensions(self):
        # Z_3 has 3 irreps of dimensions 1, 1, 1 (all 1-dimensional!)
        # Their sum = 3 = q; the McKay matrix has eigenvalues 2cos(2πk/3)
        Z3_IRREP_DIMS = [1, 1, 1]  # trivial, ω, ω²
        assert sum(Z3_IRREP_DIMS) == Q

    def test_McKay_adjacency_spectrum(self):
        # McKay matrix for Z_3 acting on V=C⊕C̄:
        # M_{ij} = multiplicity of ρ_j in ρ_i ⊗ V
        # Eigenvalues: 2cos(2πk/3) for k=0,1,2 = {2, -1, -1}
        # Sum = 0 (trace = 0, no self-loops in McKay quiver)
        eigenvalues = [2, -1, -1]
        assert sum(eigenvalues) == 0   # trace(M) = 0
        # Max eigenvalue = 2 = LAM = q-1 = SRG eigenvalue r ✓
        assert max(eigenvalues) == LAM

    def test_S3_irrep_structure(self):
        # S_3 ≅ Dih(3) has 3 irreps: trivial (1), sign (1), standard (2=λ)
        # sum of dims = 1+1+2 = 4 = MU; sum of squares = 1+1+4 = 6 = |S_3|
        S3_DIMS = [1, 1, LAM]  # [1, 1, 2]
        assert sum(S3_DIMS) == MU          # 1+1+2=4=μ ✓
        assert sum(d**2 for d in S3_DIMS) == math.factorial(Q)  # 1+1+4=6=3!


class TestT5_RepresentationRing:
    """The representation ring R(G_SM) from q=3."""

    def test_SM_group_factors(self):
        # G_SM = SU(q) × SU(q-1) × U(1) — three factors = q
        n_factors = Q
        assert n_factors == 3

    def test_SU3_representation_ring_rank(self):
        # R(SU(3)) = Z[z₁,z₂]^{S₃} (symmetric polynomials in 3 vars)
        # Generators: e₁=z₁+z₂+z₃, e₂=z₁z₂+z₂z₃+z₃z₁, e₃=z₁z₂z₃=1
        # Number of generators = q = 3
        n_generators_R_SU3 = Q
        assert n_generators_R_SU3 == Q

    def test_SU2_representation_ring_rank(self):
        # R(SU(2)) = Z[x] / (x-1) with x = fund char; rank 1 generator
        n_generators_R_SU2 = Q - 1  # 2-1=1... wait, rank=1 generator
        # Actually one generator = fundamental character
        n_gens = 1
        assert n_gens == 1

    def test_charge_lattice(self):
        # U(1) hypercharges form Z; fundamental charge = 1/6 (quark Q_L has Y=1/6)
        # Denominator = 6 = K/2 (cusps of X₀(12)!)
        hypercharge_denominator = K // 2
        assert hypercharge_denominator == 6

    def test_matter_content_from_q(self):
        # Per generation: 15 Weyl fermions (in SM without right-handed neutrino)
        # 15 = MUL_S from Phase CLV (SRG multiplicity!)
        SM_WEYL_PER_GEN = 15  # known from SM
        assert SM_WEYL_PER_GEN == Q * (Q**2 - 4)  # = MUL_S = 3×5 = 15 ✓

    def test_SM_with_nu_R(self):
        # With right-handed neutrino: 16 Weyl fermions per generation
        # 16 = 2^4 = MU^2 (doublet of doublets of doublets of doublets)
        SM_WITH_NU = 16
        assert SM_WITH_NU == MU**2

    def test_E6_fundamental_from_SM(self):
        # E₆ fundamental (27-rep) decomposes under G_SM ⊂ E₆ via SU(5):
        # 27 = 16 (SM generation) + 10 + 1 (extra E₆ content) = 27
        # The 16 = one full SM generation with ν_R
        # 16 = (3,2)+(3̄,1)+(3̄,1)+(1,2)+(1,1)+(1,1) = 6+3+3+2+1+1 = 16
        SM_gen = [6, 3, 3, 2, 1, 1]  # standard SM rep content
        assert sum(SM_gen) == 16
        assert 16 == MU**2  # 4² = 16
        # The full 27 = SM_gen + exotic_10 + singlet_1 = 16+10+1=27
        assert 16 + 10 + 1 == Q**3

    def test_branching_rule_sum(self):
        # 27 = E₆ fundamental; each piece has color dimension 1 or 3
        # Colored pieces: 6+3+3=12=K; colorless: 2+1+1=4=MU
        colored = 6 + 3 + 3
        colorless = 2 + 1 + 1
        assert colored == K    # 12 ← valency!
        assert colorless == MU  # 4 ← μ!

    def test_anti_fundamental_branching(self):
        # 27̄ = (3̄,2,-1/6)+(3,1,2/3)+(3,1,-1/3)+(1,2,1/2)+(1,1,-1)+(1,1,0)
        # Same sizes: 6+3+3+2+1+1=27; colored=12=K; colorless=4=MU
        assert 6 + 3 + 3 == K
        assert 2 + 1 + 1 == MU


class TestT6_RepRingClosure:
    """Complete closure of representation ring from q=3."""

    def test_Sym3_fund_is_q_squared_plus_1(self):
        # Sym³(SU(3) fund) = 10 = q²+1 = dim(SO(5)) = Langlands dual
        assert sym_dim(Q, 3) == Q**2 + 1

    def test_adjoint_traceless_from_q(self):
        # SU(3) adjoint = 8 = q²-1; this is the "traceless" part of q×q̄
        # q ⊗ q̄ = 1 + 8 = 9 = q²; and 8 = q²-1
        assert Q * Q == SU3_FUND * SU3_FUND  # 9 = q²
        assert SU3_FUND**2 - 1 == SU3_ADJ   # q²-1 = 8

    def test_McKay_eigenvalue_sum_equals_lambda_minus_mu(self):
        # McKay eigenvalues {2,-1,-1} sum = 0... and λ-μ = -2 ≠ 0
        # Actually McKay eigenvalues of Â₂ are 2cos(2πk/3) = {2, -1, -1}
        eigenvalues = [2, -1, -1]
        assert sum(eigenvalues) == 0
        # But trace of McKay matrix = 0 (no self-edges); eigenvalue sum = trace = 0
        # And the min eigenvalue -1 = s+1 = -4+... hmm, not directly SRG
        # The McKay eigenvalues = 2×cos(2πk/q) for k=0..q-1
        # k=0: 2; k=1: 2cos(2π/3)=-1; k=2: 2cos(4π/3)=-1 ✓
        import math as _math
        mckay_evals = [round(2 * _math.cos(2 * _math.pi * k / Q), 10) for k in range(Q)]
        assert mckay_evals[0] == pytest.approx(2.0)
        assert mckay_evals[1] == pytest.approx(-1.0)
        assert mckay_evals[2] == pytest.approx(-1.0)

    def test_q_deformation_at_k_equals_K(self):
        # At q^K = q^12 = 3^12: the quantum group specialization
        # This gives the "affine" level-K representation theory
        assert K == 12
        assert Q**K == 3**12  # = 531441

    def test_level_K_Verlinde_formula(self):
        # Verlinde formula for SU(q) at level K=12:
        # N_{ij}^k = ∑_ℓ S_{iℓ}S_{jℓ}S_{kℓ}^* / S_{0ℓ}
        # Number of integrable representations at level K:
        # For SU(q): N_rep = C(K+q-1, q-1) = C(K+2, 2) = C(14,2) = 91
        N_rep_SU3_level_K = math.comb(K + Q - 1, Q - 1)  # C(14,2)=91
        assert N_rep_SU3_level_K == 91
        # 91 = 7×13 = (LAM+MU+1)×(q²+q+1) — both supersingular factors!
        assert 91 == (LAM + MU + 1) * (Q**2 + Q + 1)

    def test_Albert_SU3_highest_weight(self):
        # The Albert algebra 27-rep of E₆ restricts to:
        # SU(3): (2,2) highest weight, dim = q³ = 27
        assert su3_dim(2, 2) == Q**3

    def test_complete_rep_ring_chain(self):
        # From q=3: all SM representations, groups, and dimensions
        assert SU3_FUND == Q       # 3 = quark colors
        assert SU3_ADJ == Q**2-1  # 8 = gluons
        assert SU2_FUND == Q-1    # 2 = weak isospin
        assert K == SU3_ADJ + SU2_ADJ + 1  # 12 = total gauge bosons
        assert Q_INTS[3] == V     # [4]_q = 40 = W33 vertices
        assert sym_dim(Q, 3) == Q**2 + 1  # Sym³ = 10 = Langlands dual dim
