#!/usr/bin/env python3
"""Find permutation mapping internal W33 vertex labels to edge-to-root labels.

The edge_to_root.json file uses some labeling of 0..39. We'll build two graphs
and run networkx isomorphism to find the mapping.
"""
import json
from pathlib import Path
import networkx as nx

# load internal adjacency
from pathlib import Path as P
import sys
ROOT = P(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from scripts.w33_homology import build_w33
n, verts, adj, edges = build_w33()

G1 = nx.Graph()
G1.add_nodes_from(range(n))
for i,j in edges:
    G1.add_edge(i,j)

# load labeling from edge_to_root
edge_to_root = json.loads((Path('artifacts')/'edge_to_e8_root.json').read_text())
G2 = nx.Graph()
for k in edge_to_root.keys():
    a,b = eval(k)
    G2.add_edge(a,b)
# ensure nodes
G2.add_nodes_from(range(40))

# compute isomorphism, may be multiple; take first
gm = nx.algorithms.isomorphism.GraphMatcher(G1, G2)
for iso in gm.isomorphisms_iter():
    print('found iso')
    # iso maps G1->G2: internal->label
    with open('internal_to_edge_labeling.json','w') as f:
        json.dump({str(k):v for k,v in iso.items()}, f, indent=2)
    break
else:
    print('no isomorphism found')
