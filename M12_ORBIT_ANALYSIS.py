"""
M12_ORBIT_ANALYSIS.py
====================

Compose multiple M12 generators, apply them to ternary Golay codewords, and analyze orbit structure.
Map orbit representatives to geometric configurations and E6 cubic invariants.
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

# 2. Define multiple M12 generators
# Generator 1: 12-cycle
gen1 = list(range(1, n)) + [0]
# Generator 2: product of 6 transpositions
gen2 = [1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10]
# Generator 3: 3-cycle (example)
gen3 = [2, 0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11]


# Compose generators: gen1 followed by gen2, then gen3
def compose_permutations(p1, p2):
    return [p1[p2[i]] for i in range(len(p1))]


composed = compose_permutations(gen1, gen2)
composed = compose_permutations(composed, gen3)

# Apply composed generator to all codewords
orbits = set()
for cw in rep_codewords:
    orbit = [cw]
    for _ in range(n):
        cw = tuple(cw[composed[i]] for i in range(len(cw)))
        orbit.append(cw)
    orbits.add(tuple(orbit))

print(f"Number of distinct orbits under composed generator: {len(orbits)}")

# Map orbit representatives to geometric configurations (placeholder)
print("\nSample orbit under composed generator:")
for orbit in list(orbits)[:1]:
    for cw in orbit:
        print(cw)

print(
    "\nFurther work: Map orbit representatives to cubic surface lines, double-sixes, tritangent planes, and E6 cubic invariants."
)
