"""Exhaustively verify the `best` candidate stored in `artifacts/sa_campaign_best.json`.
Writes results to `artifacts/sa_candidate_exhaustive.json`.
"""

import importlib.util
import json
import os
from itertools import combinations

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# load THE_EXACT_MAP as a fresh module (same pattern as check_full_cocycle)
spec = importlib.util.spec_from_file_location(
    "the_exact_map", os.path.join(ROOT, "THE_EXACT_MAP.py")
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# read candidate from artifacts
cand = json.load(open(os.path.join(ROOT, "artifacts", "sa_campaign_best.json")))[
    "best"
]["line_rep"]
mod.line_rep = [tuple(p) for p in cand]

weight6 = list(mod.weight_6)
add = mod.add
symplectic_sign = mod.symplectic_sign
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
    "passed": passed,
    "failed": failed,
    "rate": passed / (passed + failed) if (passed + failed) else None,
}
with open(
    os.path.join(ROOT, "artifacts", "sa_candidate_exhaustive.json"),
    "w",
    encoding="utf-8",
) as f:
    json.dump(out, f, indent=2, default=str)
print("WROTE artifacts/sa_candidate_exhaustive.json")
