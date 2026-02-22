"""
Load the SA campaign best candidate from artifacts/sa_campaign_best.json,
apply it to THE_EXACT_MAP module, and run the exhaustive cocycle/Jacobi
check over all unordered weight-6 triples. Prints pass/fail counts and up
to 10 failing triple examples.
"""

import importlib.util
import json
import os
import time
from itertools import combinations

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# load THE_EXACT_MAP as a fresh module
spec = importlib.util.spec_from_file_location(
    "the_exact_map", os.path.join(ROOT, "THE_EXACT_MAP.py")
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# read candidate from artifacts
cand_path = os.path.join(ROOT, "artifacts", "sa_campaign_best.json")
if not os.path.exists(cand_path):
    raise SystemExit(f"Missing {cand_path}")
with open(cand_path, "r", encoding="utf-8") as f:
    cand = json.load(f)["best"]["line_rep"]

mod.line_rep = [tuple(p) for p in cand]

weight6 = list(mod.weight_6)
add = mod.add
symplectic_sign = mod.symplectic_sign
zero = tuple([0] * 12)

print("Running exhaustive cocycle check for SA best candidate...")
start = time.time()
passed = 0
failed = 0
first_fails = []
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
        if len(first_fails) < 10:
            first_fails.append((a, b, c, s1, s2, s3))

elapsed = time.time() - start
print(f"Passed={passed}  Failed={failed}  Rate={passed/(passed+failed):.6f}")
print(f"Elapsed: {elapsed:.1f}s")
if failed:
    print("\nFirst failing examples (up to 10):")
    for a, b, c, s1, s2, s3 in first_fails:
        print(f"  a={a}\n  b={b}\n  c={c}\n  s1={s1} s2={s2} s3={s3}\n")

# write results for record
out = {
    "passed": passed,
    "failed": failed,
    "rate": passed / (passed + failed) if (passed + failed) else None,
}
with open(
    os.path.join(ROOT, "artifacts", "sa_candidate_exhaustive_manual.json"),
    "w",
    encoding="utf-8",
) as f:
    json.dump(out, f, indent=2, default=str)
print("WROTE artifacts/sa_candidate_exhaustive_manual.json")
