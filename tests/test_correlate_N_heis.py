#!/usr/bin/env python3
"""Tests for the N–Block–Grade correlation pillar (Pillar 94)."""

from __future__ import annotations

import json
from pathlib import Path

from THEORY_PART_CXCV_CORRELATE_N_HEIS import compute_correlation


def test_summary_file_created():
    repo = Path(__file__).resolve().parent.parent
    assert (repo / "N_heis_correlation_summary.json").exists()
    assert (repo / "N_heis_correlation_report.md").exists()


def test_compute_correlation_consistency():
    summary = compute_correlation()
    # T1: N has 192 elements with trivial centre
    assert summary["N_size"] == 192
    assert summary["T1_center_is_trivial"] is True
    # T2: 48 blocks, all hit
    assert summary["T2_all_blocks_hit"] is True
    assert summary["T2_num_blocks"] == 48
    # T3: t4 grade distribution sums to 192
    gd = summary["T3_t4_grade_dist"]
    assert sum(gd.values()) == 192
    # T4: no order-3 element lands on grade 1 or 2
    og = summary["T4_ord3_grade_dist"]
    assert og.get(1, 0) == 0 and og.get(2, 0) == 0
    # T4: 27 does NOT divide 192
    assert summary["T4_27_divides_192"] is False
