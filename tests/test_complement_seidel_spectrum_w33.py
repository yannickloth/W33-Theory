"""
Phase CCIV -- W(3,3) Complement Graph and Seidel Two-Graph Spectrum
==================================================================
W(3,3) = SRG(40, 12, 2, 4) with Q = 3.

The complement of W(3,3) is SRG(40, Q^3, Q^2*LAM, Q^2*LAM) = SRG(40,27,18,18).
The complement has symmetric eigenvalues +-Q = +-3, and its lambda equals its mu
(a special conference-matrix structure).  The Seidel matrix S = J-I-2A has
eigenvalues {15^1, (-5)^24, 7^15}, where the largest eigenvalue equals FANO_ORDER = 7.
The identity 7 = 2Q+1 = FANO_ORDER holds iff Q(Q-3) = 0 -- yet another Q=3 uniqueness.

All arithmetic is exact integers.

Six test groups (36 tests total):
  T1  Complement SRG parameters  -- SRG(40,27,18,18); KC=Q^3, LAMC=MUC=Q^2*LAM
  T2  Complement eigenvalues     -- +-Q symmetric; multiplicities swap with W33
  T3  Seidel matrix eigenvalues  -- {15^1, (-5)^24, 7^15}; 7 = FANO_ORDER
  T4  Seidel uniqueness Q=3      -- 7 = 2Q+1 = FANO_ORDER iff Q(Q-3)=0
  T5  Seidel spectral moments    -- Tr(S^k) for k=0,1,2
  T6  Cross-structure bridges    -- KC*LAMC=2Q^5; LAMC=2Q^2 [Q=3 only]
"""

import pytest

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
Q = 3

# W(3,3) = SRG(40, 12, 2, 4)
V = 40;  K = 12;  LAM = 2;  MU = 4
THETA = 10;  EIG_R = 2;  EIG_S = -4;  MUL_R = 24;  MUL_S = 15

# Heawood / Fano / Perkel
N_H = 14;  FANO_ORDER = 7;  K_P = 6

# Tomotope orders
P_ORDER = 96;  H_ORDER = 192

# Complement SRG(40, 27, 18, 18)
KC   = 27   # = Q^3 = V - K - 1
LAMC = 18   # = Q^2 * LAM = Q^2 * (Q-1)
MUC  = 18   # = LAMC (lambda = mu for complement!)
EIG_RC =  3  # = Q  (larger non-trivial complement eigenvalue)
EIG_SC = -3  # = -Q (smaller: -EIG_RC, symmetric)
MUL_RC = MUL_S  # multiplicities SWAP vs W33
MUL_SC = MUL_R

# Seidel matrix S = J - I - 2A, eigenvalues {SEID_T^1, SEID_R^MUL_R, SEID_S^MUL_S}
SEID_T = 15   # V - 1 - 2K   (trivial eigenvalue = MUL_S)
SEID_R = -5   # -1 - 2*EIG_R (from r-channel)
SEID_S =  7   # -1 - 2*EIG_S (from s-channel = FANO_ORDER)


# ------------------------------------------------------------------
# T1 -- Complement SRG parameters
# ------------------------------------------------------------------
class TestT1ComplementSRGParameters:

    def test_complement_k_equals_q_cubed(self):
        """KC = V-K-1 = 27 = Q^3: complement degree is the cube of Q."""
        assert V - K - 1 == KC
        assert KC == Q**3

    def test_complement_lambda_formula(self):
        """LAMC = V-2K+MU-2 = 18 = Q^2*(Q-1) = Q^2*LAM."""
        assert V - 2*K + MU - 2 == LAMC
        assert LAMC == Q**2 * LAM
        assert LAMC == 18

    def test_complement_mu_formula(self):
        """MUC = V-2K+LAM = 18 = same as LAMC [complement lambda = complement mu]."""
        assert V - 2*K + LAM == MUC
        assert MUC == 18

    def test_complement_lambda_equals_mu(self):
        """LAMC = MUC = 18: the complement SRG has equal non-trivial parameters."""
        assert LAMC == MUC

    def test_complement_params_tuple(self):
        """Complement is SRG(40, 27, 18, 18) = SRG(V, Q^3, Q^2*LAM, Q^2*LAM)."""
        assert (V, KC, LAMC, MUC) == (40, 27, 18, 18)

    def test_complement_srg_feasibility(self):
        """KC*(KC-LAMC-1) = MUC*(V-KC-1): SRG feasibility for complement."""
        assert KC * (KC - LAMC - 1) == MUC * (V - KC - 1)
        # 27*8 = 18*12 = 216 ✓
        assert KC * (KC - LAMC - 1) == 216


# ------------------------------------------------------------------
# T2 -- Complement eigenvalues
# ------------------------------------------------------------------
class TestT2ComplementEigenvalues:

    def test_complement_eig_r_equals_q(self):
        """EIG_RC = -EIG_S - 1 = Q = 3: complement larger eigenvalue = Q."""
        assert -EIG_S - 1 == EIG_RC
        assert EIG_RC == Q

    def test_complement_eig_s_equals_minus_q(self):
        """EIG_SC = -EIG_R - 1 = -Q = -3: complement smaller eigenvalue = -Q."""
        assert -EIG_R - 1 == EIG_SC
        assert EIG_SC == -Q

    def test_complement_eigenvalues_symmetric(self):
        """EIG_RC = -EIG_SC: complement eigenvalues are symmetric about zero."""
        assert EIG_RC == -EIG_SC
        assert EIG_RC + EIG_SC == 0

    def test_complement_eigenvalues_pm_q(self):
        """Complement non-trivial eigenvalues are +-Q = +-3 [general for GQ(q,q) complement]."""
        assert EIG_RC ==  Q
        assert EIG_SC == -Q

    def test_complement_multiplicities_swapped(self):
        """Complement multiplicities {1, MUL_S, MUL_R}: MUL_R and MUL_S swap vs W33."""
        assert MUL_RC == MUL_S   # = 15 for the Q=3 eigenvalue
        assert MUL_SC == MUL_R   # = 24 for the -Q=-3 eigenvalue

    def test_complement_multiplicity_sum(self):
        """1 + MUL_RC + MUL_SC = 1 + MUL_S + MUL_R = V = 40."""
        assert 1 + MUL_RC + MUL_SC == V

    def test_complement_eigenvalue_sum(self):
        """KC + EIG_RC*MUL_RC + EIG_SC*MUL_SC = 27 + 3*15 + (-3)*24 = 27+45-72 = 0."""
        eig_sum = KC * 1 + EIG_RC * MUL_RC + EIG_SC * MUL_SC
        assert eig_sum == 0


# ------------------------------------------------------------------
# T3 -- Seidel matrix eigenvalues
# ------------------------------------------------------------------
class TestT3SeidelMatrixEigenvalues:

    def test_seidel_trivial_eigenvalue(self):
        """SEID_T = V-1-2K = 40-1-24 = 15: Seidel trivial eigenvalue."""
        assert V - 1 - 2*K == SEID_T
        assert SEID_T == 15

    def test_seidel_r_eigenvalue(self):
        """SEID_R = -1 - 2*EIG_R = -1-4 = -5: Seidel eigenvalue from r-channel."""
        assert -1 - 2*EIG_R == SEID_R
        assert SEID_R == -5

    def test_seidel_s_eigenvalue(self):
        """SEID_S = -1 - 2*EIG_S = -1+8 = 7 = FANO_ORDER: Seidel eigenvalue from s-channel."""
        assert -1 - 2*EIG_S == SEID_S
        assert SEID_S == FANO_ORDER

    def test_seidel_trivial_equals_mul_s(self):
        """SEID_T = 15 = MUL_S: the trivial Seidel eigenvalue equals the smaller multiplicity."""
        assert SEID_T == MUL_S

    def test_seidel_spectrum_tuple(self):
        """Seidel spectrum {15^1, (-5)^24, 7^15} with multiplicities (1, MUL_R, MUL_S)."""
        assert (SEID_T, SEID_R, SEID_S) == (15, -5, 7)

    def test_seidel_eigenvalue_sum(self):
        """SEID_T + SEID_R*MUL_R + SEID_S*MUL_S = 15 - 120 + 105 = 0."""
        eig_sum = SEID_T * 1 + SEID_R * MUL_R + SEID_S * MUL_S
        assert eig_sum == 0


# ------------------------------------------------------------------
# T4 -- Seidel uniqueness at Q=3
# ------------------------------------------------------------------
class TestT4SeidelUniquenessQ3:

    def test_seidel_s_equals_fano_order(self):
        """SEID_S = 7 = FANO_ORDER: Seidel largest eigenvalue = Fano plane order."""
        assert SEID_S == FANO_ORDER
        assert SEID_S == 7

    def test_seidel_s_equals_2q_plus_one(self):
        """SEID_S = 2Q+1 = 7: simple linear formula in Q."""
        assert SEID_S == 2*Q + 1

    def test_2q_plus_one_equals_q_squared_minus_q_plus_one(self):
        """2Q+1 = Q^2-Q+1 = FANO_ORDER iff Q(Q-3) = 0 [Q=3 uniqueness]."""
        assert 2*Q + 1 == Q**2 - Q + 1   # = 7 = FANO_ORDER at Q=3
        assert Q * (Q - 3) == 0          # selector polynomial vanishes at Q=3

    def test_q3_uniqueness_fails_other_q(self):
        """For q=2: 2*2+1=5 != q^2-q+1=3; for q=4: 2*4+1=9 != q^2-q+1=13."""
        assert 2*2 + 1 != 2**2 - 2 + 1   # 5 != 3
        assert 2*4 + 1 != 4**2 - 4 + 1   # 9 != 13

    def test_seidel_r_equals_minus_q_minus_lam(self):
        """SEID_R = -(Q+2) = -(Q+LAM) = -5: r-channel Seidel = -(Q+LAM)."""
        assert SEID_R == -(Q + LAM)
        assert SEID_R == -5

    def test_seidel_product(self):
        """SEID_R * SEID_S = -5*7 = -35 = -(5*7) = -(5*FANO_ORDER) = -(K_P-1)*FANO_ORDER."""
        assert SEID_R * SEID_S == -35
        assert abs(SEID_R * SEID_S) == (K_P - 1) * FANO_ORDER


# ------------------------------------------------------------------
# T5 -- Seidel spectral moments
# ------------------------------------------------------------------
class TestT5SeidelSpectralMoments:

    def test_tr_s0_equals_v(self):
        """Tr(S^0) = V = 40: dimension of matrix."""
        tr0 = 1*1 + MUL_R + MUL_S
        assert tr0 == V

    def test_tr_s1_equals_zero(self):
        """Tr(S) = SEID_T + SEID_R*MUL_R + SEID_S*MUL_S = 15-120+105 = 0."""
        tr1 = SEID_T * 1 + SEID_R * MUL_R + SEID_S * MUL_S
        assert tr1 == 0

    def test_tr_s2_equals_v_v_minus_one(self):
        """Tr(S^2) = V*(V-1) = 40*39 = 1560: S has 0 diagonal, +-1 off-diagonal."""
        tr2 = SEID_T**2 * 1 + SEID_R**2 * MUL_R + SEID_S**2 * MUL_S
        assert tr2 == V * (V - 1)
        assert tr2 == 1560

    def test_seidel_frobenius_norm_squared(self):
        """||S||_F^2 = Tr(S^2) = V*(V-1) = 1560 [all off-diagonal entries +-1]."""
        assert SEID_T**2 + SEID_R**2 * MUL_R + SEID_S**2 * MUL_S == V * (V - 1)

    def test_seidel_s2_contrib_decomposition(self):
        """SEID_T^2 + SEID_R^2*MUL_R + SEID_S^2*MUL_S = 225 + 600 + 735 = 1560."""
        c_t = SEID_T**2 * 1   # = 225
        c_r = SEID_R**2 * MUL_R  # = 25*24 = 600
        c_s = SEID_S**2 * MUL_S  # = 49*15 = 735
        assert c_t == 225
        assert c_r == 600
        assert c_s == 735
        assert c_t + c_r + c_s == 1560


# ------------------------------------------------------------------
# T6 -- Cross-structure bridges
# ------------------------------------------------------------------
class TestT6CrossStructureBridges:

    def test_kc_lamc_equals_2_q5(self):
        """KC*LAMC = 27*18 = 486 = 2*Q^5 = 2*243 [Q=3 uniqueness]."""
        assert KC * LAMC == 2 * Q**5
        assert KC * LAMC == 486

    def test_lamc_equals_2_q_squared(self):
        """LAMC = 2*Q^2 = 18 iff LAM = 2 iff Q=3 [Q^2*(Q-1) = 2Q^2 iff Q=3]."""
        assert LAMC == 2 * Q**2
        # General: LAMC = Q^2 * LAM = Q^2 * (Q-1); equals 2*Q^2 only if LAM=2 i.e. Q=3
        assert Q**2 * LAM == LAMC   # general for GQ(q,q)
        assert LAM == 2              # Q=3 specific

    def test_complement_k_minus_lamc_equals_q_squared(self):
        """KC - LAMC = 27-18 = 9 = Q^2: complement degree minus lambda = Q^2."""
        assert KC - LAMC == Q**2
        assert KC - LAMC == 9

    def test_seidel_triv_times_fano(self):
        """SEID_T * FANO_ORDER = 15*7 = 105 = MUL_S * SEID_S = 15*7 ✓."""
        assert SEID_T * FANO_ORDER == MUL_S * SEID_S

    def test_complement_r_squared_plus_s_squared_equals_lamc(self):
        """EIG_RC^2 + EIG_SC^2 = Q^2 + Q^2 = 2Q^2 = 18 = LAMC = MUC."""
        assert EIG_RC**2 + EIG_SC**2 == LAMC
        assert EIG_RC**2 + EIG_SC**2 == MUC

    def test_seidel_r_s_product_abs(self):
        """|SEID_R * SEID_S| = 5*7 = 35 = (K_P-1)*FANO_ORDER = 5*7 = 35."""
        assert abs(SEID_R * SEID_S) == (K_P - 1) * FANO_ORDER
        assert abs(SEID_R * SEID_S) == 35
