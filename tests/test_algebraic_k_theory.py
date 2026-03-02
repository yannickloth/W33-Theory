"""Tests for Pillar 173 — Algebraic K-Theory."""

import pytest
from THEORY_PART_CCLXXIII_ALGEBRAIC_K_THEORY import (
    grothendieck_k0,
    bass_k1,
    milnor_k2,
    milnor_k_theory,
    quillen_higher_k_theory,
    waldhausen_s_construction,
    k_theory_and_number_theory,
    k_theory_topology_applications,
    e8_k_theory_connection,
    advanced_k_theory,
)


class TestGrothendieckK0:
    def test_k0_field(self):
        r = grothendieck_k0()
        assert 'ℤ' in r['k0_field']['description']
        assert 'dim' in r['k0_field']['map']

    def test_k0_integers(self):
        r = grothendieck_k0()
        assert 'PID' in r['k0_integers']['description']
        assert 'K̃₀(ℤ) = 0' in r['k0_integers']['reduced_k0']

    def test_k0_dedekind(self):
        r = grothendieck_k0()
        assert 'Pic' in r['k0_dedekind']['description']
        assert 'Pic' in r['k0_dedekind']['class_number_connection']

    def test_k0_ring_structure(self):
        r = grothendieck_k0()
        assert '⊗' in r['k0_ring_structure']['multiplication']
        assert 'λ-ring' in r['k0_ring_structure']['lambda_ring']

    def test_grr(self):
        r = grothendieck_k0()
        assert 'ch' in r['grothendieck_riemann_roch']['chern_character']
        assert 'td' in r['grothendieck_riemann_roch']['todd_class']


class TestBassK1:
    def test_definition(self):
        r = bass_k1()
        assert 'GL(R)/E(R)' in r['definition']['k1']
        assert 'commutator' in r['definition']['whitehead_lemma'].lower()

    def test_commutative(self):
        r = bass_k1()
        assert 'R×' in r['commutative']['splitting']
        assert 'SK₁' in r['commutative']['sk1']

    def test_k1_fields(self):
        r = bass_k1()
        assert 'k×' in r['k1_fields']['description']
        assert 'ℤ/(q-1)' in r['k1_fields']['finite_fields']

    def test_whitehead_torsion(self):
        r = bass_k1()
        assert 'Wh(π)' in r['whitehead_torsion']['whitehead_group']
        assert 'cobordism' in r['whitehead_torsion']['s_cobordism_thm'].lower()


class TestMilnorK2:
    def test_steinberg(self):
        r = milnor_k2()
        assert len(r['steinberg_group']['relations']) >= 3
        assert 'center' in r['steinberg_group']['k2_def']

    def test_matsumoto(self):
        r = milnor_k2()
        assert 'k×' in r['matsumoto']['theorem']
        assert len(r['matsumoto']['properties']) >= 4

    def test_computations(self):
        r = milnor_k2()
        assert 'ℤ/2' in r['computations']['k2_Z']
        assert '0' in r['computations']['k2_finite']
        assert 'reciprocity' in r['computations']['quadratic_reciprocity'].lower()

    def test_exact_sequences(self):
        r = milnor_k2()
        assert 'K₂' in r['exact_sequences']['relative']


class TestMilnorKTheory:
    def test_definition(self):
        r = milnor_k_theory()
        assert '⊗' in r['definition']['milnor_k_groups']
        assert 'graded' in r['definition']['graded_ring'].lower()

    def test_finite_fields(self):
        r = milnor_k_theory()
        assert 'ℤ' in r['finite_fields']['k0']
        assert '0' in r['finite_fields']['higher']

    def test_galois_symbol(self):
        r = milnor_k_theory()
        assert 'Voevodsky' in r['galois_symbol']['milnor_conjecture']
        assert 'isomorphism' in r['galois_symbol']['bloch_kato']


class TestQuillenHigherKTheory:
    def test_plus_construction(self):
        r = quillen_higher_k_theory()
        assert 'π_n' in r['plus_construction']['definition']
        assert 'BGL(R)⁺' in r['plus_construction']['definition']

    def test_q_construction(self):
        r = quillen_higher_k_theory()
        assert 'Exact category' in r['q_construction']['input']

    def test_finite_field_k_groups(self):
        r = quillen_higher_k_theory()
        assert r['finite_field_k_groups']['k0'] == 'K₀(𝔽_q) = ℤ'
        assert '0' in r['finite_field_k_groups']['even']
        assert 'q^i - 1' in r['finite_field_k_groups']['odd']

    def test_k_groups_integers(self):
        r = quillen_higher_k_theory()
        assert 'ℤ/2' in r['k_groups_integers']['k2_Z']
        assert 'Borel' in r['k_groups_integers']['borel_computation']

    def test_g_theory(self):
        r = quillen_higher_k_theory()
        assert 'regular' in r['g_theory']['regular_rings'].lower()
        assert 'Bloch' in r['g_theory']['bloch_formula']


class TestWaldhausenSConstruction:
    def test_waldhausen_categories(self):
        r = waldhausen_s_construction()
        assert len(r['waldhausen_categories']['axioms']) >= 4
        assert 'cofibration' in r['waldhausen_categories']['definition'].lower()

    def test_s_construction(self):
        r = waldhausen_s_construction()
        assert 'loop space' in r['s_construction']['k_theory_space'].lower() or 'Ω' in r['s_construction']['k_theory_space']

    def test_trace_methods(self):
        r = waldhausen_s_construction()
        assert 'THH' in r['trace_methods']['thh']
        assert 'TC' in r['trace_methods']['tc']


class TestKTheoryNumberTheory:
    def test_lichtenbaum(self):
        r = k_theory_and_number_theory()
        assert 'zeta' in r['lichtenbaum']['conjecture'].lower() or 'ζ' in r['lichtenbaum']['conjecture']

    def test_quillen_lichtenbaum(self):
        r = k_theory_and_number_theory()
        assert 'Voevodsky' in r['quillen_lichtenbaum']['status'] or 'Bloch-Kato' in r['quillen_lichtenbaum']['status']

    def test_higher_regulators(self):
        r = k_theory_and_number_theory()
        assert 'Borel' in r['higher_regulators']['borel']
        assert 'Beilinson' in r['higher_regulators']['beilinson']


class TestKTheoryTopology:
    def test_wall_finiteness(self):
        r = k_theory_topology_applications()
        assert 'K̃₀' in r['wall_finiteness']['theorem']
        assert '1963' in r['wall_finiteness']['year']

    def test_s_cobordism(self):
        r = k_theory_topology_applications()
        assert 'Whitehead torsion' in r['s_cobordism']['theorem']

    def test_assembly_map(self):
        r = k_theory_topology_applications()
        assert 'Novikov' in r['assembly_map']['novikov']
        assert 'Farrell-Jones' in r['assembly_map']['farrell_jones']


class TestE8KTheory:
    def test_e8_lattice(self):
        r = e8_k_theory_connection()
        assert '248' in str(r['e8_lattice']['dimension'])

    def test_string_theory(self):
        r = e8_k_theory_connection()
        assert 'D-brane' in r['string_theory']['d_brane_charges']
        assert 'K⁰' in r['string_theory']['type_IIA']

    def test_w33_chain(self):
        r = e8_k_theory_connection()
        assert 'W33' in r['w33_chain']['k0_w33']
        assert 'bridge' in r['w33_chain']['architecture'].lower()


class TestAdvancedKTheory:
    def test_motivic(self):
        r = advanced_k_theory()
        assert 'Voevodsky' in r['motivic']['motivic_cohomology']

    def test_chromatic(self):
        r = advanced_k_theory()
        assert 'chromatic' in r['chromatic']['redshift_conjecture']
        assert 'Rognes' in r['chromatic']['rognes']

    def test_parshin(self):
        r = advanced_k_theory()
        assert 'torsion' in r['parshin']['conjecture']

    def test_bass(self):
        r = advanced_k_theory()
        assert 'finitely generated' in r['bass']['conjecture']
