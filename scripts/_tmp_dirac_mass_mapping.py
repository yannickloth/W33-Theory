#!/usr/bin/env python3
"""Read the committed Dirac artifact and compute a compact mass-summary.
Writes checks/PART_CVII_w33_dirac_mass_summary_<ts>.json
"""
import json
import time
from pathlib import Path

# Find the latest committed dirac file
ART = Path("committed_artifacts")
files = sorted(ART.glob("PART_CVII_w33_dirac_*.json"))
if not files:
    print("No dirac artifact found in committed_artifacts")
    raise SystemExit(1)
latest = files[-1]
j = json.loads(latest.read_text(encoding="utf-8"))

# Extract multiplicities (dirac eigen multiplicity keys are strings)
mult = {float(k): int(v) for k, v in j.get("dirac_eigen_multiplicity", {}).items()}
# Consider positive eigenvalues
pos = sorted([v for v in mult.keys() if v > 1e-12])
pos_summary = [{"eig": p, "mult": mult[p]} for p in pos]

smallest_pos = pos[0] if pos else None
ratios = []
if smallest_pos:
    for p in pos:
        ratios.append({"eig": p, "ratio_to_smallest": float(p / smallest_pos)})

out = {
    "timestamp": int(time.time()),
    "dirac_artifact": str(latest),
    "smallest_positive_eig": float(smallest_pos) if smallest_pos else None,
    "positive_eigen_summary": pos_summary,
    "ratios_to_smallest": ratios,
}
OUT = Path("checks") / f"PART_CVII_w33_dirac_mass_summary_{int(time.time())}.json"
OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
print("Wrote", OUT)
