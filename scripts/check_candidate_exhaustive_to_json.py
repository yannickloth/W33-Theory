"""Compute exhaustive cocycle pass/fail counts for a candidate `line_rep`
using the `mod` instance inside `scripts.check_full_cocycle` and write results
to `artifacts/candidate_exhaustive_result.json`.
"""

import json
from itertools import combinations

import scripts.check_full_cocycle as ch

# SA candidate (from last quick run)
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

# inject candidate into the loaded THE_EXACT_MAP instance inside ch
ch.mod.line_rep = [tuple(p) for p in candidate]

weight6 = list(ch.weight6)
add = ch.add
symplectic_sign = ch.symplectic_sign
zero = tuple([0] * 12)

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

out = {
    "triples_tested": passed + failed,
    "passed": passed,
    "failed": failed,
    "rate": passed / (passed + failed) if (passed + failed) else None,
}
with open("artifacts/sa_candidate_exhaustive.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, default=str)
print("WROTE artifacts/sa_candidate_exhaustive.json")
