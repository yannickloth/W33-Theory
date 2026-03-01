#!/usr/bin/env python3
"""Pillar 96 (part CXCVI): Embedding N into an explicit Heisenberg algebra.

Using the delta map from Pillars 94–95 we build a toy Heisenberg algebra
H_{3}(\mathbb F_3) with elements represented as triples
(u,v,z)\in(\mathbb F_3)^3 and multiplication

    (u,v,z)*(u',v',z') = (u+u', v+v', z+z' + \omega((u,v),(u',v')))

where \omega((u,v),(u',v')) = u_1 v'_2 - u_2 v'_1 (mod 3) is the standard
symplectic form.  The central part is identified with the z-coordinate.

We then produce a mapping \phi:N\to H_{3}(F_3) sending each permutation to the
corresponding triple obtained from its delta vector.  The script checks that
\phi respects multiplication (i.e. defines a group homomorphism) and reports
on the central cocycle.
"""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Dict, Tuple

from THEORY_PART_CXCIII_FIND_N import compose, invert

ROOT = Path(__file__).resolve().parent


class HeisElement:
    __slots__ = ("u", "v", "z")

    def __init__(self, u: Tuple[int, int], v: Tuple[int, int], z: int):
        self.u = (u[0] % 3, u[1] % 3)
        self.v = (v[0] % 3, v[1] % 3)
        self.z = z % 3

    def __mul__(self, other: "HeisElement") -> "HeisElement":
        u = ((self.u[0] + other.u[0]) % 3, (self.u[1] + other.u[1]) % 3)
        v = ((self.v[0] + other.v[0]) % 3, (self.v[1] + other.v[1]) % 3)
        # symplectic cocycle
        omega = (self.u[0] * other.v[1] - self.u[1] * other.v[0]) % 3
        z = (self.z + other.z + omega) % 3
        return HeisElement(u, v, z)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HeisElement):
            return False
        return self.u == other.u and self.v == other.v and self.z == other.z

    def __repr__(self) -> str:
        return f"H({self.u},{self.v},{self.z})"


# utilities to load coordinates, similar to previous pillars

def _load_qid_coords():
    path = ROOT / "edges_270_transport.csv"
    coords = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            coords[int(r["qid"])] = (int(r["x"]), int(r["y"]), int(r["z"]))
    return coords


def _load_flag_coords(qid_coords):
    path = ROOT / "K54_54sheet_coords.csv"
    fc = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            if r["canonical_flag"] == "":
                continue
            fc[int(r["canonical_flag"])] = qid_coords[int(r["qid"])]
    return fc


def build_map():
    qcoords = _load_qid_coords()
    fcoords = _load_flag_coords(qcoords)
    base = fcoords[0]
    N = json.loads((ROOT / "N_subgroup.json").read_text())
    fmap = json.loads((ROOT / "N_flag_map.json").read_text())
    perm_to_flag = {tuple(v): int(k) for k, v in fmap.items()}

    mapping: Dict[Tuple[int, ...], HeisElement] = {}
    for p in N:
        f = perm_to_flag[tuple(p)]
        coord = fcoords[f]
        dx = (coord[0] - base[0]) % 3
        dy = (coord[1] - base[1]) % 3
        dz = (coord[2] - base[2]) % 3
        # interpret (dx,dy,dz) as ((dx,dy) for u,v) with z central
        mapping[tuple(p)] = HeisElement((dx, 0), (dy, 0), dz)
    return mapping


def verify_homomorphism(sample=100) -> bool:
    mapping = build_map()
    perms = list(mapping.keys())
    # test a handful of random pairs
    for _ in range(sample):
        g = random.choice(perms)
        h = random.choice(perms)
        gh = compose(g, h)
        if mapping[gh] != mapping[g] * mapping[h]:
            return False
    return True


def main():
    hom = verify_homomorphism()
    print("homomorphism holds?", hom)
    # record a few representatives for the report
    mapping = build_map()
    reps = {str(k): repr(v) for k, v in list(mapping.items())[:5]}
    out = {"sample_mapping": reps, "homomorphism": hom}
    Path(ROOT / "heis_embedding_summary.json").write_text(json.dumps(out, indent=2))
    print("wrote heis_embedding_summary.json")


if __name__ == "__main__":
    main()
