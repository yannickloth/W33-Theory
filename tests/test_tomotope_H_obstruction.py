#!/usr/bin/env python3
"""Tests for Pillar 70 (Part CLXXVIII): Tomotope-H Obstruction Theorem.

Verifies all six theorems proving that the 192-flag tomotope's connection to
the axis-line stabilizer H (order 192) is numerological, not structural:

  T1: True tomotope f-vector = (4,12,16,8), 192 flags, cells=hemioctahedra
  T2: |Gamma(tomotope)| = 18432 = |P| x |H| = 96 x 192
  T3: Stab_Gamma(flag 0) has order 96 with order-dist matching P exactly
  T4: Z(H) = {e} (trivial center), so P is NOT a quotient H/Z2 of H
  T5: Universal obstruction: H cannot host f-vector (4,12,16,8) — all 66 D4
      subgroups checked, ord(r0*r1) never equals 3
  T6: Order-8 signature: H has 48, Gamma has 3456, P has 0 — groups distinct
"""

from __future__ import annotations

import json
import os
import sys

import pytest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(repo_root, "data", "w33_tomotope_H_obstruction.json")


@pytest.fixture(scope="module")
def report():
    assert os.path.exists(DATA_FILE), (
        f"Missing data file: {DATA_FILE}\n"
        "Run THEORY_PART_CLXXVIII_TOMOTOPE_H_OBSTRUCTION.py first."
    )
    with open(DATA_FILE) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# T1: True tomotope f-vector
# ---------------------------------------------------------------------------

class TestT1TomotopeFvector:
    def test_status_ok(self, report):
        assert report["status"] == "ok"

    def test_vertices(self, report):
        assert report["T1_fvector"]["V"] == 4

    def test_edges(self, report):
        assert report["T1_fvector"]["E"] == 12

    def test_faces(self, report):
        assert report["T1_fvector"]["F"] == 16

    def test_cells(self, report):
        assert report["T1_fvector"]["C"] == 8

    def test_flag_count(self, report):
        assert report["T1_flags"] == 192

    def test_cell_type(self, report):
        assert "hemioctahedron" in report["T1_cell_type"]


# ---------------------------------------------------------------------------
# T2: Monodromy group order = |P| x |H|
# ---------------------------------------------------------------------------

class TestT2MonodromyOrder:
    def test_monodromy_order(self, report):
        assert report["T2_monodromy_order"] == 18432

    def test_P_order(self, report):
        assert report["T2_P_order"] == 96

    def test_H_order(self, report):
        assert report["T2_H_order"] == 192

    def test_product_factorization(self, report):
        assert report["T2_product_check"] is True

    def test_product_exact(self, report):
        assert report["T2_monodromy_order"] == report["T2_P_order"] * report["T2_H_order"]

    def test_monodromy_not_equal_H(self, report):
        """|Gamma| != |H| proves connection is NOT regular action of H."""
        assert report["T2_monodromy_order"] != report["T2_H_order"]


# ---------------------------------------------------------------------------
# T3: Flag stabilizer matches P
# ---------------------------------------------------------------------------

class TestT3FlagStabilizer:
    def test_stab_order(self, report):
        assert report["T3_stab_flag0_order"] == 96

    def test_stab_identity_count(self, report):
        dist = report["T3_stab_order_dist"]
        assert int(dist["1"]) == 1

    def test_stab_order2_count(self, report):
        dist = report["T3_stab_order_dist"]
        assert int(dist["2"]) == 27

    def test_stab_order3_count(self, report):
        dist = report["T3_stab_order_dist"]
        assert int(dist["3"]) == 32

    def test_stab_order4_count(self, report):
        dist = report["T3_stab_order_dist"]
        assert int(dist["4"]) == 36

    def test_stab_total_matches_P_order(self, report):
        dist = report["T3_stab_order_dist"]
        total = sum(int(v) for v in dist.values())
        assert total == 96

    def test_matches_P(self, report):
        assert report["T3_matches_P"] is True


# ---------------------------------------------------------------------------
# T4: H center is trivial
# ---------------------------------------------------------------------------

class TestT4HCenter:
    def test_H_center_size(self, report):
        assert report["T4_H_center_size"] == 1

    def test_H_center_trivial(self, report):
        assert report["T4_H_center_trivial"] is True

    def test_P_not_quotient_of_H(self, report):
        """No central Z2 in H => P cannot be H/Z2."""
        assert report["T4_P_not_quotient_of_H"] is True


# ---------------------------------------------------------------------------
# T5: Universal obstruction
# ---------------------------------------------------------------------------

class TestT5UniversalObstruction:
    def test_D4_subgroup_count(self, report):
        """Exactly 66 distinct D4 subgroups in H."""
        assert report["T5_D4_subgroups_in_H"] == 66

    def test_obstruction_universal(self, report):
        """All 66 D4 subgroups confirmed obstructed."""
        assert report["T5_obstruction_confirmed_all"] is True

    def test_obstruction_count(self, report):
        assert report["T5_obstruction_count"] == 66

    def test_H_cannot_host_fvector(self, report):
        assert report["T5_H_cannot_host_4_12_16_8"] is True


# ---------------------------------------------------------------------------
# T6: Order-8 signature
# ---------------------------------------------------------------------------

class TestT6Order8Signature:
    def test_H_order8_count(self, report):
        """H has 48 elements of order 8 (octonionic spin structure)."""
        assert report["T6_H_order8_count"] == 48

    def test_Gamma_order8_count(self, report):
        """Monodromy group has 3456 order-8 elements."""
        assert report["T6_Gamma_order8_count"] == 3456

    def test_P_order8_count(self, report):
        """Automorphism group P has no order-8 elements."""
        assert report["T6_P_order8_count"] == 0

    def test_H_not_isomorphic_to_monodromy(self, report):
        assert report["T6_H_not_isomorphic_to_monodromy"] is True

    def test_order8_all_distinct(self, report):
        """H (48), Gamma (3456), P (0) are all different."""
        h8 = report["T6_H_order8_count"]
        g8 = report["T6_Gamma_order8_count"]
        p8 = report["T6_P_order8_count"]
        assert h8 != g8 and h8 != p8 and g8 != p8


# ---------------------------------------------------------------------------
# Numerological connection summary
# ---------------------------------------------------------------------------

class TestNumerologicalConnection:
    def test_flags_equal_H_order(self, report):
        """The 192 coincidence: |flags| = |H| = |W(D4)| = 192."""
        nc = report["numerological_connection"]
        assert nc["flags"] == 192
        assert nc["H_order"] == 192
        assert nc["W_D4_order"] == 192

    def test_connection_not_structural(self, report):
        """Structural connection is False — it's numerological."""
        assert report["numerological_connection"]["structural_connection"] is False

    def test_actual_monodromy_order(self, report):
        assert report["numerological_connection"]["actual_monodromy_order"] == 18432

    def test_coxeter_r0r1_order(self, report):
        """Tomotope Coxeter diagram: |r0r1| = 3 (triangular faces)."""
        assert report["coxeter_orders"]["|r0r1|"] == 3

    def test_coxeter_r2r3_order(self, report):
        """Tomotope Coxeter diagram: |r2r3| = 4 (square cells / hemioctahedra)."""
        assert report["coxeter_orders"]["|r2r3|"] == 4

    def test_coxeter_commuting_pairs(self, report):
        """Non-adjacent generators commute: |r0r2|=|r0r3|=|r1r3|=2."""
        co = report["coxeter_orders"]
        assert co["|r0r2|"] == 2
        assert co["|r0r3|"] == 2
        assert co["|r1r3|"] == 2
