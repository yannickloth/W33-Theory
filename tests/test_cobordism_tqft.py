"""
Tests for Pillar 139 — Cobordism & Topological Quantum Field Theory
"""
import pytest

from THEORY_PART_CCXXXIX_COBORDISM_TQFT import (
    atiyah_segal_axioms, cobordism_category, tqft_2d_classification,
    chern_simons_theory, chern_simons_e8, tqft_invariants,
    cobordism_hypothesis, anomaly_cobordism, verlinde_formula,
    tqft_types, complete_chain_w33_to_tqft,
)


# -- Atiyah-Segal axioms ------------------------------------------------

class TestAxioms:
    def test_count(self):
        assert atiyah_segal_axioms()['axiom_count'] == 5

    def test_year(self):
        assert atiyah_segal_axioms()['year'] == 1988

    def test_type(self):
        assert atiyah_segal_axioms()['type'] == 'symmetric monoidal functor'

    def test_authors(self):
        a = atiyah_segal_axioms()['authors']
        assert 'Atiyah' in a and 'Segal' in a


# -- Cobordism category -------------------------------------------------

class TestCobordism:
    def test_dims(self):
        assert cobordism_category()['dimensions_shown'] == [1, 2, 3, 4]

    def test_monoidal(self):
        assert cobordism_category()['is_symmetric_monoidal'] is True

    def test_dim3_cs(self):
        assert cobordism_category()['examples'][3]['key_example'] == 'Chern-Simons theory'


# -- 2D TQFT classification ---------------------------------------------

class TestTQFT2D:
    def test_complete(self):
        assert tqft_2d_classification()['is_complete_classification'] is True

    def test_frobenius(self):
        assert 'Frobenius' in tqft_2d_classification()['theorem']

    def test_examples_count(self):
        assert len(tqft_2d_classification()['examples']) >= 4

    def test_pair_of_pants(self):
        assert 'pair_of_pants' in tqft_2d_classification()['correspondence']


# -- Chern-Simons --------------------------------------------------------

class TestChernSimons:
    def test_dim_3(self):
        assert chern_simons_theory()['dimension'] == 3

    def test_topological(self):
        assert chern_simons_theory()['is_topological'] is True

    def test_year(self):
        assert chern_simons_theory()['year'] == 1989

    def test_jones(self):
        assert chern_simons_theory()['knot_invariants'] is True

    def test_fields_medal(self):
        assert chern_simons_theory()['fields_medal'] is True

    def test_verlinde(self):
        assert chern_simons_theory()['verlinde_formula'] is True


# -- E_8 Chern-Simons ----------------------------------------------------

class TestCSE8:
    def test_level(self):
        assert chern_simons_e8()['level'] == 1

    def test_central_charge(self):
        assert chern_simons_e8()['c_at_level_1'] == 8

    def test_dual_coxeter(self):
        assert chern_simons_e8()['dual_coxeter'] == 30

    def test_primary_fields(self):
        assert chern_simons_e8()['primary_fields_count'] == 1

    def test_two_copies(self):
        assert chern_simons_e8()['two_copies_c'] == 16

    def test_with_bosons(self):
        assert chern_simons_e8()['with_8_bosons_c'] == 24

    def test_z_s3(self):
        assert chern_simons_e8()['z_s3'] == 1

    def test_self_dual(self):
        assert chern_simons_e8()['e8_self_dual'] is True


# -- Topological invariants ----------------------------------------------

class TestInvariants:
    def test_count(self):
        assert tqft_invariants()['count'] == 6

    def test_jones(self):
        knots = [i for i in tqft_invariants()['invariants']
                 if i['name'] == 'Jones polynomial']
        assert len(knots) == 1 and knots[0]['year'] == 1984

    def test_donaldson(self):
        d = [i for i in tqft_invariants()['invariants']
             if i['name'] == 'Donaldson invariants']
        assert len(d) == 1 and d[0]['dimension'] == 4


# -- Cobordism hypothesis ------------------------------------------------

class TestCobHyp:
    def test_lurie(self):
        assert cobordism_hypothesis()['proved_by'] == 'Lurie'

    def test_year(self):
        assert cobordism_hypothesis()['proof_year'] == 2009

    def test_baez_dolan(self):
        assert cobordism_hypothesis()['conjectured_by'] == 'Baez-Dolan'


# -- Anomaly cobordism ---------------------------------------------------

class TestAnomaly:
    def test_invertible(self):
        assert anomaly_cobordism()['invertible_tqft'] is True

    def test_496(self):
        assert anomaly_cobordism()['green_schwarz']['n_value'] == 496


# -- Verlinde formula ----------------------------------------------------

class TestVerlinde:
    def test_level_1(self):
        assert verlinde_formula()['su2_level_1_always_1'] is True

    def test_level_2(self):
        assert verlinde_formula()['su2_level_2_is_3_to_g'] is True

    def test_year(self):
        assert verlinde_formula()['year'] == 1988


# -- TQFT types ----------------------------------------------------------

class TestTypes:
    def test_count(self):
        assert tqft_types()['total_types'] == 2


# -- Chain ---------------------------------------------------------------

class TestChain:
    def test_length(self):
        assert len(complete_chain_w33_to_tqft()) == 7

    def test_starts_w33(self):
        assert complete_chain_w33_to_tqft()[0][0] == 'W(3,3)'
