#!/usr/bin/env python3
import json
from pathlib import Path

ART = Path("artifacts")
S = json.load(open(ART / "pysat_cryptosat_sweep_summary.json", "r", encoding="utf-8"))
summary = {
    "total": len(S),
    "xor_valid": 0,
    "cnf_valid": 0,
    "cnf_unsat_cores_appended": 0,
    "xor_failed": [],
    "cnf_failed": [],
}
for e in S:
    W = e["W_idx"]
    xor_art = e.get("xor_run", {}).get("artifact")
    cnf_art = e.get("cnf_only_run", {}).get("artifact")
    if xor_art and xor_art.get("valid"):
        summary["xor_valid"] += 1
    else:
        summary["xor_failed"].append(W)
    if cnf_art and cnf_art.get("valid"):
        summary["cnf_valid"] += 1
    else:
        summary["cnf_failed"].append(W)
    snc = e.get("cnf_only_run", {}).get("sign_unsat_cores", [])
    if any(entry.get("file") == f"pysat_mapping_W{W}_cnfonly.json" for entry in snc):
        summary["cnf_unsat_cores_appended"] += 1
print(json.dumps(summary, indent=2))

# also print which W had cnf-only unsat core appended
w_unsat = []
for e in S:
    W = e["W_idx"]
    snc = e.get("cnf_only_run", {}).get("sign_unsat_cores", [])
    for entry in snc:
        if entry.get("file") == f"pysat_mapping_W{W}_cnfonly.json":
            w_unsat.append(W)
            break
print("\nW indices with CNF-only unsat core appended:", w_unsat)
