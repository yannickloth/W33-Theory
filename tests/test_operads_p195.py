"""Tests for Pillar 195 - Operads and Modular Operads."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P195():
    return importlib.import_module("THEORY_PART_CCXCV_OPERADS_AND_MODULAR_OPERADS")

class TestOperadBasics:
    def test_may(self, P195):
        r = P195.operad_basics()
        assert 'May' in r['may_definition']['origin']
    def test_stasheff(self, P195):
        r = P195.operad_basics()
        assert 'Stasheff' in r['associahedra']['stasheff']
    def test_boardman_vogt(self, P195):
        r = P195.operad_basics()
        assert 'Boardman' in r['little_cubes']['boardman_vogt']
    def test_free_operad(self, P195):
        r = P195.operad_basics()
        assert 'tree' in r['free_and_trees']['free_operad'].lower() or 'free' in r['free_and_trees']['free_operad'].lower()

class TestExamplesClassification:
    def test_ginzburg_kapranov(self, P195):
        r = P195.examples_and_classification()
        assert 'Ginzburg' in r['koszul_duality']['ginzburg_kapranov']
    def test_lie_operad(self, P195):
        r = P195.examples_and_classification()
        assert 'Lie' in r['classical_operads']['lie']
    def test_koszul_criterion(self, P195):
        r = P195.examples_and_classification()
        assert 'Koszul' in r['koszul_duality']['criterion'] or 'koszul' in r['koszul_duality']['criterion'].lower()
    def test_a_infinity(self, P195):
        r = P195.examples_and_classification()
        assert 'A_infinity' in r['infinity_algebras']['a_infinity'] or 'A_∞' in r['infinity_algebras']['a_infinity']

class TestModularOperads:
    def test_getzler_kapranov(self, P195):
        r = P195.modular_operads()
        assert 'Getzler' in r['getzler_kapranov']['origin']
    def test_feynman(self, P195):
        r = P195.modular_operads()
        assert 'Feynman' in r['feynman_diagrams']['connection']
    def test_w33_modular(self, P195):
        r = P195.modular_operads()
        assert '40' in r['w33_modular']['genus_labeling']
    def test_moduli(self, P195):
        r = P195.modular_operads()
        assert 'moduli' in r['moduli_spaces']['moduli'].lower()

class TestHomotopyAlgebras:
    def test_kontsevich(self, P195):
        r = P195.homotopy_algebras()
        assert 'Kontsevich' in r['formality']['kontsevich']
    def test_fields(self, P195):
        r = P195.homotopy_algebras()
        assert 'Fields' in r['formality']['fields_medal']
    def test_transfer(self, P195):
        r = P195.homotopy_algebras()
        assert 'transfer' in r['homotopy_transfer']['theorem'].lower() or 'Transfer' in r['homotopy_transfer']['theorem']

class TestCyclicProperads:
    def test_vallette(self, P195):
        r = P195.cyclic_and_properads()
        assert 'Vallette' in r['properads_props']['properad']
    def test_willwacher(self, P195):
        r = P195.cyclic_and_properads()
        assert 'Willwacher' in r['graph_complexes']['willwacher']
    def test_grt(self, P195):
        r = P195.cyclic_and_properads()
        assert 'GRT' in r['grt']['definition'] or 'Grothendieck' in r['grt']['definition']

class TestW33Synthesis:
    def test_40_ops(self, P195):
        r = P195.w33_operad_synthesis()
        assert '40' in r['w33_operad']['points_as_ops']
    def test_three_families(self, P195):
        r = P195.w33_operad_synthesis()
        assert 'three' in r['arity_filtration']['arity_3'].lower()
    def test_equivariant(self, P195):
        r = P195.w33_operad_synthesis()
        assert 'Sp(6' in r['w33_operad']['equivariant']

class TestSelfChecks:
    def test_all_pass(self, P195):
        assert P195.run_self_checks() is True
