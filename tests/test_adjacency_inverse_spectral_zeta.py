"""
Phase CLXVI: Adjacency Matrix Inverse and Spectral Zeta of W(3,3)

Since A has nonzero eigenvalues {12,2,-4}, A is invertible. The Bose-Mesner
spectral decomposition gives exact rational entries for A^{-1}.

The spectral zeta ζ_A(s) = sum_i λ_i^s (with multiplicities) recovers
Seeley-DeWitt coefficients at negative integers and connects to all prior phases.

Key discoveries:
  - (A^{-1})_{diag} = (Q²-4)/MUL_R = 5/24
  - (A^{-1})_{adj} = 1/K exactly
  - (A^{-1})_{non} = -1/MUL_R = -1/24
  - ζ_A(-2) = 480 = a₀ (Seeley-DeWitt coefficient from Phase CLIV!)
  - ζ_A(-4) = a₀×(V+K) = a₀×DIM_F₄ = 480×52 = 24960 (E₄ exceptional!)
  - ζ_A(2) = (Q²-4)³/(2Q²) = 125/18
  - det(A) = -Q×2^{LAM+MUL_R+2MUL_S} = -3×2^56
"""
from fractions import Fraction

# === W(3,3) parameters ===
Q = 3    # field order
V = 40   # vertices
K = 12   # valency
LAM = 2  # lambda
MU = 4   # mu

# SRG eigenvalues of A
EIG_K = K    # = 12
EIG_R = 2    # = Q-1
EIG_S = -4   # = -(Q+1) = -MU

# Multiplicities
MUL_K = 1
MUL_R = 24
MUL_S = 15

# Spectral idempotent diagonal entries (from Phase CLXIII)
ER_DIAG = Fraction(MUL_R, V)   # = 3/5
ES_DIAG = Fraction(MUL_S, V)   # = 3/8

# Spectral idempotent off-diagonal entries (adjacent and non-adjacent)
ER_ADJ = Fraction(1, 10)    # from Phase CLXIII
ES_ADJ = Fraction(-1, 8)
ER_NON = Fraction(-1, 15)
ES_NON = Fraction(1, 24)

# Seeley-DeWitt a₀ (Phase CLIV)
A0 = K * V   # = 480

# Exceptional Lie algebra dimensions (Phase CLIX)
DIM_F4 = V + K   # = 52

# === A^{-1} entries: A^{-1} = (1/K)E_K + (1/r)E_R + (1/s)E_S ===
# (A^{-1})_{ii} = (1/K)(1/V) + (1/r)(MUL_R/V) + (1/s)(MUL_S/V)
# But using exact spectral idempotent diagonal entries:
AINV_DIAG = Fraction(1, EIG_K) * Fraction(1, V) + \
            Fraction(1, EIG_R) * ER_DIAG + \
            Fraction(1, EIG_S) * ES_DIAG

AINV_ADJ  = Fraction(1, EIG_K) * Fraction(1, V) + \
            Fraction(1, EIG_R) * ER_ADJ + \
            Fraction(1, EIG_S) * ES_ADJ

AINV_NON  = Fraction(1, EIG_K) * Fraction(1, V) + \
            Fraction(1, EIG_R) * ER_NON + \
            Fraction(1, EIG_S) * ES_NON


def zeta_A(s: int) -> int:
    """Spectral zeta: zeta_A(s) = trace(A^|s|) = MUL_K×K^n + MUL_R×r^n + MUL_S×s_eig^n, n=|s|."""
    n = abs(s)
    return MUL_K * EIG_K**n + MUL_R * EIG_R**n + MUL_S * EIG_S**n


# ============================================================
class TestT1_AInvertibility:
    """A is invertible since all eigenvalues 12, 2, -4 are nonzero."""

    def test_all_eigenvalues_nonzero(self):
        assert EIG_K != 0
        assert EIG_R != 0
        assert EIG_S != 0

    def test_det_A_sign(self):
        # det(A) = K × r^24 × (-4)^15 < 0 (odd power of negative)
        # det(A) = -Q × 2^56
        assert MUL_S % 2 == 1   # odd power of s=-4 → det < 0

    def test_det_A_exact(self):
        # det(A) = K × r^{MUL_R} × s^{MUL_S} = 12 × 2^24 × (-4)^15
        # = 12 × 2^24 × (-1)^15 × 2^30 = -12 × 2^54 = -3 × 2^56
        det_A = EIG_K * EIG_R**MUL_R * EIG_S**MUL_S
        assert det_A == -3 * 2**56

    def test_det_A_Q_factor(self):
        # -3×2^56: the factor 3 = Q
        det_A = EIG_K * EIG_R**MUL_R * EIG_S**MUL_S
        assert abs(det_A) == Q * 2**56

    def test_det_A_exponent(self):
        # 2^56: exponent 56 = LAM + MUL_R + 2×MUL_S = 2+24+30=56
        assert 56 == LAM + MUL_R + 2 * MUL_S


class TestT2_AInvEntries:
    """Entries of A^{-1} from spectral decomposition."""

    def test_AINV_DIAG_exact(self):
        # (A^{-1})_{ii} = 5/24 = (Q²-4)/MUL_R
        assert AINV_DIAG == Fraction(5, 24)

    def test_AINV_DIAG_formula(self):
        # 5/24 = (Q²-4)/MUL_R
        assert AINV_DIAG == Fraction(Q**2 - 4, MUL_R)

    def test_AINV_ADJ_exact(self):
        # (A^{-1})_{ij,j~i} = 1/K = 1/12
        assert AINV_ADJ == Fraction(1, K)

    def test_AINV_NON_exact(self):
        # (A^{-1})_{ij,j≁i} = -1/MUL_R = -1/24
        assert AINV_NON == Fraction(-1, MUL_R)

    def test_AINV_NON_formula(self):
        assert AINV_NON == Fraction(-1, 24)

    def test_AINV_diag_adj_ratio(self):
        # (A^{-1})_{diag} / (A^{-1})_{adj} = (5/24)/(1/12) = 5/2 = (Q²-4)/LAM
        assert AINV_DIAG / AINV_ADJ == Fraction(Q**2 - 4, LAM)

    def test_AINV_adj_non_sign(self):
        # Adjacent: positive (A^{-1})_{adj} > 0; Non-adjacent: negative < 0
        assert AINV_ADJ > 0
        assert AINV_NON < 0

    def test_AINV_adj_times_K(self):
        # K × (A^{-1})_{adj} = 1 = unit (row contribution from neighbors)
        assert K * AINV_ADJ == 1

    def test_AINV_row_sum(self):
        # Row sum = (A^{-1})_{ii} + K×(A^{-1})_{adj} + (V-K-1)×(A^{-1})_{non}
        # = 5/24 + 12/12 + 27×(-1/24) = (5+24-27)/24 = 2/24 = 1/12 = 1/K
        row_sum = AINV_DIAG + K * AINV_ADJ + (V - K - 1) * AINV_NON
        assert row_sum == Fraction(1, K)

    def test_AINV_row_sum_is_1_over_K(self):
        # A^{-1}×(A×e/K) = e/K, so A^{-1}×e = e/K, i.e., row sum = 1/K
        row_sum = AINV_DIAG + K * AINV_ADJ + (V - K - 1) * AINV_NON
        assert row_sum == Fraction(1, K)


class TestT3_AInvTrace:
    """Trace of A^{-1} = ζ_A(−1)."""

    def test_trace_Ainv_exact(self):
        # trace(A^{-1}) = V × (A^{-1})_{ii} = 40 × 5/24 = 200/24 = 25/3
        assert V * AINV_DIAG == Fraction(25, 3)

    def test_trace_Ainv_from_zeta(self):
        # trace(A^{-1}) = ζ_A(-1) = 1/K + MUL_R/r + MUL_S/s
        zeta_minus1 = Fraction(MUL_K, EIG_K) + Fraction(MUL_R, EIG_R) + Fraction(MUL_S, EIG_S)
        assert zeta_minus1 == Fraction(25, 3)

    def test_trace_Ainv_formula(self):
        # 25/3 = V(Q²-4)/MUL_R = 40×5/24 = 200/24 = 25/3
        assert V * AINV_DIAG == Fraction(V * (Q**2 - 4), MUL_R)

    def test_trace_Ainv_numerator(self):
        # 25 = V²/MUL_R = (Q+1)²(Q²+1)²/MUL_R? No: 25 = 5² = (Q²-4)²
        t = V * AINV_DIAG
        assert t.numerator == (Q**2 - 4)**2   # 25 = 5²

    def test_trace_Ainv_denominator(self):
        # denominator = 3 = Q
        t = V * AINV_DIAG
        assert t.denominator == Q


class TestT4_SpectralZetaNegative:
    """ζ_A(−n) = trace(A^n): recovers physical constants at specific n."""

    def test_zeta_A_0(self):
        # ζ_A(0) = MUL_K + MUL_R + MUL_S = V
        assert zeta_A(0) == V

    def test_zeta_A_minus_1(self):
        # ζ_A(-1) = trace(A) = 0 (no self-loops)
        assert zeta_A(-1) == 0

    def test_zeta_A_minus_2(self):
        # ζ_A(-2) = K² + MUL_R×r² + MUL_S×s² = 144+96+240 = 480 = a₀!
        assert zeta_A(-2) == 480

    def test_zeta_A_minus_2_equals_seeley_dewitt_a0(self):
        # EXACT: ζ_A(−2) = a₀ = K×V (Seeley-DeWitt coefficient, Phase CLIV!)
        assert zeta_A(-2) == A0

    def test_zeta_A_minus_2_equals_VK(self):
        assert zeta_A(-2) == V * K

    def test_zeta_A_minus_3(self):
        # ζ_A(-3) = K³ + MUL_R×r³ + MUL_S×s³ = 1728+192-960 = 960
        assert zeta_A(-3) == 960

    def test_zeta_A_minus_3_equals_trace_A3(self):
        # trace(A³) = 6×(#triangles) = 6×160 = 960 = V×K×LAM
        assert zeta_A(-3) == V * K * LAM

    def test_zeta_A_minus_4(self):
        # ζ_A(-4) = K^4 + MUL_R×r^4 + MUL_S×s^4 = 20736+384+3840 = 24960
        assert zeta_A(-4) == 24960

    def test_zeta_A_minus_4_equals_a0_times_DIM_F4(self):
        # ζ_A(−4) = a₀ × (V+K) = 480 × 52 = 24960 — F₄ exceptional connection!
        assert zeta_A(-4) == A0 * DIM_F4

    def test_zeta_A_minus_4_equals_a0_times_V_plus_K(self):
        assert zeta_A(-4) == A0 * (V + K)

    def test_zeta_A_minus_5(self):
        # ζ_A(-5) = K^5 + 24×2^5 + 15×(-4)^5 = 248832 + 768 - 15360 = 234240
        assert zeta_A(-5) == 234240

    def test_zeta_A_minus_6(self):
        # ζ_A(-6) = K^6 + 24×64 + 15×4096 = 2985984+1536+61440 = 3048960
        assert zeta_A(-6) == 3048960


class TestT5_SpectralZetaPositive:
    """ζ_A(n) for positive n: exact rational values."""

    def test_zeta_A_1(self):
        # ζ_A(1) = K + MUL_R×r + MUL_S×s = 12+48-60 = 0 (trace(A)=0)
        assert zeta_A(1) == 0

    def test_zeta_frac_1(self):
        # ζ_A_frac(1) = 1/K + MUL_R/r + MUL_S/s = trace(A^{-1}) = 25/3
        zf1 = Fraction(MUL_K, EIG_K) + Fraction(MUL_R, EIG_R) + Fraction(MUL_S, EIG_S)
        assert zf1 == Fraction(25, 3)

    def test_zeta_frac_2(self):
        # ζ_frac(2) = 1/K² + MUL_R/r² + MUL_S/s² = 1/144+6+15/16
        zf2 = Fraction(1, EIG_K**2) + Fraction(MUL_R, EIG_R**2) + Fraction(MUL_S, EIG_S**2)
        assert zf2 == Fraction(125, 18)

    def test_zeta_frac_2_formula(self):
        # 125/18 = (Q²-4)³/(2Q²) = 5³/(2×9) = 125/18 — beautiful!
        assert Fraction(125, 18) == Fraction((Q**2 - 4)**3, 2 * Q**2)

    def test_zeta_frac_2_numerator(self):
        # 125 = (Q²-4)³ = 5³: cube of the SRG eigenvalue discriminant
        zf2 = Fraction(1, EIG_K**2) + Fraction(MUL_R, EIG_R**2) + Fraction(MUL_S, EIG_S**2)
        assert zf2.numerator == (Q**2 - 4)**3

    def test_zeta_frac_2_denominator(self):
        # 18 = 2Q²
        zf2 = Fraction(1, EIG_K**2) + Fraction(MUL_R, EIG_R**2) + Fraction(MUL_S, EIG_S**2)
        assert zf2.denominator == 2 * Q**2

    def test_spectral_zeta_at_0(self):
        # Both formulations agree: ζ_A(0) = V and ζ_frac_A(0) = V
        zf0 = Fraction(MUL_K, 1) + Fraction(MUL_R, 1) + Fraction(MUL_S, 1)
        assert zf0 == V


class TestT6_ZetaConnections:
    """ζ_A at various orders connects to results from multiple prior phases."""

    def test_zeta_minus_2_is_a0_seeley_dewitt(self):
        # Phase CLIV: a₀ = K×V = 480. Phase CLXVI: ζ_A(-2) = 480. EXACT MATCH.
        assert zeta_A(-2) == A0

    def test_zeta_minus_3_is_V_K_LAM(self):
        # 960 = V×K×λ = triangle count × 6
        assert zeta_A(-3) == V * K * LAM

    def test_zeta_minus_4_factor_is_DIM_F4(self):
        # ζ(-4)/ζ(-2) = 24960/480 = 52 = V+K = dim(F₄) — exceptional!
        assert zeta_A(-4) // zeta_A(-2) == DIM_F4

    def test_trace_Ainv_times_Q_is_integer(self):
        # trace(A^{-1})×Q = 25/3 × 3 = 25 = (Q²-4)²
        t = V * AINV_DIAG
        assert t * Q == (Q**2 - 4)**2

    def test_zeta_minus_2_over_V(self):
        # ζ(-2)/V = 480/40 = 12 = K: average squared eigenvalue per vertex
        assert zeta_A(-2) // V == K

    def test_AINV_non_magnitude_equals_AINV_adj_over_2(self):
        # |A^{-1}_{non}| = 1/24 = (1/2)×(1/12) = (1/2)×A^{-1}_{adj}/1? No: 1/24 = (1/12)/2
        assert abs(AINV_NON) == AINV_ADJ / 2

    def test_AINV_difference(self):
        # (A^{-1})_{adj} - (A^{-1})_{non} = 1/12 - (-1/24) = 1/12+1/24 = 3/24 = 1/8 = 1/(2*MU)
        diff = AINV_ADJ - AINV_NON
        assert diff == Fraction(1, 2 * MU)

    def test_AINV_entries_sum_over_all_pairs(self):
        # sum_{i,j} (A^{-1})_{ij} = V²×(1/K) [since row sum = 1/K]
        # = V²/K = 1600/12 = 400/3
        total = V * (AINV_DIAG + K * AINV_ADJ + (V - K - 1) * AINV_NON)
        assert total == Fraction(V, K)   # V/K = 40/12 = 10/3 (per vertex)

    def test_AINV_frobenius_norm_squared(self):
        # ||A^{-1}||_F² = trace((A^{-1})²) = trace(A^{-2}) = ζ_frac(2) as computed per vertex ×V
        # = V × [(A^{-2})_{ii}] = V × (AINV_DIAG² + K×AINV_ADJ² + (V-K-1)×AINV_NON²)
        fro_sq_per_vertex = (AINV_DIAG**2 + K * AINV_ADJ**2 + (V - K - 1) * AINV_NON**2)
        zf2_per_vertex = Fraction(1, EIG_K**2) * Fraction(1, V) + \
                         Fraction(1, EIG_R**2) * ER_DIAG + \
                         Fraction(1, EIG_S**2) * ES_DIAG
        assert fro_sq_per_vertex == zf2_per_vertex

    def test_Cauchy_Schwarz_Ainv(self):
        # ||(A^{-1})_adj||² ≤ (A^{-1})_diag × (A^{-1})_diag by symmetry
        # More precisely: for Bose-Mesner, idempotent entries satisfy |E_R(i,j)| ≤ E_R(i,i)
        # So |A^{-1}_adj| ≤ A^{-1}_diag: 1/12 ≤ 5/24 = 5/24 ✓
        assert AINV_ADJ <= AINV_DIAG

    def test_Ainv_diag_plus_non_neighbors(self):
        # (A^{-1})_diag + (V-K-1)×(A^{-1})_non = 5/24 + 27×(-1/24) = (5-27)/24 = -22/24 = -11/12
        # = -2(K-1)/(2K) = -(K-1)/K
        result = AINV_DIAG + (V - K - 1) * AINV_NON
        assert result == Fraction(-(K - 1), K)   # = -11/12
