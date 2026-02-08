#!/usr/bin/env python3
import json
import numpy as np
from collections import defaultdict

# load roots
def generate_scaled_e8_roots():
    roots = set()
    for i in range(8):
        for j in range(i + 1, 8):
            for si in (-2, 2):
                for sj in (-2, 2):
                    v = [0] * 8
                    v[i] = si
                    v[j] = sj
                    roots.add(tuple(v))
    from itertools import product
    for signs in product((-1, 1), repeat=8):
        if sum(1 for s in signs if s < 0) % 2 == 0:
            roots.add(tuple(int(s) for s in signs))
    roots_list = sorted(list(roots))
    return roots_list


def build_w33_graph():
    F = 3
    all_vectors = [
        (a, b, c, d)
        for a in range(F)
        for b in range(F)
        for c in range(F)
        for d in range(F)
        if (a, b, c, d) != (0, 0, 0, 0)
    ]

    def canonical_rep(v):
        for i in range(4):
            if v[i] % F != 0:
                a = v[i] % F
                inv = 1 if a == 1 else 2
                return tuple(((x * inv) % F) for x in v)
        return None

    reps = set(canonical_rep(v) for v in all_vectors if canonical_rep(v))
    vertices = sorted(list(reps))

    def symp(x, y):
        return (x[0] * y[1] - x[1] * y[0] + x[2] * y[3] - x[3] * y[2]) % F

    n = len(vertices)
    adj = [[] for _ in range(n)]
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if symp(vertices[i], vertices[j]) == 0:
                adj[i].append(j)
                adj[j].append(i)
                edges.append((i, j))
    return n, vertices, adj, edges

roots = generate_scaled_e8_roots()
root_map = {i: tuple(roots[i]) for i in range(len(roots))}

s = json.load(open('checks/PART_CVII_e8_embedding_attempt_seed.json'))
assignment = {str(sd['edge_index']): sd['root_index'] for sd in s.get('seed_edges', [])}

n, vertices, adj, edges = build_w33_graph()
# map edge pair to index
edge_index = {edges[i]: i for i in range(len(edges))}
edge_index.update({(j,i): idx for (i,j), idx in edge_index.items()})

tris = []
for a in range(n):
    for b in adj[a]:
        if b <= a:
            continue
        for c in adj[b]:
            if c <= b:
                continue
            if a in adj[c]:
                tri = tuple(sorted((a,b,c)))
                if tri not in tris:
                    tris.append(tri)

bad = []
for (a,b,c) in tris:
    e_ab = edge_index.get((a,b))
    e_bc = edge_index.get((b,c))
    e_ac = edge_index.get((a,c))
    if str(e_ab) not in assignment or str(e_bc) not in assignment or str(e_ac) not in assignment:
        continue
    r_ab = root_map[assignment[str(e_ab)]]
    r_bc = root_map[assignment[str(e_bc)]]
    r_ac = root_map[assignment[str(e_ac)]]
    lhs = tuple(x+y - z for x,y,z in zip(r_ab, r_bc, r_ac))
    if any(v != 0 for v in lhs):
        bad.append({'tri':(a,b,c), 'edges':(e_ab,e_bc,e_ac), 'lhs':lhs, 'roots':(assignment[str(e_ab)], assignment[str(e_bc)], assignment[str(e_ac)])})

print('triangles:', len(tris), 'violations:', len(bad))
if bad:
    print('Sample violation (up to 10):')
    for x in bad[:10]:
        print(x)
