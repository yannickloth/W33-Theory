"""Tests for Pillar 191 - Derived Algebraic Geometry."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P191():
    return importlib.import_module("THEORY_PART_CCXCI_DERIVED_ALGEBRAIC_GEOMETRY")

class TestDerivedSchemes:
    def test_cotangent(self, P191):
        r = P191.derived_schemes()
        assert 'cotangent' in r['foundations']['cotangent'].lower() or 'Cotangent' in r['foundations']['cotangent']
    def test_virtual_class(self, P191):
        r = P191.derived_schemes()
        assert 'virtual' in r['moduli']['virtual_class'].lower()
    def test_virtual_dim(self, P191):
        r = P191.derived_schemes()
        assert 'unobstructed' in r['w33_derived']['virtual_dim'].lower()
    def test_gw(self, P191):
        r = P191.derived_schemes()
        assert 'GW' in r['moduli']['gw_invariants']

class TestShiftedSymplectic:
    def test_ptvv(self, P191):
        r = P191.shifted_symplectic()
        assert '2013' in r['ptvv']['ptvv_2013']
    def test_dt_invariants(self, P191):
        r = P191.shifted_symplectic()
        assert 'sheaves' in r['dt_theory']['definition']
    def test_sp6f2_count(self, P191):
        r = P191.shifted_symplectic()
        assert '1451520' in r['w33_shifted']['counting_w33']
    def test_lagrangian(self, P191):
        r = P191.shifted_symplectic()
        assert 'Lagrangian' in r['ptvv']['lagrangian']

class TestFormalModuli:
    def test_lurie_2011(self, P191):
        r = P191.formal_moduli()
        assert 'Lurie' in r['formal']['lurie_2011']
    def test_koszul(self, P191):
        r = P191.formal_moduli()
        assert 'Koszul' in r['koszul']['classical']
    def test_maurer_cartan(self, P191):
        r = P191.formal_moduli()
        assert 'MC' in r['formal']['maurer_cartan'] or 'Maurer' in r['formal']['maurer_cartan']
    def test_l_infinity(self, P191):
        r = P191.formal_moduli()
        assert 'L_infinity' in r['w33_formal']['l_infinity']

class TestDerivedIntersection:
    def test_bondal_orlov(self, P191):
        r = P191.derived_intersection()
        assert 'Bondal' in r['categories']['bondal_orlov']
    def test_bridgeland(self, P191):
        r = P191.derived_intersection()
        assert 'Bridgeland' in r['categories']['stability']
    def test_serre(self, P191):
        r = P191.derived_intersection()
        assert 'Serre' in r['intersections']['serre']

class TestDerivedLoops:
    def test_hkr(self, P191):
        r = P191.derived_loop_spaces()
        assert 'HKR' in r['loops']['hkr']
    def test_bzfn(self, P191):
        r = P191.derived_loop_spaces()
        assert 'Ben-Zvi' in r['loops']['ben_zvi_francis_nadler']
    def test_lefschetz(self, P191):
        r = P191.derived_loop_spaces()
        assert 'Lefschetz' in r['traces']['lefschetz']

class TestDerivedDeformation:
    def test_rigid(self, P191):
        r = P191.derived_deformation_theory()
        assert 'rigid' in r['w33_deformation']['rigidity'].lower()
    def test_hall(self, P191):
        r = P191.derived_deformation_theory()
        assert 'Hall' in r['moduli_objects']['hall_algebra']
    def test_unique(self, P191):
        r = P191.derived_deformation_theory()
        assert 'unique' in r['w33_deformation']['uniqueness'].lower()

class TestSelfChecks:
    def test_all_pass(self, P191):
        assert P191.run_self_checks() is True
