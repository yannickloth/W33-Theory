#!/usr/bin/env python3
"""Map extracted unsat cores to Schläfli triangles (H indices) and report involvement of H0."""
import json
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / "artifacts"

cores = json.load(open(ART / "sign_unsat_cores.json", "r", encoding="utf-8"))
perm = json.load(open(ART / "triad_label_permutation.json", "r", encoding="utf-8"))[
    "mapping"
]
inv = {int(v): int(k) for k, v in perm.items()}


def map_tri_to_H(tri):
    return tuple(sorted([inv[t] for t in tri]))


for entry in cores:
    print("\nCore from", entry["file"])
    core = entry["unsat_core"]
    for idx, tri in enumerate(core):
        htri = map_tri_to_H(tri)
        print(f"  tri {tri} -> H tri {htri} (contains H0? {0 in htri})")
    # certificate rows
    cert = entry["certificate_rows"]
    print("Certificate rows (E6 triads):", cert)
    hcert = [map_tri_to_H(tuple(t)) for t in cert]
    print("Certificate rows (H triangles):", hcert)

print("\nDone.")
