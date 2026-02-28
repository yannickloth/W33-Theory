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
            # optional fields
            if "target_qid" in r:
                r["target_qid"] = int(r["target_qid"])
            if "target_twin" in r:
                r["target_twin"] = int(r["target_twin"])
            if "u" in r:
                r["u"] = int(r["u"])
            if "v" in r:
                r["v"] = int(r["v"])
            if "cocycle_Z3_exp" in r:
                r["cocycle_Z3_exp"] = int(r["cocycle_Z3_exp"])
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
    # ensure target qid exists and is a number 0..26
    for r in rows:
        assert 0 <= r.get("target_qid", -1) < 27


def test_twin_balance(table):
    rows, _ = table
    counts = {}
    for r in rows:
        q = r["qid"]
        counts.setdefault(q, {0: 0, 1: 0})
        counts[q][r["twin_bit"]] += 1
    for q, d in counts.items():
        assert d[0] == 5 and d[1] == 5, f"qid {q} has {d}"


def test_sheet_transport_from_report(table):
    """Verify that the S3 sheet transport law previously computed still holds
    when we look at the directed edges entries produced by the 27×10 script.
    """
    rows, _ = table
    # load the transport report to obtain L_table and s_g
    report_path = repo_root / "data" / "w33_S3_sheet_transport.json"
    assert report_path.exists(), "Missing sheet transport data file"
    with open(report_path) as f:
        report = json.load(f)
    L = report["L_table_canonical"]
    s_g = report["s_g_minimal"]
    # cycle c = (1,2,0)
    def comp(p, q):
        return [p[i] for i in q]
    c = [1, 2, 0]
    c_pow = {0: [0, 1, 2], 1: c, 2: [2, 0, 1]}

    for r in rows:
        u = r["u"]
        v = r["v"]
        gen = r["gen"]
        exp = comp(s_g[gen], comp(L[u], c_pow[r.get("cocycle_Z3_exp", 0)]))
        assert exp == L[v], f"edge {u}->{v} failed transport: {exp} vs {L[v]}"
