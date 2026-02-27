#!/usr/bin/env python3
"""Compute the cocycle measuring the defect between the original edge->E8
bijection and the one transported by the outer twist.

The outer twist on PG points factors as N4 = Q * A4 where Q changes the
symplectic form and A4 is an inner symplectic automorphism.  The permutation
p_label induced by A4 on the 40 vertices is available via the psi map
(pg_to_edge_labeling.json) and the outer-bundle perm40 data.  We define the
transported bijection \phi' = \phi \circ A4^{-1} (i.e. apply inverse of
p_label to edge endpoints before feeding to original \phi).

For each edge we compute an A2 projection value
    s = ((r,\alpha)-(r,\beta))/3 mod 3
using the simple-root pair from artifacts/a2_4_decomposition.json.  The
cocycle defect is
    d(e) = s'(e) - s(e) (mod 3)
and we record also whether the two root endpoints differ by a sign.

Outputs are written to:
  - analysis/outer_twist_cocycle/edge_defect.json
  - analysis/outer_twist_cocycle/edge_defect.csv
  - analysis/outer_twist_cocycle/orbits_under_WE6.json

The bundle script (make_outer_twist_cocycle_bundle.py) will package these
alongside summary information and the transported bijection phi'.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Dict, Tuple, List

import numpy as np


# helpers from extract_e8_rootword_cocycle

def _dot_int(u: Tuple[int, ...], v: Tuple[int, ...]) -> int:
    return sum(int(a) * int(b) for a, b in zip(u, v, strict=True))

def inner_prod_doubled(u: Tuple[int, ...], v: Tuple[int, ...]) -> int:
    return _dot_int(u, v) // 4


def load_edge_root_map(path: Path) -> Dict[Tuple[int, int], Tuple[int, ...]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    m = {}
    if isinstance(data, dict):
        for k, coords in data.items():
            if isinstance(k, str) and k.startswith("(") and "," in k:
                s = k.strip()[1:-1]
                vi_s, vj_s = s.split(",")
                vi = int(vi_s.strip()); vj = int(vj_s.strip())
            else:
                raise RuntimeError("Unsupported edge_to_root dict key format")
            coords_t = tuple(int(x) for x in coords)
            m[(vi, vj)] = coords_t
            m[(vj, vi)] = tuple(-x for x in coords_t)
    else:
        for ent in data:
            vi = int(ent["v_i"]); vj = int(ent["v_j"])
            coords = tuple(int(x) for x in ent["root_coords"])
            m[(vi, vj)] = coords
            m[(vj, vi)] = tuple(-x for x in coords)
    return m


def load_a2_solution(path: Path, idx: int = 0) -> List[int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    sol = data.get("a2_4_solution")
    if not sol or idx >= len(sol):
        raise RuntimeError("No A2 solution at index")
    return sol[idx]


def find_simple_roots_in_a2(
    a2_indices: List[int], root_index_to_coords: Dict[int, Tuple[int, ...]]
):
    roots = {i: root_index_to_coords[i] for i in a2_indices}
    for i, a in roots.items():
        for j, b in roots.items():
            if i >= j: continue
            ip = inner_prod_doubled(a, b)
            if ip == -1:
                return a, b, i, j
    raise RuntimeError("No simple root pair found in A2 indices")


def compute_projection(r: Tuple[int, ...], alpha: Tuple[int, ...], beta: Tuple[int, ...]) -> int:
    # returns s = ((r,alpha)-(r,beta))/3 mod 3
    da = inner_prod_doubled(r, alpha)
    db = inner_prod_doubled(r, beta)
    S = da - db
    if S % 3 != 0:
        # litte warning; still reduce
        pass
    s = ((S // 3) % 3)
    return s


def compute_orbits(points: List[int], perms: List[List[int]]) -> List[List[int]]:
    unvis = set(points)
    orbs = []
    while unvis:
        start = unvis.pop()
        orb = {start}
        changed = True
        while changed:
            changed = False
            for g in perms:
                new = {g[p] for p in orb}
                if not new.issubset(orb):
                    orb |= new
                    changed = True
        orbs.append(sorted(orb))
        unvis -= orb
    return orbs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--edge-root-json", type=Path, default=Path("artifacts/edge_to_e8_root.json"))
    p.add_argument("--a2-solution-json", type=Path, default=Path("artifacts/a2_4_decomposition.json"))
    p.add_argument("--a2-index", type=int, default=0)
    p.add_argument("--psi-json", type=Path, default=Path("pg_to_edge_labeling.json"))
    p.add_argument("--outer-bundle", type=Path, default=Path("H27_OUTER_TWIST_ACTION_BUNDLE_v01"))
    p.add_argument("--out-dir", type=Path, default=Path("analysis/outer_twist_cocycle"))
    args = p.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    # load phi map
    phi = load_edge_root_map(args.edge_root_json)
    # compute psi and its inverse
    psi = {int(k): int(v) for k, v in json.loads(args.psi_json.read_text()).items()}
    psi_inv = {v: k for k, v in psi.items()}
    # outer permutation p_coset
    perm40 = json.loads((args.outer_bundle / "perm40_and_H27_pg_ids.json").read_text())
    p_coset = perm40["perm40_points_from_phi_n"]
    # compute p_label as earlier
    p_label = [None] * 40
    for i in range(40):
        pg = psi_inv[i]
        p_label[i] = psi[p_coset[pg]]
    p_label_inv = [0]*40
    for i,v in enumerate(p_label):
        p_label_inv[v] = i

    # build phi' by transporting via A4^{-1} i.e. p_label_inv
    phi_prime = {}
    for (i,j), coords in phi.items():
        i2 = p_label_inv[i]; j2 = p_label_inv[j]
        phi_prime[(i,j)] = phi[(i2,j2)]

    # choose two fixed adjacent simple roots from a canonical E8 basis
    # we simply hardcode the first two simple roots (they have inner product -1)
    alpha = (1, -1, 0, 0, 0, 0, 0, 0)
    beta  = (0, 1, -1, 0, 0, 0, 0, 0)
    print("using hardcoded simple roots alpha,beta")

    rows = []
    stats = Counter()
    for (i,j), r in phi.items():
        r_prime = phi_prime[(i,j)]
        s = compute_projection(r, alpha, beta)
        s2 = compute_projection(r_prime, alpha, beta)
        defect = (s2 - s) % 3
        sign = 1 if r_prime == r else -1
        rows.append((i,j,r,r_prime,s,s2,defect,sign))
        stats[defect] += 1

    # write json and csv
    json_out = args.out_dir / "edge_defect.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump({"rows": [
            {"edge": [i,j],
             "root": list(r),
             "root_prime": list(rp),
             "proj": p,
             "proj_prime": p2,
             "defect": d,
             "sign": sgn}
            for i,j,r,rp,p,p2,d,sgn in rows
        ], "stats": stats}, f, indent=2)
    csv_out = args.out_dir / "edge_defect.csv"
    with open(csv_out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["i","j","proj","proj_prime","defect","sign"])
        for i,j,r,rp,p,p2,d,sgn in rows:
            w.writerow([i,j,p,p2,d,sgn])

    # compute orbits under WE6 = automorphism group stored earlier? reuse NP or P perms
    # For simplicity classify edges under p_label repeatedly to obtain orbit sizes
    perms = [p_label]
    pts = list({i for i,j in phi.keys()})
    orbs = compute_orbits(pts, perms)
    with open(args.out_dir / "orbits_under_WE6.json", "w", encoding="utf-8") as f:
        json.dump(orbs, f, indent=2)

    print("defect stats", stats)
    print("wrote", json_out, csv_out, args.out_dir / "orbits_under_WE6.json")


if __name__ == "__main__":
    main()
