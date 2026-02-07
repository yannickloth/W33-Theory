"""Attempt W33 → E8 embedding by randomized backtracking in exact arithmetic.

Usage: sage -python sage/find_w33_e8_embedding.sage [attempts] [max_nodes]
                                             [time_limit_seconds] [seed]

Writes checks/PART_CVII_e8_embedding_sage.json with results and diagnostics.
"""
from sage.all import *
import json
import time
import random
import sys
from itertools import product

# --- params
def argv_int(i, default):
    try:
        return int(sys.argv[i])
    except Exception:
        return default

ATTEMPTS = argv_int(1, 200)
MAX_NODES = argv_int(2, 100000)
TIME_LIMIT = float(argv_int(3, 300))
SEED = argv_int(4, None)

if SEED is not None:
    random.seed(SEED)

OUT_PATH = 'checks/PART_CVII_e8_embedding_sage.json'

start_time = time.time()

# --- build W33 (projective points PG(3,3) canonical reps)
F = GF(3)
pts = []
for a0 in F:
    for a1 in F:
        for a2 in F:
            for a3 in F:
                v = vector(F, [a0, a1, a2, a3])
                if v != 0:
                    pts.append(v)
# normalized projective representatives (first nonzero coordinate set to 1)
proj = []
seen = set()
for v in pts:
    for i in range(4):
        if v[i] != 0:
            inv = 1 / v[i]
            nv = tuple([(inv * c) for c in v])
            break
    if nv not in seen:
        seen.add(nv)
        proj.append(vector(F, nv))

assert len(proj) == 40

# symplectic form J
J = matrix(F, [[0, 0, 0, 1], [0, 0, 1, 0], [0, -1, 0, 0], [-1, 0, 0, 0]])

# adjacency
adj = {i: set() for i in range(40)}
edges = []
for i in range(40):
    for j in range(i + 1, 40):
        if (proj[i].transpose() * J * proj[j])[0] == 0:
            adj[i].add(j)
            adj[j].add(i)
            edges.append((i, j))

# --- E8 roots scaled by 2 (integer vectors)
roots = []
# Type 1: permutations of (±2, ±2, 0, 0, 0, 0, 0, 0)
for i in range(8):
    for j in range(i + 1, 8):
        for si in (-2, 2):
            for sj in (-2, 2):
                v = [0] * 8
                v[i] = si
                v[j] = sj
                roots.append(tuple(v))
# Type 2: (±1)^8 with even number of -1 signs
for signs in product((-1, 1), repeat=8):
    if sum(1 for s in signs if s < 0) % 2 == 0:
        roots.append(tuple(int(s) for s in signs))
# deduplicate and sort
roots = list(set(roots))
roots.sort()
assert len(roots) == 240
root_set = set(roots)

# helpers
def vadd(a, b):
    return tuple(x + y for x, y in zip(a, b))

def vsub(a, b):
    return tuple(x - y for x, y in zip(a, b))

def vneg(a):
    return tuple(-x for x in a)

# Search with randomized backtracking and forward checking

best = {
    "found": False,
    "mapping": None,
    "edge_to_root_count": 0,
    "attempts": 0,
    "nodes": 0,
    "elapsed": 0.0,
}

# recursion with mutable counter for nodes

def search(assign, assigned_set, nodes, t0):
    # time / node limits
    if time.time() - t0 > TIME_LIMIT:
        return None
    if nodes[0] > MAX_NODES:
        return None
    if len(assigned_set) == 40:
        return dict(assign)
    # choose unassigned vertex with most assigned neighbors (MRV heuristic)
    best_v = None
    best_n = -1
    for v in range(40):
        if v in assigned_set:
            continue
        an = sum(1 for u in adj[v] if u in assigned_set)
        if an > best_n:
            best_n = an
            best_v = v
    if best_v is None:
        # choose random unassigned
        unassigned = [v for v in range(40) if v not in assigned_set]
        best_v = random.choice(unassigned)
    # collect candidate positions via intersection
    assigned_neighbors = [u for u in adj[best_v] if u in assigned_set]
    candidate = None
    for u in assigned_neighbors:
        pu = assign[u]
        S_u = set(vsub(pu, r) for r in roots)
        if candidate is None:
            candidate = S_u
        else:
            candidate &= S_u
        if not candidate:
            break
    if candidate is None:
        # no assigned neighbors -> heavy branching: create random candidate sample by taking pu - r for random r and pu from any neighbor
        candidate = set()
        sample_nb = list(adj[best_v])[:3]
        for u in sample_nb:
            pu = (0,) * 8 if u not in assigned_set else assign[u]
            for r in random.sample(roots, min(50, len(roots))):
                candidate.add(vsub(pu, r))
    if not candidate:
        return None
    # remove used positions
    used_positions = set(assign.values())
    candidates = [c for c in candidate if c not in used_positions]
    # sample down if too many
    if len(candidates) > 200:
        candidates = random.sample(candidates, 200)
    # heuristic: sort by how many assigned-neighbor constraints it satisfies (more is better)
    def score(c):
        s = 0
        for u in assigned_neighbors:
            if vsub(assign[u], c) in root_set:
                s += 1
        return -s
    candidates.sort(key=score)
    # try candidates
    for c in candidates:
        # check pairwise constraints for already-assigned neighbors (redundant but safe)
        ok = True
        for u in assigned_neighbors:
            if vsub(assign[u], c) not in root_set:
                ok = False
                break
        if not ok:
            continue
        # assign
        assign[best_v] = c
        assigned_set.add(best_v)
        nodes[0] += 1
        mapping = search(assign, assigned_set, nodes, t0)
        if mapping is not None:
            return mapping
        # backtrack
        assigned_set.remove(best_v)
        del assign[best_v]
    return None

# top-level randomized attempts
attempt = 0
while attempt < ATTEMPTS and time.time() - start_time < TIME_LIMIT:
    attempt += 1
    best["attempts"] += 1
    # initialize with v0 at origin
    assign = {0: (0,) * 8}
    assigned_set = set([0])
    # seed 1..3 neighbors with random roots to steer search
    neighs = list(adj[0])
    random.shuffle(neighs)
    k_seed = min(3, len(neighs))
    ok_seed = False
    for trial_seed in range(40):
        assign_local = dict(assign)
        assigned_local = set(assigned_set)
        valid = True
        for nb in neighs[:k_seed]:
            r = random.choice(roots)
            pos = vneg(r)
            if pos in assign_local.values():
                valid = False
                break
            assign_local[nb] = pos
            assigned_local.add(nb)
        if not valid:
            continue
        nodes = [0]
        mapping = search(assign_local, assigned_local, nodes, start_time)
        best["nodes"] = nodes[0]
        if mapping is not None:
            best["found"] = True
            best["mapping"] = mapping
            break
    if best["found"]:
        break

# post-process and write JSON
best["elapsed"] = time.time() - start_time
best["attempts"] = attempt

if best["found"]:
    # compute edge->root mapping and uniqueness
    mapping = best["mapping"]
    edge_to_root = {}
    used_roots = set()
    ok_all = True
    for (i, j) in edges:
        r = vsub(mapping[i], mapping[j])
        edge_to_root[f"{i}-{j}"] = r
        if r not in root_set:
            ok_all = False
    best["edge_to_root_count"] = len(set(edge_to_root.values()))
    best["edge_count"] = len(edges)
    best["valid_embedding"] = ok_all
    # convert mapping to lists
    best["mapping"] = {str(k): list(v) for k, v in mapping.items()}
    best["edge_to_root_sample"] = {k: list(v) for k, v in list(edge_to_root.items())[:10]}

# make JSON-safe
for k in ("attempts", "nodes"):
    best[k] = int(best.get(k, 0))
best["elapsed"] = float(best["elapsed"]) if best.get("elapsed") else 0.0

# write file
try:
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(best, f, indent=2)
    print("Wrote", OUT_PATH)
except Exception as e:
    print("Failed to write output:", e)
    # attempt to write to stdout
    print(json.dumps(best, indent=2))

print("Done. Found:", best["found"], "attempts:", best["attempts"], "nodes:", best["nodes"], "elapsed:", best["elapsed"])
