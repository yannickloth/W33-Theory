#!/usr/bin/env python3
"""CP-SAT search for a 27-subset with total deviation < hill-climb best.
Writes tools/artifacts/schlafli_cp_sat_result.json
"""
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

# ensure OR-Tools available
try:
    from ortools.sat.python import cp_model
except Exception:
    print("OR-Tools not found; installing...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "ortools"]
    )  # may take time
    from ortools.sat.python import cp_model

# helpers
import importlib.util

modp = Path(__file__).parent / "find_schlafli_embedding_in_w33.py"
spec = importlib.util.spec_from_file_location(
    "find_schlafli_embedding_in_w33", str(modp)
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
construct_w33_points = mod.construct_w33_points
compute_w33_lines = mod.compute_w33_lines

# load hill-climb best
hill_file = ART / "schlafli_near_miss_hillclimb.json"
hill = json.loads(hill_file.read_text()) if hill_file.exists() else None
hill_best = hill.get("best_score") if hill else None
hill_sel = hill.get("best_selected") if hill else None
if hill_best is None or hill_sel is None:
    print("Missing hill-climb seed; run hill-climb first")
    raise SystemExit(1)
cutoff = hill_best - 1
print(f"Hill best {hill_best}; searching for solution with total_dev <= {cutoff}")

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

model = cp_model.CpModel()
# selection
x = [model.NewBoolVar(f"x_{i}") for i in range(N)]
# degree and dev vars
deg = [model.NewIntVar(0, N, f"deg_{i}") for i in range(N)]
dev_deg = [model.NewIntVar(0, N, f"devdeg_{i}") for i in range(N)]
# pair count and dev
c = {}
dev_pair = {}
for i, j in combinations(range(N), 2):
    key = (i, j)
    c[key] = model.NewIntVar(0, N, f"c_{i}_{j}")
    dev_pair[key] = model.NewIntVar(0, N, f"devpair_{i}_{j}")

# cardinality
model.Add(sum(x) == 27)

# deg definitions
for i in range(N):
    model.Add(deg[i] == sum(A[i][j] * x[j] for j in range(N)))
    model.Add(dev_deg[i] >= deg[i] - 16)
    model.Add(dev_deg[i] >= 16 - deg[i])

# pair definitions
for i, j in combinations(range(N), 2):
    key = (i, j)
    model.Add(c[key] == sum(A[i][k] * A[j][k] * x[k] for k in range(N)))
    t = pair_target[key]
    model.Add(dev_pair[key] >= c[key] - t)
    model.Add(dev_pair[key] >= t - c[key])

# objective: minimize total deviation (no hard cutoff)
total_dev = sum(dev_deg) + sum(dev_pair.values())
model.Minimize(total_dev)

# hint from hill-climb
for i in range(N):
    hint_val = 1 if i in hill_sel else 0
    model.AddHint(x[i], hint_val)


# solution callback to capture intermediate incumbents
class IncumbentCallback(cp_model.CpSolverSolutionCallback):
    def __init__(self, x_vars, dev_deg_vars, dev_pair_vars, art_dir):
        super().__init__()
        self.x_vars = x_vars
        self.dev_deg_vars = dev_deg_vars
        self.dev_pair_vars = dev_pair_vars
        self.art_dir = Path(art_dir)
        self.best_obj = None
        self.best_sel = None
        self.last_saved = 0

    def OnSolutionCallback(self):
        # compute objective
        obj = sum(int(self.Value(v)) for v in self.dev_deg_vars) + sum(
            int(self.Value(v)) for v in self.dev_pair_vars.values()
        )
        sel = [i for i, v in enumerate(self.x_vars) if int(self.Value(v)) == 1]
        t = time.time()
        if self.best_obj is None or obj < self.best_obj:
            self.best_obj = obj
            self.best_sel = sel
            # save partial artifact
            out = {
                "status": "running",
                "time": t,
                "best_objective": int(self.best_obj),
                "best_selected": self.best_sel,
            }
            (self.art_dir / "schlafli_cp_sat_partial.json").write_text(
                json.dumps(out, indent=2), encoding="utf-8"
            )
            print(
                f"New incumbent: obj={self.best_obj}, selected_count={len(sel)} at time {t}"
            )
        # periodic save even if not improved
        if t - self.last_saved > 60:
            summary = {
                "time": t,
                "best_objective": None if self.best_obj is None else int(self.best_obj),
                "best_selected_count": (
                    None if self.best_sel is None else len(self.best_sel)
                ),
            }
            (self.art_dir / "schlafli_cp_sat_progress.json").write_text(
                json.dumps(summary, indent=2), encoding="utf-8"
            )
            self.last_saved = t


solver = cp_model.CpSolver()
# DEBUG: short run for diagnostics
solver.parameters.max_time_in_seconds = 60.0
solver.parameters.num_search_workers = 4
solver.parameters.random_seed = 42
solver.parameters.log_search_progress = True
# write debug trace file
(ART / "schlafli_cp_sat_run_debug.txt").write_text(
    f"starting debug run at {time.time()}\n", encoding="utf-8"
)
print("Starting CP-SAT debug solve (minimize total_dev, 60s)...")
start_time = time.time()
cb = IncumbentCallback(x, dev_deg, dev_pair, ART)
res = solver.Solve(model, cb)
elapsed = time.time() - start_time
status = solver.StatusName(res)
(ART / "schlafli_cp_sat_run_debug.txt").write_text(
    f"stopped at {time.time()}, status={status}, elapsed={elapsed}\n", encoding="utf-8"
)
print("Solver status", status, "elapsed", elapsed)

# prepare final summary
out = {
    "status": status,
    "elapsed": elapsed,
    "best_objective": None,
    "best_selected": None,
}
if cb.best_obj is not None:
    out["best_objective"] = int(cb.best_obj)
    out["best_selected"] = cb.best_sel
elif res == cp_model.OPTIMAL or res == cp_model.FEASIBLE:
    sel = [i for i in range(N) if solver.Value(x[i]) == 1]
    best_obj = sum(solver.Value(v) for v in dev_deg) + sum(
        solver.Value(v) for v in dev_pair.values()
    )
    out["best_objective"] = int(best_obj)
    out["best_selected"] = sel

(ART / "schlafli_cp_sat_result.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
print("Wrote", ART / "schlafli_cp_sat_result.json")
print(json.dumps(out, indent=2))
