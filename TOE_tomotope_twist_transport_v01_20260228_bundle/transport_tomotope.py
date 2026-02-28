#!/usr/bin/env python3
"""Construct conjugator \pi carrying the true tomotope model into the
axis-192 torsor coordinates, fixing r0 and aligning r3 blocks.

Outputs files:
  * pi_mapping.json              (list of 192 integers)
  * transported_r_generators.json (new r0..r3 on axis labels)
  * pi_construction_report.txt   (brief verification notes)
"""

import json, os

# helper utilities

def compose(p, q):
    return tuple(p[i] for i in q)

def inv(p):
    n = len(p)
    out = [0]*n
    for i,a in enumerate(p):
        out[a] = i
    return tuple(out)

# builds the 96 r0-pairs and flag->pair map

def r0_pairs(r0):
    n = len(r0)
    seen = [False]*n
    pairs = []
    flag2pair = [None]*n
    for i in range(n):
        if not seen[i]:
            j = r0[i]
            a,b = sorted((i,j))
            pid = len(pairs)
            pairs.append((a,b))
            flag2pair[a] = flag2pair[b] = pid
            seen[a] = seen[b] = True
    return pairs, flag2pair

# given r3 and pair data, returns undirected matching of pair-ids

def matching_on_pairs(r3, pairs, flag2pair):
    match = {}
    for pid,(a,b) in enumerate(pairs):
        # take representative a
        y = r3[a]
        qid = flag2pair[y]
        match[pid] = qid
    # sanity check
    for k,v in match.items():
        assert match[v] == k and k != v
    edges = set()
    for k,v in match.items():
        if k < v:
            edges.add((k,v))
    return sorted(edges)

# orbit of a flag under <r0,r3>

def block_orbit(r0, r3, seed):
    return sorted({seed, r0[seed], r3[seed], r0[r3[seed]]})

# build the conjugator

def build_pi(r0, r3_tomo, r3_axis):
    n = len(r0)
    pairs, flag2pair = r0_pairs(r0)
    E_t = matching_on_pairs(r3_tomo, pairs, flag2pair)
    E_a = matching_on_pairs(r3_axis, pairs, flag2pair)
    assert len(E_t) == len(E_a) == len(pairs)//2
    # map edges by sorted order
    edge_map = {e: a for e,a in zip(E_t, E_a)}
    pi = [-1]*n

    for (p,q) in E_t:
        P,Q = edge_map[(p,q)]
        seed_t = pairs[p][0]
        block_t = block_orbit(r0, r3_tomo, seed_t)
        seed_a = pairs[P][0]
        block_a = block_orbit(r0, r3_axis, seed_a)
        # compute mapping on this 4-block
        mapping = {}
        for xt in block_t:
            found = False
            for a_bit in (0,1):
                for b_bit in (0,1):
                    u = seed_t
                    if b_bit:
                        u = r3_tomo[u]
                    if a_bit:
                        u = r0[u]
                    if u == xt:
                        xa = seed_a
                        if b_bit:
                            xa = r3_axis[xa]
                        if a_bit:
                            xa = r0[xa]
                        mapping[xt] = xa
                        found = True
                        break
                if found:
                    break
            if not found:
                raise RuntimeError(f"couldn't map flag {xt} in block")
        for xt, xa in mapping.items():
            if pi[xt] != -1 and pi[xt] != xa:
                raise RuntimeError("pi conflict")
            pi[xt] = xa
    if any(v == -1 for v in pi):
        raise RuntimeError("pi not fully assigned")
    return tuple(pi)

# conjugate a generator

def conjugate_generator(pi, g):
    return compose(pi, compose(g, inv(pi)))

# load generators
axis_path = os.path.join("TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle",
                         "TOE_tomotope_flag_model_conjugacy_v01_20260228",
                         "flag_adjacency_r0_r3_permutations.json")
axis_adj = json.load(open(axis_path))
axis_r = [tuple(axis_adj[f"r{i}"]) for i in range(4)]

bundle_path = "TOE_tomotope_true_flag_model_v02_20260228_bundle.zip"
with __import__("zipfile").ZipFile(bundle_path) as zf:
    tomo_adj = json.loads(zf.read("tomotope_r_generators_192.json"))
    tomo_r = [tuple(tomo_adj[f"r{i}"]) for i in range(4)]

# construct pi
r0 = axis_r[0]
pi = build_pi(r0, tomo_r[3], axis_r[3])

# transport
transported = [conjugate_generator(pi, tomo_r[i]) for i in range(4)]

# verify
assert transported[0] == axis_r[0]
assert transported[3] == axis_r[3]

# output
json.dump(list(pi), open("pi_mapping.json","w"))
json.dump({f"r{i}": list(transported[i]) for i in range(4)},
          open("transported_r_generators.json","w"), indent=2)
with open("pi_construction_report.txt","w") as f:
    f.write("constructed pi\n")
    f.write(f"r0 fixed, r3 matched\n")
    f.write("transported r1,r2 stored in transported_r_generators.json\n")

print("pi and transported generators written")
