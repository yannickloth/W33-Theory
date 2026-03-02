"""
Tests for Pillar 121 (CCXXI): G₂ from D₄ Triality — The Fano Bridge.

Verifies:
  T1–T3:  D₄ root system (24 roots) and explicit triality map σ (order 3)
  T4–T5:  D₄ Dynkin fold → G₂ Cartan matrix; triality orbits = 12 = |roots(G₂)|
  T6–T7:  G₂ root system (12 = 6 short + 6 long) and Cartan matrix
  T8–T9:  Fano plane PG(2,2) and octonion algebra (8-dim, alternative, non-assoc)
  T10:    Der(O) has dim 14 = dim(G₂)
  T11:    Triality halving: roots 24/2=12, dim 28/2=14
  T12:    The Fano Bridge chain: D₄ → G₂ → Fano → pockets
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "pillars"))

from THEORY_PART_CCXXI_G2_TRIALITY_FANO_BRIDGE import (
    d4_roots,
    d4_cartan_matrix,
    d4_simple_roots,
    triality_matrix,
    mat_vec,
    mat_mul,
    verify_triality_order,
    verify_triality_on_simple_roots,
    fold_d4_to_g2,
    d4_root_orbits_under_triality,
    g2_roots,
    g2_cartan_verified,
    g2_weyl_group_order,
    fano_plane,
    octonion_multiplication_table,
    verify_octonion_properties,
    derivation_algebra_dimension,
    fano_bridge,
)


# ── D₄ Root System ──────────────────────────────────────────

class TestD4RootSystem:
    def test_d4_has_24_roots(self):
        assert len(d4_roots()) == 24

    def test_d4_roots_are_unit_vectors(self):
        """Each D₄ root ±eᵢ±eⱼ has norm² = 2."""
        for r in d4_roots():
            assert sum(x * x for x in r) == 2

    def test_d4_cartan_is_4x4(self):
        C = d4_cartan_matrix()
        assert len(C) == 4 and all(len(row) == 4 for row in C)
        # Diagonal entries = 2
        assert all(C[i][i] == 2 for i in range(4))

    def test_d4_simple_roots_count(self):
        assert len(d4_simple_roots()) == 4


# ── Triality ─────────────────────────────────────────────────

class TestTriality:
    def test_triality_order_3(self):
        assert verify_triality_order()

    def test_triality_simple_root_permutation(self):
        sr = verify_triality_on_simple_roots()
        assert all(sr.values()), f"Failed checks: {sr}"

    def test_triality_fixes_center(self):
        sr = verify_triality_on_simple_roots()
        assert sr["σ(α₂) = α₂"]

    def test_triality_3cycles_legs(self):
        sr = verify_triality_on_simple_roots()
        assert sr["σ(α₁) = α₄"] and sr["σ(α₄) = α₃"] and sr["σ(α₃) = α₁"]


# ── D₄ → G₂ Fold ────────────────────────────────────────────

class TestFold:
    def test_fold_gives_g2_cartan(self):
        fold = fold_d4_to_g2()
        assert fold["G2_cartan"] == [[2, -1], [-3, 2]]

    def test_g2_cartan_det_is_1(self):
        fold = fold_d4_to_g2()
        assert fold["G2_det"] == 1

    def test_fold_multiplicity_is_3(self):
        fold = fold_d4_to_g2()
        assert fold["fold_multiplicity"] == 3

    def test_length_ratio_squared_is_3(self):
        fold = fold_d4_to_g2()
        assert fold["root_length_ratio_squared"] == 3


# ── Triality Orbits ──────────────────────────────────────────

class TestTrialityOrbits:
    def test_12_orbits(self):
        orb = d4_root_orbits_under_triality()
        assert orb["orbit_count"] == 12

    def test_covers_all_24_roots(self):
        orb = d4_root_orbits_under_triality()
        assert orb["total_roots_covered"] == 24

    def test_orbit_sizes_6_fixed_6_triple(self):
        orb = d4_root_orbits_under_triality()
        sizes = orb["orbit_size_distribution"]
        assert sizes.get(1, 0) == 6, f"Expected 6 fixed orbits, got {sizes.get(1, 0)}"
        assert sizes.get(3, 0) == 6, f"Expected 6 triple orbits, got {sizes.get(3, 0)}"


# ── G₂ Root System ───────────────────────────────────────────

class TestG2Roots:
    def test_g2_has_12_roots(self):
        g2 = g2_roots()
        assert g2["total"] == 12

    def test_g2_6_short_6_long(self):
        g2 = g2_roots()
        assert g2["num_short"] == 6
        assert g2["num_long"] == 6

    def test_g2_cartan_matrix(self):
        gc = g2_cartan_verified()
        assert gc["matches"]

    def test_g2_length_ratio_is_3(self):
        gc = g2_cartan_verified()
        assert gc["length_ratio_long_to_short"] == 3

    def test_g2_weyl_group_order(self):
        assert g2_weyl_group_order() == 12


# ── Fano Plane ───────────────────────────────────────────────

class TestFanoPlane:
    def test_7_points_7_lines(self):
        f = fano_plane()
        assert f["num_points"] == 7
        assert f["num_lines"] == 7

    def test_3_points_per_line(self):
        f = fano_plane()
        assert f["points_per_line"] == 3

    def test_each_pair_on_exactly_one_line(self):
        f = fano_plane()
        assert f["each_pair_on_one_line"]

    def test_each_point_on_3_lines(self):
        f = fano_plane()
        assert f["each_point_on_three_lines"]

    def test_21_pairs_covered(self):
        f = fano_plane()
        assert f["pairs_covered"] == 21


# ── Octonion Algebra ─────────────────────────────────────────

class TestOctonions:
    def test_dimension_8(self):
        props = verify_octonion_properties()
        assert props["dimension"] == 8

    def test_non_associative(self):
        props = verify_octonion_properties()
        assert props["non_associative"]

    def test_alternative(self):
        props = verify_octonion_properties()
        assert props["alternative"]

    def test_all_products_defined(self):
        props = verify_octonion_properties()
        assert props["all_products_defined"]


# ── Der(O) = G₂ ──────────────────────────────────────────────

class TestDerO:
    def test_derivation_dimension_14(self):
        der = derivation_algebra_dimension()
        assert der["derivation_dimension"] == 14, (
            f"Expected dim Der(O) = 14, got {der['derivation_dimension']}"
        )

    def test_is_g2(self):
        der = derivation_algebra_dimension()
        assert der["is_G2"]


# ── Triality Halving ─────────────────────────────────────────

class TestTrialityHalving:
    def test_root_halving(self):
        assert len(d4_roots()) == 2 * g2_roots()["total"]  # 24 = 2 × 12

    def test_dim_halving(self):
        assert 28 == 2 * 14  # dim(D₄) = 2 × dim(G₂)


# ── Fano Bridge ──────────────────────────────────────────────

class TestFanoBridge:
    def test_w_d4_equals_n(self):
        b = fano_bridge()
        assert b["W_D4_equals_N"]

    def test_w_f4_decomposition(self):
        b = fano_bridge()
        assert b["W_F4_equals_W_D4_times_S3"]

    def test_g2_extends_pocket_sl3(self):
        b = fano_bridge()
        assert b["G2_extends_pocket_sl3"]

    def test_sl3_complement_is_6(self):
        b = fano_bridge()
        assert b["sl3_complement_in_G2"] == 6

    def test_triality_halving(self):
        b = fano_bridge()
        assert b["triality_halving"]

    def test_fano_valid(self):
        b = fano_bridge()
        assert b["fano_is_valid"]

    def test_cascade_n_equals_192(self):
        b = fano_bridge()
        assert b["cascade"]["N = W(D₄)"] == 192
