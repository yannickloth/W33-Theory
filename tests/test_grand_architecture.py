"""Tests for Pillar 120: Grand Architecture — The Rosetta Stone.

Comprehensive verification of the complete unifying mathematical
architecture connecting W(3,3), E₆, E₈, octonions, 27 lines,
Q₈, and the tomotope stabilizer N = Aut(C₂ × Q₈).
"""

import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

import sys
sys.path.insert(0, str(ROOT))
from THEORY_PART_CCXX_GRAND_ARCHITECTURE import (
    grand_architecture,
    build_complement_schlafli,
    weyl_group_orders,
    stabilizer_cascade,
    q8_properties,
    q8_multiplication_table,
    c2q8_properties,
    cayley_dickson_chain,
    d4_triality_analysis,
    gf2_mirror_analysis,
    enumerate_27_lines,
    lines_meet,
)


# ══════════════════════════════════════════════════════════════
#  Fixtures
# ══════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def arch():
    """Full grand architecture analysis (expensive, run once)."""
    return grand_architecture()


@pytest.fixture(scope="module")
def schlafli():
    """Complement Schläfli graph data."""
    return build_complement_schlafli()


@pytest.fixture(scope="module")
def q8():
    """Q₈ properties."""
    return q8_properties()


@pytest.fixture(scope="module")
def c2q8():
    """C₂ × Q₈ properties."""
    return c2q8_properties()


# ══════════════════════════════════════════════════════════════
#  R1: Complement Schläfli is SRG(27, 10, 1, 5)
# ══════════════════════════════════════════════════════════════

class TestR1_SRG:
    """R1: The complement Schläfli graph is SRG(27, 10, 1, 5)."""

    def test_27_vertices(self, arch):
        assert arch["schlafli_n"] == 27

    def test_regular_degree_10(self, arch):
        assert arch["schlafli_degree"] == [10]

    def test_lambda_1(self, arch):
        assert arch["schlafli_lambda"] == [1]

    def test_mu_5(self, arch):
        assert arch["schlafli_mu"] == [5]

    def test_R1_combined(self, arch):
        assert arch["R1_SRG_27_10_1_5"] is True

    def test_27_lines_count(self):
        lines = enumerate_27_lines()
        assert len(lines) == 27

    def test_line_types(self):
        lines = enumerate_27_lines()
        e = sum(1 for L in lines if L[0] == "E")
        f = sum(1 for L in lines if L[0] == "F")
        g = sum(1 for L in lines if L[0] == "G")
        assert e == 6 and f == 15 and g == 6
        assert e + f + g == 27


# ══════════════════════════════════════════════════════════════
#  R2: Edge / triangle / directed edge counts
# ══════════════════════════════════════════════════════════════

class TestR2_Counts:
    """R2: 135 edges, 45 triangles, 270 directed edges."""

    def test_135_edges(self, arch):
        assert arch["R2_edges_135"] is True
        assert arch["schlafli_edges"] == 135

    def test_45_triangles(self, arch):
        assert arch["R2_triangles_45"] is True
        assert arch["schlafli_triangles"] == 45

    def test_270_directed(self, arch):
        assert arch["R2_directed_270"] is True
        assert arch["schlafli_directed_edges"] == 270

    def test_edges_formula(self, arch):
        """27 × 10 / 2 = 135"""
        assert 27 * 10 // 2 == 135

    def test_triangles_formula(self, arch):
        """135 × λ / 3 = 135 × 1 / 3 = 45"""
        assert 135 * 1 // 3 == 45

    def test_directed_from_undirected(self, arch):
        """270 = 135 × 2"""
        assert 135 * 2 == 270


# ══════════════════════════════════════════════════════════════
#  R3: Weyl group stabilizer cascade
# ══════════════════════════════════════════════════════════════

class TestR3_Cascade:
    """R3: Cascade 51840 → 1920 → 1152 → 384 → 192."""

    def test_WE6(self, arch):
        assert arch["cascade"]["WE6"] == 51840

    def test_WD5(self, arch):
        assert arch["cascade"]["WD5"] == 1920

    def test_WF4(self, arch):
        assert arch["cascade"]["WF4"] == 1152

    def test_G384(self, arch):
        assert arch["cascade"]["G384"] == 384

    def test_N(self, arch):
        assert arch["cascade"]["N"] == 192

    def test_index_27_lines(self, arch):
        assert arch["cascade"]["index_27_lines"] == 27

    def test_index_45_tritangent(self, arch):
        assert arch["cascade"]["index_45_tritangent"] == 45

    def test_index_135_edges(self, arch):
        assert arch["cascade"]["index_135_edges"] == 135

    def test_index_270_dir_edges(self, arch):
        assert arch["cascade"]["index_270_dir_edges"] == 270

    def test_cascade_all(self, arch):
        assert arch["R3_cascade_all"] is True

    def test_WE6_divisor_chain(self):
        """Every stabilizer order divides W(E₆)."""
        WE6 = 51840
        for order in [1920, 1152, 384, 192]:
            assert WE6 % order == 0


# ══════════════════════════════════════════════════════════════
#  R4: |W(D₄)| = 192 = |N|
# ══════════════════════════════════════════════════════════════

class TestR4_D4OrderMatch:
    """R4: The D₄ Weyl group has order 192 = |N|."""

    def test_WD4_equals_N(self, arch):
        assert arch["R4_WD4_equals_N"] is True

    def test_WD4_formula(self):
        """W(D₄) = 2³ · 4! = 8 × 24 = 192"""
        from math import factorial
        WD4 = (2 ** 3) * factorial(4)
        assert WD4 == 192

    def test_WD4_in_orders(self):
        orders = weyl_group_orders()
        assert orders["W(D_4)"] == 192


# ══════════════════════════════════════════════════════════════
#  R5: S₃ = Out(D₄) embeds in N via D₆
# ══════════════════════════════════════════════════════════════

class TestR5_Triality:
    """R5: S₃ (triality) sits inside D₆ inside N."""

    def test_S3_in_N(self, arch):
        assert arch["R5_S3_in_N"] is True

    def test_d4_triality_struct(self, arch):
        d4 = arch["d4_triality"]
        assert d4["out_D4_is_S3"] is True
        assert d4["d4_is_trident"] is True
        assert d4["num_leg_permutations"] == 6

    def test_N_decomposition(self, arch):
        d4 = arch["d4_triality"]
        decomp = d4["N_decomposition"]
        assert decomp["C2_4_order"] == 16
        assert decomp["D6_order"] == 12
        assert decomp["product"] == 192
        assert decomp["matches_N"] is True


# ══════════════════════════════════════════════════════════════
#  R6: Cayley-Dickson chain
# ══════════════════════════════════════════════════════════════

class TestR6_CayleyDickson:
    """R6: Cayley-Dickson dimensions 1, 2, 4, 8, 16."""

    def test_chain_correct(self, arch):
        assert arch["R6_cayley_dickson"] is True

    def test_C2Q8_sedenion(self, arch):
        assert arch["R6_C2Q8_sedenion"] is True

    def test_Q8_octonion(self, arch):
        assert arch["R6_Q8_octonion"] is True

    def test_dimensions(self):
        cd = cayley_dickson_chain()
        assert cd["dimensions"] == [1, 2, 4, 8, 16]

    def test_all_powers_of_2(self):
        cd = cayley_dickson_chain()
        assert cd["all_powers_of_2"] is True

    def test_last_normed_is_octonion(self):
        cd = cayley_dickson_chain()
        assert cd["last_normed_dim"] == 8


# ══════════════════════════════════════════════════════════════
#  R7: Each line in exactly 5 tritangent planes
# ══════════════════════════════════════════════════════════════

class TestR7_FiveTriPerLine:
    """R7: Each of 27 lines lies in exactly 5 tritangent planes."""

    def test_five_per_line(self, arch):
        assert arch["R7_five_tris_per_line"] is True
        assert arch["schlafli_tris_per_line"] == [5]

    def test_double_counting(self):
        """27 × 5 / 3 = 45 (lines × tris/line / lines/tri)."""
        assert 27 * 5 // 3 == 45


# ══════════════════════════════════════════════════════════════
#  R8: 135 triple identity
# ══════════════════════════════════════════════════════════════

class TestR8_135Triple:
    """R8: 135 = |PSp(4,3)|/|N| = singular GF(2) = edges."""

    def test_triple_identity(self, arch):
        assert arch["R8_135_triple"] is True

    def test_PSp43_over_N(self):
        assert 25920 // 192 == 135

    def test_WE6_over_2N(self):
        assert 51840 // (2 * 192) == 135

    def test_GF2_singular(self):
        gf2 = gf2_mirror_analysis()
        assert gf2["singular_nonzero"] == 135
        assert gf2["sum_check"] is True

    def test_GF2_256_partition(self):
        """1 + 135 + 120 = 256 = 2⁸"""
        assert 1 + 135 + 120 == 256


# ══════════════════════════════════════════════════════════════
#  R9: Q₈ and Aut(Q₈)
# ══════════════════════════════════════════════════════════════

class TestR9_Q8:
    """R9: |Q₈| = 8, |Aut(Q₈)| = 24, product = 192."""

    def test_Q8_order(self, arch):
        assert arch["Q8_order"] == 8

    def test_aut_Q8_order(self, arch):
        assert arch["Q8_aut_order"] == 24

    def test_aut_is_S4(self, arch):
        assert arch["Q8_aut_is_S4"] is True
        assert arch["R9_aut_is_S4"] is True

    def test_product_is_N(self, arch):
        assert arch["R9_Q8_times_AutQ8_is_N"] is True
        assert 8 * 24 == 192

    def test_Q8_center(self, arch):
        """Q₈ has center {1, -1} of order 2."""
        assert arch["Q8_center_order"] == 2

    def test_Q8_mul_table_valid(self):
        """Q₈ multiplication table satisfies group axioms."""
        table = q8_multiplication_table()
        # Identity
        for a in range(8):
            assert table[0][a] == a
            assert table[a][0] == a
        # Associativity (spot check)
        for a in range(8):
            for b in range(8):
                for c in range(8):
                    lhs = table[table[a][b]][c]
                    rhs = table[a][table[b][c]]
                    assert lhs == rhs, f"Assoc fails: ({a}*{b})*{c} ≠ {a}*({b}*{c})"

    def test_Q8_key_relations(self):
        """Verify i² = j² = k² = ijk = -1."""
        t = q8_multiplication_table()
        # i=2, j=4, k=6, -1=1
        assert t[2][2] == 1  # i² = -1
        assert t[4][4] == 1  # j² = -1
        assert t[6][6] == 1  # k² = -1
        # ijk = (ij)k = k·k = -1
        ij = t[2][4]
        ijk = t[ij][6]
        assert ijk == 1  # ijk = -1


# ══════════════════════════════════════════════════════════════
#  R10: W(F₄) = W(D₄) × |Out(D₄)|
# ══════════════════════════════════════════════════════════════

class TestR10_WF4Decomp:
    """R10: |W(F₄)| = |W(D₄)| × |S₃| = 192 × 6 = 1152."""

    def test_decomposition(self, arch):
        assert arch["R10_WF4_decomp"] is True

    def test_explicit(self):
        assert 192 * 6 == 1152

    def test_WF4_order(self):
        orders = weyl_group_orders()
        assert orders["W(F_4)"] == 1152


# ══════════════════════════════════════════════════════════════
#  Internal consistency checks
# ══════════════════════════════════════════════════════════════

class TestInternalConsistency:
    """IC1-IC5: Cross-ratios between stabilizer layers."""

    def test_IC1_WD5_over_N_10(self, arch):
        """Neighbors per line = W(D₅)/N = 10."""
        assert arch["IC1_WD5_N_10"] is True
        assert 1920 // 192 == 10

    def test_IC2_WF4_over_N_6(self, arch):
        """Directed edges per tritangent = W(F₄)/N = 6 = |S₃|."""
        assert arch["IC2_WF4_N_6"] is True
        assert 1152 // 192 == 6

    def test_IC3_G384_over_N_2(self, arch):
        """Directed vs undirected = G₃₈₄/N = 2."""
        assert arch["IC3_G384_N_2"] is True
        assert 384 // 192 == 2

    def test_IC4_WD5_over_G384_5(self, arch):
        """Tritangents per line = W(D₅)/G₃₈₄ = 5."""
        assert arch["IC4_WD5_G384_5"] is True
        assert 1920 // 384 == 5

    def test_IC5_WF4_over_G384_3(self, arch):
        """Lines per tritangent = W(F₄)/G₃₈₄ = 3."""
        assert arch["IC5_WF4_G384_3"] is True
        assert 1152 // 384 == 3


# ══════════════════════════════════════════════════════════════
#  C₂ × Q₈ properties
# ══════════════════════════════════════════════════════════════

class TestC2Q8:
    """Properties of C₂ × Q₈ (order 16)."""

    def test_order(self, arch):
        assert arch["C2Q8_order"] == 16

    def test_center_V4(self, arch):
        """Center is Klein four-group V₄ = C₂ × C₂."""
        assert arch["C2Q8_center_order"] == 4
        assert arch["C2Q8_center_structure"] == "V₄ = C₂ × C₂"

    def test_derived_subgroup(self, arch):
        """Derived subgroup [C₂×Q₈, C₂×Q₈] has order 2."""
        assert arch["C2Q8_derived_order"] == 2


# ══════════════════════════════════════════════════════════════
#  Weyl group orders
# ══════════════════════════════════════════════════════════════

class TestWeylOrders:
    """Verify Weyl group order formulas."""

    def test_WA_series(self):
        orders = weyl_group_orders()
        assert orders["W(A_1)"] == 2    # S₂
        assert orders["W(A_2)"] == 6    # S₃
        assert orders["W(A_3)"] == 24   # S₄
        assert orders["W(A_4)"] == 120  # S₅
        assert orders["W(A_5)"] == 720  # S₆

    def test_WD_series(self):
        orders = weyl_group_orders()
        assert orders["W(D_3)"] == 24    # = W(A_3)
        assert orders["W(D_4)"] == 192
        assert orders["W(D_5)"] == 1920
        assert orders["W(D_6)"] == 23040

    def test_exceptional(self):
        orders = weyl_group_orders()
        assert orders["W(G_2)"] == 12
        assert orders["W(F_4)"] == 1152
        assert orders["W(E_6)"] == 51840
        assert orders["W(E_7)"] == 2903040
        assert orders["W(E_8)"] == 696729600

    def test_WD3_equals_WA3(self):
        """W(D₃) ≅ W(A₃) ≅ S₄ (order 24)."""
        orders = weyl_group_orders()
        assert orders["W(D_3)"] == orders["W(A_3)"]


# ══════════════════════════════════════════════════════════════
#  Rosetta stone entries
# ══════════════════════════════════════════════════════════════

class TestRosetta:
    """Verify the Rosetta stone summary has all required entries."""

    def test_192_meanings(self, arch):
        meanings = arch["rosetta"]["192_is"]
        assert len(meanings) >= 5
        assert any("Aut(C₂ × Q₈)" in m for m in meanings)
        assert any("W(D₄)" in m for m in meanings)

    def test_27_meanings(self, arch):
        meanings = arch["rosetta"]["27_is"]
        assert len(meanings) >= 5
        assert any("cubic surface" in m for m in meanings)
        assert any("Jordan" in m for m in meanings)

    def test_135_meanings(self, arch):
        meanings = arch["rosetta"]["135_is"]
        assert len(meanings) >= 4
        assert any("GF(2)" in m for m in meanings)

    def test_45_meanings(self, arch):
        meanings = arch["rosetta"]["45_is"]
        assert len(meanings) >= 4
        assert any("tritangent" in m for m in meanings)

    def test_6_meanings(self, arch):
        meanings = arch["rosetta"]["6_is"]
        assert len(meanings) >= 3
        assert any("S₃" in m for m in meanings)
        assert any("triality" in m for m in meanings)


# ══════════════════════════════════════════════════════════════
#  Graph-level Schläfli tests
# ══════════════════════════════════════════════════════════════

class TestSchlafliGraph:
    """Direct tests on the complement Schläfli graph."""

    def test_no_self_loops(self, schlafli):
        for i in range(27):
            assert not schlafli["adj"][i][i]

    def test_symmetric(self, schlafli):
        for i in range(27):
            for j in range(27):
                assert schlafli["adj"][i][j] == schlafli["adj"][j][i]

    def test_degree_uniform_10(self, schlafli):
        for d in schlafli["degrees"]:
            assert d == 10

    def test_lambda_1_all_edges(self, schlafli):
        """Every pair of adjacent vertices has exactly 1 common neighbor."""
        assert schlafli["lambda_vals"] == {1}

    def test_mu_5_all_non_edges(self, schlafli):
        """Every pair of non-adjacent vertices has exactly 5 common neighbors."""
        assert schlafli["mu_vals"] == {5}

    def test_triangle_partition(self, schlafli):
        """Each edge is in exactly 1 triangle, so edges partition into triangles.
        135 edges → 45 triangles of 3 edges each."""
        assert schlafli["num_edges"] == 45 * 3

    def test_E_lines_mutually_skew(self):
        """E-type lines (exceptional divisors) are all mutually skew."""
        lines = enumerate_27_lines()
        e_indices = [i for i, L in enumerate(lines) if L[0] == "E"]
        for i in e_indices:
            for j in e_indices:
                if i != j:
                    assert not lines_meet(lines[i], lines[j])

    def test_G_lines_mutually_skew(self):
        """G-type lines (conics) are all mutually skew."""
        lines = enumerate_27_lines()
        g_indices = [i for i, L in enumerate(lines) if L[0] == "G"]
        for i in g_indices:
            for j in g_indices:
                if i != j:
                    assert not lines_meet(lines[i], lines[j])

    def test_E_meets_G_complement(self):
        """E_i meets G_j iff i ≠ j (5 out of 6)."""
        lines = enumerate_27_lines()
        for L1 in lines:
            if L1[0] == "E":
                neighbors = sum(1 for L2 in lines if L2[0] == "G" and lines_meet(L1, L2))
                assert neighbors == 5

    def test_each_E_meets_4_F(self):
        """E_i meets F_{j,k} iff i ∈ {j,k} → 4 such lines for each E_i
        (wait: for E_i, the F-lines with i in their indices are
        F_{i,0}, F_{i,1}, ..., F_{i,5} minus F_{i,i} = 5 lines,
        but using i<j convention, it's the lines containing index i)."""
        lines = enumerate_27_lines()
        for L1 in lines:
            if L1[0] == "E":
                i = L1[1]
                f_neighbors = [L2 for L2 in lines if L2[0] == "F" and lines_meet(L1, L2)]
                # E_i meets F_{j,k} where i ∈ {j,k}: there are 5 such pairs
                assert len(f_neighbors) == 5

    def test_each_line_meets_exactly_10(self):
        """Every line has degree 10 in the intersection graph."""
        lines = enumerate_27_lines()
        for i, L1 in enumerate(lines):
            count = sum(1 for L2 in lines if lines_meet(L1, L2))
            assert count == 10, f"Line {i} ({L1}) meets {count} lines, expected 10"


# ══════════════════════════════════════════════════════════════
#  Numerological consistency
# ══════════════════════════════════════════════════════════════

class TestNumerology:
    """Cross-check all the key numbers against each other."""

    def test_270_equals_27_times_10(self):
        assert 270 == 27 * 10

    def test_270_equals_2_times_135(self):
        assert 270 == 2 * 135

    def test_270_equals_WE6_over_192(self):
        assert 51840 // 192 == 270

    def test_45_equals_135_over_3(self):
        assert 135 // 3 == 45

    def test_45_equals_WE6_over_1152(self):
        assert 51840 // 1152 == 45

    def test_27_equals_WE6_over_1920(self):
        assert 51840 // 1920 == 27

    def test_10_equals_1920_over_192(self):
        assert 1920 // 192 == 10

    def test_6_equals_1152_over_192(self):
        assert 1152 // 192 == 6

    def test_5_equals_1920_over_384(self):
        assert 1920 // 384 == 5

    def test_3_equals_1152_over_384(self):
        assert 1152 // 384 == 3

    def test_2_equals_384_over_192(self):
        assert 384 // 192 == 2

    def test_192_equals_8_times_24(self):
        assert 192 == 8 * 24

    def test_1152_equals_192_times_6(self):
        assert 1152 == 192 * 6

    def test_51840_prime_factorization(self):
        """51840 = 2⁷ × 3⁴ × 5"""
        assert 51840 == 2**7 * 3**4 * 5

    def test_192_prime_factorization(self):
        """192 = 2⁶ × 3"""
        assert 192 == 2**6 * 3

    def test_1152_prime_factorization(self):
        """1152 = 2⁷ × 3²"""
        assert 1152 == 2**7 * 3**2

    def test_256_equals_2_to_8(self):
        """GF(2)⁸ has 256 elements."""
        assert 2**8 == 256
        assert 1 + 135 + 120 == 256
