#!/usr/bin/env python3
"""Tests for the Heisenberg presentation of N."""

from __future__ import annotations

from pathlib import Path
import json

from THEORY_PART_CXCV_N_PRESENTATION import find_presentation


def test_presentation_exists():
    repo = Path(__file__).resolve().parent.parent
    assert (repo / "N_heis_presentation.json").exists()
    assert (repo / "N_heis_presentation_report.md").exists()


def test_presentation_properties():
    summary = find_presentation()
    # a and b project to independent xy vectors
    da = tuple(summary["a_delta"][i] for i in (0, 1))
    db = tuple(summary["b_delta"][i] for i in (0, 1))
    det = (da[0] * db[1] - da[1] * db[0]) % 3
    assert det != 0
    # orders should divide 3 and commutator central
    assert summary["a_order"] in (1, 3)
    assert summary["b_order"] in (1, 3)
    assert summary["z_order"] in (1, 3)
