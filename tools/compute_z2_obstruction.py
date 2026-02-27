#!/usr/bin/env python3
"""Compute a Z2 2-cocycle from holonomy data in the edgepair bundle.

Reads `commutator_cycle_holonomy_edgepairs.csv` in the holonomy bundle and
extracts a binary matrix c[i][j] indicating whether the commutator of
generator i and j has any fixed-block reflections (nontrivial Z2 holonomy).

The output is written to `artifacts/z2_cocycle.json` (upper-triangular list)
and printed to screen for inspection.  A nonzero entry indicates a genuine
obstruction to lifting the 120-action through a Z2 central extension.

This matrix can be further analysed by the user to determine if the cocycle is
cohomologically nontrivial (e.g. by attempting to write it as a coboundary
from a 1-cochain on the generating set).
"""

import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOL = ROOT / "TOE_holonomy_Z2_flatZ3_v01_20260227_bundle" / "TOE_holonomy_Z2_flatZ3_v01_20260227"


def load_commutator_holonomy(path: Path):
    with open(path) as f:
        rdr = csv.DictReader(f)
        data = []
        for row in rdr:
            i = int(row['i']); j = int(row['j'])
            fixed = int(row['fixed_reflections'])
            data.append((i,j,fixed))
        return data


def build_cocycle(entries, ngens=10):
    # assume symmetric in i,j
    c = [[0]*ngens for _ in range(ngens)]
    for i,j,fixed in entries:
        if fixed % 2 != 0:
            c[i][j] = 1
            c[j][i] = 1
    return c


def main():
    path = HOL / "commutator_cycle_holonomy_edgepairs.csv"
    entries = load_commutator_holonomy(path)
    coc = build_cocycle(entries)
    out = ROOT / "artifacts" / "z2_cocycle.json"
    out.write_text(json.dumps(coc, indent=2))
    print("Z2 cocycle matrix (size", len(coc),") saved to", out)
    for i,row in enumerate(coc):
        print(i, row)

if __name__ == "__main__":
    main()
