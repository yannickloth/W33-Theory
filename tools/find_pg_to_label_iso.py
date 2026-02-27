#!/usr/bin/env python3
"""Find permutation psi mapping PG point IDs (0..39) to edge-label IDs.

PG adjacency is given by the symplectic form J on PG33 points. We compute
the graph and then find an isomorphism to the adjacency of edge_to_root
labeling. The resulting psi allows us to conjugate p_coset into the same
label space used by the root bijection.
"""
import json
from pathlib import Path
from itertools import product

import networkx as nx
import numpy as np

# load PG33 points from bundle
pts = json.loads((Path('PG33_OUTER_TWIST_GEOMETRY_BUNDLE_v01') / 'PG33_points.json').read_text())
# symplectic form J
J = np.array([[0,0,0,1],[0,0,1,0],[0,2,0,0],[2,0,0,0]], dtype=int)

# build PG graph
Gpg = nx.Graph()
Gpg.add_nodes_from(range(40))
for i in range(40):
    for j in range(i+1,40):
        vi = np.array(pts[i],dtype=int)
        vj = np.array(pts[j],dtype=int)
        if int((vi @ J @ vj) % 3) == 0:
            Gpg.add_edge(i,j)

# build label graph from edge_to_root
edge_to_root = json.loads((Path('artifacts')/'edge_to_e8_root.json').read_text())
Glabel = nx.Graph()
Glabel.add_nodes_from(range(40))
for k in edge_to_root.keys():
    a,b = eval(k)
    Glabel.add_edge(a,b)

# find isomorphism
print('finding iso between PG and label graphs...')
gm = nx.algorithms.isomorphism.GraphMatcher(Gpg, Glabel)
for iso in gm.isomorphisms_iter():
    print('found iso')
    Path('pg_to_edge_labeling.json').write_text(json.dumps({str(k):v for k,v in iso.items()}, indent=2))
    break
else:
    print('no iso found')
