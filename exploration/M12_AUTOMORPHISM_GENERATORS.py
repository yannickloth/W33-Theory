# M12_AUTOMORPHISM_GENERATORS.py
"""
Explicitly construct generators for the Mathieu group M12 and apply them to ternary Golay codewords.
This script will:
- Define known M12 generators (permutation matrices or cycle notation)
- Apply them to the 27 representative codewords
- Print the orbit structure and stabilizer analysis
- Lay groundwork for full automorphism group action on the ternary Golay lattice
"""

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

rep_codewords = codewords[:27]

# 2. Define two explicit M12 generators (cycle notation)
# These are standard generators for M12 acting on 12 points
# Example: (1 2 3 4 5 6 7 8 9 10 11 12) and (1 2)(3 4)(5 6)(7 8)(9 10)(11 12)


def apply_permutation(cw, perm):
    return tuple(cw[perm[i]] for i in range(len(cw)))


# Generator 1: 12-cycle
gen1 = list(range(1, n)) + [0]
# Generator 2: product of 6 transpositions
gen2 = [1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10]

# Apply generators to all codewords
orbits = set()
for cw in rep_codewords:
    orbit = [cw]
    for _ in range(n):
        cw = apply_permutation(cw, gen1)
        orbit.append(cw)
    orbits.add(tuple(orbit))

print(f"Number of distinct orbits under 12-cycle generator: {len(orbits)}")

# Apply second generator
stabilizers = []
for cw in rep_codewords:
    permuted = apply_permutation(cw, gen2)
    if permuted == cw:
        stabilizers.append(cw)

print(
    f"Number of codewords stabilized by 6-transposition generator: {len(stabilizers)}"
)

# Print sample orbits and stabilizers
print("\nSample orbit under 12-cycle:")
for orbit in list(orbits)[:1]:
    for cw in orbit:
        print(cw)

print("\nSample stabilized codewords:")
for cw in stabilizers[:5]:
    print(cw)

print(
    "\nFull M12 action requires composition of these and other generators; use GAP/SageMath for full group structure."
)
