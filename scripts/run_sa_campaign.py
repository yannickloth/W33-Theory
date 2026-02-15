"""
Run multiple simulated-annealing restarts to collect top `line_rep` candidates
according to sampled cocycle pass-rate. Writes `artifacts/sa_campaign_best.json`.
"""

import io
import json
import random
import sys

# suppress noisy imports
_buf = io.StringIO()
_old = sys.stdout
sys.stdout = _buf
import scripts.tune_line_reps as tune

sys.stdout = _old

# campaign params
RUNS = 10
SA_ITERS = 1500
TRIPLE_SAMPLE_COUNT = 1200
SAMPLE_SIZE = 50

# prepare
random.seed(123)
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
    print(f"Run {r}: pass={pc} fail={fc} rate={rate:.4f}")

# sort and write top-5
candidates.sort(key=lambda x: (x["pass"], x["rate"]), reverse=True)
out = {"best": candidates[0], "top5": candidates[:5], "runs": RUNS}
with open("artifacts/sa_campaign_best.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, default=str)
print("WROTE artifacts/sa_campaign_best.json")
