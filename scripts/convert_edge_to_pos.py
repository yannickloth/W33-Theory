#!/usr/bin/env python3
import json
from collections import deque

IN = 'checks/PART_CVII_e8_embedding_backtrack_partial.json'
OUT = 'checks/PART_CVII_e8_backtrack_pos.json'

d = json.load(open(IN))
edge_map = {int(k): int(v) for k, v in d.get('edge_to_root', {}).items()}

# build edges list
F = 3
all_vectors = [(a, b, c, d) for a in range(F) for b in range(F) for c in range(F) for d in range(F) if (a, b, c, d) != (0,0,0,0)]

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

edges = []
adj = [set() for _ in range(40)]
for i in range(40):
    for j in range(i+1,40):
        if symp(vertices[i], vertices[j]) == 0:
            edges.append((i,j))
            adj[i].add(j)
            adj[j].add(i)

# load roots
roots = []
# generate scaled E8 roots
for i in range(8):
    for j in range(i+1,8):
        for si in (-2,2):
            for sj in (-2,2):
                v = [0]*8
                v[i] = si
                v[j] = sj
                roots.append(tuple(v))
from itertools import product
for signs in product((-1,1), repeat=8):
    if sum(1 for s in signs if s<0) % 2 == 0:
        roots.append(tuple(int(s) for s in signs))

roots_set = set(roots)

# BFS-consistent assignment
pos = {0: tuple([0]*8)}
q = deque([0])
while q:
    u = q.popleft()
    for ei, (i, j) in enumerate(edges):
        if ei not in edge_map:
            continue
        r_idx = edge_map[ei]
        rvec = roots[r_idx]
        if i == u:
            v = j
            candidate = tuple(p_u - r for p_u, r in zip(pos[u], rvec))
        elif j == u:
            v = i
            candidate = tuple(p_u + r for p_u, r in zip(pos[u], rvec))
        else:
            continue
        if v in pos:
            if pos[v] != candidate:
                # conflict: skip
                continue
        else:
            # check candidate doesn't conflict with existing positions
            conflict = False
            for z, pz in pos.items():
                diff = tuple(a - b for a,b in zip(candidate, pz))
                is_root = diff in roots_set or tuple(-d for d in diff) in roots_set
                if z in adj[v]:
                    if not is_root:
                        conflict = True
                        break
                else:
                    if is_root:
                        conflict = True
                        break
            if not conflict:
                pos[v] = candidate
                q.append(v)

out = {'best': {'pos': {str(k): list(v) for k, v in pos.items()}, 'max_assigned': len(edge_map)}, 'best_assigned': len(edge_map)}
with open(OUT, 'w') as f:
    json.dump(out, f, indent=2)
print('Wrote', OUT, 'assigned_edges=', len(edge_map), 'pos_nodes=', len(pos))
