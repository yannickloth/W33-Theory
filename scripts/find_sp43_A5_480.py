#!/usr/bin/env python3
"""Locate the canonical A5 subgroup inside the Sp(4,3) action on W33 directed edges.

This script rebuilds the PSp(4,3) group via transvections, computes the
corresponding permutation action on the 480 directed edges of W33, and then
searches for a pair of generators satisfying the (2,3,5) presentation whose
closure has order 60 and yields the orbit fingerprint 6*20 + 6*60.

The found generators and orbit decomposition are written to
``sp43_A5_data.json`` for downstream use, and the permutations themselves are
also printed for inspection.

Usage:
    python scripts/find_sp43_A5_480.py
"""
from __future__ import annotations
import json
import math
from collections import deque
from pathlib import Path
import sys

# helper functions copied from w33_480_weld so we don't require the bundle
from w33_480_weld import build_w33, build_directed_edges, directed_edge_permutation, build_sp43_group


def permutation_order(perm):
    visited = set()
    lcm = 1
    n = len(perm)
    for i in range(n):
        if i in visited:
            continue
        cur = i
        cycle = 0
        while cur not in visited:
            visited.add(cur)
            cycle += 1
            cur = perm[cur]
        lcm = math.lcm(lcm, cycle)
    return lcm


def find_a5(edge_perms):
    """Return a pair of indices (g_id, h_id) generating an A5 with desired fingerprint."""
    n = len(edge_perms[0])
    perms_to_id = {p: i for i, p in enumerate(edge_perms)}
    target = [20] * 6 + [60] * 6
    for g_id, p_g in enumerate(edge_perms):
        if permutation_order(p_g) != 2:
            continue
        for h_id, p_h in enumerate(edge_perms):
            if permutation_order(p_h) != 3:
                continue
            # check relation (gh)^5 = identity
            gh = [p_g[x] for x in p_h]
            gh5 = gh
            for _ in range(4):
                gh5 = [gh5[x] for x in gh]
            if gh5 != list(range(n)):
                continue
            # compute closure
            H = {g_id, h_id}
            dq = deque([g_id, h_id])
            while dq:
                a = dq.popleft()
                for b in list(H):
                    comp = tuple(edge_perms[a][x] for x in edge_perms[b])
                    cid = perms_to_id.get(comp)
                    if cid is not None and cid not in H:
                        H.add(cid); dq.append(cid)
                    comp2 = tuple(edge_perms[b][x] for x in edge_perms[a])
                    cid = perms_to_id.get(comp2)
                    if cid is not None and cid not in H:
                        H.add(cid); dq.append(cid)
            if len(H) == 60:
                # compute orbit fingerprint
                visited = set(); orbits = []
                for i in range(n):
                    if i in visited:
                        continue
                    orb = []
                    dq2 = deque([i])
                    while dq2:
                        j = dq2.popleft()
                        if j in visited:
                            continue
                        visited.add(j)
                        orb.append(j)
                        for eid in H:
                            k = edge_perms[eid][j]
                            if k not in visited:
                                dq2.append(k)
                    orbits.append(len(orb))
                orbits.sort()
                if orbits == target:
                    return g_id, h_id, orbits
    return None, None, None


def main():
    n, vertices, adj, edges = build_w33()
    directed_edges = build_directed_edges(edges)
    de_index = {de: i for i, de in enumerate(directed_edges)}
    all_vperms = build_sp43_group(n, vertices, adj, edges)
    print(f"PSp(4,3) group size (vertex perms) = {len(all_vperms)}")
    # compute directed-edge permutations
    all_edge_perms = [tuple(directed_edge_permutation(vp, directed_edges, de_index)) for vp in all_vperms]
    print(f"Computed {len(all_edge_perms)} edge permutations (should equal group size)")
    # search for A5
    g_id, h_id, orbit = find_a5(all_edge_perms)
    if g_id is None:
        print("no A5 found!")
        return
    print("found A5 generators g_id,h_id", g_id, h_id)
    # save data
    result = {
        "g_id": g_id,
        "h_id": h_id,
        "g_perm": list(all_edge_perms[g_id]),
        "h_perm": list(all_edge_perms[h_id]),
        "orbit_sizes": orbit,
    }
    with open("sp43_A5_data.json", "w") as f:
        json.dump(result, f, indent=2)
    print("wrote sp43_A5_data.json", result)

if __name__ == "__main__":
    main()
