"""Medium SA campaign: 20 restarts, 3k iters, larger triple sampling.
Writes artifacts/sa_medium_campaign_best.json and exhaustively verifies top-3.
"""

import json
import random
import time
from itertools import combinations

import scripts.check_full_cocycle as ch
import scripts.tune_line_reps as tune

# campaign params
RUNS = 20
SA_ITERS = 3000
SAMPLE_SIZE = 50
TRIPLE_SAMPLE_COUNT = 5000

random.seed(2026)
# tune globals
tune.SAMPLE_SIZE = SAMPLE_SIZE
tune.TRIPLE_SAMPLE_COUNT = TRIPLE_SAMPLE_COUNT

start = [tune.exact.canonical_point(l) for l in tune.exact.F3_lines]
sample_weight6 = random.sample(tune.exact.weight_6, 50)

candidates = []
for r in range(RUNS):
    seed = 2000 + r
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
out = {"best": candidates[0], "top5": candidates[:5], "runs": RUNS}
with open("artifacts/sa_medium_campaign_best.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, default=str)
print("WROTE artifacts/sa_medium_campaign_best.json")

# Exhaustively verify top-3
print("\nExhaustively verifying top-3 candidates (this may take ~12-20 minutes)")
ex_results = []
for i, cand in enumerate(out["top5"][:3]):
    print(f'Verify #{i+1} (seed={cand["seed"]})...')
    ch.mod.line_rep = [tuple(p) for p in cand["line_rep"]]
    weight6 = list(ch.weight6)
    add = ch.add
    ss = ch.symplectic_sign
    zero = tuple([0] * 12)
    passed = 0
    failed = 0
    t0 = time.time()
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
    dur = time.time() - t0
    rate = passed / (passed + failed) if (passed + failed) else None
    ex_results.append(
        {
            "seed": cand["seed"],
            "passed": passed,
            "failed": failed,
            "rate": rate,
            "time_s": dur,
        }
    )
    print(f"  done: passed={passed} failed={failed} rate={rate:.4f} time={dur:.1f}s")

with open(
    "artifacts/sa_medium_campaign_best_exhaustive.json", "w", encoding="utf-8"
) as f:
    json.dump({"top3_exhaustive": ex_results, "summary": out}, f, indent=2, default=str)
print("WROTE artifacts/sa_medium_campaign_best_exhaustive.json")
