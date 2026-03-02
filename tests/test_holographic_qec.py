"""Tests for Pillar 183 - Holographic Quantum Error Correction."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P183():
    return importlib.import_module("THEORY_PART_CCLXXXIII_HOLOGRAPHIC_QEC")

# ── quantum_error_correction_basics ────────────────────────
class TestQECBasics:
    def test_stabilizer(self, P183):
        r = P183.quantum_error_correction_basics()
        assert 'stabilizer' in r['fundamentals']['stabilizer'].lower()

    def test_sp6f2_stabilizer(self, P183):
        r = P183.quantum_error_correction_basics()
        assert 'Sp(6,F2)' in r['w33_code']['stabilizer_group']

    def test_40_qudits(self, P183):
        r = P183.quantum_error_correction_basics()
        assert '40' in r['w33_code']['structure']

    def test_code_distance(self, P183):
        r = P183.quantum_error_correction_basics()
        assert 'error' in r['fundamentals']['distance'].lower()

    def test_steane(self, P183):
        r = P183.quantum_error_correction_basics()
        assert 'Steane' in r['key_codes']['steane_7']

    def test_symplectic(self, P183):
        r = P183.quantum_error_correction_basics()
        assert 'symplectic' in r['w33_code']['symplectic'].lower() or 'Symplectic' in r['w33_code']['symplectic']

# ── holographic_codes ──────────────────────────────────────
class TestHolographicCodes:
    def test_happy_code(self, P183):
        r = P183.holographic_codes()
        assert 'HaPPY' in r['happy']['name'] or '2015' in r['happy']['name']

    def test_rt_formula(self, P183):
        r = P183.holographic_codes()
        assert 'Ryu-Takayanagi' in r['happy']['rt_formula'] or 'RT' in r['happy']['rt_formula']

    def test_mera(self, P183):
        r = P183.holographic_codes()
        assert 'MERA' in r['tensor_networks']['mera']

    def test_w33_holographic(self, P183):
        r = P183.holographic_codes()
        assert '40' in r['w33_holographic']['boundary_count']

    def test_bit_threads(self, P183):
        r = P183.holographic_codes()
        assert 'Freedman' in r['tensor_networks']['bit_threads'] or 'bit thread' in r['tensor_networks']['bit_threads'].lower()

# ── bulk_reconstruction ────────────────────────────────────
class TestBulkReconstruction:
    def test_adh_year(self, P183):
        r = P183.bulk_reconstruction()
        assert '2015' in r['adh']['year']

    def test_entanglement_wedge(self, P183):
        r = P183.bulk_reconstruction()
        assert 'entanglement' in r['entanglement_wedge']['definition'].lower() or 'wedge' in r['entanglement_wedge']['definition'].lower()

    def test_reconstruction(self, P183):
        r = P183.bulk_reconstruction()
        assert 'reconstruct' in r['entanglement_wedge']['reconstruction'].lower()

    def test_w33_graph_cuts(self, P183):
        r = P183.bulk_reconstruction()
        assert 'W(3,3)' in r['w33_reconstruction']['graph_cuts']

    def test_complementary(self, P183):
        r = P183.bulk_reconstruction()
        assert 'complementary' in r['adh']['complementary_recovery'].lower() or 'Complementary' in r['adh']['complementary_recovery']

# ── entanglement_entropy ───────────────────────────────────
class TestEntanglementEntropy:
    def test_rt_formula_area(self, P183):
        r = P183.entanglement_entropy()
        assert 'Area' in r['rt_formula']['formula']

    def test_quantum_extremal(self, P183):
        r = P183.entanglement_entropy()
        assert 'extremiz' in r['quantum_extremal']['definition'].lower() or 'extremal' in r['quantum_extremal']['definition'].lower()

    def test_island_formula(self, P183):
        r = P183.entanglement_entropy()
        assert 'island' in r['quantum_extremal']['island_formula'].lower() or 'Island' in r['quantum_extremal']['island_formula']

    def test_page_curve(self, P183):
        r = P183.entanglement_entropy()
        assert 'Page' in r['quantum_extremal']['page_curve']

    def test_replica_wormholes(self, P183):
        r = P183.entanglement_entropy()
        assert 'replica' in r['quantum_extremal']['replica_wormholes'].lower()

# ── qec_and_gravity ────────────────────────────────────────
class TestQECAndGravity:
    def test_er_epr(self, P183):
        r = P183.qec_and_gravity()
        assert 'ER' in r['gravity_entanglement']['er_epr'] and 'EPR' in r['gravity_entanglement']['er_epr']

    def test_complexity_volume(self, P183):
        r = P183.qec_and_gravity()
        assert 'volume' in r['complexity']['complexity_volume'].lower() or 'Volume' in r['complexity']['complexity_volume']

    def test_switchback(self, P183):
        r = P183.qec_and_gravity()
        assert 'switchback' in r['complexity']['switchback'].lower() or 'Switchback' in r['complexity']['switchback']

    def test_emergent_geometry(self, P183):
        r = P183.qec_and_gravity()
        assert 'emerge' in r['w33_gravity']['emergent_geometry'].lower()

# ── topological_codes ──────────────────────────────────────
class TestTopologicalCodes:
    def test_toric_code(self, P183):
        r = P183.topological_codes()
        assert 'Kitaev' in r['toric_code']['kitaev']

    def test_fibonacci_anyons(self, P183):
        r = P183.topological_codes()
        assert 'golden' in r['fibonacci']['golden_ratio'].lower() or 'phi' in r['fibonacci']['golden_ratio']

    def test_universal_computation(self, P183):
        r = P183.topological_codes()
        assert 'universal' in r['fibonacci']['universal'].lower()

    def test_w33_topological(self, P183):
        r = P183.topological_codes()
        assert 'W(3,3)' in str(r['w33_topological'])

# ── self-checks ────────────────────────────────────────────
class TestSelfChecks:
    def test_all_pass(self, P183):
        assert P183.run_self_checks() is True
