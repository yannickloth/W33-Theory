"""Tests for Pillar 141 — Topological Phases & Anyons."""

import pytest
from THEORY_PART_CCXLI_TOPOLOGICAL_PHASES_ANYONS import (
    topological_order,
    fractional_quantum_hall,
    anyons,
    kitaev_toric_code,
    modular_tensor_categories,
    string_net_condensation,
    e8_quantum_hall,
    topological_quantum_computing,
    topological_entanglement_entropy,
    spt_order,
    complete_chain_w33_to_topological,
    run_checks,
)


# ── topological_order ───────────────────────────────────────

class TestTopologicalOrder:
    def setup_method(self):
        self.t = topological_order()

    def test_year(self):
        assert self.t['year'] == 1989

    def test_beyond_landau(self):
        assert self.t['beyond_landau']

    def test_property_count(self):
        assert self.t['property_count'] == 6

    def test_effective_theory(self):
        assert 'TQFT' in self.t['effective_theory']

    def test_wen(self):
        assert 'Wen' in self.t['introduced_by']


# ── fractional_quantum_hall ─────────────────────────────────

class TestFQH:
    def setup_method(self):
        self.f = fractional_quantum_hall()

    def test_discovery_year(self):
        assert self.f['discovery_year'] == 1982

    def test_nobel(self):
        assert self.f['nobel_prize_year'] == 1998

    def test_state_count(self):
        assert self.f['state_count'] == 4

    def test_discovery_count(self):
        assert self.f['discovery_count'] == 5

    def test_effective_theory(self):
        assert 'Chern-Simons' in self.f['effective_theory']


# ── anyons ──────────────────────────────────────────────────

class TestAnyons:
    def setup_method(self):
        self.a = anyons()

    def test_three_types(self):
        assert self.a['particle_types'] == 3

    def test_naming(self):
        assert self.a['naming_year'] == 1982
        assert self.a['named_by'] == 'Frank Wilczek'

    def test_anyon_type_count(self):
        assert self.a['type_count'] == 2

    def test_why_2d(self):
        assert 'Z' in self.a['why_2d']['key_reason']

    def test_experiments(self):
        assert self.a['experiment_count'] == 4

    def test_braid_group(self):
        assert 'braid' in self.a['why_2d']['braid_group'].lower()


# ── kitaev_toric_code ───────────────────────────────────────

class TestToricCode:
    def setup_method(self):
        self.k = kitaev_toric_code()

    def test_year(self):
        assert self.k['year'] == 2003

    def test_gsd(self):
        assert self.k['ground_state_degeneracy'] == 4

    def test_gauge_group(self):
        assert self.k['gauge_group'] == 'Z₂'

    def test_excitation_count(self):
        assert self.k['excitation_count'] == 3

    def test_quantum_dimension(self):
        assert self.k['total_quantum_dimension'] == 2

    def test_anyon_count(self):
        assert self.k['anyon_count'] == 4


# ── modular_tensor_categories ───────────────────────────────

class TestMTC:
    def setup_method(self):
        self.m = modular_tensor_categories()

    def test_classifies(self):
        assert 'bosonic' in self.m['classifies']

    def test_example_count(self):
        assert self.m['example_count'] == 4

    def test_structure_count(self):
        assert self.m['structure_count'] == 5


# ── string_net_condensation ─────────────────────────────────

class TestStringNet:
    def setup_method(self):
        self.s = string_net_condensation()

    def test_year(self):
        assert self.s['year'] == 2005

    def test_emergent_count(self):
        assert self.s['emergent_count'] == 3

    def test_drinfeld(self):
        assert 'Drinfeld' in self.s['mathematical_output']


# ── e8_quantum_hall ─────────────────────────────────────────

class TestE8QH:
    def setup_method(self):
        self.e = e8_quantum_hall()

    def test_central_charge(self):
        assert self.e['chiral_central_charge'] == 8

    def test_invertible(self):
        assert self.e['total_quantum_dimension'] == 1

    def test_K_det(self):
        assert self.e['K_det'] == 1

    def test_K_rank(self):
        assert self.e['K_rank'] == 8

    def test_root_count(self):
        assert self.e['root_count'] == 240

    def test_connections(self):
        assert self.e['connection_count'] == 4


# ── topological_quantum_computing ───────────────────────────

class TestTQC:
    def setup_method(self):
        self.t = topological_quantum_computing()

    def test_year(self):
        assert self.t['proposal_year'] == 2003

    def test_approach_count(self):
        assert self.t['approach_count'] == 4

    def test_robustness_count(self):
        assert self.t['robustness_count'] == 4

    def test_fibonacci(self):
        assert 'golden' in self.t['fibonacci_fusion'].lower() or 'τ' in self.t['fibonacci_fusion']


# ── topological_entanglement_entropy ────────────────────────

class TestTEE:
    def setup_method(self):
        self.t = topological_entanglement_entropy()

    def test_year(self):
        assert self.t['year'] == 2006

    def test_discoverer_count(self):
        assert self.t['discoverer_count'] == 2


# ── spt_order ───────────────────────────────────────────────

class TestSPT:
    def setup_method(self):
        self.s = spt_order()

    def test_example_count(self):
        assert self.s['example_count'] == 4

    def test_no_fractionalization(self):
        assert not self.s['has_fractional_excitations']

    def test_has_edge_states(self):
        assert self.s['has_protected_edge_states']


# ── chain ───────────────────────────────────────────────────

class TestChain:
    def test_chain_length(self):
        chain = complete_chain_w33_to_topological()
        assert len(chain) == 7

    def test_starts_w33(self):
        chain = complete_chain_w33_to_topological()
        assert 'W(3,3)' in chain[0][0]


# ── run_checks ──────────────────────────────────────────────

class TestRunChecks:
    def test_all_pass(self):
        assert run_checks()
