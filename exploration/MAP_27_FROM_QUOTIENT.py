"""
MAP_27_FROM_QUOTIENT.py

Build the 27-element quotient F_3^6 / W discovered in GOLAY_27_REPRESENTATION.py,
map each coset representative to a codeword, and test if the induced adjacency
(graph with edges where Hamming distance == 6) matches the Schlafli graph srg(27,10,1,5)
and whether the number of tritangent triples equals 45.
"""

from itertools import combinations, product

import numpy as np

# Generator matrix (same as in repo)
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

messages = list(product(range(3), repeat=6))

# grading matrix M
M = np.array([[2, 2, 1, 2, 1, 2], [0, 2, 2, 0, 2, 1]], dtype=int)


def grade_msg(m):
    return tuple((M @ np.array(m) % 3).tolist())


# find kernel of M (should have 81 elements)
kernel = [m for m in messages if (M @ np.array(m) % 3 == 0).all()]
print("Kernel size:", len(kernel))

# find a 3-dim subspace W of ker(M) - simple choice from GOLAY_27_REPRESENTATION: use first 3 basis vectors found there
W_basis = [(0, 0, 0, 0, 1, 1), (0, 0, 1, 0, 0, 1), (0, 1, 0, 1, 0, 1)]
# Generate W
W = set()
for a, b, c in product(range(3), repeat=3):
    w = tuple(
        (a * W_basis[0][i] + b * W_basis[1][i] + c * W_basis[2][i]) % 3
        for i in range(6)
    )
    W.add(w)
print("|W| =", len(W))

# build coset representatives
used = set()
cosets = []
for m in messages:
    if m in used:
        continue
    cosets.append(m)
    for w in W:
        mw = tuple((m[i] + w[i]) % 3 for i in range(6))
        used.add(mw)
print("Number of cosets (should be 27):", len(cosets))


# map cosets to codewords via cw = m*G
def message_to_codeword(m):
    v = np.array(m)
    cw = tuple((v @ G_matrix % 3).tolist())
    return cw


codewords_27 = [message_to_codeword(m) for m in cosets]


# adjacency via Hamming distance == 6
def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))


adj = {i: set() for i in range(27)}
for i, j in combinations(range(27), 2):
    if hamming(codewords_27[i], codewords_27[j]) == 6:
        adj[i].add(j)
        adj[j].add(i)

degrees = [len(adj[i]) for i in range(27)]
print("Degrees:", sorted(degrees))
print("Min degree, Max degree:", min(degrees), max(degrees))

# check if regular of degree 10
is_regular_10 = all(d == 10 for d in degrees)
print("Is regular degree 10?", is_regular_10)

# compute common neighbors counts for adjacent and non-adjacent pairs
adj_common = []
nonadj_common = []
for i, j in combinations(range(27), 2):
    common = len(adj[i].intersection(adj[j]))
    if j in adj[i]:
        adj_common.append(common)
    else:
        nonadj_common.append(common)

print(
    "Adjacent pair common neighbors stats: min/max =",
    min(adj_common),
    "/",
    max(adj_common),
)
print(
    "Non-adjacent pair common neighbors stats: min/max =",
    min(nonadj_common),
    "/",
    max(nonadj_common),
)

# check Schlafli parameters (srg(27,10,1,5))
is_srg = (
    is_regular_10
    and min(adj_common) == 1
    and max(adj_common) == 1
    and min(nonadj_common) == 5
    and max(nonadj_common) == 5
)
print("Is Schlafli srg(27,10,1,5)?", is_srg)

# Count tritangent triples: triples where pairwise hamming distance == 6
triples = []
for i, j, k in combinations(range(27), 3):
    if (
        hamming(codewords_27[i], codewords_27[j]) == 6
        and hamming(codewords_27[i], codewords_27[k]) == 6
        and hamming(codewords_27[j], codewords_27[k]) == 6
    ):
        triples.append((i, j, k))

print("Number of tritangent-style triples (pairwise hamming=6):", len(triples))

# Print sample triples as codewords
for t in triples[:10]:
    print([codewords_27[i] for i in t])

# Compare with expected 45 tritangent planes
print("Expected number of tritangent planes: 45")

print("\nDone.")
