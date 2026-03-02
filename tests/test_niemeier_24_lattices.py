"""
Tests for Pillar 131 - The 24 Niemeier Lattices
"""
import pytest

from THEORY_PART_CCXXXI_NIEMEIER_24_LATTICES import (
    niemeier_lattices, coxeter_number, num_roots_component,
    verify_niemeier_classification, deep_hole_correspondence,
    deep_hole_count, coxeter_number_distribution, coxeter_numbers_list,
    w33_niemeier_connections, root_counts, lattices_with_e8,
    lattices_with_coxeter, smith_minkowski_siegel_mass,
    dimension_24_appearances, glue_code_index, e8_trinity,
)


# ── Classification ──────────────────────────────────────────

class TestClassification:
    def test_exactly_24_lattices(self):
        assert len(niemeier_lattices()) == 24

    def test_all_ranks_24_or_zero(self):
        for label, comps, h, n in niemeier_lattices():
            rank = sum(r for _, r in comps)
            assert rank == 24 or rank == 0, f"{label} has rank {rank}"

    def test_coxeter_consistency(self):
        for label, comps, h, n in niemeier_lattices():
            if not comps:
                continue
            h_values = set(coxeter_number(t, r) for t, r in comps)
            assert len(h_values) == 1, f"{label} has mixed Coxeter: {h_values}"
            assert h_values.pop() == h

    def test_root_counts(self):
        for label, comps, h, n in niemeier_lattices():
            computed = sum(num_roots_component(t, r) for t, r in comps)
            assert computed == n, f"{label}: expected {n}, got {computed}"

    def test_verify_all(self):
        results = verify_niemeier_classification()
        assert len(results) == 24
        for r in results:
            assert r['rank_ok']
            assert r['coxeter_ok']
            assert r['roots_ok']


# ── Coxeter Numbers ─────────────────────────────────────────

class TestCoxeterNumbers:
    def test_A_coxeter(self):
        assert coxeter_number("A", 1) == 2
        assert coxeter_number("A", 8) == 9
        assert coxeter_number("A", 24) == 25

    def test_D_coxeter(self):
        assert coxeter_number("D", 4) == 6
        assert coxeter_number("D", 8) == 14
        assert coxeter_number("D", 24) == 46

    def test_E_coxeter(self):
        assert coxeter_number("E", 6) == 12
        assert coxeter_number("E", 7) == 18
        assert coxeter_number("E", 8) == 30

    def test_distinct_coxeter_values(self):
        values = coxeter_numbers_list()
        assert 0 in values  # Leech
        assert 30 in values  # E_8^3
        assert 46 in values  # D24

    def test_distribution(self):
        dist = coxeter_number_distribution()
        # h=6 has two lattices (A5^4.D4 and D4^6)
        assert len(dist[6]) == 2
        # h=30 has two lattices (D16.E8 and E8^3)
        assert len(dist[30]) == 2


# ── Root Counts ──────────────────────────────────────────────

class TestRootCounts:
    def test_A_roots(self):
        assert num_roots_component("A", 1) == 2
        assert num_roots_component("A", 2) == 6
        assert num_roots_component("A", 8) == 72

    def test_D_roots(self):
        assert num_roots_component("D", 4) == 24
        assert num_roots_component("D", 8) == 112

    def test_E_roots(self):
        assert num_roots_component("E", 6) == 72
        assert num_roots_component("E", 7) == 126
        assert num_roots_component("E", 8) == 240

    def test_leech_zero_roots(self):
        counts = root_counts()
        assert counts[0] == 0

    def test_max_roots_d24(self):
        counts = root_counts()
        assert max(counts) == 1104


# ── Deep Holes ──────────────────────────────────────────────

class TestDeepHoles:
    def test_23_types(self):
        assert deep_hole_count() == 23

    def test_covering_radius(self):
        holes = deep_hole_correspondence()
        for h in holes:
            assert h['covering_radius_sq'] == 2

    def test_no_leech_in_holes(self):
        holes = deep_hole_correspondence()
        labels = [h['label'] for h in holes]
        assert "Leech" not in labels


# ── W(3,3) Connection ──────────────────────────────────────

class TestW33Connection:
    def test_24_connection(self):
        conns = w33_niemeier_connections()
        assert conns['24_lattices']['value'] == 24

    def test_240_connection(self):
        conns = w33_niemeier_connections()
        assert conns['240_roots']['value'] == 240

    def test_m24_connection(self):
        conns = w33_niemeier_connections()
        assert conns['M24_symmetry']['value'] == 244823040


# ── Dimension 24 ────────────────────────────────────────────

class TestDimension24:
    def test_all_24(self):
        d = dimension_24_appearances()
        for key, (desc, val) in d.items():
            assert val == 24, f"{key}: {val} != 24"

    def test_count(self):
        assert len(dimension_24_appearances()) == 12


# ── E_8 Trinity ─────────────────────────────────────────────

class TestE8Trinity:
    def test_two_e8_lattices(self):
        info = e8_trinity()
        assert info['count'] == 2

    def test_coxeter_30(self):
        info = e8_trinity()
        assert info['coxeter_number'] == 30


# ── Glue Codes ──────────────────────────────────────────────

class TestGlueCodes:
    def test_e8_cubed_self_dual(self):
        assert glue_code_index("E8^3") == 1

    def test_a1_24(self):
        assert glue_code_index("A1^24") == 2**12

    def test_leech_none(self):
        assert glue_code_index("Leech") is None

    def test_d24_index(self):
        assert glue_code_index("D24") == 2


# ── E_8 Component Lattices ──────────────────────────────────

class TestE8Lattices:
    def test_labels(self):
        e8 = lattices_with_e8()
        labels = [l for l, _, _ in e8]
        assert "E8^3" in labels
        assert "D16.E8" in labels

    def test_both_coxeter_30(self):
        e8 = lattices_with_e8()
        for l, c, h in e8:
            assert h == 30


# ── Mass Formula ────────────────────────────────────────────

class TestMassFormula:
    def test_dimension(self):
        m = smith_minkowski_siegel_mass()
        assert m['dimension'] == 24

    def test_count(self):
        m = smith_minkowski_siegel_mass()
        assert m['num_lattices'] == 24

    def test_unique_rootless(self):
        m = smith_minkowski_siegel_mass()
        assert m['unique_rootless'] == 1


# ── Lattice Lookup ──────────────────────────────────────────

class TestLatticesWithCoxeter:
    def test_h30(self):
        result = lattices_with_coxeter(30)
        assert len(result) == 2

    def test_h0(self):
        result = lattices_with_coxeter(0)
        assert len(result) == 1
        assert result[0][0] == "Leech"
