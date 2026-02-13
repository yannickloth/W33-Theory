"""Collect SA candidates (sampled scoring) and write top candidates to artifacts.

Usage: python -m scripts.collect_sa_candidates

This helper is temporary and designed to reliably write JSON artifacts so we can
exhaustively verify the best candidates afterwards.
"""

import json
import random

import scripts.tune_line_reps as tune

# campaign parameters (kept small for speed)
RUNS = 6
SA_ITERS = 1200
SAMPLE_SIZE = 50
TRIPLE_SAMPLE_COUNT = 1200

random.seed(123)
# tune globals
tune.SAMPLE_SIZE = SAMPLE_SIZE
tune.TRIPLE_SAMPLE_COUNT = TRIPLE_SAMPLE_COUNT

start = [tune.exact.canonical_point(l) for l in tune.exact.F3_lines]
sample_weight6 = random.sample(tune.exact.weight_6, 50)

candidates = []
for r in range(RUNS):
    seed = 1000 + r
    cand, metrics = tune.sa_optimize(
        start, sample_weight6, iterations=SA_ITERS, temp0=0.05, rng_seed=seed
    )
    pc, fc, rate = metrics
    candidates.append(
        {
            "seed": seed,
            "pass": int(pc),
            "fail": int(fc),
            "rate": float(rate),
            "line_rep": [[int(p[0]), int(p[1])] for p in cand],
        }
    )
    print(f"run {r}: sample pass={pc} fail={fc} rate={rate:.4f}")

candidates.sort(key=lambda x: (x["pass"], x["rate"]), reverse=True)
out = {"best": candidates[0], "top3": candidates[:3], "runs": RUNS}
with open("artifacts/sa_campaign_best.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, default=str)
print("WROTE artifacts/sa_campaign_best.json")

from itertools import combinations

# --- Exhaustive verification of top-3 candidates ---------------------------------
# Reuse the loaded THE_EXACT_MAP via scripts.check_full_cocycle to ensure the
# same runtime environment and helpers are used.
import scripts.check_full_cocycle as ch

ex_results = []
for idx, cand in enumerate(out["top3"]):
    print(f"Exhaustive verify top-{idx+1} (seed={cand['seed']}) ...")
    ch.mod.line_rep = [tuple(p) for p in cand["line_rep"]]
    weight6 = list(ch.weight6)
    zero = tuple([0] * 12)
    add = ch.add
    ss = ch.symplectic_sign

    passed = 0
    failed = 0
    for a, b, c in combinations(weight6, 3):
        ab = add(a, b)
        bc = add(b, c)
        ca = add(c, a)
        if ab == zero or bc == zero or ca == zero:
            continue
        s1 = ss(a, bc) * ss(b, c)
        s2 = ss(b, ca) * ss(c, a)
        s3 = ss(c, ab) * ss(a, b)
        if s1 == s2 == s3:
            passed += 1
        else:
            failed += 1

    rate = passed / (passed + failed) if (passed + failed) else None
    ex_results.append(
        {
            "seed": cand["seed"],
            "passed": passed,
            "failed": failed,
            "rate": rate,
        }
    )
    print(f"  -> passed={passed} failed={failed} rate={rate:.4f}")

with open("artifacts/sa_campaign_best_exhaustive.json", "w", encoding="utf-8") as f:
    json.dump({"top3_exhaustive": ex_results, "summary": out}, f, indent=2, default=str)
print("WROTE artifacts/sa_campaign_best_exhaustive.json")
# --------------------------------------------------------------------------------
