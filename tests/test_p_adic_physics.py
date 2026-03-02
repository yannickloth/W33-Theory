"""Tests for Pillar 190 - p-adic Physics & Non-Archimedean Geometry."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P190():
    return importlib.import_module("THEORY_PART_CCXC_P_ADIC_PHYSICS")

class TestPAdicNumbers:
    def test_ostrowski(self, P190):
        r = P190.p_adic_numbers()
        assert 'Ostrowski' in r['foundations']['ostrowski']
    def test_hensel(self, P190):
        r = P190.p_adic_numbers()
        assert 'Hensel' in r['foundations']['hensel']
    def test_totally_disconnected(self, P190):
        r = P190.p_adic_numbers()
        assert 'disconnected' in r['topology']['totally_disconnected']
    def test_over_f2(self, P190):
        r = P190.p_adic_numbers()
        assert 'F_2' in r['w33_padics']['over_f2']

class TestPAdicStrings:
    def test_volovich(self, P190):
        r = P190.p_adic_strings()
        assert 'Volovich' in r['amplitudes']['volovich']
    def test_freund_witten(self, P190):
        r = P190.p_adic_strings()
        assert 'Freund' in r['amplitudes']['freund_witten']
    def test_product_formula(self, P190):
        r = P190.p_adic_strings()
        assert 'product' in r['adelic']['adelic_product'].lower()
    def test_tate(self, P190):
        r = P190.p_adic_strings()
        assert 'Tate' in r['adelic']['tate_thesis']

class TestBerkovichSpaces:
    def test_berkovich_1990(self, P190):
        r = P190.berkovich_spaces()
        assert 'Berkovich' in r['berkovich']['berkovich_1990']
    def test_path_connected(self, P190):
        r = P190.berkovich_spaces()
        assert 'path-connected' in r['berkovich']['path_connected']
    def test_skeleton(self, P190):
        r = P190.berkovich_spaces()
        assert 'skeleton' in r['analytification']['skeleton'].lower()
    def test_tropicalization(self, P190):
        r = P190.berkovich_spaces()
        assert 'Payne' in r['analytification']['tropicalization'] or 'tropicalization' in r['analytification']['tropicalization'].lower()

class TestPerfectoidSpaces:
    def test_scholze(self, P190):
        r = P190.perfectoid_spaces()
        assert 'Scholze' in r['perfectoid']['scholze_2012']
    def test_fields_medal(self, P190):
        r = P190.perfectoid_spaces()
        assert 'Fields' in r['perfectoid']['scholze_2012']
    def test_tilting(self, P190):
        r = P190.perfectoid_spaces()
        assert 'Tilting' in r['perfectoid']['tilting'] or 'tilting' in r['perfectoid']['tilting']
    def test_prismatic(self, P190):
        r = P190.perfectoid_spaces()
        assert 'Prismatic' in r['applications']['prismatic'] or 'prismatic' in r['applications']['prismatic']

class TestPAdicQM:
    def test_vladimirov(self, P190):
        r = P190.p_adic_quantum_mechanics()
        assert 'Vladimirov' in r['quantum_mechanics']['vladimirov']
    def test_planck(self, P190):
        r = P190.p_adic_quantum_mechanics()
        assert 'Planck' in r['cosmology']['planck_scale']
    def test_dragovich(self, P190):
        r = P190.p_adic_quantum_mechanics()
        assert 'Dragovich' in r['quantum_mechanics']['dragovich']

class TestCondensedMath:
    def test_clausen_scholze(self, P190):
        r = P190.condensed_mathematics()
        assert 'Clausen' in r['condensed']['clausen_scholze']
    def test_abelian(self, P190):
        r = P190.condensed_mathematics()
        assert 'abelian' in r['condensed']['abelian'].lower()
    def test_solid(self, P190):
        r = P190.condensed_mathematics()
        assert 'Solid' in r['condensed']['solid'] or 'solid' in r['condensed']['solid']

class TestSelfChecks:
    def test_all_pass(self, P190):
        assert P190.run_self_checks() is True
