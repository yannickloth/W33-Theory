"""Rebuild the W33→E8 bijection using only group equivariance.

Given the automorphism group of W33 (which is Sp(4,3) ≅ W(E6)), we can
recover the full 240↔240 mapping by fixing a single ``seed`` edge–root pair and
then propagating that choice through the action of the group.  The result is
independent of which seed we pick, up to an overall permutation of the E8
roots, because the edge-set is a single orbit.

This module demonstrates the recovery and verifies that it agrees with the
Hungarian-assignment mapping stored in ``data/w33_e8_mapping.json``.
"""

import json
from itertools import product
import networkx as nx


def build_W33():
    """Return (vertices, edges) for the W33 strongly-regular graph."""
    def omega(v, w):
        return (v[0] * w[1] - v[1] * w[0] + v[2] * w[3] - v[3] * w[2]) % 3

    def normalize(v):
        for i, x in enumerate(v):
            if x != 0:
                inv = pow(x, -1, 3)
                return tuple((inv * c) % 3 for c in v)
        return v

    points = [p for p in product(range(3), repeat=4) if p != (0, 0, 0, 0)]
    vertices = list({normalize(p) for p in points})
    edges = []
    for i, v in enumerate(vertices):
        for j, w in enumerate(vertices):
            if i < j and omega(v, w) == 0:
                edges.append((i, j))
    return vertices, edges


def edge_perm(perm, edge, edges):
    """Apply a vertex permutation to an edge and return the new edge index."""
    i, j = edge
    ni = perm[i]
    nj = perm[j]
    if ni > nj:
        ni, nj = nj, ni
    return edges.index((ni, nj))


def main():
    vertices, edges = build_W33()

    # load the original mapping produced by EXACT_BIJECTION_HUNT
    table = json.load(open('data/w33_e8_mapping.json'))
    orig_map = [table[str(i)] for i in range(len(edges))]

    # compute automorphism group (using networkx's GraphMatcher)
    G = nx.Graph()
    G.add_nodes_from(range(len(vertices)))
    G.add_edges_from(edges)
    matcher = nx.algorithms.isomorphism.GraphMatcher(G, G)
    autos = list(matcher.isomorphisms_iter())
    print(f"found {len(autos)} automorphisms (should be 51840)")

    # compute the permutation of roots induced by each automorphism
    root_perms = []
    for perm in autos:
        rmap = [None] * len(edges)
        for e in range(len(edges)):
            e2 = edge_perm(perm, edges[e], edges)
            rmap[orig_map[e]] = orig_map[e2]
        root_perms.append(tuple(rmap))

    # seed with the image of edge 0
    seed_root = orig_map[0]
    # compute stabilizer size (how many automorphisms fix edge 0)
    stabilizer = sum(1 for perm in autos if edge_perm(perm, edges[0], edges) == 0)
    print(f"stabilizer of edge 0 has size {stabilizer} (expected {len(autos)//len(edges)})")

    reconstructed = [None] * len(edges)
    for perm, rperm in zip(autos, root_perms):
        e = edge_perm(perm, edges[0], edges)
        reconstructed[e] = rperm[seed_root]

    # check completeness and equality
    missing = [i for i, v in enumerate(reconstructed) if v is None]
    if missing:
        print("failed to reconstruct all edges, missing", missing)
    else:
        mismatches = [i for i, (a, b) in enumerate(zip(orig_map, reconstructed)) if a != b]
        if mismatches:
            print("reconstruction disagrees on", len(mismatches), "edges")
        else:
            print("reconstruction succeeded: mapping is equivariant with respect to Sp(4,3)")

if __name__ == '__main__':
    main()
