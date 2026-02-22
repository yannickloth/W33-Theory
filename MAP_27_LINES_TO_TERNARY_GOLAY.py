"""
MAP_27_LINES_TO_TERNARY_GOLAY.py
================================

Map the 27 lines on a cubic surface (E6 fundamental) to codewords or cycles in the ternary Golay code/W33 model.
"""

# The 27 lines on a cubic surface are classically labeled as:
# - 6 exceptional divisors: E1,...,E6
# - 15 lines: L_{ij} (joining E_i and E_j)
# - 6 conics: C_i (passing through all except E_i)

# In the ternary Golay code, we have 12 coordinates and 729 codewords.
# W33 (PG(3, GF(3))) has 40 points and 81 cycles; 81 = 3 × 27.

# For demonstration, we will:
# - Assign 27 representative codewords (or cycles) to the 27 lines
# - Print the mapping and check for symmetries

from itertools import product

import numpy as np

# Placeholder: use the first 27 codewords as representatives
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
    cw = np.dot(v, G) % q
    codewords.append(tuple(cw))
    if len(codewords) == 27:
        break

# Classical labels for the 27 lines
line_labels = (
    [f"E{i+1}" for i in range(6)]
    + [f"L{i+1}{j+1}" for i in range(6) for j in range(i + 1, 6)]
    + [f"C{i+1}" for i in range(6)]
)
line_labels = line_labels[:27]

# Map and print
print("Mapping of 27 lines to ternary Golay codewords:")
for label, cw in zip(line_labels, codewords):
    print(f"{label}: {cw}")

# Next steps:
# - Refine the mapping using automorphism group actions (M12)
# - Analyze incidence relations (which codewords/lines are 'adjacent')
# - Relate cycles in W33 to tritangent planes and E6 cubic invariants
