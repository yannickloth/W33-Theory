"""Tests for Pillar 197 - Quantum Channels & Information."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P197():
    return importlib.import_module("THEORY_PART_CCXCVII_QUANTUM_CHANNELS_INFO")

class TestQuantumChannels:
    def test_cptp(self, P197):
        r = P197.quantum_channels_basics()
        assert 'CPTP' in r['cptp_maps']['definition']
    def test_kraus(self, P197):
        r = P197.quantum_channels_basics()
        assert 'Kraus' in r['kraus_representation']['kraus_1971']
    def test_stinespring(self, P197):
        r = P197.quantum_channels_basics()
        assert 'Stinespring' in r['stinespring_dilation']['theorem']
    def test_choi(self, P197):
        r = P197.quantum_channels_basics()
        assert 'Choi' in r['choi_jamiolkowski']['choi_1975']

class TestEntanglement:
    def test_chsh(self, P197):
        r = P197.entanglement_theory()
        assert 'CHSH' in r['bell_states']['chsh_inequality']
    def test_ppt(self, P197):
        r = P197.entanglement_theory()
        assert 'Peres' in r['ppt_criterion']['peres_1996']
    def test_horodecki(self, P197):
        r = P197.entanglement_theory()
        assert 'Horodecki' in r['distillation_bound']['horodecki_1998']
    def test_negativity(self, P197):
        r = P197.entanglement_theory()
        assert 'negativity' in r['entanglement_measures']['negativity'].lower() or 'Negativity' in r['entanglement_measures']['negativity']

class TestQEC:
    def test_knill_laflamme(self, P197):
        r = P197.quantum_error_correction_channels()
        assert 'Knill' in r['knill_laflamme']['conditions']
    def test_lloyd(self, P197):
        r = P197.quantum_error_correction_channels()
        assert 'Lloyd' in r['quantum_capacity']['lloyd_1997']
    def test_devetak(self, P197):
        r = P197.quantum_error_correction_channels()
        assert 'Devetak' in r['quantum_capacity']['devetak_2005']

class TestResourceTheories:
    def test_chitambar(self, P197):
        r = P197.quantum_resource_theories()
        assert 'Chitambar' in r['framework']['chitambar_gour_2019']
    def test_veitch(self, P197):
        r = P197.quantum_resource_theories()
        assert 'Veitch' in r['magic_resource']['veitch_2014']
    def test_wigner(self, P197):
        r = P197.quantum_resource_theories()
        assert 'Wigner' in r['magic_resource']['wigner_negativity']

class TestThermo:
    def test_landauer(self, P197):
        r = P197.quantum_thermodynamics()
        assert 'Landauer' in r['landauer_principle']['erasure'] or 'erasure' in r['landauer_principle']['erasure'].lower()
    def test_brandao(self, P197):
        r = P197.quantum_thermodynamics()
        val = r['thermal_operations']['brandao_2015']
        assert 'Brand' in val or 'second' in val.lower()

class TestW33Channel:
    def test_40_kraus(self, P197):
        r = P197.w33_channel_synthesis()
        assert '40' in r['kraus_from_w33']['isotropic_lines'] or 'isotropic' in r['kraus_from_w33']['isotropic_lines'].lower()
    def test_sp6_covariance(self, P197):
        r = P197.w33_channel_synthesis()
        assert '1451520' in r['covariant_channel']['symmetry_order']

class TestSelfChecks:
    def test_all_pass(self, P197):
        assert P197.run_self_checks() is True
