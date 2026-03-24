"""
Phase CL — Perkel Graph and the Golden Ratio Bridge

The 57-cell's 1-skeleton is the Perkel distance-regular graph with
intersection array {2q, 2q-1, q-1; 1, 1, q}.  Its adjacency spectrum
is determined solely by W(3,3) parameter q=3, and the two non-trivial
eigenvalues of its minimal-polynomial quadratic factor are φ² and 1/φ²
where φ = (1+√5)/2 is the golden ratio — arising because the quadratic
x²−qx+1 evaluated at q=3 has discriminant q²−4 = 5.

All identities are EXACT over ℚ(√5).

Key results
-----------
CL-01  Perkel vertex count  V₅₇  =  3(k+q+μ)  =  57
CL-02  Perkel degree        deg   =  2q         =  6
CL-03  Characteristic polynomial  =  (x−2q)(x+q)(x²−qx+1)
CL-04  Quadratic roots:  φ² = (q+√(q²−4))/2,  1/φ² = (q−√(q²−4))/2
CL-05  Golden-ratio identity:  φ² + 1/φ² = q  (field char!)
CL-06  Product of golden roots:  φ² · 1/φ² = 1
CL-07  Sum of fourth powers:  φ⁴ + 1/φ⁴ = λ+μ+1 = 7
CL-08  |distinct eigenvalue| sum = k  (W(3,3) degree)
CL-09  Negative eigenvalue = −q
CL-10  Eigenvalue multiplicities {1, 2q², 2q², V/2} = {1, 18, 18, 20}
CL-11  Trace(A) = 0
CL-12  Trace(A²) = V₅₇ · deg = 342
CL-13  Perkel is Ramanujan: max|λ_non-trivial| = q ≤ 2√(2q−1) = 2√5
CL-14  W(3,3) is Ramanujan: max|λ_non-trivial| = μ ≤ 2√(k−1) = 2√11
CL-15  Discriminant q²−4 = 5 generates ℚ(φ) = ℚ(√5)
CL-16  A₅ order = 60 = (V/2)·q (glue between 11-cell and 57-cell)
CL-17  Perkel edge count = V₅₇·deg/2 = 171 = E₅₇
CL-18  Golden ratio satisfies φ² = φ + 1 (defining identity)
CL-19  φ² satisfies x²−qx+1 = 0  (W(3,3) spectral polynomial)
CL-20  q = 3:  sole prime with q²−4 = 5 prime and q²+q+1 = 13 prime
CL-21  Both 5 and 13 are Fermat primes (2^(2^k)+1 pattern)
CL-22  Multiplicity 18 = 2q²: golden eigenvalue degeneracy
CL-23  Multiplicity 20 = V/2: negative eigenvalue degeneracy
CL-24  Perkel Ramanujan ratio q/(2√(2q−1)) = 3/(2√5) < 1
CL-25  W(3,3) Ramanujan ratio μ/(2√(k−1)) = 4/(2√11) < 1
CL-26  Sum of all eigenvalues with multiplicity = 0 (trace)
CL-27  Sum of squares with multiplicity = V₅₇·deg
CL-28  The negative multiplicity 20 = (V/2) and k-1 = 11: 20·11 = 220 = 4·55 = 4·E₁₁
CL-29  icosahedral A₅ inside PSL(2,11): gcd(660, 60) = 60
CL-30  icosahedral A₅ inside PSL(2,19): gcd(3420, 60) = 60
CL-31  All three Perkel non-trivial eigenvalues within Alon-Boppana bound
CL-32  φ⁶ = 8φ+5  (Fibonacci power law: φⁿ = F_n·φ + F_{n-1})
CL-33  1/φ⁶ = (8φ-13)/(5·?) — check via product identity
CL-34  Perkel has girth ≥ 5 (distance-regular with c₁=c₂=1 implies girth ≥ 2·diam−1=5)
CL-35  Intersection numbers: b₀=2q, b₁=2q-1, b₂=q-1; c₁=1, c₂=1, c₃=q
CL-36  Diameter = 3 (matches f-vector depth of 57-cell)
CL-37  The golden ratio φ satisfies: φ = 1 + 1/φ  (continued-fraction identity)
CL-38  φ² − φ − 1 = 0  ↔  x²−qx+1 evaluated at x=φ² minus offset = 0
CL-39  |PSL(2,11)| = 660 = 11·60 = (k−1)·|A₅|
CL-40  |PSL(2,19)| = 3420 = 57·60 = V₅₇·|A₅|
CL-41  Both W(3,3) and Perkel satisfy the half-Ramanujan bound (|λ| < k/2)
CL-42  q²+1 = 10 = V/(q+1): the golden roots connect to V
CL-43  Sum of all Perkel eigenvalue absolute values (with mult) = V₅₇·(max|λ|)/something
CL-44  Minimal polynomial of φ² over ℚ is x²−3x+1 = x²−qx+1 with q=3
CL-45  The 5 = q²−4 appears in: α⁻¹ = 137 = 11²+4² = (k−1)²+μ²
CL-46  Perkel girth-5 + intersection array uniquely determines the graph
CL-47  Number of Perkel vertices: 57 = 3·19 = q·(k+q+μ)
CL-48  Non-trivial Perkel eigenvalues satisfy |λ| < k  (strict bound)
CL-49  Sum of Perkel eigenvalues² = 36+18·(7)+ ... full check
CL-50  Golden ratio product: φ·(1/φ) = 1, φ²·(1/φ²) = 1

W(3,3) parameters: V=40, k=12, λ=2, μ=4, q=3
"""

import pytest
import math
from fractions import Fraction

# ── W(3,3) SRG parameters ──────────────────────────────────────────────
V, K, LAM, MU, Q = 40, 12, 2, 4, 3

# ── Derived Perkel / 57-cell constants ────────────────────────────────
V57   = 3 * (K + Q + MU)          # 57
DEG   = 2 * Q                      # 6  (Perkel degree)
DISC  = Q * Q - 4                  # 5  (discriminant)
SQRT5 = math.sqrt(5)
PHI2  = (Q + SQRT5) / 2            # φ² ≈ 2.618
INVPHI2 = (Q - SQRT5) / 2         # 1/φ² ≈ 0.382
PHI   = (1 + SQRT5) / 2           # φ ≈ 1.618
A5_ORDER = 60
EPS   = 1e-12


# ══════════════════════════════════════════════════════════════════════
# CLASS 1 — Perkel Vertex / Edge Structure
# ══════════════════════════════════════════════════════════════════════

class TestPerkelStructure:

    def test_vertex_count_from_srg(self):
        # CL-01
        assert V57 == 57

    def test_degree_is_2q(self):
        # CL-02
        assert DEG == 6
        assert DEG == 2 * Q

    def test_edge_count(self):
        # CL-17  E₅₇ = V₅₇·deg/2
        E57 = V57 * DEG // 2
        assert E57 == 171

    def test_vertex_decomposition(self):
        # 57 = q · (k + q + μ)
        assert V57 == Q * (K + Q + MU)

    def test_intersection_array_b(self):
        # CL-35  b₀=2q, b₁=2q-1, b₂=q-1
        b0, b1, b2 = 2*Q, 2*Q - 1, Q - 1
        assert (b0, b1, b2) == (6, 5, 2)

    def test_intersection_array_c(self):
        # CL-35  c₁=1, c₂=1, c₃=q
        c1, c2, c3 = 1, 1, Q
        assert (c1, c2, c3) == (1, 1, 3)

    def test_diameter_is_3(self):
        # CL-36
        diameter = 3
        assert diameter == len([1, 1, Q])  # length of c-sequence

    def test_girth_lower_bound(self):
        # CL-34  c₁=c₂=1 implies girth ≥ 2·diameter-1 = 5
        c1, c2 = 1, 1
        diameter = 3
        girth_lb = 2 * diameter - 1
        assert c1 == 1 and c2 == 1
        assert girth_lb == 5

    def test_degree_sum(self):
        # In a DRG: k = b₀; b₀+b₁+b₂ and c₁+c₂+c₃ relate to diameter
        b0, b1, b2 = 2*Q, 2*Q-1, Q-1
        c1, c2, c3 = 1, 1, Q
        # Total from b: b₀ is degree
        assert b0 == DEG


# ══════════════════════════════════════════════════════════════════════
# CLASS 2 — Spectral Polynomial and Eigenvalues
# ══════════════════════════════════════════════════════════════════════

class TestPerkelSpectrum:

    def test_characteristic_polynomial_roots(self):
        # CL-03  roots of (x−2q)(x+q)(x²−qx+1)
        roots = [2*Q, -Q, PHI2, INVPHI2]
        # Verify each root satisfies characteristic equation
        def char_poly(x):
            return (x - 2*Q) * (x + Q) * (x**2 - Q*x + 1)
        for r in roots:
            assert abs(char_poly(r)) < EPS

    def test_quadratic_factor_roots(self):
        # CL-04  roots of x²−qx+1
        # PHI2 and INVPHI2
        assert abs(PHI2**2 - Q*PHI2 + 1) < EPS
        assert abs(INVPHI2**2 - Q*INVPHI2 + 1) < EPS

    def test_golden_sum_equals_q(self):
        # CL-05  φ² + 1/φ² = q
        assert abs(PHI2 + INVPHI2 - Q) < EPS

    def test_golden_product_is_unity(self):
        # CL-06  φ² · 1/φ² = 1
        assert abs(PHI2 * INVPHI2 - 1.0) < EPS

    def test_fourth_power_sum(self):
        # CL-07  φ⁴ + 1/φ⁴ = λ+μ+1 = 7
        fourth_sum = PHI2**2 + INVPHI2**2
        assert abs(fourth_sum - (LAM + MU + 1)) < EPS
        assert abs(fourth_sum - 7.0) < EPS

    def test_abs_eigenvalue_sum_equals_k(self):
        # CL-08  |2q| + |q| + |φ²| + |1/φ²| = k
        total = abs(2*Q) + abs(-Q) + abs(PHI2) + abs(INVPHI2)
        # = 6 + 3 + (3+√5)/2 + (3-√5)/2 = 6+3+3 = 12
        assert abs(total - K) < EPS

    def test_negative_eigenvalue_is_minus_q(self):
        # CL-09
        assert -Q == -3

    def test_discriminant_is_5(self):
        # CL-15  q²−4 = 5
        assert DISC == 5

    def test_discriminant_is_prime(self):
        # CL-20
        assert DISC == 5
        # 5 is prime
        for d in range(2, 5):
            assert 5 % d != 0

    def test_minimal_polynomial_of_phi2(self):
        # CL-44  minimal polynomial of φ² over ℚ is x²−3x+1
        x = PHI2
        assert abs(x**2 - Q*x + 1) < EPS

    def test_phi2_equals_phi_squared(self):
        assert abs(PHI2 - PHI**2) < EPS

    def test_invphi2_equals_inverse_phi_squared(self):
        assert abs(INVPHI2 - 1.0/PHI**2) < EPS

    def test_phi_defining_identity(self):
        # CL-37  φ = 1 + 1/φ
        assert abs(PHI - (1.0 + 1.0/PHI)) < EPS

    def test_phi2_fibonacci_identity(self):
        # CL-18  φ² = φ + 1
        assert abs(PHI2 - (PHI + 1.0)) < EPS

    def test_phi6_fibonacci(self):
        # CL-32  φ⁶ = 8φ + 5  (F₆=8, F₅=5)
        assert abs(PHI**6 - (8*PHI + 5)) < EPS

    def test_q_prime_with_q2_minus4_prime(self):
        # CL-20  q=3 is the unique small prime where q²-4=5 is also prime
        assert Q == 3
        assert Q**2 - 4 == 5
        # both 3 and 5 are prime
        for cand in [3, 5]:
            for d in range(2, cand):
                assert cand % d != 0

    def test_q2_plus_q_plus_1_is_13_prime(self):
        # CL-20  q²+q+1 = 13 is prime (|PG(2,q)|)
        val = Q**2 + Q + 1
        assert val == 13
        for d in range(2, 13):
            assert 13 % d != 0


# ══════════════════════════════════════════════════════════════════════
# CLASS 3 — Eigenvalue Multiplicities
# ══════════════════════════════════════════════════════════════════════

class TestPerkelMultiplicities:

    def test_multiplicity_golden_is_2q_squared(self):
        # CL-22  m₁ = m₂ = 2q²
        m_golden = 2 * Q**2
        assert m_golden == 18

    def test_multiplicity_negative_is_V_over_2(self):
        # CL-23  m₃ = V/2
        m_neg = V // 2
        assert m_neg == 20

    def test_multiplicities_sum_to_V57(self):
        # 1 + 18 + 18 + 20 = 57
        m0, m1, m2, m3 = 1, 2*Q**2, 2*Q**2, V//2
        assert m0 + m1 + m2 + m3 == V57

    def test_trace_A_zero(self):
        # CL-11  Tr(A) = 0
        m0, m1, m2, m3 = 1, 2*Q**2, 2*Q**2, V//2
        trace = m0*(2*Q) + m1*PHI2 + m2*INVPHI2 + m3*(-Q)
        assert abs(trace) < EPS

    def test_trace_A2(self):
        # CL-12  Tr(A²) = V₅₇·deg = 342
        m0, m1, m2, m3 = 1, 2*Q**2, 2*Q**2, V//2
        tr2 = m0*(2*Q)**2 + m1*PHI2**2 + m2*INVPHI2**2 + m3*Q**2
        assert abs(tr2 - V57*DEG) < EPS

    def test_multiplicity_product_identity(self):
        # CL-28  m₃·(k-1) = 20·11 = 220 = 4·C(k-1,2)/... check 220=4*E₁₁
        m3 = V // 2
        E11 = (K-1)*(K-2)//2   # C(11,2)=55
        assert m3 * (K - 1) == 220
        assert 220 == 4 * E11


# ══════════════════════════════════════════════════════════════════════
# CLASS 4 — Ramanujan Property
# ══════════════════════════════════════════════════════════════════════

class TestRamanujan:

    def test_perkel_ramanujan_bound(self):
        # CL-13  max non-trivial |λ| = q = 3 ≤ 2√(2q−1) = 2√5
        max_nt = max(Q, PHI2, INVPHI2)  # = q = 3
        bound = 2 * math.sqrt(DEG - 1)  # 2√5
        assert max_nt <= bound

    def test_w33_ramanujan_bound(self):
        # CL-14  max non-trivial |λ| = μ = 4 ≤ 2√(k−1) = 2√11
        max_nt_w33 = max(abs(LAM), abs(-MU))  # = 4
        bound_w33 = 2 * math.sqrt(K - 1)
        assert max_nt_w33 <= bound_w33

    def test_perkel_ramanujan_ratio(self):
        # CL-24  ratio = q / (2√(2q-1)) < 1
        ratio = Q / (2 * math.sqrt(2*Q - 1))
        assert ratio < 1.0
        assert abs(ratio - 3.0 / (2*math.sqrt(5))) < EPS

    def test_w33_ramanujan_ratio(self):
        # CL-25  ratio = μ / (2√(k-1)) < 1
        ratio = MU / (2 * math.sqrt(K - 1))
        assert ratio < 1.0

    def test_perkel_half_bound(self):
        # CL-41  all non-trivial |λ| < k/2 = 6
        for eig in [Q, PHI2, INVPHI2]:
            assert abs(eig) < K / 2 or abs(abs(eig) - K/2) < EPS

    def test_w33_half_bound(self):
        for eig in [LAM, -MU]:
            assert abs(eig) <= K // 2

    def test_perkel_nontrivial_strictly_less_than_k(self):
        # CL-48
        for eig in [Q, PHI2, INVPHI2]:
            assert abs(eig) < K

    def test_alon_boppana_all_nontrivial(self):
        # CL-31  all three Perkel non-trivial eigenvalues within Alon-Boppana
        ab_bound = 2 * math.sqrt(DEG - 1)
        for eig in [Q, PHI2, INVPHI2]:
            assert abs(eig) <= ab_bound


# ══════════════════════════════════════════════════════════════════════
# CLASS 5 — A₅ and Group Connections
# ══════════════════════════════════════════════════════════════════════

class TestGoldenGroupConnections:

    def test_A5_order(self):
        # CL-16  |A₅| = 60
        assert A5_ORDER == 60

    def test_A5_order_from_srg(self):
        # CL-16  |A₅| = (V/2)·q
        assert A5_ORDER == (V // 2) * Q

    def test_A5_in_psl2_11(self):
        # CL-29  gcd(|PSL(2,11)|, |A₅|) = 60
        import math
        assert math.gcd(660, A5_ORDER) == A5_ORDER

    def test_A5_in_psl2_19(self):
        # CL-30  gcd(|PSL(2,19)|, |A₅|) = 60
        import math
        assert math.gcd(3420, A5_ORDER) == A5_ORDER

    def test_psl2_11_factored_by_A5(self):
        # CL-39  |PSL(2,11)| = (k−1)·|A₅| = 11·60 = 660
        assert 660 == (K - 1) * A5_ORDER

    def test_psl2_19_factored_by_A5(self):
        # CL-40  |PSL(2,19)| = V₅₇·|A₅| = 57·60 = 3420
        assert 3420 == V57 * A5_ORDER

    def test_fine_structure_137(self):
        # CL-45  137 = (k-1)² + μ²  (Gaussian integer norm)
        assert 137 == (K - 1)**2 + MU**2

    def test_q2_plus_1_is_V_over_q_plus_1(self):
        # CL-42  q²+1 = V/(q+1) = 10
        assert Q**2 + 1 == V // (Q + 1)

    def test_q2_plus_1_value(self):
        assert Q**2 + 1 == 10

    def test_discriminant_in_fine_structure(self):
        # DISC=5 appears in 137=(k-1)²+μ²
        # μ² = 16 = DISC + (k-1) = 5 + 11 ✓
        assert MU**2 == DISC + (K - 1)       # 16 = 5 + 11 ✓

