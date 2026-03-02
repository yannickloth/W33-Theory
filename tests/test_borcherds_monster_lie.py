"""Tests for Pillar 140 — Borcherds Algebras & the Monster Lie Algebra."""

import pytest
from THEORY_PART_CCXL_BORCHERDS_MONSTER_LIE import (
    generalized_kac_moody,
    monster_lie_algebra,
    denominator_formula,
    no_ghost_construction,
    fake_monster_lie_algebra,
    voa_bridge,
    borcherds_products,
    number_26_connections,
    borcherds_moonshine_proof,
    complete_chain_w33_to_borcherds,
    run_checks,
)


# ── generalized_kac_moody ───────────────────────────────────

class TestGeneralizedKacMoody:
    def setup_method(self):
        self.g = generalized_kac_moody()

    def test_name(self):
        assert 'Kac-Moody' in self.g['full_name']

    def test_alt_names(self):
        assert 'Borcherds algebra' in self.g['alt_names']
        assert 'BKM algebra' in self.g['alt_names']

    def test_year(self):
        assert self.g['year'] == 1988

    def test_property_count(self):
        assert self.g['property_count'] == 5

    def test_three_types(self):
        assert self.g['type_count'] == 3

    def test_imaginary_roots(self):
        assert 'imaginary' in self.g['key_difference'].lower()

    def test_relations_count(self):
        assert len(self.g['defining_relations']) == 5


# ── monster_lie_algebra ─────────────────────────────────────

class TestMonsterLieAlgebra:
    def setup_method(self):
        self.m = monster_lie_algebra()

    def test_rank(self):
        assert self.m['rank'] == 2

    def test_cartan_dim(self):
        assert self.m['cartan_dim'] == 2

    def test_real_root(self):
        assert self.m['real_simple_root'] == (1, -1)

    def test_one_real_root(self):
        assert self.m['real_root_count'] == 1

    def test_c1_196884(self):
        assert self.m['j_coefficients'][1] == 196884

    def test_c2(self):
        assert self.m['j_coefficients'][2] == 21493760

    def test_c_minus1(self):
        assert self.m['j_coefficients'][-1] == 1

    def test_weyl_order(self):
        assert self.m['weyl_group']['order'] == 2

    def test_monster_acts(self):
        assert self.m['acted_on_by'] == 'Monster group'

    def test_proof_year(self):
        assert self.m['proof_year'] == 1992

    def test_fields_medal(self):
        assert self.m['fields_medal_year'] == 1998

    def test_type(self):
        assert 'Kac-Moody' in self.m['type']


# ── denominator_formula ─────────────────────────────────────

class TestDenominatorFormula:
    def setup_method(self):
        self.d = denominator_formula()

    def test_name(self):
        assert 'Koike' in self.d['name']
        assert 'Norton' in self.d['name']
        assert 'Zagier' in self.d['name']

    def test_three_discoverers(self):
        assert self.d['discoverer_count'] == 3

    def test_c1(self):
        assert self.d['c_1'] == 196884

    def test_moonshine(self):
        assert '196883' in self.d['moonshine_connection']

    def test_role(self):
        assert 'denominator' in self.d['role'].lower()

    def test_properties_count(self):
        assert self.d['property_count'] == 6


# ── no_ghost_construction ───────────────────────────────────

class TestNoGhostConstruction:
    def setup_method(self):
        self.n = no_ghost_construction()

    def test_step_count(self):
        assert self.n['step_count'] == 4

    def test_critical_dim(self):
        assert self.n['critical_dimension'] == 26

    def test_input_voa(self):
        assert 'V' in self.n['input_voa']

    def test_output(self):
        assert 'Monster' in self.n['output']

    def test_preserves_symmetry(self):
        assert self.n['preserves_symmetry']

    def test_monster_acts(self):
        assert self.n['monster_acts']


# ── fake_monster_lie_algebra ────────────────────────────────

class TestFakeMonster:
    def setup_method(self):
        self.f = fake_monster_lie_algebra()

    def test_lattice_dim(self):
        assert self.f['lattice_dimension'] == 26

    def test_weyl_norm_zero(self):
        assert self.f['weyl_norm_is_zero']

    def test_weyl_vector_length(self):
        assert self.f['weyl_vector_length'] == 26

    def test_lorentzian_norm(self):
        assert self.f['weyl_lorentzian_norm'] == 0

    def test_numerology_count(self):
        assert self.f['numerology_count'] == 4

    def test_lattice_even_unimodular(self):
        props = self.f['lattice_properties']
        assert props['even'] and props['unimodular']


# ── voa_bridge ──────────────────────────────────────────────

class TestVOABridge:
    def setup_method(self):
        self.v = voa_bridge()

    def test_example_count(self):
        assert self.v['example_count'] == 6

    def test_e8_c(self):
        assert self.v['e8_c'] == 8

    def test_monster_c(self):
        assert self.v['monster_voa_c'] == 24

    def test_e8_dim_weight1(self):
        assert self.v['e8_voa']['dimension_weight_1'] == 248

    def test_borcherds_year(self):
        assert self.v['borcherds_year'] == 1986

    def test_flm_year(self):
        assert self.v['flm_year'] == 1988


# ── borcherds_products ──────────────────────────────────────

class TestBorcherdsProducts:
    def setup_method(self):
        self.b = borcherds_products()

    def test_product_count(self):
        assert self.b['product_count'] == 2

    def test_fields_medal(self):
        assert self.b['fields_medal']

    def test_fields_year(self):
        assert self.b['fields_medal_year'] == 1998


# ── number_26_connections ───────────────────────────────────

class TestNumber26:
    def setup_method(self):
        self.n = number_26_connections()

    def test_number(self):
        assert self.n['number'] == 26

    def test_appearances(self):
        assert self.n['appearance_count'] == 7


# ── borcherds_moonshine_proof ───────────────────────────────

class TestMoonshineProof:
    def setup_method(self):
        self.p = borcherds_moonshine_proof()

    def test_proof_year(self):
        assert self.p['proof_year'] == 1992

    def test_steps(self):
        assert self.p['step_count'] == 5

    def test_tools(self):
        assert self.p['tool_count'] == 5

    def test_fields_medal(self):
        assert self.p['fields_medal']


# ── chain ───────────────────────────────────────────────────

class TestChain:
    def test_chain_length(self):
        chain = complete_chain_w33_to_borcherds()
        assert len(chain) == 7

    def test_chain_starts_w33(self):
        chain = complete_chain_w33_to_borcherds()
        assert 'W(3,3)' in chain[0][0]


# ── run_checks ──────────────────────────────────────────────

class TestRunChecks:
    def test_all_pass(self):
        assert run_checks()
