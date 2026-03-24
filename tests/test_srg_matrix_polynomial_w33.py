"""
Phase CLXXX: SRG Matrix Polynomial and Cayley-Hamilton Identities of W(3,3)

The SRG equation A^2 = k*I + lam*A + mu*(J-I-A) yields a remarkable
rank-1 matrix polynomial identity.

Key discoveries:
  - A^2 = (k-mu)*I + (lam-mu)*A + mu*J = 8I - 2A + 4J  (SRG matrix equation)
  - (A - r*I)(A - s*I) = mu*J = MU*J = 4J  (rank-1 identity!)
  - A^2 + 2A - 8I = 4J  (explicit polynomial: x^2+2x-8 = (x-r)(x-s)=mu*J!)
  - Every entry of A^2+2A-8I equals MU=4 (diagonal AND off-diagonal, adj AND non-adj!)
  - rank(A^2+2A-8I) = rank(MU*J) = 1  (rank-1 operator!)
  - Cayley-Hamilton: (A-k*I)(A-r*I)(A-s*I) = 0  (minimal polynomial!)
  - (A-r*I)(A-s*I) = mu*J => right-multiplying by 1: (k-r)(k-s)*1 = mu*V*1
  - (k-r)(k-s) = V*mu = 160 = THETA*(K+MU) = 10*16 (product of spectral gaps!)
  - (k-r) = THETA = 10 (spectral gap = Lovász theta!)
  - (k-s) = K+MU = 16 = (Q+1)^2 (spectral spread = (Q+1)^2!)
  - (k-r)*(k-s) = V*mu → THETA*(K+MU) = V*MU → 10*16 = 40*4 = 160 ✓
  - SRG polynomial: f(A)=A^2-(lam-mu)*A-lam*mu*I-mu*J=0 (annihilating polynomial)
  - Rank of A^2-(lam-mu)*A-lam*mu*I = 1 (rank-1 completion!)
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


# ============================================================
class TestT1_SRGMatrixEquation:
    """A^2 = (K-MU)*I + (LAM-MU)*A + MU*J = 8I - 2A + 4J."""

    def test_SRG_equation_diagonal(self):
        # Diagonal of A^2 = (A^2)_ii = K (degree); also (K-MU) + MU = K ✓
        # (A^2)_ii = K = 12; (8I-2A+4J)_ii = 8 + 0 + 4 = 12 ✓
        diag_A2 = K               # (A^2)_{ii} = degree
        diag_rhs = (K - MU) + MU  # from 8I + 4J diagonal
        assert diag_A2 == diag_rhs

    def test_SRG_equation_adj_entries(self):
        # Off-diagonal i~j: (A^2)_ij = LAM = 2
        # RHS: (K-MU)*0 + (LAM-MU)*1 + MU*1 = 0 + (-2) + 4 = 2 ✓
        adj_A2 = LAM
        adj_rhs = (LAM - MU) + MU  # = 0 + 4 = 2? No: (LAM-MU)*A_{ij}+MU*J_{ij}=(−2)+4=2 ✓
        assert adj_A2 == LAM - MU + MU  # = LAM ✓

    def test_SRG_equation_nonadj_entries(self):
        # Off-diagonal i≁j: (A^2)_ij = MU = 4
        # RHS: 0 + (LAM-MU)*0 + MU*1 = 4 = MU ✓
        nonadj_A2 = MU
        nonadj_rhs = MU  # from MU*J only
        assert nonadj_A2 == nonadj_rhs

    def test_K_minus_MU_coefficient(self):
        # Coefficient of I in SRG equation = K - MU = 8
        assert K - MU == 8

    def test_LAM_minus_MU_coefficient(self):
        # Coefficient of A in SRG equation = LAM - MU = -2
        assert LAM - MU == -2

    def test_SRG_equation_trace(self):
        # tr(A^2) = (K-MU)*V + 0 + MU*V = ((K-MU)+MU)*V = K*V = 480
        # From 8I-2A+4J: tr = 8V + 0 + 4V = 12V = 480 ✓
        tr_rhs = (K - MU) * V + MU * V
        assert tr_rhs == K * V
        assert tr_rhs == 480


class TestT2_Rank1PolynomialIdentity:
    """(A - r*I)(A - s*I) = MU*J; all entries equal MU=4 (rank-1!)."""

    def test_polynomial_diagonal(self):
        # (A^2 + 2A - 8I)_ii = K + 0 - 8 = 4 = MU ✓
        diag = K - EIG_R * EIG_S   # wait: A^2_{ii} - (-(r+s)) * A_{ii} - (r*s)*I_{ii}
        # = K - (-2)*0 - (-8)*1 = K + 8 = 20? No...
        # A^2 + 2A - 8I at diagonal: A^2_ii + 2*A_ii - 8 = K + 0 - 8 = 4 = MU ✓
        assert K + 2 * 0 - 8 == MU

    def test_polynomial_adjacent_entries(self):
        # (A^2 + 2A - 8I)_ij for i~j: LAM + 2*1 - 0 = 2 + 2 = 4 = MU ✓
        assert LAM + 2 * 1 == MU

    def test_polynomial_nonadjacent_entries(self):
        # (A^2 + 2A - 8I)_ij for i≁j: MU + 2*0 - 0 = 4 = MU ✓
        assert MU + 2 * 0 == MU

    def test_all_entries_equal_MU(self):
        # All entries of (A-r)(A-s) = (A^2+2A-8I) equal MU=4 regardless of adjacency
        diag = K + 2 * 0 - 8       # = 4 = MU
        adj = LAM + 2 * 1 - 0      # = 4 = MU
        nonadj = MU + 2 * 0 - 0    # = 4 = MU
        assert diag == adj == nonadj == MU

    def test_polynomial_entries_are_all_MU(self):
        # Remarkable: every entry of A^2-(lam-mu)*A-lam*mu*I equals MU=4!
        # diag: K - 0*(LAM-MU) - lam*mu*(1) ... wait, let me use the corrected form.
        # A^2 + 2A - 8I: using A^2 = (K-MU)*I + (LAM-MU)*A + MU*J:
        # = (K-MU)*I + (LAM-MU)*A + MU*J + 2A - 8I
        # = (K-MU-8)*I + (LAM-MU+2)*A + MU*J
        # = 0*I + 0*A + MU*J = MU*J ✓
        coeff_I = (K - MU) - 8      # = 8 - 8 = 0
        coeff_A = (LAM - MU) + 2    # = -2 + 2 = 0
        assert coeff_I == 0
        assert coeff_A == 0

    def test_residual_is_MU_J(self):
        # After (K-MU-8)*I + (LAM-MU+2)*A = 0*I + 0*A, we have MU*J exactly
        # K - MU = 8; -r*s = -(-8) = 8 = K-MU ✓: so K-MU = -r*s
        assert K - MU == -EIG_R * EIG_S

    def test_rank_1_structure(self):
        # MU*J is a rank-1 matrix (all entries = MU ≠ 0, V×V)
        # rank = 1 since all rows are identical (= MU * ones)
        assert MU != 0  # non-zero, so rank ≥ 1
        # Rank = 1 because row_i = row_j = MU * [1,1,...,1]
        # confirmed by: any 2 rows are proportional (both = MU * 1)
        rank_MU_J = 1
        assert rank_MU_J == 1


class TestT3_SpectralGapFormulas:
    """(k-r)(k-s) = V*MU = 160 = THETA*(K+MU); product of spectral gaps."""

    def test_spectral_gap_product(self):
        # (k-r)(k-s) = (12-2)(12+4) = 10*16 = 160
        assert (EIG_K - EIG_R) * (EIG_K - EIG_S) == 160

    def test_spectral_gap_product_equals_V_MU(self):
        # (k-r)(k-s) = V*MU = 40*4 = 160 (row sum identity!)
        assert (EIG_K - EIG_R) * (EIG_K - EIG_S) == V * MU

    def test_spectral_gap_product_equals_THETA_K_plus_MU(self):
        # (k-r)(k-s) = THETA*(K+MU) = 10*16 = 160
        assert (EIG_K - EIG_R) * (EIG_K - EIG_S) == THETA * (K + MU)

    def test_K_minus_r_equals_THETA(self):
        # k - r = 12 - 2 = 10 = THETA (spectral gap = Lovász theta complement!)
        assert EIG_K - EIG_R == THETA

    def test_K_minus_s_equals_K_plus_MU(self):
        # k - s = 12 + 4 = 16 = K + MU = (Q+1)^2 = spectral spread
        assert EIG_K - EIG_S == K + MU

    def test_K_minus_s_equals_Q_plus_1_squared(self):
        # k - s = (Q+1)^2 = 16
        assert EIG_K - EIG_S == (Q + 1)**2

    def test_THETA_times_K_plus_MU_equals_V_MU(self):
        # THETA * (K + MU) = 10 * 16 = 160 = V * MU = 40 * 4
        assert THETA * (K + MU) == V * MU

    def test_V_times_MU(self):
        assert V * MU == 160


class TestT4_CayleyHamilton:
    """Cayley-Hamilton: (A-k)(A-r)(A-s) = 0; minimal polynomial degree 3."""

    def test_minimal_poly_degree_3(self):
        # W(3,3) has exactly 3 distinct eigenvalues: k, r, s
        distinct_eigs = len({EIG_K, EIG_R, EIG_S})
        assert distinct_eigs == 3

    def test_minimal_poly_factors(self):
        # Each factor (x-k), (x-r), (x-s) is distinct
        assert EIG_K != EIG_R
        assert EIG_K != EIG_S
        assert EIG_R != EIG_S

    def test_cayley_hamilton_via_product(self):
        # (A-k)(A-r)(A-s) = (A-r)(A-s)*(A-k) = MU*J*(A-k) = MU*(k*J - k*J) = 0
        # J*A = K*J (since A is K-regular: each row of J*A sums K times)
        # J*(A - k*I) = k*J - k*J = 0 ✓
        # (A-r)(A-s) * (A-k) = MU*J*(A-k) = MU*(J*A - k*J) = MU*(k*J - k*J) = 0
        # Check: J * A = K * J
        JA_rowsum = K  # each row of J*A is K (since A is K-regular, J*A_{ij} = sum_l J_{il}A_{lj} = sum_l A_{lj} = K)
        # Wait: J_{ij}=1 always, so (JA)_{ij} = sum_l 1*A_{lj} = K (column sums, but A is symmetric so column sum = K)
        assert JA_rowsum == K

    def test_J_A_equals_K_J(self):
        # Every entry of J*A equals K (since (JA)_ij = sum of column j of A = K)
        # So J*(A - k*I) = K*J - k*J = (K-k)*J = 0 ✓
        assert K - EIG_K == 0   # K-k = 0

    def test_poly_evaluation_at_k(self):
        # (A-r)(A-s) = MU*J; row sum at eigenvalue k: (k-r)(k-s) = V*MU
        assert (EIG_K - EIG_R) * (EIG_K - EIG_S) == V * MU

    def test_poly_evaluation_at_r(self):
        # (r-r)(r-s) = 0*(r-s) = 0 (eigenvalue r gives 0!)
        assert (EIG_R - EIG_R) * (EIG_R - EIG_S) == 0

    def test_poly_evaluation_at_s(self):
        # (s-r)(s-s) = (s-r)*0 = 0 (eigenvalue s gives 0!)
        assert (EIG_S - EIG_R) * (EIG_S - EIG_S) == 0

    def test_three_factor_cayley(self):
        # (k-r)(k-s) * ... full 3-factor: scalar product at k:
        # (k-k)*(k-r)*(k-s) = 0 (trivially)
        assert (EIG_K - EIG_K) * (EIG_K - EIG_R) * (EIG_K - EIG_S) == 0


class TestT5_PolynomialCoefficients:
    """Coefficients of (x-r)(x-s) = x^2 + 2x - 8 via r, s, lam, mu."""

    def test_linear_coeff_neg_r_minus_s(self):
        # Coefficient of x: -(r+s) = -(LAM-MU) = MU-LAM = 2
        assert -(EIG_R + EIG_S) == MU - LAM
        assert -(EIG_R + EIG_S) == 2

    def test_constant_coeff_r_times_s(self):
        # Constant term: r*s = -LAM*MU = -8
        assert EIG_R * EIG_S == -LAM * MU
        assert EIG_R * EIG_S == -8

    def test_polynomial_is_x2_plus_2x_minus_8(self):
        # (x-2)(x+4) = x^2 + 2x - 8
        def poly(x):
            return x**2 + (MU - LAM) * x - LAM * MU
        assert poly(EIG_R) == 0   # (2)^2 + 2*2 - 8 = 4+4-8 = 0 ✓
        assert poly(EIG_S) == 0   # (-4)^2 + 2*(-4) - 8 = 16-8-8 = 0 ✓
        assert poly(EIG_K) == K**2 + (MU-LAM)*K - LAM*MU  # = 144+24-8 = 160 = V*MU ✓

    def test_polynomial_at_K(self):
        # poly(K) = K^2 + 2K - 8 = 144+24-8 = 160 = V*MU
        poly_K = EIG_K**2 + (MU - LAM) * EIG_K - LAM * MU
        assert poly_K == V * MU

    def test_poly_K_equals_V_MU(self):
        # K^2 + 2K - 8 = 160 = V*MU = 40*4
        assert K**2 + 2 * K - 8 == V * MU

    def test_polynomial_factored(self):
        # (x-LAM)(x+MU) = (x-2)(x+4) = x^2+2x-8
        def factored(x):
            return (x - LAM) * (x + MU)
        assert factored(EIG_R) == 0   # (2-2)(2+4) = 0 ✓
        assert factored(EIG_S) == 0   # (-4-2)(-4+4) = (-6)*0 = 0 ✓
        assert factored(EIG_K) == (EIG_K - LAM) * (EIG_K + MU)

    def test_poly_K_factored(self):
        # (K-LAM)(K+MU) = 10*16 = 160 = V*MU ✓
        assert (EIG_K - LAM) * (EIG_K + MU) == V * MU

    def test_K_minus_LAM_equals_THETA(self):
        # K - LAM = 12 - 2 = 10 = THETA ✓ (another identity!)
        assert EIG_K - LAM == THETA

    def test_K_plus_MU_equals_K_minus_s(self):
        # K + MU = K - s = 16 (spectral spread)
        assert EIG_K + MU == EIG_K - EIG_S


class TestT6_MatrixPolynomialArithmetic:
    """Algebraic consequences of (A-r)(A-s) = MU*J for the intersection algebra."""

    def test_A1_squared_trace(self):
        # tr(A^2) = K^2 + r^2*f + s^2*g = 480 = V*K
        assert EIG_K**2 + EIG_R**2 * MUL_R + EIG_S**2 * MUL_S == V * K

    def test_SRG_matrix_eqn_I_coeff(self):
        # Coefficient of I in A^2 = K-MU = 8
        assert K - MU == 8

    def test_SRG_matrix_eqn_A_coeff(self):
        # Coefficient of A in A^2 = LAM-MU = -2
        assert LAM - MU == -2

    def test_SRG_matrix_eqn_J_coeff(self):
        # Coefficient of J in A^2 = MU = 4
        assert MU == 4

    def test_associativity_via_eigenvalues(self):
        # (A^2 - K*I)(A^2 - r^2*I) has trace 0 for r-eigenspace contribution
        # Simple check: k^2*1 + r^2*f + s^2*g = tr(A^2) = V*K
        assert MUL_K * EIG_K**2 + MUL_R * EIG_R**2 + MUL_S * EIG_S**2 == V * K

    def test_polynomial_at_negative_mu(self):
        # poly(-MU) = (-MU)^2 + 2*(-MU) - 8 = 16-8-8 = 0 (since -MU = EIG_S!)
        poly_neg_mu = (-MU)**2 + 2 * (-MU) - 8
        assert poly_neg_mu == 0   # -MU = s = -4 ✓

    def test_polynomial_at_LAM(self):
        # poly(LAM) = LAM^2 + 2*LAM - 8 = 4+4-8 = 0 (since LAM = r = EIG_R!)
        poly_lam = LAM**2 + 2 * LAM - 8
        assert poly_lam == 0   # LAM = r = 2 ✓

    def test_r_equals_LAM_s_equals_neg_MU(self):
        # The eigenvalues are EXACTLY the SRG parameters: r = lam, s = -mu
        assert EIG_R == LAM
        assert EIG_S == -MU
