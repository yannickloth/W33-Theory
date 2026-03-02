"""Tests for Pillar 199 - Symplectic Field Theory."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P199():
    return importlib.import_module("THEORY_PART_CCXCIX_SYMPLECTIC_FIELD_THEORY")

class TestSFTFoundations:
    def test_egh(self, P199):
        r = P199.sft_foundations()
        assert 'Eliashberg' in r['eliashberg_givental_hofer']['sft_2000']
    def test_reeb(self, P199):
        r = P199.sft_foundations()
        assert 'Reeb' in r['reeb_dynamics']['reeb_orbits']
    def test_master_eq(self, P199):
        r = P199.sft_foundations()
        assert 'master' in r['eliashberg_givental_hofer']['master_equation'].lower() or 'H' in r['eliashberg_givental_hofer']['master_equation']

class TestContactTopology:
    def test_martinet(self, P199):
        r = P199.contact_topology()
        assert 'Martinet' in r['contact_structures']['martinet_theorem']
    def test_eliashberg(self, P199):
        r = P199.contact_topology()
        assert 'Eliashberg' in r['tight_overtwisted']['eliashberg_1989']
    def test_thurston_bennequin(self, P199):
        r = P199.contact_topology()
        assert 'Thurston' in r['legendrian_knots']['thurston_bennequin'] or 'tb' in r['legendrian_knots']['thurston_bennequin']

class TestLegendrian:
    def test_chekanov(self, P199):
        r = P199.legendrian_contact()
        assert 'Chekanov' in r['chekanov_eliashberg_dga']['chekanov_2002']
    def test_augmentation(self, P199):
        r = P199.legendrian_contact()
        assert 'augmentation' in r['augmentations']['definition'].lower() or 'Augmentation' in r['augmentations']['definition']
    def test_ruling(self, P199):
        r = P199.legendrian_contact()
        assert 'ruling' in r['legendrian_invariants']['ruling_polynomials'].lower() or 'Ruling' in r['legendrian_invariants']['ruling_polynomials']

class TestRationalSFT:
    def test_bee(self, P199):
        r = P199.rational_sft()
        assert 'Bourgeois' in r['surgery_formula']['bee_2012']
    def test_neck(self, P199):
        r = P199.rational_sft()
        assert 'neck' in r['neck_stretching']['neck_stretching_technique'].lower() or 'Neck' in r['neck_stretching']['neck_stretching_technique']
    def test_cobordism(self, P199):
        r = P199.rational_sft()
        assert 'cobordism' in r['cobordism_exact']['cobordism_functoriality'].lower() or 'Cobordism' in r['cobordism_exact']['cobordism_functoriality']

class TestPolyfolds:
    def test_hwz(self, P199):
        r = P199.polyfolds_and_regularization()
        assert 'Hofer' in r['polyfold_theory']['hwz_polyfolds']
    def test_kuranishi(self, P199):
        r = P199.polyfolds_and_regularization()
        assert 'Fukaya' in r['kuranishi_structures']['fukaya_ono_1999']

class TestW33SFT:
    def test_contact(self, P199):
        r = P199.w33_sft_synthesis()
        assert 'contact' in r['w33_contact_structure']['symplectic_to_contact'].lower() or 'Contact' in r['w33_contact_structure']['symplectic_to_contact']
    def test_sp6(self, P199):
        r = P199.w33_sft_synthesis()
        assert '1451520' in r['sp6f2_contactomorphisms']['group_order']
    def test_40_reeb(self, P199):
        r = P199.w33_sft_synthesis()
        assert '315' in r['legendrian_isotropic']['isotropic_lines'] or 'isotropic' in r['legendrian_isotropic']['isotropic_lines'].lower()

class TestSelfChecks:
    def test_all_pass(self, P199):
        assert P199.run_self_checks() is True
