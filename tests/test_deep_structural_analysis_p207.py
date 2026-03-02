"""
Tests for Pillar 207: Deep Structural Analysis - What W(3,3) Really Is
Module: THEORY_PART_CCCVII_DEEP_STRUCTURAL_ANALYSIS
"""
import importlib
import pytest

@pytest.fixture(scope="module")
def mod():
    return importlib.import_module("pillars.THEORY_PART_CCCVII_DEEP_STRUCTURAL_ANALYSIS")


class TestProvenTheorems:
    def test_weyl_e7_isomorphism(self, mod):
        r = mod.proven_theorems()
        assert "W(E7)" in r['weyl_e7_isomorphism']['statement']
        assert "Sp(6,F2)" in r['weyl_e7_isomorphism']['statement']

    def test_weyl_e6_identification(self, mod):
        r = mod.proven_theorems()
        assert "51840" in r['weyl_e6_identification']['order_identity']

    def test_index_28_embedding(self, mod):
        r = mod.proven_theorems()
        assert "28" in r['index_28_embedding']['statement']
        assert "bitangent" in r['index_28_embedding']['bitangent_connection']

    def test_complement_27(self, mod):
        r = mod.proven_theorems()
        assert "27" in r['complement_27']['statement']
        assert "non-neighbor" in r['complement_27']['statement']

    def test_edge_count_240(self, mod):
        r = mod.proven_theorems()
        assert "240" in r['edge_count_240']['statement']
        assert "E8" in r['edge_count_240']['e8_root_count']

    def test_eigenvalue_decomposition(self, mod):
        r = mod.proven_theorems()
        assert "1 + 24 + 15" in r['eigenvalue_decomposition']['su5_decomposition'] or "1+24+15" in r['eigenvalue_decomposition']['su5_decomposition']

    def test_all_keys_present(self, mod):
        r = mod.proven_theorems()
        expected = ['weyl_e7_isomorphism', 'weyl_e6_identification', 'index_28_embedding',
                     'complement_27', 'edge_count_240', 'eigenvalue_decomposition']
        for k in expected:
            assert k in r


class TestNumericalRelations:
    def test_e8_dimension(self, mod):
        r = mod.numerical_relations()
        assert "248" in r['e8_dimension']['formula']
        assert "6 * 40" in r['e8_dimension']['formula']

    def test_e8_roots(self, mod):
        r = mod.numerical_relations()
        assert "240" in r['e8_roots']['formula']

    def test_e6_dimension(self, mod):
        r = mod.numerical_relations()
        assert "78" in r['e6_dimension']['formula']

    def test_stabilizer_structure(self, mod):
        r = mod.numerical_relations()
        assert "36288" in r['stabilizer_structure']['formula']
        assert "72" in r['stabilizer_structure']['formula']

    def test_weyl_e8_factorization(self, mod):
        r = mod.numerical_relations()
        assert "696729600" in r['weyl_e8_factorization']['formula']


class TestAlphaFormula:
    def test_formula_expression(self, mod):
        r = mod.alpha_formula_analysis()
        assert "alpha" in r['formula']['expression']

    def test_computation_137(self, mod):
        r = mod.alpha_formula_analysis()
        assert "137" in r['formula']['computation']

    def test_denominator_1111(self, mod):
        r = mod.alpha_formula_analysis()
        assert "1111" in r['denominator_1111']['value']
        assert "11" in r['denominator_1111']['value']

    def test_experimental_value(self, mod):
        r = mod.alpha_formula_analysis()
        assert "137.035999" in r['formula']['experimental']

    def test_assessment_status(self, mod):
        r = mod.alpha_formula_analysis()
        assert isinstance(r['assessment']['status'], str)


class TestStructuralHierarchy:
    def test_level_0_geometry(self, mod):
        r = mod.structural_hierarchy()
        assert "40" in r['level_0_geometry']['points']
        assert "GF(3)" in r['level_0_geometry']['field']

    def test_level_1_automorphism(self, mod):
        r = mod.structural_hierarchy()
        assert "51840" in r['level_1_automorphism']['group']

    def test_level_2_extension(self, mod):
        r = mod.structural_hierarchy()
        assert "1451520" in r['level_2_extension']['group']
        assert "28" in r['level_2_extension']['group']

    def test_level_3_e7(self, mod):
        r = mod.structural_hierarchy()
        assert "W(E7)" in r['level_3_e7']['group']

    def test_level_4_e8(self, mod):
        r = mod.structural_hierarchy()
        assert "240" in r['level_4_e8']['root_system']


class TestOpenProblems:
    def test_bijection_240(self, mod):
        r = mod.open_problems()
        assert "bijection" in r['bijection_240']['question']
        assert "240" in r['bijection_240']['question']

    def test_alpha_derivation(self, mod):
        r = mod.open_problems()
        assert "alpha" in r['alpha_derivation']['question']

    def test_three_generations(self, mod):
        r = mod.open_problems()
        assert "3" in r['three_generations']['question']

    def test_correct_automorphism(self, mod):
        r = mod.open_problems()
        assert "51840" in r['correct_automorphism']['status'] or "W(E6)" in r['correct_automorphism']['status']

    def test_leech_connection(self, mod):
        r = mod.open_problems()
        assert "196560" in r['leech_connection']['question'] or "Leech" in r['leech_connection']['question']


class TestMetaSynthesis:
    def test_genuine_mathematics(self, mod):
        r = mod.meta_synthesis()
        assert "REAL" in r['genuine_mathematics']['summary'] or "real" in r['genuine_mathematics']['summary'].lower()

    def test_strongest_physics_claim(self, mod):
        r = mod.meta_synthesis()
        assert "alpha" in r['strongest_physics_claim']['summary']

    def test_errors_to_fix(self, mod):
        r = mod.meta_synthesis()
        assert "1451520" in r['errors_to_fix']['automorphism_group']
        assert "51840" in r['errors_to_fix']['correct_value']

    def test_research_directions(self, mod):
        r = mod.meta_synthesis()
        assert isinstance(r['research_directions']['priority_1'], str)
        assert isinstance(r['research_directions']['meta'], str)
