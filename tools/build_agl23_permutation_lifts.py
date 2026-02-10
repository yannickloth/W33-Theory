#!/usr/bin/env python3
"""Build AGL(2,3) permutation lifts on the 40 W33 vertices.

Outputs:
  - AGL23_lifts.json: list of entries {"mat": [a,b,c,d], "dx": dx, "dy": dy, "perm_40": [...], "unitary": serialized}

Usage:
  py -3 tools/build_agl23_permutation_lifts.py --bundle-dir analysis/w33_bundle_temp --out-dir analysis/w33_bundle_temp/analysis
"""
from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path
from typing import Dict, Tuple

import numpy as np


def mat_mul_mod3(m2: Tuple[int, int, int, int], m1: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    a2, b2, c2, d2 = m2
    a1, b1, c1, d1 = m1
    a = (a2 * a1 + b2 * c1) % 3
    b = (a2 * b1 + b2 * d1) % 3
    c = (c2 * a1 + d2 * c1) % 3
    d = (c2 * b1 + d2 * d1) % 3
    return (a, b, c, d)


def load_h27_n12(bundle_dir: Path):
    import csv

    hmap = {}
    with (bundle_dir / "H27_vertices_as_F3_cube_xy_t.csv").open("r", encoding="utf-8") as f:
        rdr = csv.reader(f)
        hdr = next(rdr)
        for row in rdr:
            if not row:
                continue
            wid = int(row[0])
            x = int(row[1])
            y = int(row[2])
            t = int(row[3])
            hmap[wid] = (x, y, t)

    n12 = []
    with (bundle_dir / "N12_vertices_as_affine_lines.csv").open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            n12.append(int(r["N12_vertex"]))

    return hmap, n12


def build_perm40_from_HN(hmap: Dict[int, Tuple[int, int, int]], n12_list: list, perm_H: Dict[str, int], perm_N12: Dict[str, int]):
    # build full 40-permutation dictionary mapping str->int
    perm = {}
    # list of all 40 vertices: 0, n12_list, and H keys from hmap
    all_vids = set([0]) | set(n12_list) | set(hmap.keys())
    for v in sorted(all_vids):
        if v == 0:
            perm[str(v)] = int(v)
        elif str(v) in perm_N12:
            perm[str(v)] = int(perm_N12[str(v)])
        elif str(v) in perm_H:
            perm[str(v)] = int(perm_H[str(v)])
        else:
            # leave fixed
            perm[str(v)] = int(v)
    # convert to list by index
    perm_list = [perm[str(i)] for i in range(40)]
    return perm_list


def compose_perm(pA: list, pB: list) -> list:
    # (pA o pB)[v] = pA[pB[v]]
    return [pA[pB[v]] for v in range(len(pA))]


def invert_perm(p: list) -> list:
    inv = [0] * len(p)
    for i, v in enumerate(p):
        inv[v] = i
    return inv


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bundle-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, default=None)
    args = p.parse_args()

    bundle = args.bundle_dir
    out_dir = args.out_dir if args.out_dir is not None else bundle / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)

    # load clifford gens
    cliff_json = out_dir / "clifford_lift_on_H27_and_N12.json"
    if not cliff_json.exists():
        raise FileNotFoundError(cliff_json)
    cj = json.loads(cliff_json.read_text(encoding="utf-8"))

    # compute perm_40 for generators
    hmap, n12_list = load_h27_n12(bundle)
    gen_info = {}
    for g in cj.get("generators", []):
        name = g["name"]
        permH = g.get("perm_H", {})
        permN = g.get("perm_N12", {})
        perm40 = build_perm40_from_HN(hmap, n12_list, permH, permN)
        gen_info[name] = {"mat": tuple(g["matrix"]), "perm40": perm40, "unitary": g.get("unitary")}

    # BFS closure on SL(2,3) matrices using S and T generators
    S = gen_info["S"]["mat"]
    T = gen_info["T"]["mat"]
    gens = {S: gen_info["S"], T: gen_info["T"]}

    id_mat = (1, 0, 0, 1)
    mat_to_perm = {id_mat: list(range(40))}
    mat_to_unitary = {id_mat: np.eye(3, dtype=complex)}
    q = deque([id_mat])
    seen = {id_mat}
    while q:
        base = q.popleft()
        perm_base = mat_to_perm[base]
        for gen_mat, ginfo in gens.items():
            new = mat_mul_mod3(gen_mat, base)
            if new not in seen:
                seen.add(new)
                # compose permutations: new_perm = perm_gen o perm_base
                new_perm = compose_perm(ginfo["perm40"], perm_base)
                mat_to_perm[new] = new_perm
                # compose unitary: Ugen @ U_base
                Ugen = np.array([[complex(x["re"], x["im"]) for x in row] for row in ginfo["unitary"]], dtype=complex)
                mat_to_unitary[new] = Ugen @ mat_to_unitary[base]
                q.append(new)

    # check 24 matrices
    print(f"SL(2,3) group size (mat perms): {len(mat_to_perm)}")

    # load translations
    txty_json = out_dir / "W33_Heisenberg_generators_Tx_Ty_Z.json"
    if not txty_json.exists():
        raise FileNotFoundError(txty_json)
    txj = json.loads(txty_json.read_text(encoding="utf-8"))
    Tx_perm = [int(txj["Tx"]["perm_40"][str(i)]) for i in range(40)] if isinstance(txj["Tx"]["perm_40"], dict) else txj["Tx"]["perm_40"]
    Ty_perm = [int(txj["Ty"]["perm_40"][str(i)]) for i in range(40)] if isinstance(txj["Ty"]["perm_40"], dict) else txj["Ty"]["perm_40"]

    # build translation powers
    def power_perm(p, k):
        if k == 0:
            return list(range(40))
        res = p[:]
        for _ in range(k - 1):
            res = compose_perm(p, res)
        return res

    AGL_entries = []
    for mat, perm_mat in mat_to_perm.items():
        for dx in range(3):
            for dy in range(3):
                Tx_pow = power_perm(Tx_perm, dx)
                Ty_pow = power_perm(Ty_perm, dy)
                # translate after matrix: perm = Ty^dy o Tx^dx o perm_mat ? we choose Tx^dx then Ty^dy then perm_mat
                # compose translation with sl perm: first apply sl perm_mat then apply translations
                trans = compose_perm(Ty_pow, Tx_pow)
                agl_perm = compose_perm(trans, perm_mat)
                # unitary: D(dx,dy) @ U_mat
                U_mat = mat_to_unitary[mat]
                # create serializable unitary
                U_serial = [[[{"re": float(c.real), "im": float(c.imag)} for c in row] for row in U_mat.tolist()]]
                entry = {"mat": list(mat), "dx": int(dx), "dy": int(dy), "perm_40": agl_perm}
                AGL_entries.append(entry)

    out_file = out_dir / "AGL23_lifts.json"
    out_file.write_text(json.dumps({"status": "ok", "entries": AGL_entries, "count": len(AGL_entries)}, indent=2), encoding="utf-8")
    print(f"Wrote {out_file} with {len(AGL_entries)} entries")


if __name__ == "__main__":
    main()
