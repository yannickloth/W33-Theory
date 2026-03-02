"""
Tests for Pillar 182 -- Geometric Langlands & Hitchin Systems from W(3,3)
"""
import pytest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))
from THEORY_PART_CCLXXXII_GEOMETRIC_LANGLANDS_HITCHIN import (
    hitchin_system, geometric_langlands,
    kapustin_witten, hitchin_moduli_geometry,
    ngo_fundamental_lemma, opers_and_quantization
)


class TestHitchinSystem:
    def test_hitchin_1987(self):
        r = hitchin_system()
        assert '1987' in r['higgs_bundle']['hitchin_1987']

    def test_hyperkahler(self):
        r = hitchin_system()
        assert 'hyperkahler' in r['higgs_bundle']['hyperkahler']

    def test_spectral_curve(self):
        r = hitchin_system()
        assert 'spectral' in r['hitchin_fibration']['spectral_curve']

    def test_integrability(self):
        r = hitchin_system()
        assert 'integrable' in r['hitchin_fibration']['integrability']

    def test_w33_e6(self):
        r = hitchin_system()
        assert 'E6' in r['w33_hitchin']['group']

    def test_sp6f2_action(self):
        r = hitchin_system()
        assert 'Sp(6,F2)' in r['w33_hitchin']['symmetry']


class TestGeometricLanglands:
    def test_bun_g(self):
        r = geometric_langlands()
        assert 'Bun' in r['geometric']['bun_g']

    def test_d_modules(self):
        r = geometric_langlands()
        assert 'D-module' in r['geometric']['correspondence']

    def test_hecke_eigensheaves(self):
        r = geometric_langlands()
        assert 'Hecke' in r['geometric']['hecke_eigensheaves']

    def test_langlands_dual(self):
        r = geometric_langlands()
        assert 'dual' in r['classical']['langlands_dual']

    def test_e6_self_dual(self):
        r = geometric_langlands()
        assert 'self-dual' in r['w33_langlands']['e6_dual'] or 'E6' in r['w33_langlands']['e6_dual']

    def test_categorical(self):
        r = geometric_langlands()
        assert 'categorical' in r['geometric']['categorical'].lower() or 'equivalence' in r['geometric']['categorical']


class TestKapustinWitten:
    def test_year_2006(self):
        r = kapustin_witten()
        assert '2006' in r['twist']['year']

    def test_s_duality(self):
        r = kapustin_witten()
        assert 'tau' in r['s_duality']['s_duality_action']

    def test_a_model(self):
        r = kapustin_witten()
        assert 'A-model' in r['twist']['a_twist']

    def test_b_model(self):
        r = kapustin_witten()
        assert 'B-model' in r['twist']['b_twist']

    def test_mirror_exchange(self):
        r = kapustin_witten()
        assert 'S-duality' in r['twist']['mirror'] or 'exchange' in r['twist']['mirror']

    def test_montonen_olive(self):
        r = kapustin_witten()
        assert 'Montonen' in r['s_duality']['montonen_olive']

    def test_self_mirror_w33(self):
        r = kapustin_witten()
        assert 'self-mirror' in r['w33_s_duality']['mirror_w33'] or 'mirror' in r['w33_s_duality']['mirror_w33']


class TestHitchinModuli:
    def test_quaternion_relations(self):
        r = hitchin_moduli_geometry()
        assert 'quaternion' in r['hyperkahler']['three_structures']

    def test_complex_i(self):
        r = hitchin_moduli_geometry()
        assert 'Dolbeault' in r['hyperkahler']['complex_I']

    def test_complex_j(self):
        r = hitchin_moduli_geometry()
        assert 'de Rham' in r['hyperkahler']['complex_J']

    def test_syz(self):
        r = hitchin_moduli_geometry()
        assert 'SYZ' in r['mirror']['syz']

    def test_hitchin_is_syz(self):
        r = hitchin_moduli_geometry()
        assert 'IS' in r['mirror']['hitchin_syz']

    def test_ks_wall_crossing(self):
        r = hitchin_moduli_geometry()
        assert 'Kontsevich' in r['wall_crossing']['ks_formula']


class TestNgoFundamentalLemma:
    def test_fields_medal(self):
        r = ngo_fundamental_lemma()
        assert 'Fields' in r['fundamental_lemma']['fields_medal']

    def test_year_2010(self):
        r = ngo_fundamental_lemma()
        assert '2010' in r['proof_strategy']['year']

    def test_perverse_sheaves(self):
        r = ngo_fundamental_lemma()
        assert 'perverse' in r['proof_strategy']['perverse_sheaves']

    def test_langlands_shelstad(self):
        r = ngo_fundamental_lemma()
        assert 'Langlands' in r['fundamental_lemma']['langlands_shelstad']

    def test_w33_endoscopy(self):
        r = ngo_fundamental_lemma()
        assert 'endoscopic' in r['w33_lemma']['endoscopic_groups'].lower()


class TestOpersQuantization:
    def test_borel_reduction(self):
        r = opers_and_quantization()
        assert 'Borel' in r['opers']['definition']

    def test_beilinson_drinfeld(self):
        r = opers_and_quantization()
        assert 'Beilinson' in r['opers']['beilinson_drinfeld']

    def test_quantum_gl(self):
        r = opers_and_quantization()
        assert 'hbar' in r['quantum_gl']['deformation'] or 'deform' in r['quantum_gl']['deformation']

    def test_gaudin_model(self):
        r = opers_and_quantization()
        assert 'Gaudin' in r['quantum_gl']['gaudin_model']

    def test_unification(self):
        r = opers_and_quantization()
        assert 'unif' in r['physics_connections']['unification']


class TestSelfChecks:
    def test_all_pass(self):
        from THEORY_PART_CCLXXXII_GEOMETRIC_LANGLANDS_HITCHIN import run_self_checks
        assert run_self_checks() is True
