"""Run one simulated-annealing search for `line_rep` and write best candidate.
This script suppresses import-time prints so the output is clean and machine-readable.
"""

import io
import json
import random
import sys

# suppress noisy imports
_buf = io.StringIO()
_old_stdout = sys.stdout
sys.stdout = _buf
import scripts.tune_line_reps as tune

sys.stdout = _old_stdout

# prepare start/sample
start = [tune.exact.canonical_point(l) for l in tune.exact.F3_lines]
sample_weight6 = random.sample(tune.exact.weight_6, 50)

# tuning parameters (light sampling for speed)
tune.SAMPLE_SIZE = 50
tune.TRIPLE_SAMPLE_COUNT = 1500

best, metrics = tune.sa_optimize(
    start, sample_weight6, iterations=1500, temp0=0.05, rng_seed=123
)

out = {
    "metrics": {
        "pass": int(metrics[0]),
        "fail": int(metrics[1]),
        "rate": float(metrics[2]),
    },
    "line_rep": [[int(p[0]), int(p[1])] for p in best],
}
with open("artifacts/sa_best_line_rep.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, default=str)
print("WROTE artifacts/sa_best_line_rep.json")
