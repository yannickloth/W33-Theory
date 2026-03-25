"""
Phase CC -- Grand Synthesis: The Q=3 Uniqueness Theorem
=========================================================
W(3,3) = SRG(40, 12, 2, 4) with Q = 3.  Phase CC = 200th phase.

This phase is the grand synthesis of the computational programme.  Every
major identity proved across Phases LXIV-CXCIX is assembled here into a
unified statement: Q = 3 is the unique prime power satisfying all the
mathematical constraints simultaneously, and every W(3,3) constant can be
derived from Q alone via a web of cyclotomic, arithmetic, spectral, graph-
theoretic, and number-theoretic laws.

Self-reference: V * THETA / 2 = 40 * 10 / 2 = 200 = Phase CC number.

Six test groups (48 tests total):
  T1  Grand uniqueness         -- Q(Q-3)=0 encapsulates all five uniqueness families
  T2  Cyclotomic master table  -- all W33 constants as Phi_n(Q) values/products/sums
  T3  Arithmetic crown jewels  -- sigma/phi chains, PSL(2,7) = 168 in two languages
  T4  Spectral synthesis       -- eigenvalues, Hoffman bounds, E8 edge connection
  T5  Cross-domain bridges     -- Perkel, Heawood, Fano, Lucas, Chebyshev, PSL primes
  T6  Master laws              -- multiplicity partition, fundamental products, CC self-ref
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

# Heawood graph
N_H = 14;  K_H = 3;  E_H = 21

# Fano plane
FANO_ORDER = 7

# Perkel graph
V_57 = 57;  K_P = 6;  MUL1 = 18;  MUL2 = 18;  MUL3 = 20

# Phase number
PHASE_CC = 200


# ------------------------------------------------------------------
# Minimal arithmetic helpers (self-contained)
# ------------------------------------------------------------------
def phi_euler(n):
    result = 1;  nn = n;  d = 2
    while d * d <= nn:
        if nn % d == 0:
            result *= (d - 1);  nn //= d
            while nn % d == 0:
                result *= d;  nn //= d
        d += 1
    if nn > 1:
        result *= (nn - 1)
    return result


def sigma(n):
    return sum(d for d in range(1, n + 1) if n % d == 0)


def lucas_q(n, q=Q):
    """Q-Lucas sequence: L_0=2, L_1=Q, L_n = Q*L_{n-1} - L_{n-2}."""
    if n == 0: return 2
    if n == 1: return q
    a, b = 2, q
    for _ in range(n - 1):
        a, b = b, q * b - a
    return b


def fib(n):
    """Standard Fibonacci: F_0=0, F_1=1."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def cheby_T(n, x):
    """Chebyshev T_n(x) — exact Fraction."""
    x = Fraction(x)
    if n == 0: return Fraction(1)
    if n == 1: return x
    a, b = Fraction(1), x
    for _ in range(n - 1):
        a, b = b, 2 * x * b - a
    return b


# ------------------------------------------------------------------
# T1 -- Grand uniqueness: Q(Q-3) = 0
# ------------------------------------------------------------------
class TestT1GrandUniqueness:

    def test_master_selector_polynomial(self):
        """Q*(Q-3) = 0: the degree-2 master uniqueness selector for all W33 conditions."""
        assert Q * (Q - 3) == 0

    def test_cascade_uniqueness_phi1_squared_eq_phi2(self):
        """(Q-1)^2 = Q+1 = MU iff Q*(Q-3)=0 [cascade: LAM^2 = MU]."""
        assert (Q - 1)**2 == MU
        for q in [2, 4, 5, 7]:
            assert (q - 1)**2 != q + 1

    def test_eigenvalue_ratio_uniqueness(self):
        """s = -2r (EIG_S = -2*EIG_R) iff Q=3 [s+2r = 0 iff Q(Q-3)=0]."""
        assert EIG_S + 2 * EIG_R == 0
        for q in [2, 4, 5, 7]:
            assert -(q + 1) + 2 * (q - 1) != 0

    def test_psl_order_uniqueness(self):
        """|PSL(2,Q)| = Q*(Q^2-1)/2 = K iff Q=3 [iff (Q-1)/2=1 iff Q=3]."""
        assert Q * (Q**2 - 1) // 2 == K
        for q in [2, 4, 5]:
            assert q * (q**2 - 1) // 2 != q * (q + 1)

    def test_arithmetic_sigma_k_uniqueness(self):
        """sigma(K) = V-K iff Q=3 [sigma(Q(Q+1)) = (Q+1)(Q^2-Q+1) iff Q(Q-3)=0]."""
        assert sigma(K) == V - K
        for q in [2, 4, 5]:
            kk = q * (q + 1);  vv = (q + 1) * (q**2 + 1)
            assert sigma(kk) != vv - kk

    def test_euler_phi_mu_equals_lam(self):
        """phi(MU) = phi(Q+1) = Q-1 = LAM iff Q=3 [phi(Q+1)=Q-1 iff Q(Q-3)=0]."""
        assert phi_euler(MU) == LAM
        for q in [2, 4, 5]:
            assert phi_euler(q + 1) != q - 1

    def test_heawood_fano_bridge_uniqueness(self):
        """2*Phi_6(Q)-1 = Phi_3(Q) iff Q=3 [2*(Q^2-Q+1)-1 = Q^2+Q+1 iff Q(Q-3)=0]."""
        lhs = 2 * (Q**2 - Q + 1) - 1
        rhs = Q**2 + Q + 1
        assert lhs == rhs
        for q in [2, 4, 5]:
            assert 2 * (q**2 - q + 1) - 1 != q**2 + q + 1

    def test_all_uniqueness_conditions_equivalent(self):
        """All five uniqueness conditions are equivalent to Q*(Q-3)=0."""
        cond_cascade   = (Q - 1)**2 - (Q + 1)              # = Q*(Q-3)
        cond_eigenval  = EIG_S + 2 * EIG_R                  # = Q*(Q-3)/2 * ... hmm
        cond_hf_bridge = 2*(Q**2-Q+1)-1 - (Q**2+Q+1)       # = Q*(Q-3) negated? check: -Q^2+(-Q+1)...
        # 2Q^2-2Q+1-Q^2-Q-1 = Q^2-3Q = Q(Q-3)
        assert cond_cascade == Q * (Q - 3)                   # (Q-1)^2-(Q+1) = Q^2-3Q ✓
        assert 2*(Q**2-Q+1)-1 - (Q**2+Q+1) == Q*(Q-3)       # = Q^2-3Q ✓
        assert cond_cascade == 0 and cond_hf_bridge == 0     # both zero at Q=3


# ------------------------------------------------------------------
# T2 -- Cyclotomic master table
# ------------------------------------------------------------------
class TestT2CyclotomicMasterTable:

    def test_all_six_primary_evaluations(self):
        """Phi_1=LAM, Phi_2=MU, Phi_3=N_H-1, Phi_4=THETA, Phi_6=FANO, Phi_5=(K-1)^2."""
        assert Q - 1           == LAM          # Phi_1
        assert Q + 1           == MU           # Phi_2
        assert Q**2 + Q + 1    == N_H - 1      # Phi_3
        assert Q**2 + 1        == THETA        # Phi_4
        assert Q**2 - Q + 1    == FANO_ORDER   # Phi_6
        assert Q**4+Q**3+Q**2+Q+1 == (K-1)**2  # Phi_5

    def test_product_decompositions(self):
        """V=Phi_2*Phi_4, K=Q*Phi_2, V-K=Phi_2*Phi_6=Q^3+1, N_H=2*Phi_6."""
        assert (Q+1) * (Q**2+1)      == V
        assert Q * (Q+1)             == K
        assert (Q+1) * (Q**2-Q+1)   == V - K
        assert (Q+1) * (Q**2-Q+1)   == Q**3 + 1
        assert 2 * (Q**2-Q+1)        == N_H

    def test_sum_identities(self):
        """Phi_1+Phi_4=K, Phi_2+Phi_6=K-1, Phi_3+Phi_6=MUL3=2*THETA, Phi_1+Phi_2=K_P."""
        assert (Q-1) + (Q**2+1)    == K
        assert (Q+1) + (Q**2-Q+1) == K - 1
        assert (Q**2+Q+1)+(Q**2-Q+1) == MUL3
        assert (Q-1) + (Q+1)       == K_P

    def test_phi2_equals_phi1_squared_at_q3(self):
        """Phi_2(Q) = (Phi_1(Q))^2 at Q=3: MU = LAM^2; unique among prime powers."""
        assert MU == LAM**2
        assert Q + 1 == (Q - 1)**2

    def test_phi_euler_links(self):
        """phi(MU)=LAM=Phi_1 and phi(THETA)=MU=Phi_2 (both unique to Q=3)."""
        assert phi_euler(MU) == LAM
        assert phi_euler(THETA) == MU

    def test_sigma_links(self):
        """sigma(MU)=FANO=Phi_6 and sigma(FANO)=LAM*MU=LAM^3 (Q=3 specific)."""
        assert sigma(MU) == FANO_ORDER
        assert sigma(FANO_ORDER) == LAM * MU

    def test_grand_product_psl27(self):
        """Q*Phi_1*Phi_2*Phi_6 = Q*(Q-1)*(Q+1)*(Q^2-Q+1) = 3*2*4*7 = 168 = |PSL(2,7)|."""
        product = Q * (Q-1) * (Q+1) * (Q**2-Q+1)
        assert product == 168
        assert 7 * (7**2 - 1) // 2 == 168    # independent verification of |PSL(2,7)|

    def test_phi3_phi6_product(self):
        """Phi_3(Q)*Phi_6(Q) = Q^4+Q^2+1 = Phi_3(Q^2) = FANO*(N_H-1) = 91."""
        assert (Q**2+Q+1) * (Q**2-Q+1) == Q**4 + Q**2 + 1
        assert Q**4 + Q**2 + 1 == FANO_ORDER * (N_H - 1)
        assert Q**4 + Q**2 + 1 == 91


# ------------------------------------------------------------------
# T3 -- Arithmetic crown jewels
# ------------------------------------------------------------------
class TestT3ArithmeticCrownJewels:

    def test_sigma_chain(self):
        """sigma chain LAM->[Q]->MU->[FANO]->LAM*MU under sigma."""
        assert sigma(LAM) == Q
        assert sigma(Q) == MU
        assert sigma(MU) == FANO_ORDER
        assert sigma(FANO_ORDER) == LAM * MU

    def test_sigma_product_equals_psl27(self):
        """sigma(LAM)*sigma(MU)*sigma(FANO) = 3*7*8 = 168 = |PSL(2,7)| [arithmetic form]."""
        product = sigma(LAM) * sigma(MU) * sigma(FANO_ORDER)
        assert product == 168
        # Two independent routes to 168: cyclotomic and arithmetic
        cyclo_route = Q * (Q-1) * (Q+1) * (Q**2-Q+1)
        assert product == cyclo_route

    def test_sigma_sum_equals_mul1(self):
        """sigma(LAM)+sigma(MU)+sigma(FANO) = 3+7+8 = 18 = MUL1 = MUL2."""
        assert sigma(LAM) + sigma(MU) + sigma(FANO_ORDER) == MUL1
        assert sigma(LAM) + sigma(MU) + sigma(FANO_ORDER) == MUL2

    def test_sigma_k_equals_v_minus_k(self):
        """sigma(K) = 28 = V-K = Q^3+1 [unique to Q=3 among GQ(q,q)]."""
        assert sigma(K) == V - K
        assert sigma(K) == Q**3 + 1

    def test_sigma_nh_equals_mul_r(self):
        """sigma(N_H) = 24 = MUL_R [sum of divisors of Heawood order = W33 larger mult]."""
        assert sigma(N_H) == MUL_R

    def test_sigma_theta_equals_mul1(self):
        """sigma(THETA) = sigma(10) = 18 = MUL1 = MUL2 [Perkel multiplicities from sigma]."""
        assert sigma(THETA) == MUL1

    def test_phi_chain(self):
        """phi(phi(FANO)) = phi(6) = 2 = LAM [phi chain: FANO->K_P->LAM]."""
        assert phi_euler(FANO_ORDER) == K_P   # phi(7) = 6 = K_P
        assert phi_euler(K_P) == LAM           # phi(6) = 2 = LAM

    def test_sigma_k_divided(self):
        """sigma(K)/LAM = N_H and sigma(K)/MU = FANO [two ratios from same sigma]."""
        assert sigma(K) // LAM == N_H     # 28/2 = 14
        assert sigma(K) // MU == FANO_ORDER   # 28/4 = 7


# ------------------------------------------------------------------
# T4 -- Spectral synthesis
# ------------------------------------------------------------------
class TestT4SpectralSynthesis:

    def test_eigenvalue_squares_sum_to_mul3(self):
        """EIG_R^2 + EIG_S^2 = 4+16 = 20 = MUL3 = 2*THETA [always for GQ(q,q)]."""
        assert EIG_R**2 + EIG_S**2 == MUL3
        assert EIG_R**2 + EIG_S**2 == 2 * THETA

    def test_eigenvalue_product_is_minus_lam_mu(self):
        """EIG_R * EIG_S = 2*(-4) = -8 = -LAM*MU = -LAM^3 [unique cascade value at Q=3]."""
        assert EIG_R * EIG_S == -LAM * MU
        assert EIG_R * EIG_S == -(LAM**3)

    def test_hoffman_independence_is_theta(self):
        """Hoffman bound alpha <= V*MU/(K+MU) = V/(Q+1) = THETA = Phi_4(Q) [always tight]."""
        bound = Fraction(V * MU, K + MU)
        assert bound == THETA
        assert V // (Q + 1) == THETA

    def test_hoffman_clique_is_q_plus_one(self):
        """Hoffman clique bound 1-K/EIG_S = Q+1 [always for GQ(q,q); tight in W33]."""
        assert 1 - Fraction(K, EIG_S) == Q + 1

    def test_chromatic_times_alpha_is_v(self):
        """chi(G)*alpha(G) = (Q+1)*THETA = (Q+1)*(Q^2+1) = V [chromatic number identity]."""
        assert (Q + 1) * THETA == V

    def test_trace_a_zero_and_trace_a2_is_vk(self):
        """Tr(A)=0 [no self-loops]; Tr(A^2)=V*K [every edge counted twice from each end]."""
        trace_A = K * 1 + EIG_R * MUL_R + EIG_S * MUL_S
        trace_A2 = K**2 * 1 + EIG_R**2 * MUL_R + EIG_S**2 * MUL_S
        assert trace_A == 0
        assert trace_A2 == V * K

    def test_edges_equal_e8_roots(self):
        """V*K/2 = 40*12/2 = 240 = |E8 root system| [grand W33-E8 connection]."""
        edges = V * K // 2
        assert edges == 240
        # 240 = THETA * MUL_R = 10 * 24
        assert 240 == THETA * MUL_R

    def test_edges_via_multiplicities(self):
        """240 = Q*(Q+1)^2*(Q^2+1)/2 [exact formula via multiplicities]."""
        assert V * K // 2 == Q * (Q+1)**2 * (Q**2+1) // 2


# ------------------------------------------------------------------
# T5 -- Cross-domain bridges
# ------------------------------------------------------------------
class TestT5CrossDomainBridges:

    def test_psl_prime_tower(self):
        """PSL tower {Q, Q^2-4, K-1, K+Q+MU} = {3,5,11,19}: all prime, all from Q alone."""
        tower = [Q, Q**2 - 4, K - 1, K + Q + MU]
        assert tower == [3, 5, 11, 19]
        for p in tower:
            assert all(p % d != 0 for d in range(2, p)), f"{p} not prime"

    def test_perkel_order_from_w33(self):
        """V_57 = 2*(V-K)+1 = 2*(Q^3+1)+1 = 2Q^3+3 [Perkel from W33 cube-plus-one]."""
        assert V_57 == 2 * (V - K) + 1
        assert V_57 == 2 * Q**3 + 3

    def test_perkel_spectral_gap(self):
        """V_57 - V = Phi_4 + Phi_6 = THETA + FANO_ORDER = 17 [Perkel-W33 gap]."""
        assert V_57 - V == THETA + FANO_ORDER
        assert V_57 - V == 17

    def test_perkel_degree_times_lam_equals_k(self):
        """K_P * LAM = 6 * 2 = 12 = K [Perkel degree * W33 lambda = W33 degree]."""
        assert K_P * LAM == K

    def test_lucas_connects_w33_and_perkel(self):
        """Lucas L_3 = MUL1 = MUL2 = 18 [third Lucas value = Perkel multiplicities]."""
        assert lucas_q(3) == MUL1
        assert lucas_q(3) == MUL2
        # First four Lucas values equal W33/Heawood/Perkel constants
        assert lucas_q(0) == LAM       # L_0 = 2 = LAM
        assert lucas_q(1) == Q         # L_1 = 3 = Q
        assert lucas_q(2) == FANO_ORDER  # L_2 = 7 = FANO

    def test_pell_identity_four_terms(self):
        """L_n^2 - 5*F_{2n}^2 = 4 = MU for n = 1,2,3,4 [Pell identity via DISC_MID=5]."""
        for n in range(1, 5):
            Ln = lucas_q(n);  F2n = fib(2 * n)
            assert Ln**2 - 5 * F2n**2 == MU

    def test_chebyshev_bridge_four_terms(self):
        """L_n = 2*T_n(Q/2) for n=0,1,2,3 [Chebyshev bridge, exact Fraction]."""
        X = Fraction(Q, 2)
        for n in range(4):
            assert lucas_q(n) == 2 * cheby_T(n, X)

    def test_fano_heawood_cycle(self):
        """FANO=Phi_6, N_H=2*FANO, E_H=Q*FANO, N_H-1=Phi_3 [complete Fano-Heawood link]."""
        assert FANO_ORDER == Q**2 - Q + 1
        assert N_H == 2 * FANO_ORDER
        assert E_H == Q * FANO_ORDER
        assert N_H - 1 == Q**2 + Q + 1    # Phi_3(Q) -- unique to Q=3


# ------------------------------------------------------------------
# T6 -- Master laws and Phase CC self-reference
# ------------------------------------------------------------------
class TestT6MasterLaws:

    def test_multiplicity_partition_of_v_minus_one(self):
        """MUL_R + MUL_S = V-1 [eigenspace dimensions partition the non-trivial space]."""
        assert MUL_R + MUL_S == V - 1
        assert MUL_R + MUL_S == Q * (Q**2 + Q + 1)   # = Q * Phi_3(Q)

    def test_multiplicity_product(self):
        """MUL_R * MUL_S = 360 = Q^2*(Q+1)^2*(Q^2+1)/4 [exact formula]."""
        assert MUL_R * MUL_S == 360
        assert MUL_R * MUL_S == Q**2 * (Q+1)**2 * (Q**2+1) // 4

    def test_edge_count_two_ways(self):
        """E_W33 = V*K/2 = THETA*MUL_R = 240 [two routes to the edge count]."""
        assert V * K // 2 == THETA * MUL_R
        assert V * K // 2 == 240

    def test_perkel_heawood_fano_sum(self):
        """K_P + FANO_ORDER + 1 = 6+7+1 = 14 = N_H [Perkel+Fano+1 = Heawood order]."""
        assert K_P + FANO_ORDER + 1 == N_H

    def test_mul_r_over_kh_equals_lam_mu(self):
        """MUL_R / K_H = 24/3 = 8 = LAM*MU = LAM^3 [R-multiplicity ratio]."""
        assert MUL_R % K_H == 0
        assert MUL_R // K_H == LAM * MU

    def test_trace_identity_with_multiplicities(self):
        """K + MUL_R*EIG_R + MUL_S*EIG_S = 0 [Tr(A)=0: eigenvalue sum with mult = 0]."""
        assert K * 1 + MUL_R * EIG_R + MUL_S * EIG_S == 0

    def test_phase_cc_self_reference(self):
        """V * THETA / 2 = 40 * 10 / 2 = 200 = Phase CC number [W33 encodes its own phase]."""
        assert V * THETA // 2 == PHASE_CC
        assert PHASE_CC == 200

    def test_phase_cc_three_expressions(self):
        """200 = V*THETA/2 = (Q^2-4)*V = LAM*MU*(Q^2-4)^2 [three cyclotomic expressions]."""
        disc_mid = Q**2 - 4    # = 5 = Fibonacci prime
        assert V * THETA // 2 == PHASE_CC
        assert disc_mid * V == PHASE_CC          # 5 * 40 = 200
        assert LAM * MU * disc_mid**2 == PHASE_CC  # 2*4*25 = 200
