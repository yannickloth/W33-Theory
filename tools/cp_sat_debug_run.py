#!/usr/bin/env python3
"""Minimal CP-SAT debug runner: writes initial debug file, builds model, runs 60s minimize, writes partial and final artifacts."""
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

# ensure ortools
try:
    from ortools.sat.python import cp_model
except Exception:
    print("ortools not found; installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ortools"])
    from ortools.sat.python import cp_model

# import helpers
import importlib.util

modp = Path(__file__).parent / "find_schlafli_embedding_in_w33.py"
spec = importlib.util.spec_from_file_location("m", str(modp))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
construct_w33_points = m.construct_w33_points
compute_w33_lines = m.compute_w33_lines

# load hill-climb seed
hill = json.loads((ART / "schlafli_near_miss_hillclimb.json").read_text())
hill_best = hill["best_score"]
hill_sel = hill["best_selected"]

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

# build model
model = cp_model.CpModel()
x = [model.NewBoolVar(f"x_{i}") for i in range(N)]
deg = [model.NewIntVar(0, N, f"deg_{i}") for i in range(N)]
dev_deg = [model.NewIntVar(0, N, f"devdeg_{i}") for i in range(N)]
c = {}
dev_pair = {}
for i, j in combinations(range(N), 2):
    c[(i, j)] = model.NewIntVar(0, N, f"c_{i}_{j}")
    dev_pair[(i, j)] = model.NewIntVar(0, N, f"devpair_{i}_{j}")

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
model.Minimize(total_dev)

# add hint
for i in range(N):
    model.AddHint(x[i], 1 if i in hill_sel else 0)

# debug start
start_stamp = time.time()
(ART / "schlafli_cp_sat_debug_start.txt").write_text(
    f"start {start_stamp}\nN={N}\n", encoding="utf-8"
)
print("Debug start written")


# callback
class CB(cp_model.CpSolverSolutionCallback):
    def __init__(self, x_vars, dev_deg_vars, dev_pair_vars, art_dir):
        super().__init__()
        self.x_vars = x_vars
        self.dev_deg_vars = dev_deg_vars
        self.dev_pair_vars = dev_pair_vars
        self.art_dir = Path(art_dir)
        self.best = None

    def OnSolutionCallback(self):
        t = time.time()
        obj = sum(int(self.Value(v)) for v in self.dev_deg_vars) + sum(
            int(self.Value(v)) for v in self.dev_pair_vars.values()
        )
        sel = [i for i, v in enumerate(self.x_vars) if int(self.Value(v)) == 1]
        out = {"time": t, "obj": int(obj), "sel": sel}
        (self.art_dir / "schlafli_cp_sat_partial.json").write_text(
            json.dumps(out, indent=2), encoding="utf-8"
        )
        print("partial incumbent", out)


solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 60.0
solver.parameters.num_search_workers = 8
solver.parameters.log_search_progress = True

cb = CB(x, dev_deg, dev_pair, ART)
print("Starting solve")
res = solver.Solve(model, cb)
end_stamp = time.time()
print("Solve done, status", solver.StatusName(res))

out = {"status": solver.StatusName(res), "elapsed": end_stamp - start_stamp}
if res == cp_model.OPTIMAL or res == cp_model.FEASIBLE:
    sel = [i for i in range(N) if solver.Value(x[i])]
    out["best_selected"] = sel
    out["best_objective"] = int(
        sum(solver.Value(v) for v in dev_deg)
        + sum(solver.Value(v) for v in dev_pair.values())
    )
(ART / "schlafli_cp_sat_result.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
(ART / "schlafli_cp_sat_debug_end.txt").write_text(
    f"end {end_stamp} status {solver.StatusName(res)}\n", encoding="utf-8"
)
print("Wrote final result", out)
