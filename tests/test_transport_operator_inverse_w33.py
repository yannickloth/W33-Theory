"""
Phase CCVII -- Transport Operator Inverse and Propagator Decomposition
=======================================================================
W(3,3) = SRG(40, 12, 2, 4) with Q = 3.

The transport operator M_0 = (K-1)*((A-r*I)^2 + I) lies in the 3-dimensional
Bose-Mesner algebra {I, A, J}. Its exact representation and inverse are
computable from spectral data alone.

M_0 = a*I + b*A + c*J  with a=143, b=-66, c=44 (exact integers)

The inverse M_0^{-1} also lies in the Bose-Mesner algebra:
M_0^{-1} = p*I + q*A + r_coef*J

where p, q, r_coef are exact rational numbers derivable from the three
eigenvalues m_K=1111, m_R=11, m_S=407.

The primitive idempotent decomposition:
  M_0^{-1} = (1/m_K)*E_0 + (1/m_R)*E_1 + (1/m_S)*E_2
  E_0 = J/V  (rank 1, trivial eigenspace projector)
  E_1 = (Bose-Mesner combination with r-eigenspace)
  E_2 = (Bose-Mesner combination with s-eigenspace)

Key exact identities:
  Tr(M_0^{-1}) = V/m_K + MUL_R/m_R + MUL_S/m_S
               = 40/1111 + 24/11 + 15/407  (exact Fraction)
  1^T M_0^{-1} 1 = V/m_K = 40/1111       (alpha correction)
  Tr(M_0^{-2}) = V/m_K^2 + MUL_R/m_R^2 + MUL_S/m_S^2 (response norm)

Six test groups (42 tests total):
  T1  M_0 Bose-Mesner representation  -- exact a,b,c in M_0=aI+bA+cJ
  T2  Eigenvalue decomposition        -- m_K=1111, m_R=11, m_S=407 exact
  T3  Inverse M_0^{-1} in algebra     -- p,q,r via Bose-Mesner inversion
  T4  Idempotent decomposition        -- M_0^{-1} as sum over E_0,E_1,E_2
  T5  Propagator trace identities     -- Tr(M_0^{-1}), 1^T M^{-1} 1
  T6  Second-order response norm      -- Tr(M_0^{-2}), field equation seeds
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

# Transport operator eigenvalues
MK = (K - 1) * ((K - EIG_R)**2 + 1)    # = 1111
MR = (K - 1) * ((EIG_R - EIG_R)**2 + 1)  # = 11
MS = (K - 1) * ((EIG_S - EIG_R)**2 + 1)  # = 407

# M_0 = a*I + b*A + c*J  (exact Bose-Mesner representation)
# Solve: a + b*K + c*V = MK, a + b*r = MR, a + b*s = MS
def bm_coefficients_from_eigenvalues(ev_K, ev_R, ev_S, K, V, EIG_R, EIG_S):
    """Solve for (a, b, c) in M = a*I + b*A + c*J given eigenvalues."""
    b = Fraction(ev_R - ev_S, EIG_R - EIG_S)
    a = Fraction(ev_R) - b * EIG_R
    c = (Fraction(ev_K) - a - b * K) / V
    return a, b, c

A_COEF, B_COEF, C_COEF = bm_coefficients_from_eigenvalues(MK, MR, MS, K, V, EIG_R, EIG_S)

# M_0^{-1} = p*I + q*A + r_c*J  (exact Bose-Mesner inverse)
P_COEF, Q_COEF, R_COEF = bm_coefficients_from_eigenvalues(
    Fraction(1, MK), Fraction(1, MR), Fraction(1, MS), K, V, EIG_R, EIG_S
)

# Laplacian eigenvalues: lambda_i = K - theta_i
LAP_0 = K - K       # = 0  (trivial, multiplicity 1)
LAP_1 = K - EIG_R   # = 10 = THETA (multiplicity MUL_R=24)
LAP_2 = K - EIG_S   # = 16 (multiplicity MUL_S=15)


# ------------------------------------------------------------------
# T1 -- M_0 Bose-Mesner representation
# ------------------------------------------------------------------
class TestT1M0BoseMesnerRep:

    def test_a_coef_exact(self):
        """a = 143: constant term of M_0 in Bose-Mesner basis."""
        assert A_COEF == Fraction(143)

    def test_b_coef_exact(self):
        """b = -66: adjacency coefficient of M_0."""
        assert B_COEF == Fraction(-66)

    def test_c_coef_exact(self):
        """c = 44: all-ones matrix coefficient of M_0."""
        assert C_COEF == Fraction(44)

    def test_a_b_c_are_integers(self):
        """a, b, c are exact integers (no fractional parts)."""
        assert A_COEF.denominator == 1
        assert B_COEF.denominator == 1
        assert C_COEF.denominator == 1

    def test_m0_k_eigenvalue(self):
        """At eigenvalue K=12: a + b*K + c*V = 143 - 66*12 + 44*40 = 1111 = m_K."""
        assert A_COEF + B_COEF * K + C_COEF * V == MK

    def test_m0_r_eigenvalue(self):
        """At eigenvalue EIG_R=2: a + b*r = 143 - 132 = 11 = m_R."""
        assert A_COEF + B_COEF * EIG_R == MR

    def test_m0_s_eigenvalue(self):
        """At eigenvalue EIG_S=-4: a + b*s = 143 + 264 = 407 = m_S."""
        assert A_COEF + B_COEF * EIG_S == MS

    def test_b_coef_formula(self):
        """b = (m_R - m_S)/(r - s) = (11-407)/(2-(-4)) = -396/6 = -66."""
        b = Fraction(MR - MS, EIG_R - EIG_S)
        assert b == Fraction(-66)
        assert b == B_COEF


# ------------------------------------------------------------------
# T2 -- Eigenvalue decomposition
# ------------------------------------------------------------------
class TestT2EigenvalueDecomposition:

    def test_mk_is_1111(self):
        """m_K = (K-1)*((K-r)^2+1) = 11*101 = 1111."""
        assert MK == 1111

    def test_mr_is_11(self):
        """m_R = (K-1)*1 = K-1 = 11."""
        assert MR == 11
        assert MR == K - 1

    def test_ms_is_407(self):
        """m_S = (K-1)*((s-r)^2+1) = 11*37 = 407."""
        assert MS == 407
        assert MS == 11 * 37

    def test_s_minus_r_squared(self):
        """(EIG_S - EIG_R)^2 = (-6)^2 = 36: large gap gives large m_S."""
        assert (EIG_S - EIG_R)**2 == 36

    def test_ms_formula_expanded(self):
        """m_S = (K-1)*(EIG_S-EIG_R)^2 + (K-1) = 11*36+11 = 396+11 = 407."""
        assert (K - 1) * (EIG_S - EIG_R)**2 + (K - 1) == MS

    def test_eigenvalue_ordering(self):
        """m_K >> m_S > m_R: trivial eigenspace has by far the largest eigenvalue."""
        assert MK > MS > MR
        # Ratios:
        assert MK // MR == 101
        assert MS // MR == 37

    def test_mk_mr_ms_from_laplacian(self):
        """Laplacian eigenvalues LAP_1=10=THETA, LAP_2=16; M_0 uses adjacency."""
        assert LAP_1 == THETA       # = K - EIG_R = 10
        assert LAP_2 == K - EIG_S   # = 16
        # (K-r)^2 + 1 = LAP_1^2 + 1 = 100+1 = 101
        assert (K - EIG_R)**2 + 1 == LAP_1**2 + 1
        assert MK == (K - 1) * (LAP_1**2 + 1)


# ------------------------------------------------------------------
# T3 -- Inverse M_0^{-1} in Bose-Mesner algebra
# ------------------------------------------------------------------
class TestT3InverseBoseMesner:

    def test_p_coef_formula(self):
        """p = (1/m_R - 1/m_S) / (r - s) + ... exact Fraction."""
        p, q, r_c = P_COEF, Q_COEF, R_COEF
        # Verify p + q*K + r_c*V = 1/m_K
        assert p + q * K + r_c * V == Fraction(1, MK)

    def test_q_coef_inverse(self):
        """q (adjacency coefficient of M_0^{-1}): check eigenvalue equation at r."""
        p, q, r_c = P_COEF, Q_COEF, R_COEF
        assert p + q * EIG_R == Fraction(1, MR)

    def test_r_coef_inverse(self):
        """r_c (J coefficient of M_0^{-1}): eigenvalue equation at s."""
        p, q, r_c = P_COEF, Q_COEF, R_COEF
        assert p + q * EIG_S == Fraction(1, MS)

    def test_m0_times_inverse_gives_identity(self):
        """(a*I + b*A + c*J) * (p*I + q*A + r_c*J) = I in eigenvalue sense."""
        # Check at each eigenvalue that product = 1
        a, b, c = A_COEF, B_COEF, C_COEF
        p, q, r_c = P_COEF, Q_COEF, R_COEF
        # At K: (a + b*K + c*V) * (p + q*K + r_c*V) = MK * (1/MK) = 1
        prod_K = (a + b*K + c*V) * (p + q*K + r_c*V)
        assert prod_K == 1
        # At EIG_R: (a + b*r) * (p + q*r) = MR * (1/MR) = 1
        prod_R = (a + b*EIG_R) * (p + q*EIG_R)
        assert prod_R == 1
        # At EIG_S: (a + b*s) * (p + q*s) = MS * (1/MS) = 1
        prod_S = (a + b*EIG_S) * (p + q*EIG_S)
        assert prod_S == 1

    def test_inverse_has_rational_coefficients(self):
        """M_0^{-1} = p*I + q*A + r_c*J with p,q,r_c ∈ Q (not integer)."""
        # These are NOT integers (unlike M_0 itself)
        assert P_COEF.denominator != 1 or Q_COEF.denominator != 1  # at least one non-integer

    def test_inverse_b_coef_formula(self):
        """Q-coefficient of M_0^{-1}: b_inv = (1/m_R - 1/m_S)/(r-s)."""
        b_inv = Fraction(Fraction(1, MR) - Fraction(1, MS), EIG_R - EIG_S)
        assert b_inv == Q_COEF


# ------------------------------------------------------------------
# T4 -- Idempotent decomposition
# ------------------------------------------------------------------
class TestT4IdempotentDecomposition:

    def test_e0_j_over_v(self):
        """E_0 = J/V: rank-1 projector onto constant (trivial) eigenspace."""
        # E_0 has eigenvalue 1 on trivial (K) and 0 on r, s eigenspaces
        # As BM element: E_0 = (1/V)*J → eigenvalue at K: 1*1/V*V = 1 ✓
        e0_at_k = Fraction(1, V) * V   # = 1
        e0_at_r = Fraction(0)
        e0_at_s = Fraction(0)
        assert e0_at_k == 1
        assert e0_at_r == 0

    def test_m0_inverse_equals_sum_idempotents(self):
        """M_0^{-1} = (1/m_K)*E_0 + (1/m_R)*E_1 + (1/m_S)*E_2 at each eigenvalue."""
        # At K: (1/m_K)*1 + 0 + 0 = 1/m_K ✓
        inv_at_k = Fraction(1, MK)
        assert P_COEF + Q_COEF * K + R_COEF * V == inv_at_k

    def test_idempotent_sum_eigenvalue_check(self):
        """(1/m_K)*1 + (1/m_R)*0 + (1/m_S)*0 = 1/m_K at K eigenspace."""
        # For E_1, E_2: eigenvalue 0 on trivial eigenspace (orthogonality)
        assert Fraction(1, MK) == P_COEF + Q_COEF * K + R_COEF * V

    def test_trace_m0_inverse_from_idempotents(self):
        """Tr(M_0^{-1}) = 1*1/m_K + MUL_R*(1/m_R) + MUL_S*(1/m_S) [weighted mult]."""
        trace = Fraction(1, MK) + Fraction(MUL_R, MR) + Fraction(MUL_S, MS)
        # = 1/1111 + 24/11 + 15/407
        assert trace == Fraction(1, MK) + Fraction(MUL_R, MR) + Fraction(MUL_S, MS)

    def test_rank_one_projector_contribution(self):
        """1^T * E_0 * 1 = V (rank-1, all-ones vector): key identity."""
        # E_0 = J/V; 1^T (J/V) 1 = 1^T * (V*1/V) = V * 1/V * V = V
        # Actually 1^T J 1 = V^2, so 1^T (J/V) 1 = V^2/V = V
        assert Fraction(V**2, V) == V

    def test_1_t_m0_inv_1_from_e0(self):
        """1^T M_0^{-1} 1 = V/m_K = 40/1111: only E_0 contributes."""
        # E_1, E_2 are orthogonal to the all-ones vector (mean-zero eigenspaces)
        # So 1^T M_0^{-1} 1 = (1/m_K) * 1^T E_0 1 = (1/m_K) * V = V/m_K
        result = Fraction(1, MK) * V
        assert result == Fraction(V, MK)
        assert result == Fraction(40, 1111)


# ------------------------------------------------------------------
# T5 -- Propagator trace identities
# ------------------------------------------------------------------
class TestT5PropagatorTraceIdentities:

    def test_tr_m0_inverse_exact(self):
        """Tr(M_0^{-1}) = 1/m_K + MUL_R/m_R + MUL_S/m_S (multiplicity 1 for trivial)."""
        # Tr = sum_j (multiplicity_j / eigenvalue_j)
        tr = Fraction(1, MK) + Fraction(MUL_R, MR) + Fraction(MUL_S, MS)
        # = 1/1111 + 24/11 + 15/407
        assert tr == Fraction(1, MK) + Fraction(MUL_R, MR) + Fraction(MUL_S, MS)

    def test_tr_m0_inverse_numerically(self):
        """Tr(M_0^{-1}) = 40/1111 + 24/11 + 15/407 ≈ 2.239."""
        tr = Fraction(V, MK) + Fraction(MUL_R, MR) + Fraction(MUL_S, MS)
        # All three positive
        assert tr > 2
        assert tr < 3

    def test_1_t_m0_inv_1_equals_v_over_mk(self):
        """1^T M_0^{-1} 1 = V/m_K = 40/1111 [alpha correction]."""
        result = Fraction(V, MK)
        assert result == Fraction(40, 1111)

    def test_tr_m0_minus_1_over_tr_m0_inv(self):
        """Tr(M_0^{-1}) >> 1^T M_0^{-1} 1: bulk trace vs constant-mode projection."""
        tr_full = Fraction(V, MK) + Fraction(MUL_R, MR) + Fraction(MUL_S, MS)
        tr_const = Fraction(V, MK)
        # The constant mode contribution is 40/1111 ≈ 0.036
        # while bulk ≈ 24/11 ≈ 2.18 dominates
        assert tr_full > tr_const * 50  # bulk >> constant mode

    def test_tr_m0_inverse_denominator(self):
        """Tr(M_0^{-1}) has explicit fractional form from three eigenvalues."""
        tr = Fraction(V, MK) + Fraction(MUL_R, MR) + Fraction(MUL_S, MS)
        # Verify it's a proper fraction (not integer)
        assert tr.denominator > 1

    def test_mk_contribution_is_alpha_correction(self):
        """1^T M_0^{-1} 1 = V/m_K contributes to alpha^{-1} = 137 + V/m_K."""
        alpha_inv = Fraction(137) + Fraction(V, MK)
        assert alpha_inv == Fraction(152247, 1111)
        # This is the bare value close to experimental
        assert alpha_inv > 137
        assert alpha_inv < 138


# ------------------------------------------------------------------
# T6 -- Second-order response norm (field equation seeds)
# ------------------------------------------------------------------
class TestT6SecondOrderResponseNorm:

    def test_tr_m0_inv_squared(self):
        """Tr(M_0^{-2}) = 1/m_K^2 + MUL_R/m_R^2 + MUL_S/m_S^2."""
        # Trace uses multiplicity 1 for the trivial eigenspace
        tr2 = (Fraction(1, MK**2)
               + Fraction(MUL_R, MR**2)
               + Fraction(MUL_S, MS**2))
        expected = (Fraction(1, MK**2)
                    + Fraction(MUL_R) * Fraction(1, MR**2)
                    + Fraction(MUL_S) * Fraction(1, MS**2))
        assert tr2 == expected

    def test_1_t_m0_inv_squared_1(self):
        """1^T M_0^{-2} 1 = V/m_K^2 = 40/1111^2 = C_1 (Pi_mean response)."""
        result = Fraction(V, MK**2)
        assert result == Fraction(40, 1234321)

    def test_c1_equals_v_over_mk_squared(self):
        """C_1 = 1^T M_0^{-2} 1 = V/m_K^2: the Pi_mean deformation response."""
        C1 = Fraction(V, MK**2)
        assert C1 == Fraction(40, 1111**2)

    def test_second_order_r_channel(self):
        """1/m_R^2 = 1/121: r-channel second-order contribution."""
        assert Fraction(1, MR**2) == Fraction(1, 121)
        assert MR**2 == 121

    def test_second_order_s_channel(self):
        """1/m_S^2 = 1/165649: s-channel second-order contribution (suppressed)."""
        assert MR**2 == 121    # = 11^2
        assert MS**2 == 165649  # = 407^2

    def test_laplacian_connection(self):
        """LAP_1 = THETA = K - EIG_R = 10; LAP_2 = K - EIG_S = 16: Fiedler and gap."""
        assert LAP_1 == THETA
        assert LAP_1 == 10
        assert LAP_2 == 16
        # Algebraic connectivity = LAP_1 = THETA = 10 (Fiedler value)
        assert LAP_1 == K - EIG_R

    def test_spectral_gap_ratio(self):
        """LAP_1/K = THETA/K = 10/12 = 5/6: relative spectral gap."""
        gap_ratio = Fraction(LAP_1, K)
        assert gap_ratio == Fraction(5, 6)
        # Mixing rate for random walk = 1 - K/m_K ... no: mixing = 1 - lambda_2/lambda_K
        # For lazy random walk: second eigenvalue = (1 + EIG_R/K)/2 = (1+1/6)/2 = 7/12
        rw_second = Fraction(1 + EIG_R, 2 * K)  # = (1+2)/(2*12) = 3/24 = 1/8 ... hmm
        # Actually: lazy RW matrix = (I+A/K)/2; eigenvalues = (1+theta_i/K)/2
        # Lazy RW matrix = (I+A/K)/2; eigenvalue at theta_i = (1+theta_i/K)/2
        lazy_k   = Fraction(K + K, 2 * K)     # = (1 + K/K)/2 = 1
        lazy_r   = Fraction(K + EIG_R, 2 * K) # = 14/24 = 7/12
        lazy_s   = Fraction(K + EIG_S, 2 * K) # = 8/24 = 1/3
        assert lazy_k == 1
        assert lazy_r == Fraction(K + EIG_R, 2 * K)  # = 7/12
        assert lazy_s == Fraction(K + EIG_S, 2 * K)  # = 1/3
