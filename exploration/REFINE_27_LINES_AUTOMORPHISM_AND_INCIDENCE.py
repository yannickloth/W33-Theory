"""
REFINE_27_LINES_AUTOMORPHISM_AND_INCIDENCE.py
=============================================

Refine the mapping of the 27 lines to ternary Golay codewords using automorphism group (M12) actions,
analyze incidence relations, and relate W33 cycles to tritangent planes and E6 cubic invariants.
"""

from collections import defaultdict
from itertools import product

import numpy as np

# 1. Generate ternary Golay codewords
n = 12
k = 6
q = 3
G = np.array(
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
for v in product(range(q), repeat=k):
    cw = tuple(np.dot(v, G) % q)
    codewords.append(cw)

# 2. Select 27 codewords as representatives (placeholder: first 27)
rep_codewords = codewords[:27]


# 3. Define a simple automorphism: cyclically permute coordinates (as a toy M12 action)
def permute_codeword(cw, perm):
    return tuple(cw[i] for i in perm)


# Example: apply a cyclic permutation to all codewords
perm = list(range(1, n)) + [0]
permuted_codewords = [permute_codeword(cw, perm) for cw in rep_codewords]

print("Sample automorphism (cyclic permutation) applied to 27 codewords:")
for i, (orig, permuted) in enumerate(zip(rep_codewords, permuted_codewords)):
    print(f"{i+1:2}: {orig} -> {permuted}")


# 4. Incidence relation: two codewords are 'adjacent' if their Hamming distance is minimal (e.g., 6 for Golay)
def hamming_distance(a, b):
    return sum(x != y for x, y in zip(a, b))


adjacency = defaultdict(list)
for i, cw1 in enumerate(rep_codewords):
    for j, cw2 in enumerate(rep_codewords):
        if i < j and hamming_distance(cw1, cw2) == 6:
            adjacency[i].append(j)
            adjacency[j].append(i)

print("\nIncidence (adjacency) relations among 27 codewords (Hamming distance 6):")
for i, neighbors in adjacency.items():
    print(f"Codeword {i+1}: adjacent to {[j+1 for j in neighbors]}")

# 5. Relate W33 cycles to tritangent planes and E6 cubic invariants (outline)
# - W33 has 81 cycles = 3 × 27; each set of 3 cycles may correspond to a line/class
# - Tritangent planes: sets of 3 lines with special incidence (from E6 geometry)
# - For demonstration, group codewords into 9 groups of 3 (placeholder)

cycle_groups = [rep_codewords[i * 3 : (i + 1) * 3] for i in range(9)]
print("\nW33 cycle groups (placeholder, 9 groups of 3 codewords):")
for idx, group in enumerate(cycle_groups):
    print(f"Group {idx+1}: {group}")

print(
    "\nFurther work: Implement full M12 action, true incidence from geometry, and explicit E6 cubic invariant mapping."
)
