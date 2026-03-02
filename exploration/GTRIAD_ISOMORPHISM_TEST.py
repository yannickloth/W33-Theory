"""
GTRIAD_ISOMORPHISM_TEST.py

Use networkx's isomorphism routines to find a mapping between the E6 triad graph
(36 triads -> adjacency by appearing together in a triad) and the coset triad graph.
"""

import json
from itertools import combinations

import networkx as nx

# load e6 triads
with open(
    "artifacts/e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    e6_heis = json.load(f)

# extract triads
e6_triads = []
for item in e6_heis["affine_u_lines"]:
    for tri in item["triads"]:
        e6_triads.append(tuple(sorted(tri)))

from itertools import product

# coset triads from previous scripts
# replicate quick
import numpy as np

G_matrix = np.array(
    [
        [1, 0, 0, 0, 0, 0, 1, 1, 2, 2, 1, 2],
        [0, 1, 0, 0, 0, 0, 1, 2, 1, 2, 2, 1],
        [0, 0, 1, 0, 0, 0, 2, 1, 1, 1, 2, 2],
        [0, 0, 0, 1, 0, 0, 2, 2, 1, 1, 1, 2],
        [0, 0, 0, 0, 1, 0, 1, 2, 2, 1, 1, 2],
        [0, 0, 0, 0, 0, 1, 2, 1, 2, 2, 1, 1],
    ]
)
M = np.array([[2, 2, 1, 2, 1, 2], [0, 2, 2, 0, 2, 1]], dtype=int)
messages = list(product(range(3), repeat=6))
kernel = [m for m in messages if (M @ np.array(m) % 3 == 0).all()]
W_basis = [(0, 0, 0, 0, 1, 1), (0, 0, 1, 0, 0, 1), (0, 1, 0, 1, 0, 1)]
W = set()
for a, b, c in product(range(3), repeat=3):
    w = tuple(
        (a * W_basis[0][i] + b * W_basis[1][i] + c * W_basis[2][i]) % 3
        for i in range(6)
    )
    W.add(w)

used = set()
cosets = []
for m in messages:
    if m in used:
        continue
    cosets.append(m)
    for w in W:
        used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))

codewords_27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]


def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))


coset_triads = []
for i, j, k in combinations(range(27), 3):
    if (
        hamming(codewords_27[i], codewords_27[j]) == 6
        and hamming(codewords_27[i], codewords_27[k]) == 6
        and hamming(codewords_27[j], codewords_27[k]) == 6
    ):
        coset_triads.append(tuple(sorted((i, j, k))))

# Build graphs: nodes 0..26, edge between nodes that occur in same triad
G_e6 = nx.Graph()
G_e6.add_nodes_from(range(27))
for a, b, c in e6_triads:
    for u, v in combinations((a, b, c), 2):
        G_e6.add_edge(u, v)

G_coset = nx.Graph()
G_coset.add_nodes_from(range(27))
for a, b, c in coset_triads:
    for u, v in combinations((a, b, c), 2):
        G_coset.add_edge(u, v)

# compute basic invariants
print(
    "E6 degrees range:",
    min(dict(G_e6.degree()).values()),
    max(dict(G_e6.degree()).values()),
)
print(
    "COS degrees range:",
    min(dict(G_coset.degree()).values()),
    max(dict(G_coset.degree()).values()),
)

# Try VF2 isomorphism
GM = nx.algorithms.isomorphism.GraphMatcher(G_e6, G_coset)
if GM.is_isomorphic():
    print("Graphs are isomorphic! Extracting mapping...")
    mapping = list(GM.isomorphisms_iter())[0]
    # mapping is a dict mapping nodes in G_e6 to nodes in G_coset
    mapped_triads = [
        tuple(sorted((mapping[a], mapping[b], mapping[c]))) for (a, b, c) in e6_triads
    ]
    matched = set(mapped_triads) & set(coset_triads)
    print("Mapped triads that are in coset triads:", len(matched), "/", len(e6_triads))
    print("Sample mapping (first 10):", list(mapping.items())[:10])
else:
    print("Graphs are NOT isomorphic")

print("Done")
