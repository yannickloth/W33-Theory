"""Tests for Pillar 143 — Mirror Symmetry & Calabi-Yau Duality."""

import pytest
from THEORY_PART_CCXLIII_MIRROR_SYMMETRY_CALABI_YAU import (
    calabi_yau_manifolds,
    hodge_diamond_mirror,
    enumerative_geometry,
    homological_mirror_symmetry,
    syz_conjecture,
    topological_strings,
    string_dualities,
    twentyseven_lines_e6,
    k3_surface,
    complete_chain_w33_to_mirror,
    run_checks,
)


class TestCalabiYau:
    def setup_method(self):
        self.c = calabi_yau_manifolds()

    def test_properties(self):
        assert self.c['property_count'] == 5

    def test_dimensions(self):
        assert self.c['dimension_count'] == 3

    def test_yau(self):
        assert self.c['yau_year'] == 1978

    def test_fields(self):
        assert self.c['yau_fields_medal'] == 1982


class TestHodgeDiamond:
    def setup_method(self):
        self.h = hodge_diamond_mirror()

    def test_quintic_h11(self):
        assert self.h['quintic_h11'] == 1

    def test_quintic_h21(self):
        assert self.h['quintic_h21'] == 101

    def test_quintic_euler(self):
        assert self.h['quintic_euler'] == -200

    def test_mirror_euler(self):
        assert self.h['mirror_euler'] == 200

    def test_mirror_swap(self):
        assert self.h['quintic']['h11'] == self.h['mirror']['h21']
        assert self.h['quintic']['h21'] == self.h['mirror']['h11']


class TestEnumerative:
    def setup_method(self):
        self.e = enumerative_geometry()

    def test_lines(self):
        assert self.e['degree_1_lines'] == 2875

    def test_conics(self):
        assert self.e['degree_2_conics'] == 609250

    def test_cubics(self):
        assert self.e['degree_3_cubics'] == 317206375

    def test_count(self):
        assert self.e['count_count'] == 4


class TestHMS:
    def setup_method(self):
        self.h = homological_mirror_symmetry()

    def test_year(self):
        assert self.h['conjecture']['proposed_year'] == 1994

    def test_fields(self):
        assert self.h['kontsevich_fields_medal'] == 1998

    def test_proved(self):
        assert self.h['proved_count'] == 4

    def test_bridge(self):
        assert 'Complex' in self.h['bridge'] and 'Symplectic' in self.h['bridge']


class TestSYZ:
    def setup_method(self):
        self.s = syz_conjecture()

    def test_year(self):
        assert self.s['year'] == 1996

    def test_k3_singular(self):
        assert self.s['k3_singular_fibers'] == 24

    def test_examples(self):
        assert self.s['example_count'] == 3


class TestTopologicalStrings:
    def setup_method(self):
        self.t = topological_strings()

    def test_models(self):
        assert self.t['model_count'] == 2

    def test_year(self):
        assert self.t['year'] == 1990


class TestStringDualities:
    def setup_method(self):
        self.s = string_dualities()

    def test_duality_count(self):
        assert self.s['duality_count'] == 5

    def test_five_theories(self):
        assert self.s['theory_count'] == 5

    def test_m_theory(self):
        assert self.s['unified_by']['dimension'] == 11


class Test27Lines:
    def setup_method(self):
        self.t = twentyseven_lines_e6()

    def test_lines(self):
        assert self.t['line_count'] == 27

    def test_weyl(self):
        assert self.t['group_order'] == 51840


class TestK3:
    def setup_method(self):
        self.k = k3_surface()

    def test_euler(self):
        assert self.k['euler_characteristic'] == 24

    def test_self_mirror(self):
        assert self.k['mirror_self']

    def test_e8(self):
        assert self.k['e8_copies'] == 2

    def test_betti(self):
        assert self.k['betti_numbers'] == [1, 0, 22, 0, 1]


class TestChain:
    def test_length(self):
        assert len(complete_chain_w33_to_mirror()) == 7


class TestRunChecks:
    def test_all_pass(self):
        assert run_checks()
