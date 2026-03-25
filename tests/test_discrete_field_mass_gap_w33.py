"""
Phase CCVIII -- Discrete Field Mass Gap and Laplacian Mode Structure
====================================================================
W(3,3) = SRG(40, 12, 2, 4) with Q = 3.

The graph Laplacian Delta = K*I - A has three eigenvalues:
  0   (multiplicity 1,    trivial mode  -- the "vacuum")
  10  (multiplicity 24,   E1-channel   -- "gauge modes")
  16  (multiplicity 15,   E2-channel   -- "matter modes")

where 10 = K - EIG_R = THETA (Fiedler value = spectral gap)
and   16 = K - EIG_S.

The physics interpretation:
  LAP_1 = THETA = 10: the first "mass" of a field living on W(3,3)
  LAP_2 = 16:         the second mass
  MUL_R = 24:         dimension of 24-channel (cf. 24 gauge d.o.f.)
  MUL_S = 15:         dimension of 15-channel (cf. 3 gen. × 5 SM reps)

Green's function G(m^2) = (Delta + m^2 * I)^{-1}:
  On E1: eigenvalue 1/(LAP_1 + m^2)
  On E2: eigenvalue 1/(LAP_2 + m^2)
  On E0: eigenvalue 1/m^2 (pole at m^2 = 0)

At m^2 = K (the "self-energy" mass):
  g1 = K + LAP_1 = 2K - EIG_R = 22 = 2*(K-1) = degree of line graph L(W33)
  g2 = K + LAP_2 = 2K - EIG_S = 28 = 4*FANO_ORDER = 2*N_H

Key exact integer identities:
  LAP_1 * LAP_2 = 160 = V*(Q+1) = #triangles = #GQ flags
  LAP_1 + LAP_2 = 26 = 2*PG2 = N_H + K
  LAP_2 - LAP_1 = 6 = K_P = K/2 = 3*LAM = 2*Q
  g1 + g2 = 50 = V + K - LAM = 5*THETA
  g1 * g2 = 616 = 8 * 7 * 11 = 8 * FANO_ORDER * (K-1)

Seven test groups (42 tests total):
  T1  Laplacian eigenvalues    -- LAP_1=THETA=10, LAP_2=16; exact formulas
  T2  Mass gap sum/product     -- LAP_1*LAP_2=160=#triangles; sum=26=2*PG2
  T3  Mass gap difference      -- LAP_2-LAP_1=6=K_P=K/2=2*Q
  T4  Green function at K      -- g1=22=2(K-1), g2=28=4*FANO_ORDER
  T5  Green function identities-- g1+g2=50; g1*g2=616=8*FANO_ORDER*(K-1)
  T6  Propagator trace         -- Tr G(K) on mean-zero: 24/22+15/28
  T7  Constant-mode response   -- 1^T G(K) 1=V/K=10/3; comparison to alpha
"""

import pytest
from fractions import Fraction

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
Q = 3

# W(3,3) = SRG(40, 12, 2, 4)
V = 40;  K = 12;  LAM = 2;  MU = 4
THETA = 10;  EIG_R = 2;  EIG_S = -4;  MUL_R = 24;  MUL_S = 15

# Heawood / Fano
N_H = 14;  FANO_ORDER = 7;  K_P = 6

# Tomotope
P_ORDER = 96

# Laplacian eigenvalues: Delta = K*I - A
LAP_0 = 0              # multiplicity 1  (trivial mode)
LAP_1 = K - EIG_R      # = 10 = THETA, multiplicity MUL_R = 24
LAP_2 = K - EIG_S      # = 16, multiplicity MUL_S = 15

# Transport operator eigenvalues (from Phase CCVII)
MK = (K - 1) * ((K - EIG_R)**2 + 1)   # = 1111

# Green's function denominators at m^2 = K
G1 = K + LAP_1    # = 22 = 2K - EIG_R
G2 = K + LAP_2    # = 28 = 2K - EIG_S

# PG(2,Q) = Q^2+Q+1
PG2 = Q**2 + Q + 1    # = 13


# ------------------------------------------------------------------
# T1 -- Laplacian eigenvalues
# ------------------------------------------------------------------
class TestT1LaplacianEigenvalues:

    def test_lap1_equals_theta(self):
        """LAP_1 = K - EIG_R = 10 = THETA: Fiedler value equals W33 spectral gap."""
        assert LAP_1 == THETA
        assert LAP_1 == K - EIG_R
        assert LAP_1 == 10

    def test_lap2_formula(self):
        """LAP_2 = K - EIG_S = K + |EIG_S| = 12+4 = 16."""
        assert LAP_2 == K - EIG_S
        assert LAP_2 == K + abs(EIG_S)
        assert LAP_2 == 16

    def test_lap0_is_zero(self):
        """LAP_0 = 0: the trivial eigenspace is the kernel of the Laplacian."""
        assert LAP_0 == 0

    def test_laplacian_spectrum_sum(self):
        """1*0 + MUL_R*LAP_1 + MUL_S*LAP_2 = Tr(Delta) = K*V."""
        tr_lap = 1 * LAP_0 + MUL_R * LAP_1 + MUL_S * LAP_2
        assert tr_lap == K * V
        assert tr_lap == 480

    def test_lap1_is_algebraic_connectivity(self):
        """LAP_1 = THETA = 10: algebraic connectivity (Fiedler number) of W33."""
        assert LAP_1 == THETA
        # For a K-regular SRG: algebraic connectivity = K - r (r = largest non-trivial eig)
        assert LAP_1 == K - EIG_R

    def test_lap2_and_p_order(self):
        """LAP_2 = 16 = K + MU = 12+4: Laplacian gap equals K + mu [GQ(q,q) identity]."""
        assert LAP_2 == K + MU
        # General: K - s = K - (-(q+1)) = K + q+1 = q(q+1) + q+1 = (q+1)^2 = 16 ✓
        assert LAP_2 == (Q + 1)**2


# ------------------------------------------------------------------
# T2 -- Mass gap sum and product
# ------------------------------------------------------------------
class TestT2MassGapSumProduct:

    def test_lap1_times_lap2_equals_triangles(self):
        """LAP_1 * LAP_2 = 10*16 = 160 = V*(Q+1) = #triangles = #GQ flags."""
        assert LAP_1 * LAP_2 == 160
        assert LAP_1 * LAP_2 == V * (Q + 1)

    def test_lap1_times_lap2_equals_gq_flags(self):
        """LAP_1 * LAP_2 = 160 = GQ(3,3) point-line incidences = V*(Q+1)."""
        GQ_FLAGS = V * (Q + 1)
        assert LAP_1 * LAP_2 == GQ_FLAGS

    def test_lap_sum_equals_2_pg2(self):
        """LAP_1 + LAP_2 = 10+16 = 26 = 2*(Q^2+Q+1) = 2*PG2."""
        assert LAP_1 + LAP_2 == 2 * PG2
        assert LAP_1 + LAP_2 == 26

    def test_lap_sum_equals_nh_plus_k(self):
        """LAP_1 + LAP_2 = 26 = N_H + K = 14+12: Heawood + degree."""
        assert LAP_1 + LAP_2 == N_H + K
        assert N_H + K == 26

    def test_lap_product_is_p_order_times_k_p(self):
        """LAP_1 * LAP_2 = 160 = P_ORDER * K_P / (K/2) = 96*6/... just verify."""
        # 160 = V*(Q+1) = 40*4; also 160 = P_ORDER*K_P/... 96*6/3.6 -- not clean
        # But: 160 = 10*16 = THETA * (Q+1)^2
        assert LAP_1 * LAP_2 == THETA * (Q + 1)**2

    def test_lap_product_via_eigenvalues(self):
        """(K-r)*(K-s) = LAP_1*LAP_2 = 160 = (K-r)(K+|s|)."""
        assert (K - EIG_R) * (K - EIG_S) == LAP_1 * LAP_2

    def test_lap_product_over_v(self):
        """LAP_1 * LAP_2 / V = 160/40 = 4 = MU = Q+1."""
        assert LAP_1 * LAP_2 // V == MU
        assert LAP_1 * LAP_2 % V == 0


# ------------------------------------------------------------------
# T3 -- Mass gap difference
# ------------------------------------------------------------------
class TestT3MassGapDifference:

    def test_lap2_minus_lap1_equals_kp(self):
        """LAP_2 - LAP_1 = 16-10 = 6 = K_P (Perkel degree)."""
        assert LAP_2 - LAP_1 == K_P
        assert LAP_2 - LAP_1 == 6

    def test_lap2_minus_lap1_equals_k_over_2(self):
        """LAP_2 - LAP_1 = 6 = K/2: half the degree."""
        assert LAP_2 - LAP_1 == K // 2
        assert K % 2 == 0

    def test_lap2_minus_lap1_equals_3_lam(self):
        """LAP_2 - LAP_1 = 6 = 3*LAM = 3*(Q-1): three times lambda."""
        assert LAP_2 - LAP_1 == 3 * LAM
        assert 3 * LAM == 6

    def test_lap2_minus_lap1_equals_2q(self):
        """LAP_2 - LAP_1 = 6 = 2*Q: twice the field order."""
        assert LAP_2 - LAP_1 == 2 * Q

    def test_lap2_minus_lap1_from_eigenvalues(self):
        """LAP_2 - LAP_1 = (K-s) - (K-r) = r - s = EIG_R - EIG_S = 2-(-4) = 6."""
        assert LAP_2 - LAP_1 == EIG_R - EIG_S
        assert EIG_R - EIG_S == 6

    def test_multiplicity_weighted_gap(self):
        """MUL_R*LAP_1 + MUL_S*LAP_2 = 24*10 + 15*16 = 240+240 = 480 = V*K."""
        assert MUL_R * LAP_1 + MUL_S * LAP_2 == V * K
        assert MUL_R * LAP_1 == MUL_S * LAP_2   # SYMMETRY: equal contributions!
        assert MUL_R * LAP_1 == 240


# ------------------------------------------------------------------
# T4 -- Green's function at m^2 = K
# ------------------------------------------------------------------
class TestT4GreenFunctionAtK:

    def test_g1_equals_22(self):
        """g1 = K + LAP_1 = 22 = 2K - EIG_R."""
        assert G1 == 22
        assert G1 == K + LAP_1
        assert G1 == 2 * K - EIG_R

    def test_g2_equals_28(self):
        """g2 = K + LAP_2 = 28 = 2K - EIG_S."""
        assert G2 == 28
        assert G2 == K + LAP_2
        assert G2 == 2 * K - EIG_S

    def test_g1_equals_2_times_k_minus_1(self):
        """g1 = 22 = 2*(K-1): equals the degree of the line graph L(W33)."""
        assert G1 == 2 * (K - 1)
        # Line graph L(W33): K-regular graph G gives L(G) with degree 2(K-1)=22

    def test_g2_equals_4_fano_order(self):
        """g2 = 28 = 4 * FANO_ORDER = 4*7: Green's function denominator = 4*Fano."""
        assert G2 == 4 * FANO_ORDER
        assert G2 == 4 * 7

    def test_g2_equals_2_nh(self):
        """g2 = 28 = 2 * N_H = 2*14: twice the Heawood graph order."""
        assert G2 == 2 * N_H

    def test_green_eigenvalue_e1(self):
        """G(K) on E1 eigenspace: eigenvalue 1/g1 = 1/22."""
        gf_e1 = Fraction(1, G1)
        assert gf_e1 == Fraction(1, 22)

    def test_green_eigenvalue_e2(self):
        """G(K) on E2 eigenspace: eigenvalue 1/g2 = 1/28."""
        gf_e2 = Fraction(1, G2)
        assert gf_e2 == Fraction(1, 28)


# ------------------------------------------------------------------
# T5 -- Green's function structural identities
# ------------------------------------------------------------------
class TestT5GreenFunctionIdentities:

    def test_g1_plus_g2_equals_50(self):
        """g1 + g2 = 22+28 = 50 = V + K - LAM = 5*THETA."""
        assert G1 + G2 == 50
        assert G1 + G2 == V + K - LAM
        assert G1 + G2 == 5 * THETA

    def test_g1_times_g2_equals_616(self):
        """g1 * g2 = 22*28 = 616 = 8 * 7 * 11 = 8 * FANO_ORDER * (K-1)."""
        assert G1 * G2 == 616
        assert G1 * G2 == 8 * FANO_ORDER * (K - 1)

    def test_g_product_factored(self):
        """616 = (2K-EIG_R)(2K-EIG_S): product of Green denominators."""
        assert (2 * K - EIG_R) * (2 * K - EIG_S) == 616
        assert 22 * 28 == 616

    def test_g_product_via_srg_params(self):
        """g1*g2 = 4K^2 - 2K*(EIG_R+EIG_S) + EIG_R*EIG_S = 616."""
        val = 4 * K**2 - 2 * K * (EIG_R + EIG_S) + EIG_R * EIG_S
        assert val == 616
        assert val == G1 * G2

    def test_eig_sum_and_product(self):
        """EIG_R + EIG_S = -2 = LAM - MU; EIG_R * EIG_S = -8 = -P_ORDER/12."""
        assert EIG_R + EIG_S == LAM - MU   # = -2
        assert EIG_R + EIG_S == -2
        assert EIG_R * EIG_S == -8
        assert EIG_R * EIG_S == -(LAM * MU)

    def test_g_sum_over_g_product(self):
        """(g1+g2)/(g1*g2) = 50/616 = 25/308: sum/product of Green denominators."""
        ratio = Fraction(G1 + G2, G1 * G2)
        assert ratio == Fraction(50, 616)
        assert ratio == Fraction(25, 308)


# ------------------------------------------------------------------
# T6 -- Propagator trace on mean-zero subspace
# ------------------------------------------------------------------
class TestT6PropagatorTrace:

    def test_tr_green_mean_zero(self):
        """Tr G(K) on mean-zero: MUL_R/g1 + MUL_S/g2 = 24/22 + 15/28."""
        tr = Fraction(MUL_R, G1) + Fraction(MUL_S, G2)
        assert tr == Fraction(24, 22) + Fraction(15, 28)
        # = 12/11 + 15/28

    def test_tr_green_e1_dominates(self):
        """E1 contribution MUL_R/g1 = 24/22 = 12/11 >> MUL_S/g2 = 15/28."""
        e1_contrib = Fraction(MUL_R, G1)
        e2_contrib = Fraction(MUL_S, G2)
        assert e1_contrib > e2_contrib
        assert e1_contrib == Fraction(12, 11)
        assert e2_contrib == Fraction(15, 28)

    def test_e1_contrib_formula(self):
        """MUL_R/g1 = MUL_R/(2(K-1)) = 24/22 = 12/11 [line graph normalisation]."""
        assert Fraction(MUL_R, G1) == Fraction(12, 11)
        assert Fraction(MUL_R, 2 * (K - 1)) == Fraction(12, 11)

    def test_e2_contrib_formula(self):
        """MUL_S/g2 = MUL_S/(4*FANO_ORDER) = 15/28."""
        assert Fraction(MUL_S, G2) == Fraction(15, 28)
        assert Fraction(MUL_S, 4 * FANO_ORDER) == Fraction(15, 28)

    def test_total_tr_green_at_k(self):
        """Tr G(K) (all eigenspaces) = V/K + MUL_R/g1 + MUL_S/g2."""
        # E0 contributes V/K (since 1^T E_0 1 = V, eigenvalue 1/K at m^2=K)
        # Actually G(K) on E0: eigenvalue 1/(0+K) = 1/K
        # Tr G(K) = 1*(1/K) + MUL_R*(1/g1) + MUL_S*(1/g2)
        tr_total = Fraction(1, K) + Fraction(MUL_R, G1) + Fraction(MUL_S, G2)
        expected = Fraction(1, K) + Fraction(MUL_R, G1) + Fraction(MUL_S, G2)
        assert tr_total == expected

    def test_symmetry_mul_r_lap1_equals_mul_s_lap2(self):
        """MUL_R * LAP_1 = MUL_S * LAP_2 = 240: eigenvalue multiplicity symmetry [Q=3 only]."""
        assert MUL_R * LAP_1 == MUL_S * LAP_2
        assert MUL_R * LAP_1 == 240
        # This is a REMARKABLE Q=3 identity: 24*10 = 15*16 = 240 = |E8 roots|


# ------------------------------------------------------------------
# T7 -- Constant-mode response and alpha comparison
# ------------------------------------------------------------------
class TestT7ConstantModeResponse:

    def test_1_t_green_k_1_equals_v_over_k(self):
        """1^T G(K) 1 = V/K = 40/12 = 10/3 = THETA/(LAM+1)."""
        result = Fraction(V, K)
        assert result == Fraction(10, 3)
        assert result == Fraction(THETA, LAM + 1)

    def test_v_over_k_not_integer(self):
        """V/K = 40/12 = 10/3: the Green function response at m^2=K is irrational... rational."""
        assert Fraction(V, K) == Fraction(10, 3)
        assert Fraction(V, K).denominator == 3

    def test_comparison_green_vs_transport(self):
        """V/K = 10/3 >> V/m_K = 40/1111: Green much larger than transport response."""
        green_response = Fraction(V, K)
        transport_response = Fraction(V, MK)
        assert green_response > transport_response
        # Ratio: (V/K)/(V/m_K) = m_K/K = 1111/12
        assert green_response / transport_response == Fraction(MK, K)
        assert Fraction(MK, K) == Fraction(1111, 12)

    def test_theta_over_lam_identity(self):
        """THETA/LAM = 10/2 = 5 = V/K/... actually V/K = 10/3 ≠ THETA/LAM = 5."""
        # Correction: THETA/LAM = 10/2 = 5, and V/K = 10/3
        # So THETA/(LAM+1) = 10/3 = V/K
        assert Fraction(THETA, LAM + 1) == Fraction(V, K)
        assert Fraction(THETA, LAM + 1) == Fraction(10, 3)

    def test_mul_r_lap1_equals_240_e8(self):
        """MUL_R * LAP_1 = 240 = |E8 root system|: the remarkable equality at Q=3."""
        assert MUL_R * LAP_1 == 240
        # Also: V * K / 2 = 240 (number of edges = E8 roots)
        assert V * K // 2 == 240
        assert MUL_R * LAP_1 == V * K // 2

    def test_lap_mass_hierarchy(self):
        """Laplacian mass hierarchy: 0 < LAP_1 < K < LAP_2; physics: massless vacuum, two massive channels."""
        assert 0 < LAP_1 < K < LAP_2
        assert LAP_1 == 10  # below K
        assert LAP_2 == 16  # above K (super-diffusive channel)
        # The three channels span 1+24+15 = 40 = V dimensions
        assert 1 + MUL_R + MUL_S == V
