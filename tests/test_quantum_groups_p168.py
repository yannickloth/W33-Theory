"""Tests for Pillar 168 – Quantum Groups (CCLXVIII)."""

import pytest
from THEORY_PART_CCLXVIII_QUANTUM_GROUPS import (
    quantum_group_foundations,
    drinfeld_jimbo,
    yang_baxter,
    knot_invariants,
    crystal_bases,
    roots_of_unity,
    quantum_e8,
    integrable_systems,
    connections_to_prior,
    hopf_algebra_structure,
    quantum_groups_physics,
    w33_chain,
    quantum_doubles,
    modern_developments,
    complete_chain,
    run_all_checks,
)


# ── 1. Foundations ──────────────────────────────────────────────────────────

class TestFoundations:
    def test_founders(self):
        r = quantum_group_foundations()
        assert 'Drinfeld' in r['founders']
        assert 'Jimbo' in r['founders']
        assert r['year'] == 1985

    def test_hopf(self):
        r = quantum_group_foundations()
        assert 'Hopf' in r['definition']['hopf_algebra']

    def test_history(self):
        r = quantum_group_foundations()
        assert 'Faddeev' in r['history']['leningrad_school']


# ── 2. Drinfeld-Jimbo ──────────────────────────────────────────────────────

class TestDrinfeldJimbo:
    def test_generators(self):
        r = drinfeld_jimbo()
        for key in ('cartan', 'raising', 'lowering'):
            assert key in r['generators']

    def test_coproduct(self):
        r = drinfeld_jimbo()
        assert 'tensor' in r['coproduct']['delta_k'].lower()

    def test_q_serre(self):
        r = drinfeld_jimbo()
        assert 'q-Serre' in r['relations']['q_serre']


# ── 3. Yang-Baxter ─────────────────────────────────────────────────────────

class TestYangBaxter:
    def test_equation(self):
        r = yang_baxter()
        assert 'R_{12}' in r['equation']['form']

    def test_universal_r(self):
        r = yang_baxter()
        assert 'quasitriangular' in r['universal_r']['existence'].lower()

    def test_applications(self):
        r = yang_baxter()
        assert 'braid' in r['applications']['braiding'].lower()
        assert 'knot' in r['applications']['knot_invariants'].lower()


# ── 4. Knot Invariants ─────────────────────────────────────────────────────

class TestKnotInvariants:
    def test_jones(self):
        r = knot_invariants()
        assert 'Jones' in r['jones_polynomial']['discovery']
        assert 'U_q(sl_2)' in r['jones_polynomial']['quantum_group']

    def test_homfly(self):
        r = knot_invariants()
        assert 'HOMFLY' in r['generalizations']['homfly']

    def test_reshetikhin_turaev(self):
        r = knot_invariants()
        assert 'Reshetikhin-Turaev' in r['generalizations']['reshetikhin_turaev']

    def test_3_manifolds(self):
        r = knot_invariants()
        assert 'Witten' in r['3_manifolds']['witten']


# ── 5. Crystal Bases ───────────────────────────────────────────────────────

class TestCrystalBases:
    def test_discoverer(self):
        r = crystal_bases()
        assert 'Kashiwara' in r['discoverer']
        assert '1990' in r['discoverer']

    def test_canonical(self):
        r = crystal_bases()
        assert 'canonical' in r['properties']['canonical'].lower()

    def test_lusztig(self):
        r = crystal_bases()
        assert 'Lusztig' in r['properties']['lusztig']


# ── 6. Roots of Unity ─────────────────────────────────────────────────────

class TestRootsOfUnity:
    def test_root_of_unity(self):
        r = roots_of_unity()
        assert 'root of unity' in r['setting']['parameter']

    def test_kazhdan_lusztig(self):
        r = roots_of_unity()
        assert 'Kazhdan-Lusztig' in r['representation']['tensor_category']

    def test_modular(self):
        r = roots_of_unity()
        assert 'modular tensor' in r['representation']['modular'].lower()

    def test_tqft(self):
        r = roots_of_unity()
        assert 'TQFT' in r['tqft']['connection']


# ── 7. Quantum E8 ──────────────────────────────────────────────────────────

class TestQuantumE8:
    def test_rank(self):
        r = quantum_e8()
        assert r['structure']['rank'] == 8

    def test_248(self):
        r = quantum_e8()
        assert '248' in r['structure']['dimension']
        assert '248' in r['representation']['fundamental']

    def test_self_dual(self):
        r = quantum_e8()
        assert 'self-dual' in r['significance']['self_dual'].lower()


# ── 8. Integrable Systems ──────────────────────────────────────────────────

class TestIntegrableSystems:
    def test_xxz(self):
        r = integrable_systems()
        assert 'XXZ' in r['statistical']['xxz']

    def test_faddeev(self):
        r = integrable_systems()
        assert 'Faddeev' in r['quantum_inverse']['method']

    def test_yangian(self):
        r = integrable_systems()
        assert 'Yangian' in r['affine']['yangian']


# ── 9. Connections ─────────────────────────────────────────────────────────

class TestConnections:
    def test_langlands(self):
        r = connections_to_prior()
        assert 'Drinfeld' in r['langlands_P167']['connection']

    def test_modular_tensor(self):
        r = connections_to_prior()
        assert 'Kazhdan-Lusztig' in r['modular_tensor_P162']['detail']


# ── 10. Hopf Algebra ──────────────────────────────────────────────────────

class TestHopfAlgebra:
    def test_axioms(self):
        r = hopf_algebra_structure()
        for key in ('algebra', 'coalgebra', 'bialgebra', 'antipode'):
            assert key in r['axioms']

    def test_quantum_type(self):
        r = hopf_algebra_structure()
        assert 'NEITHER' in r['types']['quantum']

    def test_duality(self):
        r = hopf_algebra_structure()
        assert 'dual' in r['duality']['statement'].lower()


# ── 11. Physics ────────────────────────────────────────────────────────────

class TestPhysics:
    def test_chern_simons(self):
        r = quantum_groups_physics()
        assert 'Chern-Simons' in r['chern_simons']['theory']

    def test_witten(self):
        r = quantum_groups_physics()
        assert 'Witten' in r['chern_simons']['witten']

    def test_poisson_lie(self):
        r = quantum_groups_physics()
        assert 'Poisson-Lie' in r['deformation_quantization']['poisson_lie']


# ── 12. W33 Chain ──────────────────────────────────────────────────────────

class TestW33Chain:
    def test_path(self):
        r = w33_chain()
        assert any('W(3,3)' in p for p in r['path'])
        assert any('Yang-Baxter' in p for p in r['path'])

    def test_deep(self):
        r = w33_chain()
        assert 'modular tensor' in r['deep_connection'].lower()


# ── 13. Quantum Doubles ───────────────────────────────────────────────────

class TestQuantumDoubles:
    def test_double(self):
        r = quantum_doubles()
        assert 'Drinfeld double' in r['double']['construction']

    def test_braided(self):
        r = quantum_doubles()
        assert 'braided' in r['center']['braided'].lower()

    def test_kitaev(self):
        r = quantum_doubles()
        assert 'Kitaev' in r['applications']['tqft']


# ── 14. Modern Developments ───────────────────────────────────────────────

class TestModern:
    def test_khovanov(self):
        r = modern_developments()
        assert 'Khovanov' in r['categorification']['khovanov']

    def test_cluster(self):
        r = modern_developments()
        assert 'Fomin-Zelevinsky' in r['cluster']['cluster_algebras']

    def test_nakajima(self):
        r = modern_developments()
        assert 'Nakajima' in r['geometric']['nakajima']


# ── 15. Complete Chain ─────────────────────────────────────────────────────

class TestCompleteChain:
    def test_links(self):
        r = complete_chain()
        assert len(r['links']) == 6

    def test_miracle(self):
        r = complete_chain()
        assert 'MIRACLE' in r['miracle']['statement']
        assert 'topology' in r['miracle']['depth']


# ── Integration ────────────────────────────────────────────────────────────

class TestSelfChecks:
    def test_all_pass(self):
        assert run_all_checks()
