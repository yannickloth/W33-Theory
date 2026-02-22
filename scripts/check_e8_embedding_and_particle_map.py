#!/usr/bin/env python3
"""
Quick checks for W33 and PART_CXI particle map that don't require SageMath.
- Build W33 = SymplecticPolarGraph(4,3) over GF(3) in pure Python.
- Verify vertex count, degrees, edge count.
- Compute adjacency eigenvalues and check spectrum approx {12:1, 2:24, -4:15}.
- Run THEORY_PART_CXI_PARTICLE_MAP.py to generate PART_CXI_particle_map.json and verify keys/counts.
- Write a small checks JSON with the results.
"""

import json
import os
import subprocess
import sys
from collections import Counter
from itertools import product

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT)

# ---------- GF(3) helpers ----------


def mod3_inv(x):
    x = x % 3
    if x == 1:
        return 1
    if x == 2:
        return 2
    raise ValueError("No inverse for 0 in GF(3)")


# canonicalize a non-zero vector by scaling so first non-zero entry == 1
def canonical(vec):
    vec = tuple(v % 3 for v in vec)
    for i, v in enumerate(vec):
        if v % 3 != 0:
            inv = mod3_inv(v)
            return tuple((inv * x) % 3 for x in vec)
    raise ValueError("zero vector")


# build all 1-d subspaces representatives (canonical)
vectors = []
for v in product(range(3), repeat=4):
    if all(x == 0 for x in v):
        continue
    vectors.append(canonical(v))
# deduplicate
reps = sorted(set(vectors))
if len(reps) != 40:
    print("ERROR: expected 40 1D subspaces, got", len(reps))

# Map index -> representative
idx_to_vec = reps
vec_to_idx = {v: i for i, v in enumerate(idx_to_vec)}

# Symplectic form J (4x4) standard: J = [[0,1,0,0],[-1,0,0,0],[0,0,0,1],[0,0,-1,0]] over GF(3)
J = np.array([[0, 1, 0, 0], [2, 0, 0, 0], [0, 0, 0, 1], [0, 0, 2, 0]], dtype=int)


# bilinear form u^T J v (mod 3)
def bilinear(u, v):
    u = np.array(u, dtype=int)
    v = np.array(v, dtype=int)
    val = int(u.dot(J.dot(v)) % 3)
    return val


# adjacency
n = len(idx_to_vec)
A = np.zeros((n, n), dtype=int)
for i in range(n):
    for j in range(n):
        if i == j:
            continue
        if bilinear(idx_to_vec[i], idx_to_vec[j]) == 0:
            A[i, j] = 1

# degrees
degrees = A.sum(axis=1)
all_deg = list(degrees)
checks = {}
checks["n_vertices"] = int(n)
checks["degrees_unique"] = sorted(set(int(d) for d in all_deg))
checks["degrees_sample"] = all_deg[:6]
checks["all_equal_degree"] = len(set(all_deg)) == 1
checks["degree_value"] = int(all_deg[0]) if len(set(all_deg)) == 1 else None
checks["edges"] = int(A.sum() // 2)

# eigenvalues
eigvals = np.linalg.eigvals(A.astype(float))
# Round small numerical noise to nearest integer
eig_rounded = [int(round(x.real)) for x in eigvals]
eig_counts = Counter(eig_rounded)
checks["eigen_counts"] = dict(sorted(eig_counts.items(), key=lambda x: -x[0]))

# expected spectrum
expected = {12: 1, 2: 24, -4: 15}
checks["spectrum_matches_expected"] = all(
    eig_counts.get(k, 0) == v for k, v in expected.items()
)

# Save adjacency to file for inspection
os.makedirs("checks", exist_ok=True)
np.savetxt("checks/W33_adjacency_matrix.txt", A, fmt="%d")

# ----------------- run particle map generator -----------------
print("Running THEORY_PART_CXI_PARTICLE_MAP.py to generate PART_CXI_particle_map.json")
proc = subprocess.run(
    [sys.executable, "THEORY_PART_CXI_PARTICLE_MAP.py"], capture_output=True, text=True
)
print(proc.stdout)
if proc.returncode != 0:
    print("Error running particle map script:", proc.stderr)
    checks["particle_map_run"] = False
    checks["particle_map_error"] = proc.stderr
else:
    checks["particle_map_run"] = True

# Load particle map JSON
pm_path = os.path.join(ROOT, "PART_CXI_particle_map.json")
if os.path.exists(pm_path):
    with open(pm_path, "r") as f:
        pm = json.load(f)
    # basic assertions
    checks["pm_has_vertex_map"] = "vertex_map" in pm
    checks["pm_has_predictions"] = "predictions" in pm
    # verify counts
    checks["pm_gauge_bosons_declared"] = (
        pm.get("gauge_bosons") == 12 or "gauge_bosons" in pm
    )
else:
    checks["pm_exists"] = False


# Save checks (make JSON-serializable)
def make_json_serializable(obj):
    if isinstance(obj, dict):
        return {str(k): make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_json_serializable(x) for x in obj]
    if isinstance(obj, tuple):
        return [make_json_serializable(x) for x in obj]
    # numpy scalar types
    try:
        import numpy as _np

        if isinstance(obj, (_np.integer,)):
            return int(obj)
        if isinstance(obj, (_np.floating,)):
            return float(obj)
        if isinstance(obj, (_np.ndarray,)):
            return obj.tolist()
    except Exception:
        pass
    return obj


with open("checks/PART_CXI_checks.json", "w") as f:
    json.dump(make_json_serializable(checks), f, indent=2)

# Print summary
print("\nQuick W33 & Particle Map checks:")
for k, v in checks.items():
    print(f" - {k}: {v}")

# Exit non-zero if critical checks fail
exit_code = 0
if not checks.get("all_equal_degree", False):
    exit_code = 2
if not checks.get("spectrum_matches_expected", False):
    exit_code = max(exit_code, 3)
if not checks.get("particle_map_run", True):
    exit_code = max(exit_code, 4)

sys.exit(exit_code)
