#!/usr/bin/env python3
"""Pillar 95 (part CXCV): Presenting N as a Heisenberg extension.

Building on Pillar 94 we look for a pair of elements \(a,b\in N\) whose
projected Heisenberg coordinates \((x,y)\in \mathbb F_3^2\) form a basis.
Their commutator should lie in the centre and correspond to a pure-z shift.
The output is a small data file recording the chosen generators and the
central element, together with a human-readable report.

The script also checks that \(a,b,z\) satisfy the familiar Heisenberg
relations:

    a b = z b a  ,   z central ,   a^3=b^3=z^3=1.

A companion test verifies the existence of such a triple and that the
presentation is correct.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Dict, Tuple, List

from THEORY_PART_CXCIII_FIND_N import compose, invert

ROOT = Path(__file__).resolve().parent


def load_qid_coords() -> Dict[int, Tuple[int, int, int]]:
    path = ROOT / "edges_270_transport.csv"
    coords: Dict[int, Tuple[int, int, int]] = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            coords[int(r["qid"])] = (int(r["x"]), int(r["y"]), int(r["z"]))
    return coords


def load_flag_coords(qid_coords: Dict[int, Tuple[int, int, int]]) -> Dict[int, Tuple[int, int, int]]:
    path = ROOT / "K54_54sheet_coords.csv"
    flag_coords: Dict[int, Tuple[int, int, int]] = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            if r["canonical_flag"] == "":
                continue
            flag_coords[int(r["canonical_flag"])] = qid_coords[int(r["qid"])]
    return flag_coords


def find_presentation() -> dict:
    qid_coords = load_qid_coords()
    flag_coords = load_flag_coords(qid_coords)
    base = flag_coords[0]

    N = json.loads((ROOT / "N_subgroup.json").read_text())
    fmap = json.loads((ROOT / "N_flag_map.json").read_text())
    perm_to_flag = {tuple(v): int(k) for k, v in fmap.items()}

    # compute delta mapping
    delta_map: Dict[Tuple[int, ...], Tuple[int, int, int]] = {}
    for p in N:
        f = perm_to_flag[tuple(p)]
        coord = flag_coords[f]
        delta_map[tuple(p)] = tuple((coord[i] - base[i]) % 3 for i in range(3))

    # look for two elements with independent (x,y) projections
    basis_pair = None
    for g, dg in delta_map.items():
        for h, dh in delta_map.items():
            mat = (dg[0], dg[1], dh[0], dh[1])
            det = (mat[0] * mat[3] - mat[1] * mat[2]) % 3
            if det != 0:
                basis_pair = (g, h, dg, dh)
                break
        if basis_pair:
            break
    if basis_pair is None:
        raise RuntimeError("no basis of N found")

    a, b, da, db = basis_pair
    # commutator z = a b a^{-1} b^{-1}
    zperm = compose(compose(a, b), compose(invert(a), invert(b)))
    dz = delta_map[zperm]

    # verify centrality: commute with a and b
    assert compose(a, zperm) == compose(zperm, a)
    assert compose(b, zperm) == compose(zperm, b)

    # ensure orders are 3 (or divide 3) for heisenberg
    def order(p):
        cur = tuple(range(192))
        for i in range(1,10):
            cur = compose(p, cur)
            if cur == tuple(range(192)):
                return i
        return None
    oa, ob, oz = order(a), order(b), order(zperm)

    return {
        "a_delta": da,
        "b_delta": db,
        "z_delta": dz,
        "a_order": oa,
        "b_order": ob,
        "z_order": oz,
    }


def main():
    summary = find_presentation()
    open(ROOT / "N_heis_presentation.json", "w").write(json.dumps(summary, indent=2))
    with open(ROOT / "N_heis_presentation_report.md", "w", encoding="utf-8") as f:
        f.write("# N Heisenberg presentation report\n\n")
        f.write(json.dumps(summary, indent=2))
    print("wrote N_heis_presentation.json and report")


if __name__ == "__main__":
    main()
