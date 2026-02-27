#!/usr/bin/env python3
"""Construct an explicit equivariant map from W33 edges to oriented root-pair triples.

Usage: run from workspace root. Outputs JSON/CSV in artifacts.

The map is built as follows:
  - load duad bundle and compute the 240-edge permutation action of PSp(4,3).
  - load WE6 root permutation generators from the fixed bundle.
  - perform simultaneous closure of both actions to enumerate the group G (size 25920).
  - for each edge index e, record a group element g_e sending base edge 0 -> e.
  - apply the corresponding root permutation to a chosen base triple of antipodal pairs
    (six roots) and canonicalize the triple under even pair-permutations.

The resulting mapping is saved as
  artifacts/edge_to_rootpair_triple.json and .csv

"""

from __future__ import annotations
import json
from pathlib import Path
from collections import deque
from typing import List, Tuple, Dict
import math

ROOT = Path(__file__).resolve().parents[1]

# reuse utility functions from duad_we6_conjugacy where appropriate

def read_from_bundle(bundle: Path, name: str) -> bytes:
    import zipfile
    if bundle.is_file():
        with zipfile.ZipFile(bundle) as z:
            zlist = z.namelist()
            if name in zlist:
                entry = name
            else:
                cand = [x for x in zlist if x.endswith('/' + name)]
                if cand:
                    entry = cand[0]
                else:
                    raise KeyError(f"{name} not in {bundle}")
            return z.read(entry)
    else:
        return (bundle / name).read_bytes()


def load_json(bundle: Path, name: str):
    return json.loads(read_from_bundle(bundle, name))


def closure_pair(gens1: List[List[int]], gens2: List[List[int]]) -> List[Tuple[List[int],List[int]]]:
    # BFS closure of pairs of permutations, keeping them in sync
    n1 = len(gens1[0])
    n2 = len(gens2[0])
    id1 = list(range(n1))
    id2 = list(range(n2))
    seen = {(tuple(id1), tuple(id2)): True}
    queue = deque([(id1, id2)])
    all_pairs = [(id1.copy(), id2.copy())]
    while queue:
        p1,p2 = queue.popleft()
        for h1,h2 in zip(gens1, gens2):
            q1 = [p1[h1[i]] for i in range(n1)]
            q2 = [p2[h2[i]] for i in range(n2)]
            key = (tuple(q1), tuple(q2))
            if key not in seen:
                seen[key] = True
                queue.append((q1, q2))
                all_pairs.append((q1.copy(), q2.copy()))
    return all_pairs


def build_edges_from_lines(lines: List[List[int]]) -> List[Tuple[int,int]]:
    edges = set()
    for L in lines:
        for i in range(len(L)):
            for j in range(i+1, len(L)):
                a,b = L[i], L[j]
                edges.add((a,b) if a<b else (b,a))
    edges = sorted(edges)
    assert len(edges)==240
    return edges


def point_perms_to_edge_perms(point_gens: List[List[int]], edges: List[Tuple[int,int]]) -> List[List[int]]:
    edge_index = {e:i for i,e in enumerate(edges)}
    result=[]
    for pg in point_gens:
        perm=[]
        for a,b in edges:
            a2=pg[a]; b2=pg[b]
            if a2<b2:
                perm.append(edge_index[(a2,b2)])
            else:
                perm.append(edge_index[(b2,a2)])
        result.append(perm)
    return result


def canonicalize_triple(triple: List[Tuple[int,int]]) -> List[Tuple[int,int]]:
    # sort each pair internally then sort the list lexicographically; if the
    # permutation applied to the original paired list to reach sorted order is
    # odd, swap the first two pairs to enforce even parity.
    orig = [tuple(sorted(p)) for p in triple]
    sorted_pairs = sorted(orig)
    # determine parity of permutation from orig->sorted
    perm = [sorted_pairs.index(o) for o in orig]
    # compute parity
    seen = [False]*3
    parity = 0
    for i in range(3):
        if not seen[i]:
            j=i
            cycle_len=0
            while not seen[j]:
                seen[j]=True
                j=perm[j]
                cycle_len+=1
            parity ^= (cycle_len-1)
    if parity%2==1:
        # swap first two
        sorted_pairs[0], sorted_pairs[1] = sorted_pairs[1], sorted_pairs[0]
    return sorted_pairs


def main():
    bundle = ROOT / "TOE_duad_algebra_v06_20260227_bundle.zip"
    if not bundle.exists():
        bundle = ROOT / "TOE_duad_algebra_v06_20260227_bundle"
    # adjust for subdir
    sub = bundle / "TOE_duad_algebra_v05_20260227"
    if sub.exists():
        bundle = sub

    lines = load_json(bundle, "W33_lines_40.json")["lines"]
    pgpts = load_json(bundle, "psp43_generators_on_points_40.json")
    if isinstance(pgpts, dict) and "generators" in pgpts:
        pgpt_gens = pgpts["generators"]
    else:
        pgpt_gens = pgpts
    pgpt_gens = [[int(x) for x in perm] for perm in pgpt_gens]
    edges = build_edges_from_lines(lines)
    duad_edge_gens = point_perms_to_edge_perms(pgpt_gens, edges)

    root_gens = load_json(ROOT / "SP43_TO_WE6_TRUE_FIXED_BUNDLE_v01_2026-02-25", "sp43_root_perms_fixed.json")
    root_gens = [[int(x) for x in perm] for perm in root_gens]

    # We only have two duad edge generators; the root side has more generators.
    # To build an equivariant map we need an isomorphism sending the duad
    # generators to appropriate elements of the root group.  Each duad generator
    # has order 9 and their product has order 6, so we search among the root
    # group elements for a matching pair.

    # first compute full closure of the root group (should be size 25920)
    print("building closure of root generators")
    nroot = len(root_gens[0])
    seen_root = {tuple(range(nroot)): True}
    queue = deque([list(range(nroot))])
    all_root = [list(range(nroot))]
    while queue:
        g = queue.popleft()
        for h in root_gens:
            q = [g[h[i]] for i in range(nroot)]
            t = tuple(q)
            if t not in seen_root:
                seen_root[t] = True
                queue.append(q)
                all_root.append(q)
    print("root closure size", len(all_root))
    # helper function for order
    def order(perm: List[int]) -> int:
        m = len(perm)
        vis = [False]*m
        l = 1
        for i in range(m):
            if not vis[i]:
                j=i; c=0
                while not vis[j]:
                    vis[j]=True
                    j = perm[j]
                    c+=1
                if c:
                    l = math.lcm(l, c)
        return l
    # find root elements of order 9
    order9 = [p for p in all_root if order(p)==9]
    print("root elements of order9", len(order9))

    # product order for duad generators
    g1,g2 = duad_edge_gens
    def compose(a,b):
        return [a[b[i]] for i in range(len(a))]
    prod12 = compose(g1,g2)
    prod21 = compose(g2,g1)
    target_prod_order = order(prod12)
    print("duad product order", target_prod_order)

    # attempt random pairings until we find a consistent homomorphism
    import random
    random.shuffle(order9)
    found_mapping = None
    maxtries = 5000
    for idx in range(min(maxtries, len(order9)**2)):
        r1 = random.choice(order9)
        r2 = random.choice(order9)
        if order(compose(r1,r2)) != target_prod_order or order(compose(r2,r1)) != target_prod_order:
            continue
        # try to build mapping by BFS
        mapping = {}
        seen = {tuple(range(len(g1))): tuple(range(nroot))}
        q = deque([(list(range(len(g1))), list(range(nroot)))])
        gens_map = {0: r1, 1: r2}
        ok = True
        while q and ok:
            pe, pr = q.popleft()
            for gi, gen in enumerate((g1,g2)):
                qe = [pe[gen[i]] for i in range(len(pe))]
                rr = gens_map[gi]
                qr = [pr[rr[i]] for i in range(nroot)]
                tqe = tuple(qe)
                if tqe in seen:
                    if seen[tqe] != tuple(qr):
                        ok = False
                        break
                else:
                    seen[tqe] = tuple(qr)
                    q.append((qe, qr))
        if ok:
            found_mapping = seen
            print("found candidate mapping after", idx, "tries")
            break
    if found_mapping is None:
        raise RuntimeError("failed to find isomorphism between generators")

    # now build edge->root_perm from found_mapping
    edge_to_perm: Dict[int, List[int]] = {}
    for pe_tuple, pr_tuple in found_mapping.items():
        pe = list(pe_tuple)
        pr = list(pr_tuple)
        eimg = pe[0]
        if eimg not in edge_to_perm:
            edge_to_perm[eimg] = pr.copy()
        if len(edge_to_perm) == 240:
            break
    assert len(edge_to_perm) == 240, "did not cover all edges"

    # base triple of antipodal pairs in root indices
    base_pairs = [(46,166),(91,211),(93,213)]
    mapping = {}
    for e in range(240):
        g = edge_to_perm[e]
        image_pairs = []
        for (u,v) in base_pairs:
            u2 = g[u]
            v2 = g[v]
            image_pairs.append((u2,v2))
        mapping[e] = canonicalize_triple(image_pairs)

    outjson = ROOT / "artifacts" / "edge_to_rootpair_triple.json"
    outcsv = ROOT / "artifacts" / "edge_to_rootpair_triple.csv"
    outjson.write_text(json.dumps(mapping, indent=2))
    with open(outcsv, "w") as f:
        f.write("edge,rootpair1,rootpair2,rootpair3\n")
        for e,pairs in mapping.items():
            f.write(f"{e},{pairs[0]},{pairs[1]},{pairs[2]}\n")
    print("wrote", outjson, outcsv)

if __name__=="__main__":
    main()
