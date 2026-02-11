#!/usr/bin/env python3
"""Scan candidate base roots (in color orbits) and evaluate how many triangles are satisfied
by the generator-induced mapping when using that base root.

Writes summary to checks/PART_CVII_coset_base_scan.json
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def invert_perm(perm: List[int]) -> List[int]:
    n = len(perm)
    inv = [0] * n
    for i, v in enumerate(perm):
        inv[v] = i
    return inv


def build_w33_edges() -> List[Tuple[int, int]]:
    F3 = [0, 1, 2]
    vectors = [
        v
        for v in __import__("itertools").product(F3, repeat=4)
        if any(x != 0 for x in v)
    ]

    proj_points = []
    seen = set()
    for v in vectors:
        v = list(v)
        for i in range(4):
            if v[i] != 0:
                inv = 1 if v[i] == 1 else 2
                v = tuple((x * inv) % 3 for x in v)
                break
        if v not in seen:
            seen.add(v)
            proj_points.append(v)

    def omega(x, y):
        return (x[0] * y[2] - x[2] * y[0] + x[1] * y[3] - x[3] * y[1]) % 3

    edges = []
    for i in range(len(proj_points)):
        for j in range(i + 1, len(proj_points)):
            if omega(proj_points[i], proj_points[j]) == 0:
                edges.append((i, j))
    return edges


def count_tri_satisfied(
    predicted: dict, roots: List[Tuple[int, ...]], edge_entries: dict
) -> Tuple[int, int]:
    # build vertex adjacency and pair_to_edge from edge_entries
    edge_to_pair = {}
    for eidx in edge_entries:
        ent = edge_entries[eidx]
        if ent.get("edge"):
            pair = tuple(map(int, ent["edge"]))
        else:
            pair = (int(ent.get("v_i", 0)), int(ent.get("v_j", 0)))
        edge_to_pair[int(eidx)] = pair
    pair_to_edge = {tuple(sorted(v)): k for k, v in edge_to_pair.items()}
    nverts = 40
    adj = {i: set() for i in range(nverts)}
    for i, j in edge_to_pair.values():
        adj[i].add(j)
        adj[j].add(i)
    triangles = []
    for a in range(nverts):
        for b in sorted(adj[a]):
            if b <= a:
                continue
            for c in sorted(adj[b]):
                if c <= b:
                    continue
                if a in adj[c]:
                    e_ab = pair_to_edge[(a, b)]
                    e_bc = pair_to_edge[(b, c)]
                    e_ac = pair_to_edge[(a, c)]
                    triangles.append((e_ab, e_bc, e_ac))
    tri_ok = 0
    for e1, e2, e3 in triangles:
        r1 = roots[predicted[e1]]
        r2 = roots[predicted[e2]]
        r3 = roots[predicted[e3]]
        ok = all(int(r1[i] + r2[i]) == int(r3[i]) for i in range(8))
        if ok:
            tri_ok += 1
    return tri_ok, len(triangles)


def main():
    canonical_path = ROOT / "artifacts" / "edge_root_bijection_canonical.json"
    canonical = load_json(canonical_path)
    edge_entries = {int(e["edge_index"]): e for e in canonical}

    gen_map_path = ROOT / "artifacts" / "sp43_we6_generator_map_full_we6.json"
    gen_data = load_json(gen_map_path)
    gens = gen_data.get("generators")
    inv_gens = [invert_perm(g) for g in gens]

    # load E8 roots via compute_double_sixes (if available)
    try:
        import importlib.util as _importlib_util

        spec = _importlib_util.spec_from_file_location(
            "compute_double_sixes", str(ROOT / "tools" / "compute_double_sixes.py")
        )
        cds = _importlib_util.module_from_spec(spec)
        spec.loader.exec_module(cds)
        roots = cds.construct_e8_roots()
    except Exception:
        raise

    # find candidate base roots: color orbits
    # reuse logic from compute_e6/exports to find color orbits
    orbits = cds.compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    # su3 weight projection (local helper)
    import numpy as _np

    SU3_ALPHA = _np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    SU3_BETA = _np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])

    def su3_weight(r):
        A = _np.stack([SU3_ALPHA, SU3_BETA], axis=1)
        G = A.T @ A
        coeffs = _np.linalg.solve(G, A.T @ _np.array(r))
        # return integer pair as used elsewhere
        return (
            int(round(float(_np.dot(r, SU3_ALPHA)))),
            int(round(float(_np.dot(r, SU3_BETA)))),
        )

    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    color_orbs = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument(
        "--all-roots",
        action="store_true",
        help="scan all 240 root indices instead of only color orbit roots",
    )
    args = p.parse_args()
    if args.all_roots:
        candidates = list(range(len(roots)))
    else:
        candidates = []
        for oi in color_orbs:
            candidates.extend(orbits[oi])

    results = []
    # iterate candidates
    for b in candidates:
        # apply word for each edge (as in apply_coset_match)
        preds = {}
        for eidx, ent in edge_entries.items():
            word = ent.get("word", []) or []
            p = b
            for tok in word:
                if tok >= 0:
                    p = gens[tok][p]
                else:
                    idx = -tok - 1
                    p = inv_gens[idx][p]
            preds[eidx] = int(p)
        bij = len(set(preds.values())) == len(preds)
        tri_ok, tri_tot = count_tri_satisfied(preds, roots, edge_entries)
        results.append(
            {"base_root": b, "bijective": bij, "tri_ok": tri_ok, "tri_total": tri_tot}
        )

    results.sort(key=lambda r: r["tri_ok"], reverse=True)
    out = {"candidates_tested": len(results), "top": results[:10]}
    out_path = ROOT / "checks" / "PART_CVII_coset_base_scan.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
