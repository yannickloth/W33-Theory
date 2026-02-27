#!/usr/bin/env python3
"""Compute the rootword cocycle defect induced by the outer twist.

This driver performs all steps described in the user's note:
  * loads the canonical W33 graph and edge->E8-root bijection
  * reads the outer-twist permutation from the H27 bundle and conjugates
    it to the "w33line" labelling using the WE6->PSp43 conjugacy bundle
  * constructs the isomorphic target graph G' and finds a deterministic
    isomorphism q: G'->G fixing a colored basepoint
  * defines the effective W33 automorphism A = q \circ p_line
  * rebuilds the extraspecial Heisenberg subgroup (Tx,Ty,Z) inside the
    stabilizer of the basepoint by enumerating PSp(4,3) via the 6 generators
  * computes a collection of minimal commutator cycles on W33 using the
    Tx/Ty words and shortest-path substitutions
  * for each of the four A2 choices in the precomputed decomposition, picks
    a simple root pair (\alpha,\beta) and evaluates the cocycle
    S(cycle)=\sum (\alpha-\beta)·root/4 along each cycle
  * repeats with the pulled-back edge->root map under A and records
    delta = s_A - s (mod 3) for every cycle

The result is written to
  artifacts/outer_twist_rootword_cocycle_defect.json

The script is self-contained and deterministic given the two bundle
directories H27_OUTER_TWIST_ACTION_BUNDLE_v01 and
WE6_EVEN_to_PSp43_CONJUGACY_BUNDLE_v01, which may either be present as
zipped archives or unpacked folders in the repository root.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path
from collections import Counter, deque
import networkx as nx
from typing import Tuple, Dict

ROOT = Path(__file__).resolve().parents[1]

# allow either zip or directory locations
def load_json_from_bundle(bundle: Path, name: str):
    if bundle.is_file():
        with zipfile.ZipFile(bundle) as z:
            return json.loads(z.read(name))
    elif bundle.is_dir():
        return json.loads((bundle / name).read_text())
    else:
        raise FileNotFoundError(bundle)

# bundle paths (relative to repo root); allow wildcard suffixes
# (some directories have a trailing " (1)" after extraction).
def find_bundle(pattern: str) -> Path:
    # try exact zip
    p = ROOT / f"{pattern}.zip"
    if p.exists():
        return p
    # try exact dir
    p2 = ROOT / pattern
    if p2.exists():
        return p2
    # try wildcard
    candidates = list(ROOT.glob(pattern + "*") )
    if candidates:
        return candidates[0]
    raise FileNotFoundError(pattern)

OUTER_ZIP = find_bundle("H27_OUTER_TWIST_ACTION_BUNDLE_v01")
CONJ_ZIP  = find_bundle("WE6_EVEN_to_PSp43_CONJUGACY_BUNDLE_v01")

# ---------- Load canonical W33 graph ----------
adj_path = ROOT / "W33_adjacency_matrix.txt"
lines = [l.strip() for l in adj_path.read_text().splitlines() if l.strip()]
adj = {i: [j for j, v in enumerate(line.split()) if v == "1"] for i, line in enumerate(lines)}

G = nx.Graph()
G.add_nodes_from(range(40))
for i in range(40):
    for j in adj[i]:
        if i < j:
            G.add_edge(i, j)

# ---------- Load canonical edge->root map ----------
edge_to_root_und = json.loads((ROOT / "artifacts" / "edge_to_e8_root.json").read_text())
edge_to_root = {}
for k, v in edge_to_root_und.items():
    i, j = [int(x.strip()) for x in k.strip()[1:-1].split(",")]
    r = tuple(int(t) for t in v)
    edge_to_root[(i, j)] = r
    edge_to_root[(j, i)] = tuple(-t for t in r)

# ---------- compute mapping from adjacency labels to edge_to_root labels ----------
G_root = nx.Graph()
G_root.add_nodes_from(range(40))
for (i, j) in edge_to_root.keys():
    if i < j:
        G_root.add_edge(i, j)

# find isomorphism between adjacency and root graphs (they are both W33)
gm2 = nx.algorithms.isomorphism.GraphMatcher(G, G_root)
label_map = next(gm2.isomorphisms_iter())
print('adjacency->root label map sample', {k: label_map[k] for k in range(5)})

# ---------- Load outer twist permutation on cosets and conjugate ----------
perm40 = load_json_from_bundle(OUTER_ZIP, "perm40_and_H27_pg_ids.json")
p_coset = perm40["perm40_points_from_phi_n"]

sig = load_json_from_bundle(CONJ_ZIP, "sigma_we6coset_to_w33line.json")
sigma = sig["sigma_we6coset_to_w33line"]
sigma_inv = sig["sigma_inv_w33line_to_we6coset"]

def conj_perm(p):
    return [sigma[p[sigma_inv[i]]] for i in range(40)]

p_line = conj_perm(p_coset)

# basepoint in coset labeling
base = sigma[0]

# ---------- Build image graph G' ----------
Eprime = set()
for (u, v) in G.edges():
    u2, v2 = p_line[u], p_line[v]
    if u2 > v2:
        u2, v2 = v2, u2
    Eprime.add((u2, v2))

Gp = nx.Graph()
Gp.add_nodes_from(range(40))
Gp.add_edges_from(Eprime)

# ---------- Find deterministic isomorphism q: G'->G fixing base ----------
for n in G.nodes():
    G.nodes[n]["col"] = (1 if n == base else 0, 1 if G.has_edge(n, base) else 0)
    Gp.nodes[n]["col"] = (1 if n == base else 0, 1 if Gp.has_edge(n, base) else 0)

gm = nx.algorithms.isomorphism.GraphMatcher(
    Gp, G, node_match=lambda a, b: a["col"] == b["col"]
)
q = next(gm.isomorphisms_iter())
assert q[base] == base

# effective automorphism on canonical labeling
A = [q[p_line[v]] for v in range(40)]

# ---------- Load PSp(4,3) generators and build Heisenberg subgroup ----------
genobj = load_json_from_bundle(CONJ_ZIP, "psp43_line_generators_6.json")["generators"]
# values are the actual permutations (lists of length 40)
gens = [tuple(v) for v in genobj.values()]

def compose(p, q):
    return tuple(p[i] for i in q)

def inv(p):
    r = [0] * len(p)
    for i, v in enumerate(p):
        r[v] = i
    return tuple(r)

def order(p):
    seen = set()
    o = 1
    for i in range(len(p)):
        if i in seen:
            continue
        cur = i
        L = 0
        while cur not in seen:
            seen.add(cur)
            cur = p[cur]
            L += 1
        if L > 0:
            from math import gcd

            o = o * L // gcd(o, L)
    return o

# enumerate group by BFS
Gset = {tuple(range(40))}
Q = deque([tuple(range(40))])
while Q:
    g = Q.popleft()
    for gen in gens:
        h = compose(gen, g)
        if h not in Gset:
            Gset.add(h)
            Q.append(h)
print("Group size:", len(Gset))

# stabilizer of base
stab = [g for g in Gset if g[base] == base]
print("Stabilizer size:", len(stab))

stab_ord3 = [g for g in stab if order(g) == 3]
print("Order-3 in stabilizer:", len(stab_ord3))

Tx = Ty = Z = None
for i, a in enumerate(stab_ord3):
    for b in stab_ord3[i + 1 :]:
        c = compose(compose(compose(a, b), inv(a)), inv(b))
        if order(c) != 3:
            continue
        # generated subgroup
        H = {tuple(range(40))}
        dq = deque([tuple(range(40))])
        while dq:
            g = dq.popleft()
            for gen in (a, b):
                h = compose(gen, g)
                if h not in H:
                    H.add(h)
                    dq.append(h)
        if len(H) == 27:
            Tx, Ty, Z = a, b, c
            break
    if Tx is not None:
        break

if Tx is None:
    raise RuntimeError("Failed to find Heisenberg subgroup of size 27")

print("Found Tx,Ty,Z with orders:", order(Tx), order(Ty), order(Z))

# ---------- build commutator cycles ----------
def bfs_path(a, b):
    if a == b:
        return [a]
    prev = {a: None}
    dq = deque([a])
    while dq:
        x = dq.popleft()
        for y in adj[x]:
            if y in prev:
                continue
            prev[y] = x
            if y == b:
                path = [b]
                while path[-1] != a:
                    path.append(prev[path[-1]])
                return list(reversed(path))
            dq.append(y)
    return None


def pow_perm(p, k):
    if k % 3 == 0:
        return tuple(range(40))
    if k % 3 == 1:
        return p
    return compose(p, p)


def apply(p, v):
    return p[v]

F3 = [0, 1, 2]
nonzero = [(x, y) for x in F3 for y in F3 if (x, y) != (0, 0)]
pairs = []
for u in nonzero:
    for v in nonzero:
        det = (u[0] * v[1] - u[1] * v[0]) % 3
        if det != 0:
            pairs.append((u, v, det))

# use every vertex as a potential start, then filter trivial walks
reps = list(range(40))

cycles = set()
cycle_list = []
for (ux, uy), (vx, vy), det in pairs:
    Tu = compose(pow_perm(Tx, ux), pow_perm(Ty, uy))
    Tv = compose(pow_perm(Tx, vx), pow_perm(Ty, vy))
    Tu_inv, Tv_inv = inv(Tu), inv(Tv)
    for w0 in reps:
        w1 = apply(Tu, w0)
        w2 = apply(Tv, w1)
        w3 = apply(Tu_inv, w2)
        w4 = apply(Tv_inv, w3)
        # skip degenerate steps
        if w1 == w0 or w2 == w1 or w3 == w2 or w4 == w3:
            continue
        segs = [bfs_path(w0, w1), bfs_path(w1, w2), bfs_path(w2, w3), bfs_path(w3, w4)]
        if any(s is None or len(s) <= 1 for s in segs):
            continue
        cyc = [segs[0][0]]
        for s in segs:
            cyc += s[1:]
        back = bfs_path(w4, w0)
        if back is None or len(back) <= 1:
            continue
        cyc += back[1:]
        # remove any consecutive duplicate vertices
        cleaned = [cyc[0]]
        for v in cyc[1:]:
            if v != cleaned[-1]:
                cleaned.append(v)
        # drop last element if it equals first to avoid wrap-around duplicate
        if len(cleaned) > 1 and cleaned[-1] == cleaned[0]:
            cleaned.pop()
        if len(cleaned) < 3:
            continue
        cyc = cleaned
        # canonicalize (using adjacency labels) for uniqueness
        n = len(cyc)
        rots = [tuple(cyc[i:] + cyc[:i]) for i in range(n)]
        rev = list(reversed(cyc))
        rots += [tuple(rev[i:] + rev[:i]) for i in range(n)]
        can = min(rots)
        if can not in cycles:
            cycles.add(can)
            cycle_list.append(cyc[:])

print("Canonical cycles:", len(cycle_list))
for idx,cyc in enumerate(cycle_list[:5]):
    print('cycle',idx,'len',len(cyc),cyc[:10], '...')
# also detect any consecutive duplicates
badcount=0
for cyc in cycle_list:
    if any(cyc[i]==cyc[(i+1)%len(cyc)] for i in range(len(cyc))):
        badcount+=1
print('cycles with adjacent duplicates', badcount)

# ---------- cocycle evaluation ----------
a2 = json.loads((ROOT / "artifacts" / "a2_4_decomposition.json").read_text())
edge_bij = json.loads((ROOT / "artifacts" / "edge_root_bijection.json").read_text())
root_index_map: Dict[int, Tuple[int, ...]] = {}
for e in edge_bij:
    ridx = int(e["root_index"])
    if ridx not in root_index_map:
        root_index_map[ridx] = tuple(int(x) for x in e["root_coords"])


def dot(u, v):
    return sum(int(a) * int(b) for a, b in zip(u, v))

def ip(u, v):
    return dot(u, v) // 4


def find_simple_pair(a2_indices):
    for i in a2_indices:
        for j in a2_indices:
            if i >= j:
                continue
            if ip(root_index_map[i], root_index_map[j]) == -1:
                return root_index_map[i], root_index_map[j], i, j
    raise RuntimeError("no A2 simple pair")

A_inv = [0] * 40
for i, v in enumerate(A):
    A_inv[v] = i

def get_root_std(a, b):
    # map adjacency vertices to root-label vertices
    ra = label_map[a]
    rb = label_map[b]
    return edge_to_root[(ra, rb)]

def get_root_pullback_A(a, b):
    # first apply adjacency automorphism, then map
    aa = A_inv[a]
    bb = A_inv[b]
    ra = label_map[aa]
    rb = label_map[bb]
    return edge_to_root[(ra, rb)]

def S_mod3_for_cycle(cyc, get_root, alpha, beta):
    S = 0
    for i in range(len(cyc)):
        a = cyc[i]
        b = cyc[(i + 1) % len(cyc)]
        if a == b:
            # degenerate step, no contribution
            continue
        r = get_root(a, b)
        S += (ip(r, alpha) - ip(r, beta))
    # mirror compute_projection: integer division by 3 regardless of remainder
    return (S // 3) % 3

out = {"cycles": [], "stats": {}}
for a2_index in range(4):
    sol = a2["a2_4_solution"][a2_index]
    alpha, beta, ai, bi = find_simple_pair(sol)
    deltas = []
    rows = []
    for cyc in cycle_list:
        # ignore degenerate cycles with repeated adjacent vertices
        if any(cyc[i] == cyc[(i+1) % len(cyc)] for i in range(len(cyc))):
            continue
        s = S_mod3_for_cycle(cyc, get_root_std, alpha, beta)
        sA = S_mod3_for_cycle(cyc, get_root_pullback_A, alpha, beta)
        if s is None or sA is None:
            continue
        d = (sA - s) % 3
        deltas.append(d)
        rows.append({"cycle": ",".join(map(str, cyc)), "s": s, "sA": sA, "delta": d})
    out["cycles"].append({"a2_index": a2_index, "ai": ai, "bi": bi, "rows": rows, "delta_stats": dict(Counter(deltas))})

(out_path := ROOT / "artifacts" / "outer_twist_rootword_cocycle_defect.json").write_text(json.dumps(out, indent=2))
print("Wrote", out_path)
