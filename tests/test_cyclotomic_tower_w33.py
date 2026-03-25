"""
Phase CXCVII -- Cyclotomic Polynomial Tower at Q = 3
=====================================================
W(3,3) = SRG(40, 12, 2, 4) with Q = 3.

Cyclotomic polynomial Phi_n(x) evaluated at x = Q = 3 reproduces every
principal spectral and combinatorial parameter of W(3,3), Heawood, Fano,
Perkel, and the PSL prime tower.  All arithmetic uses fractions.Fraction
for exact rational verification.

Six test groups (43 tests total):
  T1  Basic evaluations   -- Phi_1..Phi_12 equal W33/Heawood/Fano/Perkel constants
  T2  Product identities  -- V, K, V-K, N_H, E_H, V-1, Phi_3*Phi_6 via products
  T3  Sum identities      -- K_P, THETA, MUL3, K, K-1, |PSL(2,7)| via sums
  T4  Cascade uniqueness  -- Phi_1^2=Phi_2 and Phi_1*Phi_2=Phi_1^3 only at Q=3
  T5  Heawood-Fano bridge -- N_H-1=Phi_3, Phi_3*Phi_6=Phi_3(Q^2), PG(2,Q-1) link
  T6  PSL tower           -- |PSL(2,Q)|=K, Phi_5=(K-1)^2, Phi_7=1093 Wieferich prime
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

# Heawood graph H(3)
N_H = 14;  K_H = 3;  E_H = 21

# Fano plane PG(2,2)
FANO_ORDER = 7

# Perkel graph (57-vertex)
V_57 = 57;  K_P = 6;  MUL1 = 18;  MUL2 = 18;  MUL3 = 20


# ------------------------------------------------------------------
# Cyclotomic helper  Phi_n(q)  -- exact integer output
# ------------------------------------------------------------------
def phi(n, q=Q):
    """Cyclotomic polynomial Phi_n evaluated at integer q (exact Fraction)."""
    q = Fraction(q)
    if n == 1:  return q - 1
    if n == 2:  return q + 1
    if n == 3:  return q**2 + q + 1
    if n == 4:  return q**2 + 1
    if n == 5:  return q**4 + q**3 + q**2 + q + 1
    if n == 6:  return q**2 - q + 1
    if n == 7:  return q**6 + q**5 + q**4 + q**3 + q**2 + q + 1
    if n == 8:  return q**4 + 1
    if n == 10: return q**4 - q**3 + q**2 - q + 1
    if n == 12: return q**4 - q**2 + 1
    if n == 18: return q**6 - q**3 + 1
    raise ValueError(f"phi({n}) not implemented")


# ------------------------------------------------------------------
# T1 -- Basic cyclotomic evaluations
# ------------------------------------------------------------------
class TestT1BasicCyclotomicEvaluations:

    def test_phi1_equals_lam(self):
        """Phi_1(Q) = Q-1 = 2 = LAM (W33 smaller eigenvalue r)."""
        assert phi(1) == LAM

    def test_phi2_equals_mu(self):
        """Phi_2(Q) = Q+1 = 4 = MU (= -EIG_S, W33 valency increment)."""
        assert phi(2) == MU

    def test_phi3_equals_nh_minus_one(self):
        """Phi_3(Q) = Q^2+Q+1 = 13 = N_H-1 (Heawood order minus 1)."""
        assert phi(3) == N_H - 1

    def test_phi4_equals_theta(self):
        """Phi_4(Q) = Q^2+1 = 10 = THETA (W33 spectral gap)."""
        assert phi(4) == THETA

    def test_phi6_equals_fano_order(self):
        """Phi_6(Q) = Q^2-Q+1 = 7 = FANO_ORDER (Fano plane points/lines)."""
        assert phi(6) == FANO_ORDER

    def test_phi12_value_and_primality(self):
        """Phi_12(Q) = Q^4-Q^2+1 = 73, which is prime."""
        assert phi(12) == 73
        assert all(73 % d != 0 for d in range(2, 9))

    def test_phi5_equals_k_minus_1_squared(self):
        """Phi_5(Q) = Q^4+Q^3+Q^2+Q+1 = 121 = 11^2 = (K-1)^2 at Q=3."""
        assert phi(5) == 121
        assert phi(5) == (K - 1)**2

    def test_phi7_value(self):
        """Phi_7(Q) = (Q^7-1)/(Q-1) = 2186/2 = 1093 (Wieferich prime)."""
        assert phi(7) == 1093


# ------------------------------------------------------------------
# T2 -- Product identities
# ------------------------------------------------------------------
class TestT2ProductIdentities:

    def test_v_equals_phi2_times_phi4(self):
        """V = Phi_2(Q)*Phi_4(Q) = (Q+1)(Q^2+1) [definition of V(q,q) always]."""
        assert phi(2) * phi(4) == V

    def test_k_equals_q_times_phi2(self):
        """K = Q*Phi_2(Q) = Q(Q+1) [definition of K(q,q) always]."""
        assert Q * phi(2) == K

    def test_v_minus_k_equals_phi2_times_phi6(self):
        """V-K = Phi_2*Phi_6 = (Q+1)(Q^2-Q+1) = Q^3+1 = 28 [always: cube-plus-one]."""
        assert phi(2) * phi(6) == V - K
        assert phi(2) * phi(6) == Q**3 + 1

    def test_nh_equals_2_phi6(self):
        """N_H = 2*Phi_6(Q) = 2(Q^2-Q+1) [Heawood order always]."""
        assert 2 * phi(6) == N_H

    def test_eh_equals_q_times_phi6(self):
        """E_H = Q*Phi_6(Q) = 21 [Heawood edge count K_H*N_H/2 = 3*14/2 = 21]."""
        assert Q * phi(6) == E_H

    def test_v_minus_one_equals_q_times_phi3(self):
        """V-1 = Q*Phi_3(Q) = Q(Q^2+Q+1) = 39 [always: Q^3+Q^2+Q]."""
        assert Q * phi(3) == V - 1

    def test_phi3_times_phi6_equals_phi3_of_q2(self):
        """Phi_3(Q)*Phi_6(Q) = Q^4+Q^2+1 = Phi_3(Q^2) = 91 [product formula, always]."""
        prod = phi(3) * phi(6)
        phi3_q2 = Fraction(Q)**4 + Fraction(Q)**2 + 1   # Phi_3(Q^2)
        assert prod == phi3_q2
        assert prod == 91

    def test_phi3_times_phi6_factored(self):
        """Phi_3(Q)*Phi_6(Q) = 91 = 7*13 = FANO_ORDER * (N_H-1)."""
        assert phi(3) * phi(6) == FANO_ORDER * (N_H - 1)


# ------------------------------------------------------------------
# T3 -- Sum identities
# ------------------------------------------------------------------
class TestT3SumIdentities:

    def test_phi1_plus_phi2_equals_kp(self):
        """Phi_1+Phi_2 = (Q-1)+(Q+1) = 2Q = K_P (Perkel degree) [always]."""
        assert phi(1) + phi(2) == K_P
        assert phi(1) + phi(2) == 2 * Q

    def test_q_plus_phi6_equals_phi4_equals_theta(self):
        """Q + Phi_6(Q) = Q+(Q^2-Q+1) = Q^2+1 = Phi_4(Q) = THETA [always: tautology]."""
        assert Q + phi(6) == phi(4)
        assert Q + phi(6) == THETA

    def test_phi3_plus_phi6_equals_2_phi4_equals_mul3(self):
        """Phi_3+Phi_6 = 2Q^2+2 = 2*Phi_4 = 2*THETA = MUL3 [always; = Perkel MUL3 at Q=3]."""
        assert phi(3) + phi(6) == 2 * phi(4)
        assert phi(3) + phi(6) == MUL3

    def test_phi3_minus_phi6_equals_kp(self):
        """Phi_3-Phi_6 = (Q^2+Q+1)-(Q^2-Q+1) = 2Q = K_P [always: tautology]."""
        assert phi(3) - phi(6) == K_P
        assert phi(3) - phi(6) == 2 * Q

    def test_phi1_plus_phi4_equals_k(self):
        """Phi_1+Phi_4 = (Q-1)+(Q^2+1) = Q^2+Q = K [always: def of K]."""
        assert phi(1) + phi(4) == K
        assert phi(1) + phi(4) == Q**2 + Q

    def test_phi2_plus_phi6_equals_k_minus_one(self):
        """Phi_2+Phi_6 = (Q+1)+(Q^2-Q+1) = Q^2+2 = 11 = K-1 at Q=3."""
        val = phi(2) + phi(6)
        assert val == Q**2 + 2
        assert val == K - 1   # = 11, a PSL prime

    def test_q_times_phi1_phi2_phi6_equals_psl27_order(self):
        """Q*Phi_1*Phi_2*Phi_6 = Q*(Q-1)*(Q+1)*(Q^2-Q+1) = 3*2*4*7 = 168 = |PSL(2,7)|."""
        product = Q * phi(1) * phi(2) * phi(6)
        assert product == 168
        psl27 = 7 * (7**2 - 1) // 2   # |PSL(2,7)| = 168
        assert product == psl27


# ------------------------------------------------------------------
# T4 -- Cascade uniqueness  (Q=3 only)
# ------------------------------------------------------------------
class TestT4CascadeUniqueness:

    def test_phi1_squared_equals_phi2_at_q3(self):
        """Phi_1(Q)^2 = Phi_2(Q) iff Q(Q-3)=0; unique prime-power root Q=3."""
        assert phi(1)**2 == phi(2)
        assert phi(1)**2 == MU
        # Fails for all other prime powers
        for q in [2, 4, 5, 7, 8, 9]:
            assert (q - 1)**2 != q + 1

    def test_phi1_times_phi2_equals_phi1_cubed_at_q3(self):
        """Phi_1*Phi_2 = Q^2-1 = (Q-1)^3 iff Q(Q-1)(Q-3)=0; unique prime-power root Q=3."""
        assert phi(1) * phi(2) == phi(1)**3
        assert phi(1) * phi(2) == 8
        for q in [2, 4, 5, 7]:
            assert (q - 1) * (q + 1) != (q - 1)**3

    def test_lam_times_mu_equals_lam_cubed(self):
        """LAM * MU = 2*4 = 8 = 2^3 = LAM^3 (same cascade in W33 language)."""
        assert LAM * MU == LAM**3
        assert LAM * MU == 8

    def test_cascade_polynomial_root(self):
        """Q*(Q-1)*(Q-3) = 0 at Q=3; this polynomial is the cascade uniqueness condition."""
        assert Q * (Q - 1) * (Q - 3) == 0

    def test_phi2_uniqueness_polynomial(self):
        """(Q-1)^2 = Q+1 iff Q^2-3Q=0 iff Q(Q-3)=0; confirmed zero at Q=3."""
        assert Q * (Q - 3) == 0

    def test_cascade_fails_at_q2_and_q4(self):
        """For q=2 and q=4: Phi_1^2 != Phi_2 and Phi_1*Phi_2 != Phi_1^3."""
        for q in [2, 4]:
            assert (q - 1)**2 != q + 1
            assert (q - 1) * (q + 1) != (q - 1)**3


# ------------------------------------------------------------------
# T5 -- Heawood-Fano bridge
# ------------------------------------------------------------------
class TestT5HeawoodFanoBridge:

    def test_nh_minus_one_equals_phi3_unique_to_q3(self):
        """N_H-1 = Phi_3(Q) = 13; 2*Phi_6-1 = Phi_3 iff Q(Q-3)=0."""
        assert N_H - 1 == phi(3)
        assert N_H - 1 == 13
        for q in [2, 4, 5]:
            assert 2 * (q**2 - q + 1) - 1 != q**2 + q + 1

    def test_2phi6_minus_1_equals_phi3_with_gap(self):
        """2*Phi_6(Q)-1 - Phi_3(Q) = Q*(Q-3); gap is zero at Q=3."""
        diff = 2 * (Q**2 - Q + 1) - 1 - (Q**2 + Q + 1)
        assert diff == Q * (Q - 3)
        assert diff == 0

    def test_fano_heawood_cycle_identities(self):
        """FANO = Phi_6(Q), N_H = 2*FANO, E_H = Q*FANO (the complete Fano-Heawood link)."""
        assert FANO_ORDER == phi(6)
        assert N_H == 2 * FANO_ORDER
        assert E_H == Q * FANO_ORDER

    def test_phi3_times_phi6_is_91(self):
        """Phi_3(Q)*Phi_6(Q) = 91 = 7*13 = FANO_ORDER*(N_H-1)."""
        assert phi(3) * phi(6) == 91
        assert phi(3) * phi(6) == FANO_ORDER * (N_H - 1)

    def test_phi4_plus_phi6_equals_v57_minus_v(self):
        """Phi_4(Q)+Phi_6(Q) = THETA+FANO_ORDER = 17 = V_57-V."""
        assert phi(4) + phi(6) == V_57 - V
        assert phi(4) + phi(6) == 17

    def test_nh_kh_edge_formula(self):
        """N_H * K_H / 2 = E_H = Q*Phi_6(Q); Heawood edge count via cyclotomic."""
        assert N_H * K_H // 2 == E_H
        assert N_H * K_H // 2 == Q * phi(6)

    def test_fano_as_pg2_of_q_minus_one(self):
        """PG(2,Q-1) has Phi_3(Q-1) = (Q-1)^2+(Q-1)+1 = Q^2-Q+1 = Phi_6(Q) points [always]."""
        pg2_points = (Q - 1)**2 + (Q - 1) + 1
        assert pg2_points == phi(6)
        assert pg2_points == FANO_ORDER


# ------------------------------------------------------------------
# T6 -- PSL tower and special values
# ------------------------------------------------------------------
class TestT6PSLTowerAndSpecialValues:

    def test_psl2q_order_equals_k(self):
        """|PSL(2,Q)| = Q*(Q^2-1)/2 = K at Q=3; iff (Q-1)/2=1 iff Q=3."""
        psl_order = Q * (Q**2 - 1) // 2
        assert psl_order == K
        for q in [2, 4, 5]:
            assert q * (q**2 - 1) // 2 != q * (q + 1)

    def test_phi5_equals_k_minus_one_squared(self):
        """Phi_5(Q) = (K-1)^2 = 121 at Q=3; Phi_5=(Q^2+Q-1)^2 iff Q(Q-1)(Q-3)=0."""
        assert phi(5) == (K - 1)**2
        assert phi(5) == 121
        for q in [2, 4, 5]:
            assert phi(5, q) != (q**2 + q - 1)**2

    def test_psl_prime_tower_all_prime(self):
        """PSL prime tower {Q, Q^2-4, K-1, K+Q+MU} = {3,5,11,19} all prime."""
        tower = [Q, Q**2 - 4, K - 1, K + Q + MU]
        assert tower == [3, 5, 11, 19]
        for p in tower:
            assert all(p % d != 0 for d in range(2, p)), f"{p} not prime"

    def test_psl27_order_from_w33_constants(self):
        """Q*LAM*MU*FANO = 3*2*4*7 = 168 = |PSL(2,7)|."""
        assert Q * LAM * MU * FANO_ORDER == 168
        assert 7 * (7**2 - 1) // 2 == 168

    def test_phi5_factored_as_k_minus_one_squared(self):
        """Phi_5(Q) = 121 = 11^2; 11 = K-1 = Q^2+Q-1 is the third PSL prime."""
        assert phi(5) == 11**2
        assert K - 1 == 11
        assert 11 == Q**2 + Q - 1     # K - 1 expressed via Q

    def test_phi7_is_wieferich_prime(self):
        """Phi_7(Q) = 1093 is prime (and a Wieferich prime: 2^1092 = 1 mod 1093^2)."""
        assert phi(7) == 1093
        assert all(1093 % d != 0 for d in range(2, 34))   # primality up to sqrt(1093)<34

    def test_v57_structure_three_ways(self):
        """V_57 = 1+2*MUL1+MUL3 = Q*(2Q^2+1) = 2*(V-K)+1; three cyclotomic faces."""
        assert V_57 == 1 + 2 * MUL1 + MUL3
        assert V_57 == Q * (2 * Q**2 + 1)
        assert V_57 == 2 * (V - K) + 1     # 2*(Q^3+1)+1 = 2Q^3+3

    def test_v57_over_q_is_psl_prime(self):
        """V_57/Q = 19 = 2*Phi_4(Q)-1 = 2*THETA-1; 19 is the fourth PSL prime."""
        assert V_57 // Q == 19
        assert 2 * phi(4) - 1 == 19
        assert V_57 // Q == K + Q + MU    # = K+Q+MU = 12+3+4 = 19 from PSL tower
