#!/usr/bin/env python3
"""Short CP-SAT run (30s) to test feasibility and get immediate feedback."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

try:
    from ortools.sat.python import cp_model
except Exception:
    print("OR-Tools missing; installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ortools"])
    from ortools.sat.python import cp_model

import importlib.util

modp = Path(__file__).parent / "find_schlafli_embedding_in_w33.py"
spec = importlib.util.spec_from_file_location(
    "find_schlafli_embedding_in_w33", str(modp)
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
construct_w33_points = mod.construct_w33_points
compute_w33_lines = mod.compute_w33_lines

hill = json.loads((ART / "schlafli_near_miss_hillclimb.json").read_text())
hill_best = hill["best_score"]
hill_sel = hill["best_selected"]
cutoff = hill_best - 1

pts = construct_w33_points()
lines = compute_w33_lines(pts)
N = len(lines)
A = [[0] * N for _ in range(N)]
for i in range(N):
    for j in range(N):
        if i != j and set(lines[i]).isdisjoint(set(lines[j])):
            A[i][j] = 1

pair_target = {
    (i, j): (10 if A[i][j] == 1 else 8) for i, j in combinations(range(N), 2)
}

# write debug start file so we always have a visible trace
(ART / "schlafli_cp_sat_short_debug.txt").write_text("started\n", encoding="utf-8")

model = cp_model.CpModel()
# selection variables
x = [model.NewBoolVar(f"x_{i}") for i in range(N)]
# degree and deviation vars
deg = [model.NewIntVar(0, N, f"deg_{i}") for i in range(N)]
dev_deg = [model.NewIntVar(0, N, f"devdeg_{i}") for i in range(N)]

c = {}
dev_pair = {}
for i, j in combinations(range(N), 2):
    c[(i, j)] = model.NewIntVar(0, N, f"c_{i}_{j}")
    dev_pair[(i, j)] = model.NewIntVar(0, N, f"devpair_{i}_{j}")

# basic sizes for debug
(ART / "schlafli_cp_sat_short_debug.txt").write_text(
    f"N={N}, num_pairs={len(c)}\n", encoding="utf-8"
)
print(f"N={N}, num_pairs={len(c)}")

model.Add(sum(x) == 27)
for i in range(N):
    model.Add(deg[i] == sum(A[i][j] * x[j] for j in range(N)))
    model.Add(dev_deg[i] >= deg[i] - 16)
    model.Add(dev_deg[i] >= 16 - deg[i])
for i, j in combinations(range(N), 2):
    model.Add(c[(i, j)] == sum(A[i][k] * A[j][k] * x[k] for k in range(N)))
    t = pair_target[(i, j)]
    model.Add(dev_pair[(i, j)] >= c[(i, j)] - t)
    model.Add(dev_pair[(i, j)] >= t - c[(i, j)])

total_dev = sum(dev_deg) + sum(dev_pair.values())
model.Add(total_dev <= cutoff)
for i in range(N):
    model.AddHint(x[i], 1 if i in hill_sel else 0)

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30.0
solver.parameters.num_search_workers = 8
solver.parameters.log_search_progress = True

start = time.time()
res = None
elapsed = None
out = {"status": "error", "elapsed": None}
try:
    res = solver.Solve(model)
    elapsed = time.time() - start
    print("status", solver.StatusName(res), "elapsed", elapsed)
    out = {"status": solver.StatusName(res), "elapsed": elapsed}
    if res == cp_model.OPTIMAL or res == cp_model.FEASIBLE:
        sel = [i for i in range(N) if solver.Value(x[i])]
        out["best_selected"] = sel
        out["best_objective"] = int(
            sum(solver.Value(v) for v in dev_deg)
            + sum(solver.Value(v) for v in dev_pair.values())
        )
except KeyboardInterrupt:
    elapsed = time.time() - start
    out = {"status": "interrupted", "elapsed": elapsed}
    print("Solver interrupted by user")
except Exception as e:
    elapsed = time.time() - start
    out = {"status": f"error: {e}", "elapsed": elapsed}
    print("Solver error:", e)

(ART / "schlafli_cp_sat_short.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
print("wrote", ART / "schlafli_cp_sat_short.json")
