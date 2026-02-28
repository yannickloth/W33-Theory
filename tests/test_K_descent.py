#!/usr/bin/env python3
"""Tests for Pillar 71 (Part CLXXIX): K-Subgroup E6/D4 Descent and C3 Torsor Weld.

Verifies all six theorems about K (order 162 = 2 * 3^4), the K-orbit of 54
octonion pockets, and the C3 torsor weld into the axis-line stabiliser H:

  T1: K transitive on 54 pockets; 270 Schreier edges = |W(E6)|/|W(D4)|
  T2: C3 voltage non-exact: discrepancies {0:148, 1:33, 2:36}
  T3: 3-Sylow P3 order=81, spectrum {1:1,3:44,9:36}; |Z(P3)|=3; |[P3,P3]|=9
  T4: Non-trivial Z3 weld sigmas map to order-3 elements in H
  T5: Schreier graph connected; Stab_K(pocket 0) = Z3 (order 3)
  T6: K/[K,K] ~ Z6; derived subgroup [K,K] has order 27
"""

from __future__ import annotations

import json
import os

import pytest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(repo_root, "data", "w33_K_descent.json")


@pytest.fixture(scope="module")
def report():
    assert os.path.exists(DATA_FILE), (
        f"Missing data file: {DATA_FILE}\n"
        "Run THEORY_PART_CLXXIX_K_DESCENT.py first."
    )
    with open(DATA_FILE) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# T1: K order, transitivity, Schreier edges
# ---------------------------------------------------------------------------

class TestT1KSchreieredges:
    def test_K_order(self, report):
        assert report["T1_K_order"] == 162

    def test_K_transitive(self, report):
        assert report["T1_transitive"] is True

    def test_schreier_edge_count(self, report):
        assert report["T1_schreier_edges"] == 270

    def test_W_E6_over_W_D4(self, report):
        assert report["T1_W_E6_over_W_D4"] == 270

    def test_schreier_equals_coset_count(self, report):
        assert report["T1_schreier_edges"] == report["T1_W_E6_over_W_D4"]

    def test_match_flag(self, report):
        assert report["T1_match"] is True

    def test_K_factorisation(self, report):
        """K has order 2 * 3^4 = 162."""
        assert report["T1_K_order"] == 2 * 3 ** 4


# ---------------------------------------------------------------------------
# T2: C3 voltage cocycle discrepancies
# ---------------------------------------------------------------------------

class TestT2VoltageDiscrepancies:
    def test_fundamental_cycles(self, report):
        """270 edges - 53 spanning-tree edges = 217 fundamental cycles."""
        assert report["T2_fundamental_cycles"] == 217

    def test_disc_zero_count(self, report):
        assert report["T2_discrepancy_counts"]["0"] == 148

    def test_disc_one_count(self, report):
        assert report["T2_discrepancy_counts"]["1"] == 33

    def test_disc_two_count(self, report):
        assert report["T2_discrepancy_counts"]["2"] == 36

    def test_total_discrepancies(self, report):
        d = report["T2_discrepancy_counts"]
        total = sum(int(v) for v in d.values())
        assert total == 217

    def test_not_exact(self, report):
        assert report["T2_cocycle_exact"] is False

    def test_nontrivial_count(self, report):
        assert report["T2_nontrivial_cycles"] == 69


# ---------------------------------------------------------------------------
# T3: 3-Sylow structure
# ---------------------------------------------------------------------------

class TestT3SylowStructure:
    def test_P3_order(self, report):
        assert report["T3_P3_order"] == 81

    def test_P3_is_3_power(self, report):
        """81 = 3^4."""
        assert report["T3_P3_order"] == 3 ** 4

    def test_P3_identity_count(self, report):
        dist = report["T3_P3_order_dist"]
        assert int(dist["1"]) == 1

    def test_P3_order3_count(self, report):
        dist = report["T3_P3_order_dist"]
        assert int(dist["3"]) == 44

    def test_P3_order9_count(self, report):
        dist = report["T3_P3_order_dist"]
        assert int(dist["9"]) == 36

    def test_P3_total(self, report):
        dist = report["T3_P3_order_dist"]
        assert sum(int(v) for v in dist.values()) == 81

    def test_Z_P3_order(self, report):
        assert report["T3_Z_P3_order"] == 3

    def test_derived_P3_order(self, report):
        assert report["T3_derived_P3_order"] == 9

    def test_lower_central_series(self, report):
        """P3 > [P3,P3] > Z(P3) > {e}: orders 81 > 9 > 3 > 1."""
        assert report["T3_P3_order"] > report["T3_derived_P3_order"]
        assert report["T3_derived_P3_order"] > report["T3_Z_P3_order"]
        assert report["T3_Z_P3_order"] > 1


# ---------------------------------------------------------------------------
# T4: Weld identity
# ---------------------------------------------------------------------------

class TestT4WeldIdentity:
    def test_identity_sigma_order1(self, report):
        orders = report["T4_weld_orders"]
        assert orders["(0, 1, 2, 3, 4, 5, 6)"] == 1

    def test_sigma_order3(self, report):
        orders = report["T4_weld_orders"]
        assert orders["(1, 3, 5, 0, 2, 4, 6)"] == 3

    def test_sigma_inv_order3(self, report):
        orders = report["T4_weld_orders"]
        assert orders["(3, 0, 4, 1, 5, 2, 6)"] == 3

    def test_non_trivial_order(self, report):
        assert report["T4_non_trivial_sigma_order"] == 3

    def test_weld_verified(self, report):
        assert report["T4_weld_verified"] is True

    def test_weld_forms_Z3(self, report):
        """The three weld elements {e, sigma, sigma^{-1}} form Z3."""
        orders = report["T4_weld_orders"]
        order_counts = {}
        for v in orders.values():
            order_counts[v] = order_counts.get(v, 0) + 1
        assert order_counts[1] == 1
        assert order_counts[3] == 2


# ---------------------------------------------------------------------------
# T5: Connectivity and stabiliser
# ---------------------------------------------------------------------------

class TestT5Connectivity:
    def test_connected(self, report):
        assert report["T5_connected"] is True

    def test_stab_pocket0_order(self, report):
        """Stabiliser of pocket 0 in K has order 3 (= Z3)."""
        assert report["T5_stab_pocket0_order"] == 3

    def test_stab_identity_count(self, report):
        dist = report["T5_stab_order_dist"]
        assert int(dist["1"]) == 1

    def test_stab_order3_count(self, report):
        dist = report["T5_stab_order_dist"]
        assert int(dist["3"]) == 2

    def test_orbit_size(self, report):
        assert report["T5_orbit_pocket0_size"] == 54

    def test_orbit_stabiliser_product(self, report):
        """|K| = |orbit| * |stab|: 162 = 54 * 3."""
        assert report["T1_K_order"] == (
            report["T5_orbit_pocket0_size"] * report["T5_stab_pocket0_order"]
        )


# ---------------------------------------------------------------------------
# T6: K abelianisation
# ---------------------------------------------------------------------------

class TestT6Abelianisation:
    def test_derived_K_order(self, report):
        assert report["T6_derived_K_order"] == 27

    def test_abelianisation_order(self, report):
        assert report["T6_abelianisation_order"] == 6

    def test_abelianisation_label(self, report):
        assert report["T6_abelianisation"] == "Z6"

    def test_K_metabelian(self, report):
        assert report["T6_K_metabelian"] is True

    def test_index_check(self, report):
        """[K:[K,K]] = 6 = |K|/|[K,K]| = 162/27."""
        assert report["T1_K_order"] // report["T6_derived_K_order"] == 6

    def test_derived_contains_3_sylow_derived(self, report):
        """[K,K] (order 27) contains [P3,P3] (order 9) as a subgroup."""
        assert report["T6_derived_K_order"] % report["T3_derived_P3_order"] == 0
