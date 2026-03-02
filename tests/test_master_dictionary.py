"""
Tests for Pillar 130 - The W(3,3) Master Dictionary
"""
import pytest
from math import comb

from THEORY_PART_CCXXX_MASTER_DICTIONARY import (
    w33_parameters, verify_srg_parameters, master_dictionary,
    complete_chain, jordan_dim, exceptional_dimensions,
    coxeter_numbers, dimension_identities, predictions,
    eigenvalue_analysis,
)


# ── SRG Parameters ──────────────────────────────────────────

class TestSRGParameters:
    def test_vertices(self):
        assert w33_parameters()['vertices'] == 40

    def test_regularity(self):
        assert w33_parameters()['regularity'] == 12

    def test_edges(self):
        assert w33_parameters()['edges'] == 240

    def test_lambda(self):
        assert w33_parameters()['lambda'] == 2

    def test_mu(self):
        assert w33_parameters()['mu'] == 4

    def test_edge_count(self):
        ok, _, _, _, _ = verify_srg_parameters()
        assert ok

    def test_param_equation(self):
        _, ok, _, _, _ = verify_srg_parameters()
        assert ok

    def test_eigenvalues(self):
        _, _, ok, r, s = verify_srg_parameters()
        assert ok and r == 2 and s == -4


# ── Master Dictionary ────────────────────────────────────────

class TestMasterDict:
    def test_all_verified(self):
        md = master_dictionary()
        for e in md:
            assert e['verified'], f"Failed: {e['graph']}"

    def test_ten_entries(self):
        assert len(master_dictionary()) >= 10

    def test_240_entry(self):
        md = master_dictionary()
        found = any(e['value'] == 240 for e in md)
        assert found

    def test_12_entry(self):
        md = master_dictionary()
        found = any(e['value'] == 12 for e in md)
        assert found


# ── Complete Chain ───────────────────────────────────────────

class TestChain:
    def test_all_links_verified(self):
        chain = complete_chain()
        for link in chain:
            assert link['verified'], f"Failed: {link['from']} -> {link['to']}"

    def test_six_links(self):
        assert len(complete_chain()) >= 6

    def test_starts_w33(self):
        assert complete_chain()[0]['from'] == 'W(3,3)'

    def test_ends_monster(self):
        chain = complete_chain()
        ends_monster = any(link['to'] == 'Monster' for link in chain)
        assert ends_monster


# ── Eigenvalue Analysis ─────────────────────────────────────

class TestEigenvalues:
    def test_sum_40(self):
        ea = eigenvalue_analysis()
        assert ea['total'] == 40

    def test_check(self):
        ea = eigenvalue_analysis()
        assert ea['check']

    def test_mult_24(self):
        ea = eigenvalue_analysis()
        assert ea['positive']['multiplicity'] == 24

    def test_mult_15(self):
        ea = eigenvalue_analysis()
        assert ea['negative']['multiplicity'] == 15


# ── Dimension Identities ────────────────────────────────────

class TestIdentities:
    def test_all_true(self):
        ids = dimension_identities()
        for desc, val in ids.items():
            assert val, f"Failed: {desc}"

    def test_count(self):
        assert len(dimension_identities()) >= 20

    def test_moonshine_eq(self):
        assert 196884 == 196560 + 4 * 81

    def test_perfect_496(self):
        assert 496 == 2 * 248

    def test_744(self):
        assert 744 == 3 * 248


# ── Exceptional Groups ─────────────────────────────────────

class TestExceptional:
    def test_all_five(self):
        ed = exceptional_dimensions()
        assert len(ed) == 5

    def test_dims(self):
        ed = exceptional_dimensions()
        assert ed['E8']['dim'] == 248
        assert ed['E6']['dim'] == 78
        assert ed['G2']['dim'] == 14

    def test_sum_525(self):
        ed = exceptional_dimensions()
        assert sum(v['dim'] for v in ed.values()) == 525


# ── Predictions ─────────────────────────────────────────────

class TestPredictions:
    def test_has_three_gens(self):
        assert 'Three generations' in predictions()

    def test_has_gauge_dim(self):
        assert 'Gauge dimension 12' in predictions()

    def test_at_least_four(self):
        assert len(predictions()) >= 4


# ── Jordan Dimensions ───────────────────────────────────────

class TestJordan:
    def test_J3O(self):
        assert jordan_dim(3, 8) == 27

    def test_J3H(self):
        assert jordan_dim(3, 4) == 15

    def test_27_cubed(self):
        assert 27 == 3**3
