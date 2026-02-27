#!/usr/bin/env python3
"""Compute orbit structure of the infinity-neighbor 4-sets under key subgroups.

This script builds the full W33 graph, computes its automorphism group via
networkx, identifies the parabolic subgroup P stabilizing vertex 0, and then
computes the normalizer N(P) inside the automorphism group.  Using those
permutations we classify the 27 affine points by the orbit of their set of
four infinity neighbours.

Outputs (JSON files in the current directory):
  P_perms.json        - list of permutations in P (each a list of length 40)
  NP_perms.json       - list of permutations in N(P)
  neighbor_map.json   - mapping 13..39 -> 4-member list at infinity
  orbits_outer.json   - orbit decomposition under the outer 8-element twist
  orbits_P.json       - orbit decomposition under P (size 648)
  orbits_NP.json      - orbit decomposition under N(P) (size 1296)

The orbit lists record orbits of indices within the affine set (13..39).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

import networkx as nx
import numpy as np

import sys
from pathlib import Path
# ensure we can import modules located in the `scripts` folder
ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
from w33_homology import build_w33


def build_graph() -> nx.Graph:
    n, verts, adj, edges = build_w33()
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in adj[i]:
            if i < j:
                G.add_edge(i, j)
    return G


def perm_tuple_from_dict(d: dict[int, int], n: int) -> Tuple[int, ...]:
    return tuple(d[i] for i in range(n))


def invert_perm(p: Tuple[int, ...]) -> Tuple[int, ...]:
    n = len(p)
    inv = [0] * n
    for i, v in enumerate(p):
        inv[v] = i
    return tuple(inv)


def compose(p: Tuple[int, ...], q: Tuple[int, ...]) -> Tuple[int, ...]:
    # p o q
    return tuple(p[q[i]] for i in range(len(p)))


def main():
    G = build_graph()
    n = G.number_of_nodes()

    # compute automorphism group
    print("computing automorphisms (this may take a few seconds)...")
    gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
    autos = []
    for iso in gm.isomorphisms_iter():
        autos.append(perm_tuple_from_dict(iso, n))
    print(f"found {len(autos)} automorphisms")

    # load PG(3,3) coordinates to classify symplectic vs anti
    pts = json.loads((Path("PG33_OUTER_TWIST_GEOMETRY_BUNDLE_v01") / "PG33_points.json").read_text())
    # convert to numpy arrays mod3
    import numpy as np
    vecs = [np.array(p, dtype=int) for p in pts]
    # symplectic form J
    J = np.array([[0,0,0,1],[0,0,1,0],[0,2,0,0],[2,0,0,0]], dtype=int)

    def is_symplectic(perm):
        # check v_i^T J v_j == v_{perm(i)}^T J v_{perm(j)} mod3 for all i<j
        for i in range(n):
            for j in range(i+1, n):
                lhs = int((vecs[i] @ J @ vecs[j]) % 3)
                rhs = int((vecs[perm[i]] @ J @ vecs[perm[j]]) % 3)
                if lhs != rhs:
                    return False
        return True

    symp_autos = [p for p in autos if is_symplectic(p)]
    print(f"symplectic automorphisms: {len(symp_autos)} (should be 25920)")

    # stabilizer of 0 in full group = normalizer NP
    NP = [p for p in autos if p[0] == 0]
    print(f"full stabilizer size (N(P)) = {len(NP)}")

    # define P_s as a canonical half of NP (first 648 lexicographically)
    P_s = sorted(NP)[: len(NP) // 2]
    print(f"chosen P_s size = {len(P_s)} (first half of NP)")

    # compute neighbor map using infinity list
    n, verts, adj, edges = build_w33()
    infinity = list(range(13))
    affine = list(range(13, 40))
    neighbor_map = {}
    for i in affine:
        neigh = [j for j in infinity if j in adj[i]]
        neighbor_map[i] = neigh
    # outer twist permutation we know from earlier script
    perm40 = json.loads((Path("PG33_OUTER_TWIST_GEOMETRY_BUNDLE_v01") / "perm40_from_canonical.json").read_text())
    # compute orbits
    def compute_orbits(group: List[Tuple[int, ...]]) -> List[List[int]]:
        unvis = set(affine)
        orbits = []
        while unvis:
            start = unvis.pop()
            orbit = [start]
            cur = start
            while True:
                # apply each generator by default? we want full orbit under group
                # but group may be large; easiest: repeatedly apply all perms until closure
                new = set(orbit)
                for g in group:
                    nxt = g[cur]
                    if nxt in new:
                        continue
                    new.add(nxt)
                if new == set(orbit):
                    break
                orbit = sorted(new)
                cur = orbit[0]  # just restart
            for v in orbit:
                unvis.discard(v)
            orbits.append(sorted(orbit))
        return orbits

    # outer orbit using single perm40
    outer = []
    unvis = set(affine)
    while unvis:
        start = unvis.pop()
        orbit = [start]
        cur = start
        while True:
            nxt = perm40[cur]
            if nxt == start:
                break
            orbit.append(nxt)
            unvis.discard(nxt)
            cur = nxt
        outer.append(sorted(orbit))

    orbits_P = compute_orbits(P_s)
    orbits_NP = compute_orbits(NP)

    outdir = Path(".")
    json.dump([list(p) for p in P_s], open(outdir / "P_perms.json", "w"))
    json.dump([list(g) for g in NP], open(outdir / "NP_perms.json", "w"))
    json.dump(neighbor_map, open(outdir / "neighbor_map.json", "w"), indent=2)
    json.dump(outer, open(outdir / "orbits_outer.json", "w"), indent=2)
    json.dump(orbits_P, open(outdir / "orbits_P.json", "w"), indent=2)
    json.dump(orbits_NP, open(outdir / "orbits_NP.json", "w"), indent=2)
    print("wrote orbit classification files")

if __name__ == '__main__':
    main()
