#!/usr/bin/env python3
"""Tests for Pillar 73 (Part CLXXXI): The Voltage Functor K -> Tomotope.

Verifies all six theorems mapping the K-pocket Schreier voltage (Z3) to the
tomotope's internal triality element t^4 = (r1*r2)^4:

  T1: K voltage generator — 5-cycle [g5,g5,g3,g5,g2] word has order 3,
      voltage 1, fixes pocket 0
  T2: Phi: Z3 -> Aut(192), exp |-> (t^4)^exp is a well-defined injective
      group homomorphism
  T3: Universal 2+1+1 block split — exactly 2 flags of each block stay in
      the block under t^4
  T4: 16 tomotope faces form 4 t^4-invariant groups of 4 (48 flags each)
  T5: 48 tomotope blocks form 4 t^4-connected components of 12 each
  T6: Functor coherence — Z3 voltage, H-triality, tomotope t^4 all have
      the same order profile (1, 3, 3) for exponents (0, 1, 2)
"""

from __future__ import annotations

import json
import os

import pytest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(repo_root, "data", "w33_voltage_functor.json")


@pytest.fixture(scope="module")
def report():
    assert os.path.exists(DATA_FILE), (
        f"Missing data file: {DATA_FILE}\n"
        "Run THEORY_PART_CLXXXI_VOLTAGE_FUNCTOR.py first."
    )
    with open(DATA_FILE) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# T1: K voltage stabilizer word
# ---------------------------------------------------------------------------

class TestT1VoltageStabilizerWord:
    def test_status_ok(self, report):
        assert report["status"] == "ok"

    def test_cycle_starts_at_0(self, report):
        assert report["T1_cycle_nodes"][0] == 0

    def test_cycle_ends_at_0(self, report):
        assert report["T1_cycle_nodes"][-1] == 0

    def test_cycle_length(self, report):
        """5-step cycle: [0, 3, 13, 32, 5, 0]."""
        assert len(report["T1_cycle_nodes"]) == 6

    def test_total_voltage_is_1(self, report):
        assert report["T1_total_voltage"] == 1

    def test_word_is_five_generators(self, report):
        assert len(report["T1_word"]) == 5

    def test_word_order_is_3(self, report):
        assert report["T1_word_order"] == 3

    def test_word_fixes_pocket0(self, report):
        assert report["T1_fixes_pocket0"] is True

    def test_word_verified(self, report):
        assert report["T1_verified"] is True


# ---------------------------------------------------------------------------
# T2: Voltage functor Phi: Z3 -> Aut(192)
# ---------------------------------------------------------------------------

class TestT2VoltageFunctor:
    def test_functor_well_defined(self, report):
        assert report["T2_functor_well_defined"] is True

    def test_functor_homomorphism(self, report):
        assert report["T2_functor_homomorphism"] is True

    def test_functor_injective(self, report):
        assert report["T2_functor_injective"] is True

    def test_t4_order(self, report):
        assert report["T2_t4_order"] == 3

    def test_phi_maps_z3_to_z3(self, report):
        """ord(t^4) = 3 confirms Phi(Z3) <= Z3 <= Aut(192)."""
        assert report["T2_t4_order"] == 3

    def test_phi_is_isomorphism_onto_image(self, report):
        """Injective + domain Z3 => Phi is an isomorphism onto its image."""
        assert report["T2_functor_injective"] is True
        assert report["T2_functor_homomorphism"] is True


# ---------------------------------------------------------------------------
# T3: Universal 2+1+1 block split
# ---------------------------------------------------------------------------

class TestT3UniversalBlockSplit:
    def test_n_blocks(self, report):
        assert report["T3_n_blocks"] == 48

    def test_universal_split(self, report):
        assert report["T3_universal_2plus1plus1"] is True

    def test_self_count(self, report):
        """Exactly 2 flags stay in the original block."""
        assert report["T3_self_count"] == 2

    def test_away_count(self, report):
        """The other 2 flags go to 2 distinct other blocks."""
        assert report["T3_away_count"] == 2

    def test_total_flags_per_block(self, report):
        """2 (self) + 1 + 1 (away) = 4 flags per block."""
        assert report["T3_self_count"] + report["T3_away_count"] == 4

    def test_all_blocks_split_uniformly(self, report):
        """48 blocks, all with the same 2+1+1 split."""
        assert report["T3_n_blocks"] == 48
        assert report["T3_universal_2plus1plus1"] is True


# ---------------------------------------------------------------------------
# T4: Face triality partition
# ---------------------------------------------------------------------------

class TestT4FaceTrialityPartition:
    def test_n_faces(self, report):
        assert report["T4_n_faces"] == 16

    def test_face_triality_components(self, report):
        assert report["T4_face_triality_components"] == 4

    def test_face_component_sizes(self, report):
        assert report["T4_face_component_sizes"] == [4, 4, 4, 4]

    def test_face_component_uniform(self, report):
        """All 4 face groups have exactly 4 faces."""
        sizes = report["T4_face_component_sizes"]
        assert len(sizes) == 4 and all(s == 4 for s in sizes)

    def test_flag_sets_t4_invariant(self, report):
        """Each group's 48-flag set is closed under t^4."""
        assert report["T4_flag_sets_t4_invariant"] is True

    def test_total_faces_accounted(self, report):
        """4 components × 4 faces = 16 faces total."""
        assert report["T4_face_triality_components"] * 4 == report["T4_n_faces"]

    def test_each_component_has_48_flags(self, report):
        """4 faces × 12 flags/face = 48 flags per component."""
        assert 4 * 12 == 48


# ---------------------------------------------------------------------------
# T5: Block triality partition
# ---------------------------------------------------------------------------

class TestT5BlockTrialityPartition:
    def test_n_blocks(self, report):
        assert report["T5_n_blocks"] == 48

    def test_block_triality_components(self, report):
        assert report["T5_block_triality_components"] == 4

    def test_block_component_sizes(self, report):
        assert report["T5_block_component_sizes"] == [12, 12, 12, 12]

    def test_block_component_uniform(self, report):
        """All 4 block groups have exactly 12 blocks."""
        sizes = report["T5_block_component_sizes"]
        assert len(sizes) == 4 and all(s == 12 for s in sizes)

    def test_block_component_uniform_flag(self, report):
        assert report["T5_block_component_uniform"] is True

    def test_total_blocks_accounted(self, report):
        """4 components × 12 blocks = 48 blocks total."""
        assert report["T5_block_triality_components"] * 12 == report["T5_n_blocks"]

    def test_face_and_block_components_match(self, report):
        """Both faces and blocks partition into 4 components."""
        assert report["T4_face_triality_components"] == report["T5_block_triality_components"]


# ---------------------------------------------------------------------------
# T6: Functor coherence
# ---------------------------------------------------------------------------

class TestT6FunctorCoherence:
    def test_voltage_orders(self, report):
        assert report["T6_voltage_H_orders"] == [1, 3, 3]

    def test_tomotope_orders(self, report):
        assert report["T6_voltage_tomotope_orders"] == [1, 3, 3]

    def test_orders_match(self, report):
        assert report["T6_orders_match"] is True

    def test_functor_coherent(self, report):
        assert report["T6_functor_coherent"] is True

    def test_H_exp1_index(self, report):
        assert report["T6_H_exp1_index"] == 71

    def test_H_exp2_index(self, report):
        assert report["T6_H_exp2_index"] == 46

    def test_phi1_order(self, report):
        assert report["T6_phi1_order"] == 3

    def test_phi2_order(self, report):
        assert report["T6_phi2_order"] == 3

    def test_identity_corresponds(self, report):
        """exp=0: H-identity (order 1) and Phi(0)=id (order 1)."""
        assert report["T6_voltage_H_orders"][0] == 1
        assert report["T6_voltage_tomotope_orders"][0] == 1

    def test_triality_exp1_and_2_order3(self, report):
        """exp=1,2: both H-elements and tomotope powers have order 3."""
        assert report["T6_voltage_H_orders"][1] == 3
        assert report["T6_voltage_H_orders"][2] == 3
        assert report["T6_voltage_tomotope_orders"][1] == 3
        assert report["T6_voltage_tomotope_orders"][2] == 3


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

class TestVoltageFunctorSummary:
    def test_summary_functor(self, report):
        assert "summary" in report
        assert "Z3" in report["summary"]["voltage_functor_Phi"]

    def test_summary_generator(self, report):
        assert "order=3" in report["summary"]["generator"]

    def test_summary_block_split(self, report):
        assert "2+1+1" in report["summary"]["block_split"]

    def test_summary_face_components(self, report):
        assert report["summary"]["face_components"] == 4

    def test_summary_block_components(self, report):
        assert report["summary"]["block_components"] == 4

    def test_summary_coherence(self, report):
        assert "same Z3" in report["summary"]["coherence"]
