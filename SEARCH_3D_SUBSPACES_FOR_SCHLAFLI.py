"""
SEARCH_3D_SUBSPACES_FOR_SCHLAFLI.py

Enumerate all 3-dimensional subspaces W of ker(M) (ker of grading M) and for each:
 - Form coset representatives of F3^6 / W (27 cosets)
 - Map representatives to codewords via G
 - Compute adjacency graph using Hamming distance==6
 - Check if adjacency graph is srg(27,10,1,5) or whether there are 45 tritangent triples

Report any W that matches the Schlafli parameters or yields 45 tritangent triples.
"""

from itertools import combinations, product

import numpy as np

# Generator matrix
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

# grading matrix M
M = np.array([[2, 2, 1, 2, 1, 2], [0, 2, 2, 0, 2, 1]], dtype=int)

messages = list(product(range(3), repeat=6))


def grade_msg(m):
    return tuple((M @ np.array(m) % 3).tolist())


# find kernel of M
kernel = [m for m in messages if (M @ np.array(m) % 3 == 0).all()]
print("Kernel size:", len(kernel))


# function to get span of basis vectors (list of tuples)
def span(basis):
    S = set()
    for coeffs in product(range(3), repeat=len(basis)):
        v = tuple(
            sum((coeffs[i] * basis[i][j]) for i in range(len(basis))) % 3
            for j in range(6)
        )
        S.add(v)
    return S


# generate all 3-dim subspaces of ker by enumerating candidate bases and dedup
subspaces = set()
subspace_list = []
for a, b, c in combinations(kernel, 3):
    # check linear independence
    # quick independence test: see if a is in span(b,c) etc
    # compute span of [a,b,c]
    sp = span([a, b, c])
    if len(sp) == 27:
        key = tuple(sorted(sp))
        if key not in subspaces:
            subspaces.add(key)
            subspace_list.append(sp)

print(f"Found {len(subspace_list)} distinct 3-dim subspaces (expected 40)")

# helper funcs


def message_to_codeword(m):
    v = np.array(m)
    cw = tuple((v @ G_matrix % 3).tolist())
    return cw


def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))


matching_subspaces = []

for idx, W in enumerate(subspace_list):
    # build coset reps
    used = set()
    cosets = []
    for m in messages:
        if m in used:
            continue
        cosets.append(m)
        for w in W:
            mw = tuple((m[i] + w[i]) % 3 for i in range(6))
            used.add(mw)
    if len(cosets) != 27:
        print("Skipping W with incorrect coset count", len(cosets))
        continue

    codewords_27 = [message_to_codeword(m) for m in cosets]
    # adjacency
    adj = {i: set() for i in range(27)}
    for i, j in combinations(range(27), 2):
        if hamming(codewords_27[i], codewords_27[j]) == 6:
            adj[i].add(j)
            adj[j].add(i)
    degrees = [len(adj[i]) for i in range(27)]
    is_regular_10 = all(d == 10 for d in degrees)

    adj_common = []
    nonadj_common = []
    for i, j in combinations(range(27), 2):
        common = len(adj[i].intersection(adj[j]))
        if j in adj[i]:
            adj_common.append(common)
        else:
            nonadj_common.append(common)

    # compute tritangent-style triples
    triples = []
    for i, j, k in combinations(range(27), 3):
        if (
            hamming(codewords_27[i], codewords_27[j]) == 6
            and hamming(codewords_27[i], codewords_27[k]) == 6
            and hamming(codewords_27[j], codewords_27[k]) == 6
        ):
            triples.append((i, j, k))
    # check conditions
    if (
        is_regular_10
        and min(adj_common) == 1
        and max(adj_common) == 1
        and min(nonadj_common) == 5
        and max(nonadj_common) == 5
    ):
        matching_subspaces.append((idx, "srg"))
    elif len(triples) == 45:
        matching_subspaces.append((idx, "45triples"))

    # print some stats occasionally
    if idx % 5 == 0:
        print(
            f"Checked W idx {idx}: degs={sorted(degrees)[:3]}... triples={len(triples)}"
        )

print("\nSearch complete. Matches found:")
print(matching_subspaces)

# If none found, print highest triple counts
if not matching_subspaces:
    best = []
    for idx, W in enumerate(subspace_list):
        used = set()
        cosets = []
        for m in messages:
            if m in used:
                continue
            cosets.append(m)
            for w in W:
                used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
        codewords_27 = [message_to_codeword(m) for m in cosets]
        triples = 0
        for i, j, k in combinations(range(27), 3):
            if (
                hamming(codewords_27[i], codewords_27[j]) == 6
                and hamming(codewords_27[i], codewords_27[k]) == 6
                and hamming(codewords_27[j], codewords_27[k]) == 6
            ):
                triples += 1
        best.append((triples, idx))
    best_sorted = sorted(best, reverse=True)
    print("Top 10 subspaces by triple count:")
    for t, idx in best_sorted[:10]:
        print(idx, t)

print("\nDone.")
