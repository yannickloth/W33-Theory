#!/usr/bin/env python3
"""Search for one-dimensional cellular-automaton embeddings in W33.

The idea is to look for simple cycles in the W33 edge graph and then
examine the restriction of the GF(2)-reduced QCA evolution operator to that
cycle.  If the restricted map is circulant, then the cycle implements a
translation-invariant elementary CA rule, and we can check whether it's one of
the well-known universal rules (e.g. Rule 110).

Run as:
    python scripts/w33_universal_search.py

This is exploratory code and may take a few seconds as it enumerates cycles.
"""

# This script searches for one-dimensional elementary cellular automata that
# can be embedded along cycles in the W33 line graph.  It is primarily an
# exploratory tool; the default search depth is intentionally conservative to
# avoid long runs during automated testing.
#
# Usage examples:
#     python scripts/w33_universal_search.py                # default quick search
#     python scripts/w33_universal_search.py --max-length 10 --output data/ca.json
#     python scripts/w33_universal_search.py --cycle 13       # analyze a single cycle
#
# The CLI options allow limiting the maximum cycle length and specifying an
# output JSON file.  When imported by other modules or tests, the heavy search
# is not executed automatically.

from __future__ import annotations

import argparse
import sys, os
from pathlib import Path

# ensure repository root and scripts folder are on sys.path so we can import
# other modules the same way as the other scripts do.
ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent.resolve()))

import itertools
import json

import numpy as np
import networkx as nx

# reuse geometry builder from w33_algebra_qca
import w33_algebra_qca as qca


def build_graph_and_l1():
    points, edges, adj, triangles, J = qca.build_w33_geometry()
    L1, d1, d2, edge_idx = qca.hodge_laplacian_1(len(points), edges, triangles)
    m = len(edges)
    return edges, L1, edge_idx


def gf2_projector(L1):
    """Return operator U = I - L1 (mod 2) as a 0/1 numpy array."""
    m = L1.shape[0]
    I = np.eye(m, dtype=int)
    U = (I - (L1 % 2)) % 2
    return U


def is_circulant(submat):
    """Return True if matrix is circulant (each row is cyclic shift of first)."""
    rows, cols = submat.shape
    if rows != cols:
        return False
    first = submat[0]
    for i in range(1, rows):
        if not np.array_equal(np.roll(first, i), submat[i]):
            return False
    return True


def rule_from_row(row):
    """Compute the elementary CA rule (0..255) from a 3-bit neighbourhood.

    The input `row` encodes the values of the left, center, and right
    neighbours.  The return value is an integer whose binary expansion
    gives the output for each of the eight possible patterns.
    """
    if len(row) < 3:
        return None
    # pattern order: 111,110,101,100,011,010,001,000
    rule = 0
    for pat in range(8):
        bits = [(pat >> j) & 1 for j in reversed(range(3))]
        # compute output for this pattern
        out = int(np.dot(bits, row[:3]) % 2)
        rule |= out << (7 - pat)
    return rule


def search_cycles(max_length=10, save_path=None, target_rule=None):
    # Enumerate simple cycles in the W33 vertex graph up to `max_length` edges.
    # If `target_rule` is provided (0..255) filter to that elementary rule.
    # The depth defaults to 10; adjust via CLI for longer exploratory searches.
    edges, L1, edge_idx = build_graph_and_l1()
    U2 = gf2_projector(L1)
    # build the original W33 vertex graph (40 verts) for cycle enumeration
    Gv = nx.Graph()
    npoints = max(max(u, v) for u, v in edges) + 1
    Gv.add_nodes_from(range(npoints))
    for u, v in edges:
        Gv.add_edge(u, v)

    print(f"W33 vertex graph: {Gv.number_of_nodes()} nodes, {Gv.number_of_edges()} edges")
    print(f"Cycle search max_length={max_length}, target_rule={target_rule}")

    def canonical_cycle(cycle: list[int]) -> tuple[int, ...]:
        if not cycle:
            return ()
        if cycle[0] == cycle[-1]:
            cycle = cycle[:-1]
        rots = [(tuple(cycle[i:] + cycle[:i])) for i in range(len(cycle))]
        rots += [(tuple(reversed(r))) for r in rots]
        return min(rots)

    found = []
    seen_cycles = set()

    def dfs(start, current, visited):
        if len(current) > max_length:
            return
        for nbr in Gv[current[-1]]:
            if nbr == start and len(current) >= 3:
                cyc = canonical_cycle(current)
                if cyc not in seen_cycles:
                    seen_cycles.add(cyc)
                    edge_inds = []
                    for a, b in zip(cyc, cyc[1:] + (cyc[0],)):
                        eidx = edge_idx.get((a, b), edge_idx.get((b, a)))
                        edge_inds.append(eidx)
                    M = U2[np.ix_(edge_inds, edge_inds)]
                    if is_circulant(M):
                        rule = rule_from_row(M[0])
                        if target_rule is None or rule == target_rule:
                            found.append((edge_inds, len(edge_inds), rule))
                            print(f"Found circulant cycle length {len(edge_inds)}, rule={rule}")
            elif nbr not in visited and nbr > start:
                dfs(start, current + [nbr], visited | {nbr})

    for v in sorted(Gv.nodes()):
        dfs(v, [v], {v})

    if save_path is not None:
        json.dump(found, open(save_path, "w"))
    return found


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Search for elementary CA cycles on W33")
    p.add_argument("--max-length", type=int, default=10,
                   help="maximum cycle length to explore (default 10)")
    p.add_argument("--rule", type=int, choices=range(0,256), metavar="RULE",
                   help="filter to cycles implementing this elementary rule")
    p.add_argument("--output", "-o", default="data/ca_cycles.json",
                   help="path to write JSON results")
    args = p.parse_args()

    print("Searching for cycles that support an elementary CA rule...")
    result = search_cycles(max_length=args.max_length,
                           save_path=args.output,
                           target_rule=args.rule)
    print(f"Done.  Results saved to {args.output}")
    print(result)
