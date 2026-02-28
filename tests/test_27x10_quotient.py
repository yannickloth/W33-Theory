#!/usr/bin/env python3
"""Tests for Pillar 88 (Part CXCIV): 27x10 Heisenberg-Quotient of the K-Schreier Graph."""

from __future__ import annotations
import json, os
import pytest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(repo_root, "data", "w33_27x10_quotient.json")

@pytest.fixture(scope="module")
def report():
    assert os.path.exists(DATA_FILE), f"Missing: {DATA_FILE}\nRun THEORY_PART_CXCIV_27x10_QUOTIENT.py first."
    with open(DATA_FILE) as f:
        return json.load(f)

class TestT127x10Table:
    def test_status_ok(self, report): assert report["status"] == "ok"
    def test_total_edges(self, report): assert report["T1_total_edges"] == 270
    def test_qid_count(self, report): assert report["T1_qid_count"] == 27
    def test_orient_count(self, report): assert report["T1_orient_count"] == 10
    def test_edges_per_qid(self, report): assert report["T1_edges_per_qid"] == 10
    def test_edges_per_orient(self, report): assert report["T1_edges_per_orient"] == 27
    def test_sources_per_pocket(self, report): assert report["T1_sources_per_pocket"] == 5
    def test_product_check(self, report): assert report["T1_qid_count"] * report["T1_orient_count"] == 270
    def test_orient_0_4_from_twin0(self, report): assert report["T1_orient_0_4_from_twin0"] is True
    def test_orient_5_9_from_twin1(self, report): assert report["T1_orient_5_9_from_twin1"] is True

class TestT2PairStability:
    def test_all_generators_pair_stable(self, report): assert report["T2_all_generators_pair_stable"] is True
    def test_g2_stable(self, report): assert report["T2_gen_stable"]["g2"] is True
    def test_g3_stable(self, report): assert report["T2_gen_stable"]["g3"] is True
    def test_g5_stable(self, report): assert report["T2_gen_stable"]["g5"] is True
    def test_g8_stable(self, report): assert report["T2_gen_stable"]["g8"] is True
    def test_g9_stable(self, report): assert report["T2_gen_stable"]["g9"] is True
    def test_all_5_gens_in_stable_dict(self, report):
        assert set(report["T2_gen_stable"].keys()) == {"g2", "g3", "g5", "g8", "g9"}

class TestT3TwinBitFlip:
    def test_g2_no_flip(self, report): assert report["T3_flip_counts"]["g2"] == 0
    def test_g3_flip_6(self, report): assert report["T3_flip_counts"]["g3"] == 6
    def test_g5_flip_6(self, report): assert report["T3_flip_counts"]["g5"] == 6
    def test_g8_flip_15(self, report): assert report["T3_flip_counts"]["g8"] == 15
    def test_g9_flip_15(self, report): assert report["T3_flip_counts"]["g9"] == 15
    def test_g2_no_flip_flag(self, report): assert report["T3_g2_no_flip"] is True
    def test_g3_g5_flag(self, report): assert report["T3_g3_g5_flip_6"] is True
    def test_g8_g9_flag(self, report): assert report["T3_g8_g9_flip_15"] is True
    def test_total_flips_sum(self, report):
        flips = report["T3_flip_counts"]
        assert sum(flips.values()) == 42

class TestT4CocycleSplit:
    def test_twin0_nontriv(self, report): assert report["T4_twin0_nontriv"] == 24
    def test_twin1_nontriv(self, report): assert report["T4_twin1_nontriv"] == 45
    def test_total_nontriv(self, report): assert report["T4_total_nontriv"] == 69
    def test_twin0_edges(self, report): assert report["T4_twin0_edges"] == 135
    def test_twin1_edges(self, report): assert report["T4_twin1_edges"] == 135
    def test_total_edges_check(self, report):
        assert report["T4_twin0_edges"] + report["T4_twin1_edges"] == 270
    def test_nontriv_sum_correct(self, report):
        assert report["T4_twin0_nontriv"] + report["T4_twin1_nontriv"] == 69
    def test_nontrivial_asymmetry(self, report):
        assert report["T4_twin1_nontriv"] > report["T4_twin0_nontriv"]

class TestT5QuotientGraph:
    def test_self_loop_count(self, report): assert report["T5_self_loop_count"] == 12
    def test_g8_self_loops(self, report): assert report["T5_g8_self_loops"] == 6
    def test_g9_self_loops(self, report): assert report["T5_g9_self_loops"] == 6
    def test_g8_g9_self_loops_sum(self, report):
        assert report["T5_g8_self_loops"] + report["T5_g9_self_loops"] == 12
    def test_degree_5_count(self, report):
        assert report["T5_quotient_degree_distribution"]["5"] == 9
    def test_degree_6_count(self, report):
        assert report["T5_quotient_degree_distribution"]["6"] == 6
    def test_degree_7_count(self, report):
        assert report["T5_quotient_degree_distribution"]["7"] == 12
    def test_degree_distribution_sum(self, report):
        total = sum(report["T5_quotient_degree_distribution"].values())
        assert total == 27
    def test_weighted_degree_sum(self, report): assert report["T5_weighted_degree_sum"] == 165
    def test_sheet_count(self, report): assert report["T5_sheet_count"] == 6
    def test_pockets_per_sheet(self, report): assert report["T5_pockets_per_sheet"] == 9
    def test_total_pockets(self, report):
        assert report["T5_sheet_count"] * report["T5_pockets_per_sheet"] == 54
    def test_uniform_sheets(self, report): assert report["T5_uniform_sheets"] is True

class TestT6SheetAssignment:
    def test_same_sheet_pairs(self, report): assert report["T6_same_sheet_pairs"] == 7
    def test_diff_sheet_pairs(self, report): assert report["T6_diff_sheet_pairs"] == 20
    def test_total_pairs(self, report): assert report["T6_total_pairs"] == 27
    def test_partition_sum(self, report):
        assert report["T6_same_sheet_pairs"] + report["T6_diff_sheet_pairs"] == 27
    def test_partition_exact(self, report): assert report["T6_partition_exact"] is True
    def test_inter_sheet_majority(self, report):
        assert report["T6_diff_sheet_pairs"] > report["T6_same_sheet_pairs"]

class Test27x10QuotientSummary:
    def test_summary_present(self, report): assert "summary" in report
    def test_summary_table(self, report):
        assert "270" in report["summary"]["table_structure"]
        assert "27" in report["summary"]["table_structure"]
    def test_summary_pair_stability(self, report):
        assert "pair" in report["summary"]["pair_stability"]
    def test_summary_twin_flip(self, report):
        assert "15" in report["summary"]["twin_flip_pattern"]
    def test_summary_cocycle(self, report):
        assert "24" in report["summary"]["cocycle_split"]
        assert "45" in report["summary"]["cocycle_split"]
    def test_summary_quotient(self, report):
        assert "27" in report["summary"]["quotient_graph"]
    def test_summary_sheet(self, report):
        assert "7" in report["summary"]["sheet_assignment"]
        assert "20" in report["summary"]["sheet_assignment"]
