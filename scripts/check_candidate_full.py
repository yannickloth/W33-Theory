"""Exhaustive cocycle check for a hard-coded candidate `line_rep`.
Suppresses THE_EXACT_MAP import-time prints for clean output.
"""

import io
import sys
from itertools import combinations

# suppress noisy imports
_buf = io.StringIO()
_old = sys.stdout
sys.stdout = _buf
import THE_EXACT_MAP as exact

sys.stdout = _old

# candidate (from recent SA quick run)
candidate = [
    (0, 0),
    (1, 0),
    (0, 0),
    (1, 2),
    (2, 2),
    (1, 1),
    (2, 0),
    (2, 1),
    (1, 1),
    (2, 2),
    (1, 2),
    (2, 1),
]

exact.line_rep = [tuple(p) for p in candidate]

weight6 = list(exact.weight_6)
zero = tuple([0] * 12)
add = exact.add
symplectic_sign = exact.symplectic_sign

passed = 0
failed = 0

for a, b, c in combinations(weight6, 3):
    ab = add(a, b)
    bc = add(b, c)
    ca = add(c, a)
    if ab == zero or bc == zero or ca == zero:
        continue
    s1 = symplectic_sign(a, bc) * symplectic_sign(b, c)
    s2 = symplectic_sign(b, ca) * symplectic_sign(c, a)
    s3 = symplectic_sign(c, ab) * symplectic_sign(a, b)
    if s1 == s2 == s3:
        passed += 1
    else:
        failed += 1

print("Candidate exhaustive result:")
print("  Triples tested:", passed + failed)
print("  Passed:", passed)
print("  Failed:", failed)
print("  Rate:", passed / (passed + failed))
