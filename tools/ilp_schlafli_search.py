#!/usr/bin/env python3
"""ILP search for a 27-subset of W33 lines inducing the Schlaefli SRG (27,16,10,8).

This encodes the SRG constraints as an integer program with binary variables
x_i indicating whether line i is selected and y_{i,j}=x_i x_j linearized
for pairwise constraints on common neighbors. If infeasible, this proves
no induced Schlaefli subgraph exists in the W33 line-disjointness graph.

Writes: tools/artifacts/schlafli_ilp_result.json
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import pulp

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

# reuse helper from existing script (import by path to avoid package issues)
import importlib.util
from pathlib import Path

modp = Path(__file__).parent / "find_schlafli_embedding_in_w33.py"
spec = importlib.util.spec_from_file_location(
    "find_schlafli_embedding_in_w33", str(modp)
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
construct_w33_points = mod.construct_w33_points
compute_w33_lines = mod.compute_w33_lines

pts = construct_w33_points()
lines = compute_w33_lines(pts)
N = len(lines)
A = [[0] * N for _ in range(N)]
for i in range(N):
    for j in range(N):
        if i != j and set(lines[i]).isdisjoint(set(lines[j])):
            A[i][j] = 1

prob = pulp.LpProblem("schlafli_in_w33", pulp.LpStatusOptimal)
# binary variables
x = pulp.LpVariable.dicts("x", range(N), lowBound=0, upBound=1, cat="Binary")
y = {}
for i, j in combinations(range(N), 2):
    y[(i, j)] = pulp.LpVariable(f"y_{i}_{j}", lowBound=0, upBound=1, cat="Binary")

# constraints
prob += pulp.lpSum([x[i] for i in range(N)]) == 27
for i in range(N):
    prob += pulp.lpSum([A[i][j] * x[j] for j in range(N)]) == 16 * x[i]

for i, j in combinations(range(N), 2):
    rhs_val = 10 if A[i][j] == 1 else 8
    prob += (
        pulp.lpSum([A[i][k] * A[j][k] * x[k] for k in range(N)]) == rhs_val * y[(i, j)]
    )
    prob += y[(i, j)] <= x[i]
    prob += y[(i, j)] <= x[j]
    prob += y[(i, j)] >= x[i] + x[j] - 1

prob += 0

# solve with a time limit to guard resources
solver = pulp.PULP_CBC_CMD(msg=True, timeLimit=600)
status = prob.solve(solver)
status_str = pulp.LpStatus[status]

out = {
    "status": status_str,
    "n_vars": len(prob.variables()),
    "n_constraints": len(prob.constraints),
}
(ART / "schlafli_ilp_result.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
print("Wrote", ART / "schlafli_ilp_result.json")
print(out)
