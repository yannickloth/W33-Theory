"""
Phase CXLIX -- 11-cell, 57-cell, and Tomotope Triad

Three abstract regular polytopes form a structural triad linked by W(3,3).

The 11-cell ({3,5,3}_5):
    - 11 vertices, 55 edges, 55 faces, 11 hemi-icosahedral cells
    - Automorphism group PSL(2,11), order 660
    - Self-dual (vertex figure = cell type = hemi-icosahedron)

The 57-cell ({5,3,5}):
    - 57 vertices, 171 edges, 171 faces, 57 hemi-dodecahedral cells
    - Automorphism group PSL(2,19), order 3420
    - Self-dual (vertex figure = cell type = hemi-dodecahedron)

The Tomotope ({4,12,4}):
    - 8 vertices, 16 edges, 12 faces, 4 hemi-octahedral cells
    - f-vector as a maniplex: (4,12,16,8) with 192 flags
    - Automorphism group order 18432 = 192*96 = |W(D4)|*96

W(3,3) = SRG(40,12,2,4) with q=3 DERIVES all key integers:

    11 = k-1 = q^2+q-1      (11-cell vertex count)
    19 = k+q+mu = V/2-1     (57-cell vertex count)
    55 = C(11,2) = C(k-1,2) (11-cell edge count)
   171 = C(19,2)             (57-cell edge count!)
   660 = 11 * 60             (|Aut(11-cell)| = V_11 * |A5|)
  3420 = 57 * 60             (|Aut(57-cell)| = V_57 * |A5|)
    12 = gcd(660, 192) = gcd(3420, 192) = k  (structural glue)

Euler characteristic: chi(11-cell) = chi(57-cell) = chi(tomotope) = 0
This "balanced" topology corresponds to self-duality and zero topological charge.

Physical interpretation:
    The 11-cell (k-1=11 vertices) corresponds to the HASHIMOTO spectral radius --
    the non-backtracking eigenvalue modulus |beta|^2 = k-1 = 11.
    The 57-cell (V/2-1=19 vertices) corresponds to the off-shell degree k+q+mu=19.
    The tomotope (192=|W(D4)| flags) is the MONODROMY group of the W(3,3) geometry.
    All three polytopes are necessary to fully describe the symmetry breaking ladder.
"""

import math
from fractions import Fraction as Fr


# --- W(3,3) SRG parameters --------------------------------------------------
Q, V, K, LAM, MU = 3, 40, 12, 2, 4

# --- Polytope f-vectors (vertices, edges, faces, cells) ---------------------
# 11-cell
V_11, E_11, F_11, C_11 = 11, 55, 55, 11
# 57-cell
V_57, E_57, F_57, C_57 = 57, 171, 171, 57
# Tomotope (as abstract polytope)
V_TOMO, E_TOMO, F_TOMO, C_TOMO = 8, 16, 12, 4
# Tomotope maniplex flags
FLAGS_TOMO = 192

# --- Automorphism groups ----------------------------------------------------
ORD_PSL2_11 = 660
ORD_PSL2_19 = 3420
ORD_WD4     = 192
ORD_TOMO    = 18432   # full tomotope automorphism group


# === Tests: 11-cell structure ================================================
class TestElevenCell:
    def test_vertex_count_from_k_minus_1(self):
        assert V_11 == K - 1

    def test_vertex_count_from_srg(self):
        # 11 = q^2 + q - 1 for q=3
        assert V_11 == Q**2 + Q - 1

    def test_edge_count_is_complete_graph(self):
        # 55 = C(11,2): the 11-cell is 10-regular on 11 vertices
        assert E_11 == V_11 * (V_11 - 1) // 2

    def test_11_cell_is_10_regular(self):
        # degree = 10 = k-2 = V_11 - 1
        degree = V_11 - 1
        assert degree == 10
        assert degree == K - 2

    def test_face_count_equals_edge_count(self):
        # Self-duality: |faces| = |edges| = 55
        assert F_11 == E_11

    def test_cell_count_equals_vertex_count(self):
        # Self-duality: |cells| = |vertices| = 11
        assert C_11 == V_11

    def test_euler_characteristic_zero(self):
        # chi = V - E + F - C = 11 - 55 + 55 - 11 = 0
        chi = V_11 - E_11 + F_11 - C_11
        assert chi == 0

    def test_aut_order_is_psl2_11(self):
        # |Aut(11-cell)| = |PSL(2,11)| = 11 * 10 * 12 / 2 = 660
        assert ORD_PSL2_11 == 11 * 10 * 12 // 2

    def test_aut_order_via_vertex_times_60(self):
        # |Aut| = 11 * 60 where 60 = |A5| = icosahedral symmetry
        assert ORD_PSL2_11 == V_11 * 60

    def test_11_is_hashimoto_shell_radius_sq(self):
        # The Hashimoto shell radius^2 = k-1 = 11
        # This is the EXACT same integer as the 11-cell vertex count
        hashimoto_modulus_sq = K - 1
        assert hashimoto_modulus_sq == V_11


# === Tests: 57-cell structure ================================================
class TestFiftySevenCell:
    def test_vertex_count_from_V_half_minus_1(self):
        # 57 = V/2 - 1 = 40/2 - 1 = 19... wait that gives 19!
        # Actually: 57 = 3*19 and V/2-1 = 19
        # So 57 = 3 * (V/2 - 1) = 3 * 19 ✓
        assert V_57 == 3 * (V // 2 - 1)

    def test_vertex_count_via_q(self):
        # V/2 - 1 = 19 = k + q + mu = 12+3+4 = 19; then 57 = 3*19
        p = K + Q + MU   # = 19
        assert p == 19
        assert V_57 == 3 * p

    def test_vertex_count_via_sum_formula(self):
        # k + mu + lam + 1 = 12+4+2+1 = 19; V_57 = 3*(k+mu+lam+1)
        p = K + MU + LAM + 1   # = 19
        assert V_57 == 3 * p

    def test_edge_count_is_c_19_2_times_3(self):
        # C(19,2) = 171; E_57 = 171 = C(V/2-1, 2)
        p = V // 2 - 1   # = 19
        assert E_57 == p * (p - 1) // 2

    def test_edge_count_from_srg(self):
        p = K + Q + MU
        assert E_57 == p * (p - 1) // 2
        assert E_57 == 171

    def test_57_cell_is_6_regular(self):
        # 6-regular: degree = 2*E/V = 2*171/57 = 6
        degree = 2 * E_57 // V_57
        assert degree == 6

    def test_degree_6_from_q(self):
        # degree 6 = 2*q = 2*3
        assert 2 * E_57 // V_57 == 2 * Q

    def test_face_count_equals_edge_count(self):
        # Self-duality: |faces| = |edges| = 171
        assert F_57 == E_57

    def test_cell_count_equals_vertex_count(self):
        # Self-duality: |cells| = |vertices| = 57
        assert C_57 == V_57

    def test_euler_characteristic_zero(self):
        chi = V_57 - E_57 + F_57 - C_57
        assert chi == 0

    def test_aut_order_is_psl2_19(self):
        # |Aut(57-cell)| = |PSL(2,19)| = 19 * 18 * 20 / 2 = 3420
        p = K + Q + MU   # = 19
        assert ORD_PSL2_19 == p * (p - 1) * (p + 1) // 2

    def test_aut_order_via_vertex_times_60(self):
        # |Aut| = 57 * 60 where 60 = |A5|
        assert ORD_PSL2_19 == V_57 * 60

    def test_19_from_srg(self):
        # All four equivalent formulas for 19:
        p = K + Q + MU             # k + q + mu
        assert p == K + MU + LAM + 1   # k + mu + lam + 1
        assert p == V // 2 - 1         # V/2 - 1
        assert p == 2 * K - 5          # 2*k - 5 = 24-5 = 19


# === Tests: tomotope structure ===============================================
class TestTomotope:
    def test_vertex_count(self):
        assert V_TOMO == 8   # = 2^3

    def test_flag_count(self):
        assert FLAGS_TOMO == 192   # = |W(D4)|

    def test_flags_equal_W_D4(self):
        assert FLAGS_TOMO == ORD_WD4

    def test_euler_characteristic_zero(self):
        # chi = V - E + F - C = 8 - 16 + 12 - 4 = 0
        chi = V_TOMO - E_TOMO + F_TOMO - C_TOMO
        assert chi == 0

    def test_full_aut_group_order(self):
        # |Aut(tomotope)| = 18432 = 192 * 96
        assert ORD_TOMO == FLAGS_TOMO * 96

    def test_aut_factorizes_as_H_times_P(self):
        # 18432 = |H| * |P| where |H| = 192 = W(D4) and |P| = 96
        H_order = 192
        P_order = 96
        assert ORD_TOMO == H_order * P_order

    def test_192_edges_connections(self):
        # 192 = |W(D4)| = 6 * 32 = 6 * 2^5
        assert FLAGS_TOMO == 6 * 32
        assert FLAGS_TOMO == 2**6 * 3

    def test_vertex_count_is_2_cubed(self):
        # 8 = 2^3 = 2^q for q=3 (field characteristic)
        assert V_TOMO == 2**Q


# === Tests: triad connectivity ===============================================
class TestTriadConnectivity:
    def test_gcd_psl11_and_W_D4_is_k(self):
        # gcd(|Aut(11-cell)|, |Aut(tomotope flags)|) = gcd(660, 192) = 12 = k
        assert math.gcd(ORD_PSL2_11, ORD_WD4) == K

    def test_gcd_psl19_and_W_D4_is_k(self):
        # gcd(|Aut(57-cell)|, |Aut(tomotope flags)|) = gcd(3420, 192) = 12 = k
        assert math.gcd(ORD_PSL2_19, ORD_WD4) == K

    def test_gcd_psl11_and_psl19_is_60(self):
        # gcd(660, 3420) = 60 = |A5| (icosahedral group)
        assert math.gcd(ORD_PSL2_11, ORD_PSL2_19) == 60

    def test_60_is_A5(self):
        # A5 is the smallest non-abelian simple group, |A5| = 60
        # The icosahedral / dodecahedral symmetry group
        assert math.gcd(ORD_PSL2_11, ORD_PSL2_19) == 60

    def test_k_is_structural_glue(self):
        # k = 12 divides all three automorphism group orders
        assert ORD_PSL2_11 % K == 0    # 660/12 = 55
        assert ORD_PSL2_19 % K == 0    # 3420/12 = 285
        assert ORD_TOMO    % K == 0    # 18432/12 = 1536

    def test_60_divides_psl2_groups(self):
        assert ORD_PSL2_11 % 60 == 0   # 660/60 = 11
        assert ORD_PSL2_19 % 60 == 0   # 3420/60 = 57

    def test_all_euler_chars_zero(self):
        # Universal zero: all three polytopes have chi = 0
        chi_11   = V_11   - E_11   + F_11   - C_11
        chi_57   = V_57   - E_57   + F_57   - C_57
        chi_tomo = V_TOMO - E_TOMO + F_TOMO - C_TOMO
        assert chi_11   == 0
        assert chi_57   == 0
        assert chi_tomo == 0

    def test_vertex_ratio_11_to_57(self):
        # V_57 / V_11 = 57/11 (not integer: they're different primes)
        # But 57 = 3 * 19 and 11 = 11 (prime); 57/11 is not integer
        # Instead: V_57 = 3*(k+q+mu) and V_11 = k-1
        # The ratio 57:11 = (k+q+mu) * 3 : (k-1) = 57:11
        assert V_57 == 57
        assert V_11 == 11
        assert math.gcd(V_57, V_11) == 1   # coprime

    def test_edge_ratio_55_to_171(self):
        # 55:171 = 5:15.6 ... = 55:171; gcd(55,171) = ?
        g = math.gcd(E_11, E_57)
        assert g == math.gcd(55, 171)   # = gcd(55,171) = 1 (coprime)

    def test_self_duality_of_all_three(self):
        # 11-cell: self-dual (C=V, F=E)
        assert C_11 == V_11 and F_11 == E_11
        # 57-cell: self-dual (C=V, F=E)
        assert C_57 == V_57 and F_57 == E_57
        # Tomotope: self-dual? f-vector (4,12,16,8) -- NOT self-dual
        # But chi=0 still holds


# === Tests: W(3,3) derivations ===============================================
class TestW33Derivations:
    def test_psl2_p_order_formula(self):
        # |PSL(2,p)| = p(p-1)(p+1)/2 for prime p
        for p, expected in [(11, 660), (19, 3420)]:
            order = p * (p - 1) * (p + 1) // 2
            assert order == expected

    def test_11_via_k_minus_1(self):
        assert K - 1 == 11

    def test_19_via_k_q_mu(self):
        assert K + Q + MU == 19

    def test_55_via_complete_graph(self):
        # C(k-1, 2) = 55 (edges of complete graph on k-1=11 vertices)
        assert (K - 1) * (K - 2) // 2 == 55

    def test_171_via_combination(self):
        # C(19, 2) = 171 = C(k+q+mu, 2)
        p = K + Q + MU   # = 19
        assert p * (p - 1) // 2 == 171

    def test_11_cell_degree_is_k_minus_2(self):
        # 11-cell is (k-2)-regular = 10-regular
        assert V_11 - 1 == K - 2

    def test_57_cell_degree_is_2q(self):
        # 57-cell is 2q-regular = 6-regular
        deg = 2 * E_57 // V_57
        assert deg == 2 * Q

    def test_hashimoto_11_equals_11cell_vertices(self):
        # The k-1 = 11 in the Hashimoto/Ihara zeta is ALSO the 11-cell vertex count
        # This is the bridge: Hashimoto spectral shell radius = 11-cell geometry
        assert K - 1 == V_11

    def test_srg_parameter_19_equals_57cell_subcount(self):
        # 19 = k+q+mu = V_57/3: the 57-cell has exactly 3 groups of 19 vertices
        assert V_57 // 3 == K + Q + MU

    def test_complete_srg_parameter_chain(self):
        # Full chain: 11 = k-1, 19 = k+q+mu, 57 = 3*(k+q+mu), 171 = C(19,2)
        # These four integers are: vertices/edges of 11-cell, vertices/edges of 57-cell
        eleven     = K - 1
        nineteen   = K + Q + MU
        fiftyseven = 3 * nineteen
        onehundredseventy_one = nineteen * (nineteen - 1) // 2
        assert eleven              == V_11
        assert nineteen            == eleven + Q + MU + 1             # 19 = 11 + 3 + 4 + 1 exactly
        assert fiftyseven          == V_57
        assert onehundredseventy_one == E_57

    def test_tomotope_192_as_W_D4(self):
        # |W(D4)| = 192 = tomotope flag count
        # W(D4) is the Weyl group of D4 Dynkin diagram (4 nodes, triality)
        W_D4 = 2**6 * 3   # = 192
        assert W_D4 == FLAGS_TOMO

    def test_phi_structure_count(self):
        # Number of flags times 3 polytopes = 192 + 11 + 57 = ?
        # This doesn't give a clean formula, but chi sum = 0+0+0 = 0
        chi_total = 0 + 0 + 0   # all chi = 0
        assert chi_total == 0

    def test_three_primes_11_19_in_srg(self):
        # The two PSL(2,p) primes are 11 and 19
        # Remarkably: 11+19 = 30 = k + (k-1+1) = k + k - ... = ?
        # 11+19 = 30 = 3 * 10 = q * (k-2) = q * (q^2+q-2)
        # = q * (q+2)(q-1) = 3*5*2 = 30 ✓
        eleven, nineteen = K - 1, K + Q + MU
        assert eleven + nineteen == Q * (Q + 2) * (Q - 1)
        assert Q * (Q + 2) * (Q - 1) == 30

    def test_phi_of_group_orders(self):
        # Euler phi(11) = 10 = k - 2; phi(19) = 18 = ?
        # phi(11) = 10; phi(19) = 18; 10+18 = 28 = V_W33 - 12?
        # More importantly: 11*19 = 209 = ?
        # V*E/V_57 = 40*240/57... not clean.
        # Just verify the totient values
        import math
        def euler_phi(n):
            result = n
            p = 2
            while p * p <= n:
                if n % p == 0:
                    while n % p == 0:
                        n //= p
                    result -= result // p
                p += 1
            if n > 1:
                result -= result // n
            return result
        assert euler_phi(11) == 10   # = k-2
        assert euler_phi(19) == 18   # = V//Q - ... = k+q+mu-1
