#!/usr/bin/env python3
"""Tests for Pillar 72 (Part CLXXX): The Triality Bridge.

Verifies all six theorems linking the K-pocket Heisenberg geometry to the
tomotope's internal triality and the octonion axis-line stabiliser H:

  T1: [K,K] is extraspecial 3^{1+2}: order 27, non-abelian, |Z([K,K])|=3,
      [[K,K],[K,K]]=Z([K,K]), exponent 3
  T2: [K,K] acts REGULARLY on the 27 canonical twin-pairs
      (transitive, trivial stabiliser), matching K54_to_K27_twin_map.csv
  T3: t = r1*r2 in tomotope has ord(t)=12; t^4 has order 3, fixes 96 flags
  T4: t^4 on 48 <r0,r3>-blocks gives (48_3) symmetric configuration, 6-regular
  T5: H has exactly 3 Sylow-2 subgroups of order 64; triality element (H-index
      71, order 3) permutes them as [1, 2, 0] (no fixed subgroup)
  T6: Pairwise Sylow-2 intersections have size 32; each normal in its Sylow-2
"""

from __future__ import annotations

import json
import os

import pytest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(repo_root, "data", "w33_triality_bridge.json")


@pytest.fixture(scope="module")
def report():
    assert os.path.exists(DATA_FILE), (
        f"Missing data file: {DATA_FILE}\n"
        "Run THEORY_PART_CLXXX_TRIALITY_BRIDGE.py first."
    )
    with open(DATA_FILE) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# T1: [K,K] is extraspecial 3^{1+2}
# ---------------------------------------------------------------------------

class TestT1ExtraspecialDerivedSubgroup:
    def test_DK_order(self, report):
        assert report["T1_DK_order"] == 27

    def test_DK_is_3_power(self, report):
        """27 = 3^3."""
        assert report["T1_DK_order"] == 3 ** 3

    def test_DK_identity_count(self, report):
        dist = report["T1_DK_order_dist"]
        assert int(dist["1"]) == 1

    def test_DK_order3_count(self, report):
        dist = report["T1_DK_order_dist"]
        assert int(dist["3"]) == 26

    def test_DK_total(self, report):
        dist = report["T1_DK_order_dist"]
        assert sum(int(v) for v in dist.values()) == 27

    def test_DK_non_abelian(self, report):
        assert report["T1_DK_non_abelian"] is True

    def test_DK_centre_order(self, report):
        assert report["T1_Z_DK_order"] == 3

    def test_DK_inner_derived_order(self, report):
        """[[K,K],[K,K]] has order 3 (= centre)."""
        assert report["T1_inner_derived_order"] == 3

    def test_inner_derived_equals_centre(self, report):
        """Z([K,K]) = [[K,K],[K,K]] — hallmark of extraspecial p-group."""
        assert report["T1_Z_DK_order"] == report["T1_inner_derived_order"]

    def test_extraspecial_flag(self, report):
        assert report["T1_extraspecial"] is True


# ---------------------------------------------------------------------------
# T2: [K,K] acts regularly on 27 twin-pairs
# ---------------------------------------------------------------------------

class TestT2RegularActionOnTwinPairs:
    def test_twin_pairs_count(self, report):
        assert report["T2_twin_pairs"] == 27

    def test_DK_on_27_order(self, report):
        """[K,K] induced on 27 twin-pairs still has order 27 (faithful)."""
        assert report["T2_DK_on_27_order"] == 27

    def test_DK_on_27_transitive(self, report):
        assert report["T2_DK_on_27_transitive"] is True

    def test_DK_on_27_regular(self, report):
        """Regular = transitive with trivial point-stabiliser."""
        assert report["T2_DK_on_27_regular"] is True

    def test_DK_on_27_matches_csv(self, report):
        assert report["T2_matches_csv"] is True

    def test_regular_action_order_equals_degree(self, report):
        """|[K,K]| == number of twin-pairs (27 == 27)."""
        assert report["T2_DK_on_27_order"] == report["T2_twin_pairs"]


# ---------------------------------------------------------------------------
# T3: Tomotope triality power
# ---------------------------------------------------------------------------

class TestT3TomotopeTrality:
    def test_ord_t(self, report):
        assert report["T3_ord_t"] == 12

    def test_ord_t4(self, report):
        assert report["T3_ord_t4"] == 3

    def test_t4_fixed_flags(self, report):
        assert report["T3_t4_fixed_flags"] == 96

    def test_t4_fixes_half_flags(self, report):
        """t^4 fixes exactly 96 of 192 flags (half)."""
        assert report["T3_t4_fixed_flags"] == 96
        assert 2 * report["T3_t4_fixed_flags"] == 192

    def test_t4_is_cube_root(self, report):
        """ord(t^4) = 3 and ord(t) = 12; 12/3 = 4 consistently."""
        assert report["T3_ord_t"] // report["T3_ord_t4"] == 4


# ---------------------------------------------------------------------------
# T4: (48_3) block configuration
# ---------------------------------------------------------------------------

class TestT4BlockConfiguration:
    def test_n_blocks(self, report):
        assert report["T4_n_blocks"] == 48

    def test_block_image_size(self, report):
        """Each block's 4 flags map to exactly 3 distinct blocks under t^4."""
        assert report["T4_block_image_size"] == 3

    def test_each_block_in_triples(self, report):
        """Each block appears in exactly 3 of the 48 image triples."""
        assert report["T4_each_block_in_triples"] == 3

    def test_block_graph_degree(self, report):
        """The block incidence graph is 6-regular."""
        assert report["T4_block_graph_degree"] == 6

    def test_configuration_label(self, report):
        assert report["T4_configuration"] == "(48_3)"

    def test_symmetric_configuration(self, report):
        """(48_3): 48 points, each in 3 blocks; 48 blocks, each with 3 points."""
        assert report["T4_n_blocks"] == 48
        assert report["T4_block_image_size"] == 3
        assert report["T4_each_block_in_triples"] == 3


class TestT4bHeisTranslation:
    def test_block_qids_exist(self, report):
        """Report records the qid set attached to each spa block."""
        assert "T4b_block_qids" in report
        # there should be 24 spa blocks with associated sets
        assert len(report["T4b_block_qids"]) == 24

    def test_unique_qid_count(self, report):
        assert report.get("T4b_total_unique_qids") == 6

    def test_each_block_two_qids(self, report):
        for qs in report["T4b_block_qids"].values():
            assert len(qs) == 2


# ---------------------------------------------------------------------------
# T5: 3 Sylow-2 subgroups cycled by triality element
# ---------------------------------------------------------------------------

class TestT5Sylow2Triality:
    def test_n_sylow2(self, report):
        assert report["T5_n_sylow2"] == 3

    def test_sylow2_order(self, report):
        assert report["T5_sylow2_order"] == 64

    def test_sylow2_order_is_2_power(self, report):
        """64 = 2^6."""
        assert report["T5_sylow2_order"] == 2 ** 6

    def test_sylow2_times_3_equals_H(self, report):
        """H has order 192 = 3 * 64."""
        assert 3 * report["T5_sylow2_order"] == 192

    def test_triality_H_index(self, report):
        assert report["T5_triality_H_index"] == 71

    def test_triality_order(self, report):
        assert report["T5_triality_order"] == 3

    def test_triality_perm_is_3_cycle(self, report):
        """Triality permutes all 3 Sylow-2 subgroups: [1, 2, 0]."""
        perm = report["T5_triality_perm_on_sylow2"]
        assert sorted(perm) == [0, 1, 2]
        # No fixed points
        assert all(perm[i] != i for i in range(3))

    def test_triality_cycles_all(self, report):
        assert report["T5_triality_cycles_all"] is True

    def test_triality_perm_cubic(self, report):
        """Applying triality permutation 3 times returns to identity."""
        perm = report["T5_triality_perm_on_sylow2"]
        perm2 = [perm[perm[i]] for i in range(3)]
        perm3 = [perm[perm2[i]] for i in range(3)]
        assert perm3 == [0, 1, 2]


# ---------------------------------------------------------------------------
# T6: Pairwise Sylow-2 intersections of size 32
# ---------------------------------------------------------------------------

class TestT6Sylow2Intersections:
    def test_off_diagonal_size(self, report):
        assert report["T6_off_diagonal"] == 32

    def test_intersection_matrix_diagonal(self, report):
        mat = report["T6_pairwise_intersections"]
        for i in range(3):
            assert mat[i][i] == 64

    def test_intersection_matrix_off_diagonal(self, report):
        mat = report["T6_pairwise_intersections"]
        for i in range(3):
            for j in range(3):
                if i != j:
                    assert mat[i][j] == 32

    def test_intersections_normal(self, report):
        assert report["T6_intersections_normal"] is True

    def test_intersection_index2_in_sylow2(self, report):
        """32 = 64/2: each intersection has index 2 in its Sylow-2."""
        assert report["T5_sylow2_order"] // report["T6_off_diagonal"] == 2

    def test_intersection_matrix_symmetric(self, report):
        mat = report["T6_pairwise_intersections"]
        for i in range(3):
            for j in range(3):
                assert mat[i][j] == mat[j][i]


# ---------------------------------------------------------------------------
# Bridge summary: Z3 voltage = H triality
# ---------------------------------------------------------------------------

class TestTrialityBridgeSummary:
    def test_status_ok(self, report):
        assert report["status"] == "ok"

    def test_DK_extraspecial(self, report):
        assert report["summary"]["DK_is_extraspecial_3_group"] is True

    def test_twin_pairs_confirmed(self, report):
        assert report["summary"]["twin_pairs_27"] is True

    def test_48_block_config(self, report):
        assert report["summary"]["48_block_configuration"] == "(48_3) symmetric"

    def test_bridge_note_present(self, report):
        """Summary includes the Z3 voltage = triality bridge note."""
        assert "note" in report["summary"]
        assert "triality" in report["summary"]["note"].lower()
