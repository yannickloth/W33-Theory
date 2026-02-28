#!/usr/bin/env python3
"""Tests for Pillar 79 (Part CLXXXVII): 27×10 quotient transport structure."""

from __future__ import annotations

import json
import os
import csv
from pathlib import Path

import pytest

repo_root = Path(__file__).resolve().parent.parent

CSV_PATH = repo_root / "edges_27x10.csv"
JSON_PATH = repo_root / "27x10_table.json"


@pytest.fixture(scope="module")
def table():
    assert CSV_PATH.exists() and JSON_PATH.exists(), (
        "Run THEORY_PART_CLXXXVII_27x10_quotient.py to generate the data files."
    )

    # load csv rows
    rows = []
    with open(CSV_PATH) as f:
        reader = csv.DictReader(f)
        for r in reader:
            r["qid"] = int(r["qid"])
            r["twin_bit"] = int(r["twin_bit"])
            r["orient_index"] = int(r["orient_index"])
            rows.append(r)

    # load json table
    with open(JSON_PATH) as f:
        table = json.load(f)

    return rows, table


def test_counts(table):
    rows, tab = table
    assert len(rows) == 270
    assert len(tab) == 27


def test_each_qid_has_ten(table):
    _, tab = table
    for q, lst in tab.items():
        assert len(lst) == 10, f"qid {q} has {len(lst)} entries"
        assert all(item is not None for item in lst)


def test_orient_indices(table):
    rows, _ = table
    seen = set()
    for r in rows:
        seen.add((r["qid"], r["orient_index"]))
    assert len(seen) == 270
    # ensure orient_index in 0..9
    for _, oi in seen:
        assert 0 <= oi < 10


def test_twin_balance(table):
    rows, _ = table
    counts = {}
    for r in rows:
        q = r["qid"]
        counts.setdefault(q, {0: 0, 1: 0})
        counts[q][r["twin_bit"]] += 1
    for q, d in counts.items():
        assert d[0] == 5 and d[1] == 5, f"qid {q} has {d}"
