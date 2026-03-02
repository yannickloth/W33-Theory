"""Tests for Pillar 202 - Tensor Networks & MERA."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P202():
    return importlib.import_module("THEORY_PART_CCCII_TENSOR_NETWORKS_MERA")

class TestTensorNetworkBasics:
    def test_contraction(self, P202):
        r = P202.tensor_network_basics()
        assert 'contraction' in r['tensors']['contraction'].lower()
    def test_white_dmrg(self, P202):
        r = P202.tensor_network_basics()
        assert 'White' in r['dmrg']['white_1992']
    def test_area_law(self, P202):
        r = P202.tensor_network_basics()
        assert 'area' in r['entanglement']['area_law'].lower()
    def test_mps(self, P202):
        r = P202.tensor_network_basics()
        assert 'matrix product' in r['mps']['definition'].lower() or 'MPS' in r['mps']['definition']

class TestMERA:
    def test_vidal(self, P202):
        r = P202.mera()
        assert 'Vidal' in r['definition']['vidal_2007']
    def test_disentanglers(self, P202):
        r = P202.mera()
        assert 'disentangler' in r['definition']['disentanglers'].lower()
    def test_scale(self, P202):
        r = P202.mera()
        assert 'scale' in r['scale_invariance']['fixed_point'].lower() or 'Scale' in r['scale_invariance']['fixed_point']

class TestPEPS:
    def test_peps_def(self, P202):
        r = P202.peps_and_tns()
        assert 'PEPS' in r['peps']['definition'] or 'projected' in r['peps']['definition'].lower()
    def test_p_hard(self, P202):
        r = P202.peps_and_tns()
        assert '#P' in r['complexity']['contraction']
    def test_anyons(self, P202):
        r = P202.peps_and_tns()
        assert 'anyon' in r['topological']['anyons'].lower()

class TestHolographic:
    def test_swingle(self, P202):
        r = P202.holographic_tensor_networks()
        assert 'Swingle' in r['ads_cft_tn']['swingle']
    def test_happy(self, P202):
        r = P202.holographic_tensor_networks()
        assert 'Pastawski' in r['happy_code']['authors'] or 'HaPPY' in r['happy_code']['authors']
    def test_rt(self, P202):
        r = P202.holographic_tensor_networks()
        assert 'Ryu' in r['ryu_takayanagi']['formula'] or 'RT' in r['ryu_takayanagi']['formula']

class TestQComputing:
    def test_stabilizer(self, P202):
        r = P202.quantum_computing_tn()
        assert 'stabilizer' in r['error_correction']['stabilizer_tn'].lower()
    def test_magic(self, P202):
        r = P202.quantum_computing_tn()
        assert 'stabilizer' in r['magic_states']['stabilizer_rank'].lower()

class TestW33TN:
    def test_40_tensors(self, P202):
        r = P202.w33_tensor_network_synthesis()
        assert '40' in r['w33_network']['points_as_tensors']
    def test_sp6f2(self, P202):
        r = P202.w33_tensor_network_synthesis()
        assert 'Sp(6' in r['sp6f2_symmetry']['symmetry'] or '1451520' in r['sp6f2_symmetry']['symmetry']
    def test_holographic_w33(self, P202):
        r = P202.w33_tensor_network_synthesis()
        assert 'holographic' in r['holographic_w33']['holographic'].lower()

class TestSelfChecks:
    def test_all_pass(self, P202):
        assert P202.run_self_checks() is True
