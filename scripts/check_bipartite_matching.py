#!/usr/bin/env python3
"""Check maximum bipartite matching between edges and roots for candidate lists."""
import json
import os
import sys
from collections import deque

import numpy as np

# Ensure 'scripts' module imports work when running as a script
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# copy candidate computation from earlier
from check_triangle_coverage import build_w33_graph, load_seed_k


def hopcroft_karp(adj, n_left, n_right):
    # adj: list of neighbors in right for each left vertex, left indices 0..n_left-1, right 0..n_right-1
    pair_u = [-1] * n_left
    pair_v = [-1] * n_right
    dist = [0] * n_left

    INF = 10**9

    def bfs():
        queue = deque()
        for u in range(n_left):
            if pair_u[u] == -1:
                dist[u] = 0
                queue.append(u)
            else:
                dist[u] = INF
        found = False
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if pair_v[v] != -1 and dist[pair_v[v]] == INF:
                    dist[pair_v[v]] = dist[u] + 1
                    queue.append(pair_v[v])
                if pair_v[v] == -1:
                    found = True
        return found

    def dfs(u):
        for v in adj[u]:
            if pair_v[v] == -1 or (dist[pair_v[v]] == dist[u] + 1 and dfs(pair_v[v])):
                pair_u[u] = v
                pair_v[v] = u
                return True
        dist[u] = INF
        return False

    result = 0
    while bfs():
        for u in range(n_left):
            if pair_u[u] == -1 and dfs(u):
                result += 1
    return result, pair_u, pair_v


if __name__ == "__main__":
    import argparse
    import importlib.util as _importlib_util

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--seed-json",
        type=str,
        default="checks/PART_CVII_e8_embedding_attempt_seed.json",
        help="seed JSON (for candidate lists)",
    )
    p.add_argument(
        "--mapping-json",
        type=str,
        default=None,
        help="explicit mapping JSON (edge->root entries)",
    )
    p.add_argument(
        "--ks",
        type=str,
        default="30,60,120,240",
        help="comma-separated k values to test",
    )
    p.add_argument(
        "--write-match",
        type=str,
        default=None,
        help="path to write matching assignment JSON",
    )
    p.add_argument(
        "--write-seed",
        type=str,
        default=None,
        help="path to write seed JSON from matching (for repair/backtrack)",
    )
    p.add_argument(
        "--check-triangles",
        action="store_true",
        help="compute triangle satisfaction for matching (requires E8 roots)",
    )
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    ks = [int(x) for x in args.ks.split(",") if x.strip()]

    # helper: load explicit mapping (various artifact formats)
    def load_mapping(path):
        j = json.loads(open(path).read())
        mapping = {}
        # accept {'seed_edges': [{'edge_index':..,'root_index':..}, ...]}
        if isinstance(j, dict) and "seed_edges" in j:
            for it in j["seed_edges"]:
                mapping[int(it["edge_index"])] = int(it["root_index"])
            return mapping
        # accept list of entries like artifacts/edge_root_bijection_*
        if isinstance(j, list):
            for it in j:
                if "edge_index" in it and "root_index" in it:
                    mapping[int(it["edge_index"])] = int(it["root_index"])
            return mapping
        # accept dict edge->root
        if isinstance(j, dict):
            for k, v in j.items():
                try:
                    mapping[int(k)] = int(v)
                except Exception:
                    pass
            return mapping
        return mapping

    # optional triangle checker
    def compute_triangles_satisfaction(pair_u, edges, roots):
        # build adjacency -> triangles
        nverts, _, adj, _ = build_w33_graph()
        # map pair -> edge index
        pair_to_edge = {tuple(sorted(edges[i])): i for i in range(len(edges))}
        triangles = []
        for a in range(nverts):
            for b in adj[a]:
                if b <= a:
                    continue
                for c in adj[b]:
                    if c <= b:
                        continue
                    if a in adj[c]:
                        e_ab = pair_to_edge[(a, b)]
                        e_bc = pair_to_edge[(b, c)]
                        e_ac = pair_to_edge[(a, c)]
                        triangles.append((e_ab, e_bc, e_ac))
        tri_ok = 0
        tri_total = len(triangles)
        bad = []
        for e1, e2, e3 in triangles:
            r1_idx = pair_u[e1] if e1 < len(pair_u) else -1
            r2_idx = pair_u[e2] if e2 < len(pair_u) else -1
            r3_idx = pair_u[e3] if e3 < len(pair_u) else -1
            if r1_idx == -1 or r2_idx == -1 or r3_idx == -1:
                bad.append((e1, e2, e3))
                continue
            r1 = roots[r1_idx]
            r2 = roots[r2_idx]
            r3 = roots[r3_idx]
            # check any orientation equality
            ok = (
                all(int(r1[i] + r2[i]) == int(r3[i]) for i in range(8))
                or all(int(r1[i] + r3[i]) == int(r2[i]) for i in range(8))
                or all(int(r2[i] + r3[i]) == int(r1[i]) for i in range(8))
            )
            if ok:
                tri_ok += 1
            else:
                bad.append((e1, e2, e3))
        return tri_ok, tri_total, bad

    # run mapping-json mode (explicit mapping)
    if args.mapping_json:
        mapping = load_mapping(args.mapping_json)
        _, _, _, edges_all = build_w33_graph()
        n_edges = len(edges_all)
        candidates = [[] for _ in range(n_edges)]
        for i in range(n_edges):
            if i in mapping:
                candidates[i] = [int(mapping[i])]
            else:
                candidates[i] = []
        match_size, pair_u, pair_v = hopcroft_karp(candidates, n_edges, 240)
        print(f"MAPPING JSON: match_size={match_size} / {n_edges}")
        if args.write_match:
            json.dump({"pair_u": pair_u}, open(args.write_match, "w"), indent=2)
            print("Wrote match to", args.write_match)
        if args.write_seed:
            seed_edges = [
                {"edge_index": i, "root_index": pair_u[i]}
                for i in range(len(pair_u))
                if pair_u[i] != -1
            ]
            json.dump({"seed_edges": seed_edges}, open(args.write_seed, "w"), indent=2)
            print("Wrote seed from matching to", args.write_seed)
        if args.check_triangles:
            # load roots
            spec = _importlib_util.spec_from_file_location(
                "compute_double_sixes",
                os.path.join(
                    os.path.dirname(__file__), "..", "tools", "compute_double_sixes.py"
                ),
            )
            cds = _importlib_util.module_from_spec(spec)
            spec.loader.exec_module(cds)
            roots = cds.construct_e8_roots()
            tri_ok, tri_tot, bad = compute_triangles_satisfaction(
                pair_u, edges_all, roots
            )
            print(f"Triangles satisfied: {tri_ok}/{tri_tot} ({tri_ok/tri_tot:.3f})")
        sys.exit(0)

    # default seed JSON candidate run
    for k in ks:
        candidates, edges = load_seed_k(k=k, seed_json=args.seed_json)
        n_edges = len(candidates)
        n_roots = 240
        match_size, pair_u, pair_v = hopcroft_karp(candidates, n_edges, n_roots)
        print(f"k={k} match_size={match_size} out_of={n_edges}")
        if args.write_match:
            json.dump(
                {"k": k, "pair_u": pair_u},
                open(args.write_match.replace(".json", f".k{k}.json"), "w"),
                indent=2,
            )
            if args.verbose:
                print(
                    "Wrote match to", args.write_match.replace(".json", f".k{k}.json")
                )
        if args.write_seed:
            seed_edges = [
                {"edge_index": i, "root_index": pair_u[i]}
                for i in range(len(pair_u))
                if pair_u[i] != -1
            ]
            json.dump(
                {"seed_edges": seed_edges},
                open(args.write_seed.replace(".json", f".k{k}.json"), "w"),
                indent=2,
            )
            if args.verbose:
                print(
                    "Wrote seed file to",
                    args.write_seed.replace(".json", f".k{k}.json"),
                )
        if args.check_triangles:
            # load roots
            spec = _importlib_util.spec_from_file_location(
                "compute_double_sixes",
                os.path.join(
                    os.path.dirname(__file__), "..", "tools", "compute_double_sixes.py"
                ),
            )
            cds = _importlib_util.module_from_spec(spec)
            spec.loader.exec_module(cds)
            roots = cds.construct_e8_roots()
            tri_ok, tri_tot, bad = compute_triangles_satisfaction(pair_u, edges, roots)
            print(
                f"k={k} triangles satisfied: {tri_ok}/{tri_tot} ({tri_ok/tri_tot:.3f})"
            )
