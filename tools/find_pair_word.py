#!/usr/bin/env python3
"""Find a word in the sp43_edgepair generators giving the duad-edge generators.

Usage: run from workspace root.  It reads
  - artifacts/sp43_edgepair_generators.json  (120 pairs + 10 generators)
  - TOE_duad_algebra.../psp43_generators_on_points_40.json (2 point gens)
and tries to express each duad-edge generator (converted to pair action) as a
short word in the pair generators.  Output is a list of word indices.

This will help tie the two generating sets together, allowing us to rebuild an
explicit equivariant map from 240 edges to 240 roots by piggybacking on the
existing SP43→WE6 mapping in the bundle.
"""

from __future__ import annotations
import json, pathlib, zipfile
from collections import deque
from typing import List, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[1]


def read_json(bundle: pathlib.Path, name: str):
    if bundle.is_file():
        with zipfile.ZipFile(bundle) as z:
            return json.loads(z.read(name))
    else:
        return json.loads((bundle / name).read_text())


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


def perm_apply(perm: List[int], arr: List[int]) -> List[int]:
    return [arr[perm[i]] for i in range(len(arr))]


def compose(p: List[int], q: List[int]) -> List[int]:
    # p after q
    return [p[q[i]] for i in range(len(p))]


def invert(p: List[int]) -> List[int]:
    inv = [0]*len(p)
    for i,v in enumerate(p):
        inv[v]=i
    return inv


def find_word(target: List[int], gens: List[List[int]], maxlen: int=8):
    n = len(gens[0])
    # BFS on words in generators to match target
    seen = {tuple(range(n)): []}
    queue = deque([(list(range(n)), [])])
    while queue:
        perm, word = queue.popleft()
        if perm == target:
            return word
        if len(word) >= maxlen:
            continue
        for i,g in enumerate(gens):
            new = compose(g, perm)
            key = tuple(new)
            if key not in seen:
                seen[key] = word + [i]
                queue.append((new, word+[i]))
    return None


def main():
    # load duad bundle
    duad_bundle = ROOT / "TOE_duad_algebra_v06_20260227_bundle" / "TOE_duad_algebra_v05_20260227"
    lines = read_json(duad_bundle, "W33_lines_40.json")["lines"]
    pgpts = read_json(duad_bundle, "psp43_generators_on_points_40.json")["generators"]
    pgpts = [[int(x) for x in perm] for perm in pgpts]
    edges = build_edges_from_lines(lines)
    edge_index = {e:i for i,e in enumerate(edges)}

    # compute duad-edge generators (on 240 edges)
    def pt_to_edge(pg):
        perm = []
        for a,b in edges:
            a2=pg[a]; b2=pg[b]
            if a2<b2:
                perm.append(edge_index[(a2,b2)])
            else:
                perm.append(edge_index[(b2,a2)])
        return perm
    duad_edge_gens = [pt_to_edge(pg) for pg in pgpts]

    # load edgepair data
    ep = json.loads((ROOT/"artifacts/sp43_edgepair_generators.json").read_text())
    pairs = ep['pairs']
    pair_gens = ep['pair_generators']

    # build edge->pair index map
    edge_to_pair = {}
    for i,p in enumerate(pairs):
        for e in p:
            edge = tuple(sorted(e))
            edge_to_pair[edge] = i
    assert len(edge_to_pair)==240

    # convert duad_edge_gens to action on 120 pair indices (ignore orientation)
    duad_pair_gens = []
    for g in duad_edge_gens:
        perm = list(range(120))
        for ei in range(240):
            pi = edge_to_pair[tuple(sorted(edges[ei]))]
            ei2 = g[ei]
            pj = edge_to_pair[tuple(sorted(edges[ei2]))]
            perm[pi] = pj
        duad_pair_gens.append(perm)

    # now attempt to express each duad_pair_gen as word in pair_gens
    print("searching for words for duad pair generators (colored by order)...")
    for idx, target in enumerate(duad_pair_gens):
        from math import gcd
        def ord_(p):
            n=len(p); vis=[False]*n; o=1
            for i in range(n):
                if not vis[i]:
                    j=i; cyc=0
                    while not vis[j]:
                        vis[j]=True; cyc+=1; j=p[j]
                    o=(o*cyc)//gcd(o,cyc)
            return o
        print(f"duad gen {idx} order", ord_(target))
        word = find_word(target, pair_gens, maxlen=10)
        if word is None:
            print("  no short word found (len<=10)")
        else:
            print("  word in pair gens:", word)
            # also verify by composing
            comp = list(range(120))
            for i in word:
                comp = compose(pair_gens[i], comp)
            assert comp == target
    print("done")

if __name__=="__main__":
    main()
