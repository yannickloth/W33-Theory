"""
M12_SYMPY_BUILD.py
===================
Build Mathieu group M12 using PSL(2,11) generators and an involution, compute order,
and act on ternary Golay coordinates and the 27 representatives.
"""

from sympy.combinatorics.perm_groups import PermutationGroup
from sympy.combinatorics.permutations import Permutation

# Build permutations on 12 points labeled 0..11 (0..10 = field elements 0..10, 11 = infinity)

# Translation T: x -> x+1 mod 11, infinity fixed
T_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 11]
T = Permutation(T_list)

# Inversion S: x -> -1/x mod 11, with S(0)=infty=11, S(infty)=0
mod = 11
inv = {0: 11, 11: 0}  # S(0)=infty, S(infty)=0
for x in range(1, 11):
    # compute modular inverse
    # find y s.t. x*y % mod == 1
    y = pow(x, -1, mod)
    inv_x = (-1 * y) % mod
    inv[x] = inv_x
# Build S list
S_list = [inv[i] if i in inv else i for i in range(12)]
S = Permutation(S_list)

# Extra involution p from Wikipedia: (2,10)(3,4)(5,9)(6,7) using 1-based labels
# Map 1..12 -> 0..11 by subtracting 1
p_map = list(range(12))
pairs = [(2, 10), (3, 4), (5, 9), (6, 7)]
for a, b in pairs:
    a0 = a - 1
    b0 = b - 1
    p_map[a0] = b0
    p_map[b0] = a0
p = Permutation(p_map)

G = PermutationGroup(T, S, p)
print("Constructed group with generators T, S, p")
print("Group degree:", G.degree)
print("Group order (may be slow):", G.order())

# Basic sanity checks
print("\nConjugacy class sizes sample:")
try:
    print(G.conjugacy_class(0)[:10])
except Exception as e:
    print("Conjugacy listing not available:", e)

# Now act on 27 representatives (from previously created file); for self-contained demo recreate 27 reps
from itertools import product

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
codewords = []
for v in product(range(3), repeat=6):
    cw = tuple(np.dot(v, G_matrix) % 3)
    codewords.append(cw)
rep27 = codewords[:27]

# function to apply permutation (as sympy Permutation) to codeword


def apply_perm_to_cw(perm, cw):
    # perm(i) gives image of i
    images = [perm(i) for i in range(12)]
    return tuple(cw[images[i]] for i in range(12))


# compute orbits of the 27 reps under G (may be heavy; use group.generators for closure)
from collections import deque

orbits = []
seen = set()
for i, cw in enumerate(rep27):
    if i in seen:
        continue
    # BFS style orbit generation using group generators
    orbit_indices = set()
    queue = deque([cw])
    while queue:
        x = queue.popleft()
        if x in orbit_indices:
            continue
        orbit_indices.add(x)
        for g in G.generators:
            y = apply_perm_to_cw(g, x)
            if y not in orbit_indices:
                queue.append(y)
    # mark indices
    for idx, ccw in enumerate(rep27):
        if ccw in orbit_indices:
            seen.add(idx)
    orbits.append(orbit_indices)

print("\nNumber of orbits among 27 reps under generated group:", len(orbits))
for idx, orb in enumerate(orbits):
    print(f"Orbit {idx+1} size: {len(orb)}")

print("\nDone.")
