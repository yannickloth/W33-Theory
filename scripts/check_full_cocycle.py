"""
Exhaustive cocycle / Jacobi check using the canonical `line_rep` in
`THE_EXACT_MAP.py`.

This replicates THE_EXACT_MAP.py's sampled cocycle test but runs it
for every unordered triple of distinct weight-6 codewords.

Exit code: 0 on success (no failures), 2 if any triple fails.
"""

import importlib.util
import os
import time
from itertools import combinations

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
spec = importlib.util.spec_from_file_location(
    "the_exact_map", os.path.join(ROOT, "THE_EXACT_MAP.py")
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

weight6 = list(mod.weight_6)
zero = tuple([0] * 12)
add = mod.add
symplectic_sign = mod.symplectic_sign


def check_all_triples():
    total = 0
    passed = 0
    failed = 0
    first_fail_examples = []

    start = time.time()
    # iterate unordered triples (combinations)
    for a, b, c in combinations(weight6, 3):
        # skip degenerate sums as THE_EXACT_MAP.py does
        ab = add(a, b)
        bc = add(b, c)
        ca = add(c, a)
        if ab == zero or bc == zero or ca == zero:
            continue

        s1 = symplectic_sign(a, bc) * symplectic_sign(b, c)
        s2 = symplectic_sign(b, ca) * symplectic_sign(c, a)
        s3 = symplectic_sign(c, ab) * symplectic_sign(a, b)

        total += 1
        if s1 == s2 == s3:
            passed += 1
        else:
            failed += 1
            if len(first_fail_examples) < 10:
                first_fail_examples.append((a, b, c, s1, s2, s3))

        # progress indicator every 100k tested triples
        if total % 100000 == 0:
            elapsed = time.time() - start
            print(
                f"Checked {total} triples — passed={passed} failed={failed} — {elapsed:.1f}s elapsed"
            )

    elapsed = time.time() - start
    print("\nExhaustive cocycle check finished:")
    print(f"  Weight-6 codewords: {len(weight6)}")
    print(f"  Triples tested: {total}")
    print(
        f"  Passed: {passed}  Failed: {failed}  Rate: {passed/(passed+failed):.4f}"
        if (passed + failed) > 0
        else "No triples tested"
    )
    print(f"  Elapsed: {elapsed:.1f}s")

    if failed:
        print("\nFirst failing examples (up to 10):")
        for a, b, c, s1, s2, s3 in first_fail_examples:
            print(f"  a={a}\n  b={b}\n  c={c}\n  s1={s1} s2={s2} s3={s3}\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(check_all_triples())
