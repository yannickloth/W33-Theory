"""
M12_CODEWORD_ORBITS_ANALYSIS.py
================================
Compute orbits of the 729 ternary Golay codewords under the M12 group
constructed from PSL(2,11) + involution, and search for orbits of size 27.
Analyze candidate orbits for Schlafli graph (27-line) incidence.
"""

from collections import defaultdict, deque
from itertools import combinations, product

import numpy as np
from sympy.combinatorics.perm_groups import PermutationGroup
from sympy.combinatorics.permutations import Permutation

# Reuse generator construction from M12_SYMPY_BUILD
mod = 11
# Translation T
T_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 11]
T = Permutation(T_list)
# Inversion S
inv = {0: 11, 11: 0}
for x in range(1, 11):
    y = pow(x, -1, mod)
    inv_x = (-1 * y) % mod
    inv[x] = inv_x
S_list = [inv[i] if i in inv else i for i in range(12)]
S = Permutation(S_list)
# involution p
p_map = list(range(12))
pairs = [(2, 10), (3, 4), (5, 9), (6, 7)]
for a, b in pairs:
    a0 = a - 1
    b0 = b - 1
    p_map[a0] = b0
    p_map[b0] = a0
p = Permutation(p_map)

G = PermutationGroup(T, S, p)
print("M12 built: order", G.order())

# Build codewords
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
codewords = []
for v in product(range(3), repeat=6):
    cw = tuple(np.dot(v, G_matrix) % 3)
    codewords.append(cw)


# apply permutation to codeword
def apply_perm_to_cw(perm, cw):
    images = [perm(i) for i in range(12)]
    return tuple(cw[images[i]] for i in range(12))


# compute all orbits among 729 codewords
seen = set()
orbits = []
for cw in codewords:
    if cw in seen:
        continue
    orbit = set()
    q = deque([cw])
    while q:
        x = q.popleft()
        if x in orbit:
            continue
        orbit.add(x)
        for g in G.generators:
            y = apply_perm_to_cw(g, x)
            if y not in orbit:
                q.append(y)
    for x in orbit:
        seen.add(x)
    orbits.append(orbit)

sizes = sorted([len(o) for o in orbits])
print("Orbit size distribution (sorted):", sizes)

# find orbits of size 27
orbits_27 = [o for o in orbits if len(o) == 27]
print("Number of orbits of size 27:", len(orbits_27))

# For each orbit of size 27, build adjacency graph using Hamming distance 6 (candidate for Schlafli graph)


def hamming_distance(a, b):
    return sum(x != y for x, y in zip(a, b))


for idx, o in enumerate(orbits_27):
    o_list = list(o)
    # build adjacency
    adj = {i: [] for i in range(len(o_list))}
    for i, j in combinations(range(len(o_list)), 2):
        if hamming_distance(o_list[i], o_list[j]) == 6:
            adj[i].append(j)
            adj[j].append(i)
    degrees = sorted([len(adj[i]) for i in adj])
    print(
        f"Orbit {idx+1}: degree sequence min/max = {min(degrees)}/{max(degrees)} (should be 10 for Schlafli)"
    )
    # check triangles count
    triangles = 0
    for i, j, k in combinations(range(len(o_list)), 3):
        if j in adj[i] and k in adj[i] and k in adj[j]:
            triangles += 1
    print(f"Orbit {idx+1}: triangle count = {triangles} (Schlafli has specific counts)")

print("\nDone.")
