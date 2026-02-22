"""Targeted repair of `line_rep` using failing-triple hotspots.

Algorithm (greedy single-line flips):
 - Scan all unordered triples and collect a SAMPLE of failing triples + frequency counts
   per-position and per-line (positions map to lines via pos_to_line_mog).
 - Sort lines by failure frequency; for top-K lines try their alternative reps using
   the sampled failing-triple set to estimate improvement.
 - For promising flips, run exhaustive verification; accept the flip if exhaustive
   pass count increases. Repeat until no single-line flip improves the exhaustive rate.

This is conservative (only apply a flip after exhaustive confirmation).
"""

import importlib.util
import os
import random
import time
from collections import Counter
from itertools import combinations

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
spec = importlib.util.spec_from_file_location(
    "the_exact_map", os.path.join(ROOT, "THE_EXACT_MAP.py")
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Parameters
SAMPLE_FAIL_TRIPLES = 50000  # sample size to evaluate candidate flips quickly
TOP_K_LINES = 6
random.seed(42)

print("Scanning all triples to collect failing-triple hotspots (this may take ~3-5m)")
start = time.time()
weight6 = list(mod.weight_6)
zero = tuple([0] * 12)
add = mod.add
symp = mod.symplectic_sign
pos_to_line = mod.pos_to_line_mog

# counters
pos_counts = Counter()
line_counts = Counter()
failed_sample = []
failed_total = 0

for a, b, c in combinations(weight6, 3):
    ab = add(a, b)
    bc = add(b, c)
    ca = add(c, a)
    if ab == zero or bc == zero or ca == zero:
        continue
    s1 = symp(a, bc) * symp(b, c)
    s2 = symp(b, ca) * symp(c, a)
    s3 = symp(c, ab) * symp(a, b)
    if not (s1 == s2 == s3):
        failed_total += 1
        # accumulate per-position and per-line counts
        for cw in (a, b, c):
            for pos, val in enumerate(cw):
                if val != 0:
                    pos_counts[pos] += 1
                    line_counts[pos_to_line[pos]] += 1
        # reservoir sample for failed triples
        if len(failed_sample) < SAMPLE_FAIL_TRIPLES:
            failed_sample.append((a, b, c))
        else:
            # replace with decreasing probability
            i = random.randrange(failed_total)
            if i < SAMPLE_FAIL_TRIPLES:
                failed_sample[i] = (a, b, c)

elapsed = time.time() - start
print(
    f"  Total failing triples: {failed_total}  (collected sample={len(failed_sample)})  elapsed={elapsed:.1f}s"
)

# show top positions/lines
print("\nTop positions by failure frequency:")
for pos, cnt in pos_counts.most_common(8):
    print(f"  pos {pos}: {cnt}")

print("\nTop lines by failure frequency:")
for lid, cnt in line_counts.most_common(TOP_K_LINES):
    print(f"  line {lid}: {cnt} failures")


# Helper: evaluate a proposed line_rep (only on the sampled failing triples)
def sample_fix_rate(proposed_line_rep, failed_sample):
    # build a temporary symplectic_sign using proposed_line_rep via mod helpers
    # We'll monkeypatch mod.line_rep and call mod.symplectic_sign on samples
    old = list(mod.line_rep)
    mod.line_rep = [tuple(p) for p in proposed_line_rep]
    fixed = 0
    for a, b, c in failed_sample:
        ab = add(a, b)
        bc = add(b, c)
        ca = add(c, a)
        s1 = symp(a, bc) * symp(b, c)
        s2 = symp(b, ca) * symp(c, a)
        s3 = symp(c, ab) * symp(a, b)
        if s1 == s2 == s3:
            fixed += 1
    mod.line_rep = old
    return fixed


# Greedy single-line flip loop
current_line_rep = [tuple(p) for p in mod.line_rep]
# current exhaustive baseline: run full exhaustive to get baseline pass count
print("\nComputing current exhaustive baseline (this is the ground truth)...")
start = time.time()
weight6 = list(mod.weight_6)
passed = 0
failed = 0
for a, b, c in combinations(weight6, 3):
    ab = add(a, b)
    bc = add(b, c)
    ca = add(c, a)
    if ab == zero or bc == zero or ca == zero:
        continue
    s1 = symp(a, bc) * symp(b, c)
    s2 = symp(b, ca) * symp(c, a)
    s3 = symp(c, ab) * symp(a, b)
    if s1 == s2 == s3:
        passed += 1
    else:
        failed += 1
base_pass = passed
base_fail = failed
print(
    f"  Baseline exhaustive: passed={base_pass} failed={base_fail} rate={base_pass/(base_pass+base_fail):.4f}  elapsed={time.time()-start:.1f}s"
)

improved = True
iteration = 0
while improved and iteration < 6:
    iteration += 1
    improved = False
    # consider top lines by failure frequency
    top_lines = [lid for lid, _ in line_counts.most_common(TOP_K_LINES)]
    best_local = None
    best_delta = 0
    for lid in top_lines:
        cur_pt = current_line_rep[lid]
        for pt in sorted(list(mod.F3_lines[lid])):
            if tuple(pt) == cur_pt:
                continue
            trial = list(current_line_rep)
            trial[lid] = tuple(pt)
            fixed = sample_fix_rate(trial, failed_sample)
            # normalized by sample size to get estimated improvement
            if fixed > 0 and fixed > best_delta:
                best_delta = fixed
                best_local = (lid, tuple(pt), fixed)
    if best_local:
        lid, new_pt, fixed_est = best_local
        print(
            f"Iteration {iteration}: best sampled flip -> line {lid} -> {new_pt} (estimated fixes on sample={fixed_est})"
        )
        # do exhaustive verification of this single flip
        trial = list(current_line_rep)
        trial[lid] = new_pt
        # inject trial and run full exhaustive
        mod.line_rep = trial
        start = time.time()
        passed = 0
        failed = 0
        for a, b, c in combinations(weight6, 3):
            ab = add(a, b)
            bc = add(b, c)
            ca = add(c, a)
            if ab == zero or bc == zero or ca == zero:
                continue
            s1 = symp(a, bc) * symp(b, c)
            s2 = symp(b, ca) * symp(c, a)
            s3 = symp(c, ab) * symp(a, b)
            if s1 == s2 == s3:
                passed += 1
            else:
                failed += 1
        dur = time.time() - start
        print(
            f"  Exhaustive with flip line {lid}->{new_pt}: passed={passed} failed={failed} rate={passed/(passed+failed):.4f}  elapsed={dur:.1f}s"
        )
        if passed > base_pass:
            # accept change
            print(
                f"  ACCEPTING flip on line {lid} (improves exhaustive pass by {passed-base_pass})"
            )
            current_line_rep = list(trial)
            base_pass = passed
            base_fail = failed
            improved = True
            # update pos/line counts heuristically by re-scanning failed_sample (cheap)
            # (keep the global counters approx. correct for next iter)
            # recompute line_counts from sample
            line_counts = Counter()
            for a, b, c in failed_sample:
                # recompute whether triple still fails under current_line_rep
                mod.line_rep = current_line_rep
                ab = add(a, b)
                bc = add(b, c)
                ca = add(c, a)
                s1 = symp(a, bc) * symp(b, c)
                s2 = symp(b, ca) * symp(c, a)
                s3 = symp(c, ab) * symp(a, b)
                if not (s1 == s2 == s3):
                    for cw in (a, b, c):
                        for pos, val in enumerate(cw):
                            if val != 0:
                                line_counts[pos_to_line[pos]] += 1
            mod.line_rep = current_line_rep
        else:
            print("  Rejecting flip (no exhaustive improvement)")
    else:
        print("No promising single-line flip found on sample")

# Final decision: if improved, update THE_EXACT_MAP.py and tests
if base_pass > passed:
    # this condition should not occur; defensive
    print("No improvement found; exiting")
else:
    if base_pass > int(passed):
        print("No improvement over baseline; nothing to apply")
    else:
        # Check whether current_line_rep differs from file; if so, write it
        old = [tuple(p) for p in mod.line_rep]
        if current_line_rep != old:
            print("Applying improved line_rep to THE_EXACT_MAP.py")
            # update THE_EXACT_MAP.py's line_rep literal
            from pathlib import Path

            exact_path = Path(os.path.join(ROOT, "THE_EXACT_MAP.py"))
            text = exact_path.read_text(encoding="utf-8")
            # replace the block starting at the comment above line_rep
            start_marker = "# Canonical representatives (SA-refined candidate)"
            idx = text.find(start_marker)
            if idx == -1:
                print("Could not find marker to replace line_rep; aborting apply")
            else:
                # locate the 'line_rep = [' block after the marker
                tail = text[idx:]
                import re

                m = re.search(r"line_rep\s*=\s*\[.*?\]\n", tail, flags=re.S)
                if not m:
                    print("Could not locate existing line_rep literal; abort")
                else:
                    new_list = (
                        "["
                        + ",\n    ".join(str(list(p)) for p in current_line_rep)
                        + "]\n"
                    )
                    new_tail = (
                        tail[: m.start()] + "line_rep = " + new_list + tail[m.end() :]
                    )
                    new_text = text[:idx] + new_tail
                    exact_path.write_text(new_text, encoding="utf-8")
                    print("WROTE updated THE_EXACT_MAP.py")
                    # update tests/test_exact_map_line_rep.py expected list
                    test_path = Path(
                        os.path.join(ROOT, "tests", "test_exact_map_line_rep.py")
                    )
                    test_text = test_path.read_text(encoding="utf-8")
                    import ast

                    # replace the expected list literal in the test
                    test_text_new = re.sub(
                        r"expected\s*=\s*\[.*?\]\n",
                        "expected = " + new_list,
                        test_text,
                        flags=re.S,
                    )
                    test_path.write_text(test_text_new, encoding="utf-8")
                    print("Updated test_expected in tests/test_exact_map_line_rep.py")
        else:
            print("Current in-memory line_rep equals file; no file update necessary")

print("\nRepair script finished. Final exhaustive pass count:", base_pass)
