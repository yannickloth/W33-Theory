"""Tests for Pillar 176 — Categorification."""

import pytest
from THEORY_PART_CCLXXVI_CATEGORIFICATION import (
    categorification_philosophy,
    khovanov_homology,
    soergel_bimodules,
    geometric_categorification,
    quantum_group_categorification,
    knot_homology_theories,
    higher_categorification,
    e8_categorification_connection,
)


class TestCategorificationPhilosophy:
    def test_core_idea(self):
        r = categorification_philosophy()
        assert 'categorical' in r['core_idea']['principle']
        assert 'FinVect' in r['core_idea']['example_basic']
        assert 'Euler' in r['core_idea']['example_ring']

    def test_levels(self):
        r = categorification_philosophy()
        assert 'Sets' in r['levels']['level_0']
        assert 'Categories' in r['levels']['level_1']
        assert '2-categories' in r['levels']['level_2']

    def test_benefits(self):
        r = categorification_philosophy()
        assert 'positivity' in r['benefits']['positivity'].lower()
        assert 'Natural numbers' in r['benefits']['integrality']

    def test_history(self):
        r = categorification_philosophy()
        assert '1994' in r['history']['crane_frenkel']
        assert '2000' in r['history']['khovanov']


class TestKhovanovHomology:
    def test_definition(self):
        r = khovanov_homology()
        assert 'bigraded' in r['definition']['chain_complex']
        assert 'resolution' in r['definition']['cube_of_resolutions'].lower()

    def test_properties(self):
        r = khovanov_homology()
        assert 'Jones' in r['properties']['jones_polynomial']
        assert 'link invariant' in r['properties']['link_invariant'].lower()
        assert 'distinguishes' in r['properties']['strictly_stronger']

    def test_functoriality(self):
        r = khovanov_homology()
        assert 'cobordism' in r['functoriality']['cobordism_maps'].lower()
        assert 'TQFT' in r['functoriality']['tqft']

    def test_detection(self):
        r = khovanov_homology()
        assert 'unknot' in r['detection']['unknot']
        assert 'Kronheimer-Mrowka' in r['detection']['unknot']
        assert 'Rasmussen' in r['detection']['genus']
        assert 'Milnor' in r['detection']['milnor_conjecture']


class TestSoergelBimodules:
    def test_hecke_algebra(self):
        r = soergel_bimodules()
        assert 'KL' in r['hecke_algebra']['kazhdan_lusztig']
        assert 'deformation' in r['hecke_algebra']['definition'].lower()

    def test_soergel(self):
        r = soergel_bimodules()
        assert 'R ⊗' in r['soergel_bimodules']['definition']
        assert 'indecomposable' in r['soergel_bimodules']['indecomposables'].lower()

    def test_elias_williamson(self):
        r = soergel_bimodules()
        assert 'Soergel' in r['elias_williamson']['theorem']
        assert '2014' in r['elias_williamson']['proof']
        assert 'positivity' in r['elias_williamson']['consequence'].lower()

    def test_applications(self):
        r = soergel_bimodules()
        assert 'Williamson' in r['applications']['p_kl_theory']


class TestGeometricCategorification:
    def test_perverse_sheaves(self):
        r = geometric_categorification()
        assert 'abelian' in r['perverse_sheaves']['abelian_category'].lower()
        assert 'IC' in r['perverse_sheaves']['ic_complexes']

    def test_springer(self):
        r = geometric_categorification()
        assert 'nilpotent' in r['springer']['springer_resolution'].lower()
        assert 'Perverse' in r['springer']['categorification']

    def test_geometric_langlands(self):
        r = geometric_categorification()
        assert 'D-modules' in r['geometric_langlands']['automorphic']
        assert 'Fargues-Scholze' in r['geometric_langlands']['fargues_scholze']

    def test_nakajima(self):
        r = geometric_categorification()
        assert 'quiver' in r['nakajima']['quiver_varieties'].lower()
        assert 'instanton' in r['nakajima']['instantons'].lower()


class TestQuantumGroupCategorification:
    def test_klr_algebras(self):
        r = quantum_group_categorification()
        assert '2008' in r['klr_algebras']['year']
        assert 'Rouquier' in r['klr_algebras']['year']

    def test_categorification_theorem(self):
        r = quantum_group_categorification()
        assert 'canonical basis' in r['categorification_theorem']['canonical_basis']
        assert 'crystal' in r['categorification_theorem']['crystal'].lower()

    def test_cyclotomic(self):
        r = quantum_group_categorification()
        assert 'V(λ)' in r['cyclotomic']['categorification']
        assert 'Ariki' in r['cyclotomic']['hecke']

    def test_two_category(self):
        r = quantum_group_categorification()
        assert 'E_i' in r['two_category']['one_morphisms']
        assert 'Natural' in r['two_category']['two_morphisms']


class TestKnotHomologyTheories:
    def test_knot_floer(self):
        r = knot_homology_theories()
        assert 'Alexander' in r['knot_floer']['definition']
        assert 'genus' in r['knot_floer']['detects_genus'].lower()
        assert 'fibered' in r['knot_floer']['detects_fibered']

    def test_homflypt(self):
        r = knot_homology_theories()
        assert 'HOMFLY' in r['homflypt']['target']
        assert 'triply' in r['homflypt']['triply_graded'].lower()

    def test_colored(self):
        r = knot_homology_theories()
        assert 'sl(n)' in r['colored']['sl_n']
        assert 'foam' in r['colored']['foam_category'].lower()

    def test_heegaard_floer(self):
        r = knot_homology_theories()
        assert 'HF' in r['heegaard_floer']['hf_hat']
        assert 'surgery' in r['heegaard_floer']['surgery_formula'].lower()


class TestHigherCategorification:
    def test_extended_tqft(self):
        r = higher_categorification()
        assert 'Lurie' in r['extended_tqft']['cobordism_hypothesis']
        assert 'point' in r['extended_tqft']['cobordism_hypothesis'].lower()

    def test_factorization_homology(self):
        r = higher_categorification()
        assert 'E_n' in r['factorization_homology']['definition']

    def test_derived(self):
        r = higher_categorification()
        assert 'DG' in r['derived']['dg_enhancement']
        assert 'stable' in r['derived']['stable_infinity'].lower()

    def test_symplectic_duality(self):
        r = higher_categorification()
        assert 'Coulomb' in r['symplectic_duality']['exchanges']
        assert 'mirror' in r['symplectic_duality']['physics'].lower()


class TestE8CategorificationConnection:
    def test_e8_categorified(self):
        r = e8_categorification_connection()
        assert 'KLR' in r['e8_categorified']['quantum_e8']
        assert '696729600' in r['e8_categorified']['soergel_e8']

    def test_geometric_e8(self):
        r = e8_categorification_connection()
        assert '120' in r['geometric_e8']['flag_variety']
        assert '70' in r['geometric_e8']['orbits']

    def test_w33_chain(self):
        r = e8_categorification_connection()
        assert 'categories' in r['w33_chain']['categorified_w33']
        assert 'positivity' in r['w33_chain']['positivity'].lower()
        assert '2-category' in r['w33_chain']['two_category']

    def test_future(self):
        r = e8_categorification_connection()
        assert '4-manifold' in r['future']['four_manifolds']
        assert 'Langlands' in r['future']['langlands']
