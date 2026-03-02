"""Tests for Pillar 148: Quantum Groups & Yangian Symmetry."""
import pytest, math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))

from THEORY_PART_CCXLVIII_QUANTUM_GROUPS import (
    yang_baxter_equation,
    hopf_algebras,
    drinfeld_jimbo,
    knot_invariants,
    yangians,
    integrable_systems,
    crystal_bases,
    quantum_groups_topology,
    r_matrix_quantum_det,
    fields_1990,
    quantum_e8,
    complete_chain_w33_to_quantum_groups,
    run_all_checks,
)


# ── Yang-Baxter Equation ─────────────────────────────────────────────────

class TestYangBaxterEquation:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = yang_baxter_equation()

    def test_yang_year(self):
        assert self.r['yang_year'] == 1967

    def test_baxter_year(self):
        assert self.r['baxter_year'] == 1972

    def test_equation_has_matrix_form(self):
        assert 'R_12' in self.r['equation']['matrix_form']
        assert 'R_23' in self.r['equation']['matrix_form']

    def test_physics_integrability(self):
        assert 'exact' in self.r['physics']['integrability'].lower() or \
               'solvab' in self.r['physics']['integrability'].lower()

    def test_solutions_types(self):
        assert 'rational' in self.r['solutions']
        assert 'trigonometric' in self.r['solutions']
        assert 'elliptic' in self.r['solutions']

    def test_braid_group_connection(self):
        assert 'knot_invariants' in self.r['braid_group']


# ── Hopf Algebras ─────────────────────────────────────────────────────────

class TestHopfAlgebras:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = hopf_algebras()

    def test_has_algebra_structure(self):
        assert 'multiplication' in self.r['structure']['algebra'].lower() or \
               'algebra' in self.r['structure']['algebra'].lower()

    def test_has_coalgebra_structure(self):
        assert 'comultiplication' in self.r['structure']['coalgebra'].lower()

    def test_antipode(self):
        assert 'antipode' in self.r['structure']

    def test_quantum_groups_neither_commutative_nor_cocommutative(self):
        qg = self.r['key_properties']['quantum_groups'].lower()
        assert 'commutative' in qg

    def test_quasitriangular_gives_ybe(self):
        assert 'yang-baxter' in self.r['quasitriangular']['yang_baxter'].lower() or \
               'Yang-Baxter' in self.r['quasitriangular']['yang_baxter']


# ── Drinfeld-Jimbo Quantum Groups ────────────────────────────────────────

class TestDrinfeldJimbo:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = drinfeld_jimbo()

    def test_year_1985(self):
        assert self.r['year'] == 1985

    def test_authors_include_drinfeld(self):
        assert any('Drinfeld' in a for a in self.r['authors'])

    def test_authors_include_jimbo(self):
        assert any('Jimbo' in a for a in self.r['authors'])

    def test_notation(self):
        assert self.r['notation'] == 'U_q(g)'

    def test_classical_limit(self):
        assert 'q -> 1' in self.r['definition']['limit'] or \
               'q->1' in self.r['definition']['limit']

    def test_uq_e8_rank(self):
        assert self.r['examples']['U_q_E8']['rank'] == 8

    def test_uq_e8_dim(self):
        assert self.r['examples']['U_q_E8']['dimension'] == 248

    def test_uq_e8_w33(self):
        assert 'W(3,3)' in self.r['examples']['U_q_E8']['w33_connection']

    def test_hopf_structure_coproduct(self):
        assert 'tensor' in self.r['hopf_structure']['coproduct_e'].lower()

    def test_crystal_base_representation(self):
        assert 'Kashiwara' in self.r['representations']['crystal_base']


# ── Knot Invariants ──────────────────────────────────────────────────────

class TestKnotInvariants:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = knot_invariants()

    def test_jones_year(self):
        assert self.r['jones_polynomial']['year'] == 1984

    def test_jones_fields_medal(self):
        assert 'Fields Medal' in self.r['jones_polynomial']['discoverer']

    def test_jones_from_quantum_group(self):
        assert 'sl_2' in self.r['jones_polynomial']['quantum_group_origin']

    def test_rt_year(self):
        assert self.r['reshetikhin_turaev']['year'] == 1990

    def test_chern_simons_year(self):
        assert self.r['chern_simons']['year'] == 1989

    def test_chern_simons_witten(self):
        assert 'Witten' in self.r['chern_simons']['author']

    def test_categorification_khovanov(self):
        assert 'Khovanov' in self.r['categorification']['khovanov']


# ── Yangians ─────────────────────────────────────────────────────────────

class TestYangians:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = yangians()

    def test_year(self):
        assert self.r['year'] == 1985

    def test_named_after_yang(self):
        assert self.r['named_after'] == 'C.N. Yang'

    def test_introduced_by_drinfeld(self):
        assert 'Drinfeld' in self.r['introduced_by']

    def test_psu224_symmetry(self):
        assert 'N=4 SYM' in self.r['psu224']['relevance']

    def test_psu224_discovery(self):
        assert '2009' in self.r['psu224']['discovery']

    def test_infinite_dimensional(self):
        assert self.r['properties']['infinite_dimensional'] is True

    def test_drinfeld_polynomials(self):
        assert 'Drinfeld' in self.r['representations']['finite_dim']


# ── Integrable Systems ───────────────────────────────────────────────────

class TestIntegrableSystems:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = integrable_systems()

    def test_xxx_yangian(self):
        assert 'Yangian' in self.r['spin_chains']['xxx_chain']['symmetry']

    def test_xxz_quantum_group(self):
        assert 'U_q' in self.r['spin_chains']['xxz_chain']['symmetry']

    def test_xyz_elliptic(self):
        assert 'elliptic' in self.r['spin_chains']['xyz_chain']['r_matrix'].lower()

    def test_qism_school(self):
        assert 'Leningrad' in self.r['qism']['school'] or \
               'Petersburg' in self.r['qism']['school']


# ── Crystal Bases ────────────────────────────────────────────────────────

class TestCrystalBases:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = crystal_bases()

    def test_kashiwara_1990(self):
        assert self.r['year'] == 1990
        assert self.r['introduced_by'] == 'Masaki Kashiwara'

    def test_e8_crystal(self):
        assert 'E8' in self.r['e8_crystal']['crystal_of_248']

    def test_w33_origin(self):
        assert 'W(3,3)' in self.r['e8_crystal']['w33_origin']


# ── Quantum Groups & Topology ───────────────────────────────────────────

class TestQuantumGroupsTopology:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = quantum_groups_topology()

    def test_fibonacci_universal(self):
        assert self.r['topological_qc']['fibonacci']['universal'] is True

    def test_golden_ratio(self):
        phi = (1 + math.sqrt(5)) / 2
        assert abs(self.r['golden_ratio_value'] - phi) < 1e-6

    def test_golden_ratio_property(self):
        assert self.r['golden_ratio_check'] is True


# ── R-Matrix & Quantum Determinant ───────────────────────────────────────

class TestRMatrixQuantumDet:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = r_matrix_quantum_det()

    def test_sl2_r_matrix_shape(self):
        assert len(self.r['sl2_r_matrix']['on_2d_rep']) == 4

    def test_frt_year(self):
        assert self.r['frt']['year'] == 1990


# ── Fields Medals 1990 ───────────────────────────────────────────────────

class TestFieldsMedals1990:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = fields_1990()

    def test_four_medal_recipients(self):
        assert len(self.r['medals']) == 4

    def test_three_connected(self):
        assert '3/4' in self.r['convergence']['observation']

    def test_drinfeld_present(self):
        assert 'drinfeld' in self.r['medals']

    def test_jones_present(self):
        assert 'jones' in self.r['medals']

    def test_witten_present(self):
        assert 'witten' in self.r['medals']


# ── Quantum E8 ───────────────────────────────────────────────────────────

class TestQuantumE8:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = quantum_e8()

    def test_rank_8(self):
        assert self.r['u_q_e8']['rank'] == 8

    def test_golden_ratio_mass(self):
        phi = (1 + math.sqrt(5)) / 2
        assert abs(self.r['e8_masses']['mass_ratios']['m2'] - phi) < 0.001

    def test_experimental_verification(self):
        assert 'Coldea' in self.r['e8_masses']['experimental_verification']

    def test_w33_chain_path(self):
        paths = self.r['w33_chain']['path']
        assert any('W(3,3)' in p for p in paths)
        assert any('U_q(E8)' in p for p in paths)


# ── Complete Chain ───────────────────────────────────────────────────────

class TestCompleteChain:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = complete_chain_w33_to_quantum_groups()

    def test_six_links(self):
        assert len(self.r['links']) == 6

    def test_miracle_integrability(self):
        assert 'INTEGRABILITY' in self.r['miracle']['statement']

    def test_three_fields_medals_referenced(self):
        assert '1990' in str(self.r['awards'])


# ── Integration Test ─────────────────────────────────────────────────────

class TestRunAllChecks:
    def test_all_checks_pass(self):
        assert run_all_checks() is True
