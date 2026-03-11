#!/usr/bin/env python3
"""Holonomy of the Z2 flip field on SRG cycles derived from the 36-vertex graph.

This script uses the edgepair transport data computed previously to assign a
flip value to each SRG edge by finding a generator-word connecting the two
corresponding blocks.  A cycle in the SRG (list of vertices) then has holonomy
= XOR of flips on the edges it traverses.

Outputs:
  - artifacts/srg_cycle_holonomy.csv : one row per basis cycle with parity
  - artifacts/srg_flip_edge.csv : flip value for each SRG edge (0/1)
  - prints a summary including number of odd cycles and minimal length.

"""

from __future__ import annotations
import json, csv
from pathlib import Path
from collections import deque
from typing import List, Tuple, Dict
import networkx as nx
import zipfile
import numpy as np
from itertools import combinations

ROOT = Path(__file__).resolve().parents[1]

# load bundles same as previous scripts
EDGEPAIR_BUNDLE = ROOT / "TOE_E6pair_SRG_triangle_decomp_v01_20260227_bundle.zip"
TRANSPORT_BUNDLE = ROOT / "TOE_holonomy_Z2_flatZ3_v01_20260227_bundle" / "TOE_holonomy_Z2_flatZ3_v01_20260227"


def read_from_bundle(bundle: Path, name: str) -> bytes:
    import zipfile
    if bundle.is_file():
        with zipfile.ZipFile(bundle) as z:
            entry = [x for x in z.namelist() if x.endswith(name)]
            if not entry:
                raise KeyError(name)
            return z.read(entry[0])
    else:
        return (bundle / name).read_bytes()


def load_json(bundle: Path, name: str):
    return json.loads(read_from_bundle(bundle, name))


def load_transport():
    # returns pair_perm, pair_flip (120x10)
    df = None
    if (TRANSPORT_BUNDLE / "edgepair_transport_D6.csv").exists():
        with open(TRANSPORT_BUNDLE / "edgepair_transport_D6.csv") as f:
            df = list(csv.DictReader(f))
    else:
        data = read_from_bundle(TRANSPORT_BUNDLE, "edgepair_transport_D6.csv")
        df = list(csv.DictReader(data.decode().splitlines()))
    # we want pair_perm[g][pid] and pair_flip[g][pid]
    perm = [[0]*120 for _ in range(10)]
    flip = [[0]*120 for _ in range(10)]
    for row in df:
        pid = int(row['edgepair_id']); g = int(row['gen'])
        perm[g][pid] = int(row['edgepair_image'])
        flip[g][pid] = int(row['flip_Z2'])
    return perm, flip


def closure_and_rep(gens: List[List[int]]) -> Tuple[List[List[int]], List[List[int]]]:
    # return full group closure plus representative words as lists of generators
    n=len(gens[0])
    seen={tuple(range(n)): []}
    queue=deque([list(range(n))])
    all_perms=[list(range(n))]
    while queue:
        g=queue.popleft()
        w=seen[tuple(g)]
        for gi,perm in enumerate(gens):
            h=[g[perm[i]] for i in range(n)]
            t=tuple(h)
            if t not in seen:
                seen[t]=w+[gi]
                queue.append(h)
                all_perms.append(h)
    reps=[seen[tuple(p)] for p in all_perms]
    return all_perms, reps


def find_flip_for_adj(u:int, v:int, edge_to_pair:Dict[int,int], pair_perm:List[List[int]], pair_flip:List[List[int]])->int:
    # find a word sending block u -> block v and accumulate flip parity
    # BFS on Cayley graph of pairs
    n=len(pair_perm[0])
    start=u; target=v
    seen={start: 0}
    queue=deque([(start,0)])
    while queue:
        current,par=queue.popleft()
        if current==target:
            return par
        for g in range(len(pair_perm)):
            nxt=pair_perm[g][current]
            newpar = par ^ pair_flip[current][g]
            if nxt not in seen:
                seen[nxt]=1
                queue.append((nxt,newpar))
    raise RuntimeError("no path in Cayley graph")


def main():
    # load SRG data and triangle-blocks
    with zipfile.ZipFile(EDGEPAIR_BUNDLE) as zf:
        srg_adj = np.load(zf.open("TOE_E6pair_SRG_triangle_decomp_v01_20260227/e6pair_srg_adj_36x36.npy"))
        triangle_data = json.loads(zf.read("TOE_E6pair_SRG_triangle_decomp_v01_20260227/w33_line_to_e6pair_triangles.json"))
    # build SRG graph
    n = srg_adj.shape[0]
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i+1,n):
            if srg_adj[i,j] == 1:
                G.add_edge(i,j)
    cycles = nx.cycle_basis(G)

    # load edgepair transport and precompute orientation per block via BFS
    pair_perm, pair_flip = load_transport()
    # BFS from block 0 to assign orientation
    orientation = {0: 0}
    queue = deque([0])
    while queue:
        b = queue.popleft()
        for g in range(len(pair_perm)):
            b2 = pair_perm[g][b]
            if b2 not in orientation:
                orientation[b2] = orientation[b] ^ pair_flip[g][b]
                queue.append(b2)

    # triangle_data is 40 lines each containing three triangle_blocks
    # flatten into list of 120 block triples
    blocks = []
    for entry in triangle_data:
        for tri in entry['triangle_blocks']:
            blocks.append(tri)
    assert len(blocks)==120
    # mapping SRG edge -> block id
    edge2block = {}
    for block_id, verts in enumerate(blocks):
        for a,b in combinations(verts,2):
            edge2block[(a,b) if a<b else (b,a)] = block_id

    # assign flip to each SRG edge equal to orientation of corresponding block
    flip_edge = {}
    for u,v in G.edges():
        bid = edge2block[(u,v) if u<v else (v,u)]
        flip_edge[(u,v)] = orientation[bid]

    # compute cycle parities
    cycle_parities = []
    for cyc in cycles:
        par = 0
        for i in range(len(cyc)):
            a = cyc[i]; b = cyc[(i+1)%len(cyc)]
            key = (a,b) if a<b else (b,a)
            par ^= flip_edge[key]
        cycle_parities.append((cyc, par))

    # output results
    with open(ROOT/"artifacts"/"srg_flip_edge.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["u","v","flip"])
        for (u,v),fl in flip_edge.items():
            w.writerow([u,v,fl])
    with open(ROOT/"artifacts"/"srg_cycle_holonomy.csv","w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cycle","parity"])
        for cyc,par in cycle_parities:
            w.writerow(["-".join(str(x) for x in cyc), par])

    odd = [cyc for cyc,par in cycle_parities if par]
    print("SRG cycles total", len(cycle_parities), "odd", len(odd))
    if odd:
        print("smallest odd length", min(len(c) for c in odd))

if __name__=="__main__":
    main()
