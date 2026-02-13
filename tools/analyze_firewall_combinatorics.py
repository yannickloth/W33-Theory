#!/usr/bin/env python3
"""
Quick combinatorics analysis of the firewall Jacobiator per-triad data.
- Tests for Pascal/binomial matches on scaled integer representations
- Correlates triad e6 magnitudes with Heisenberg u=(u1,u2) coordinates
- Writes a small report JSON
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "artifacts" / "firewall_jacobiator_tensor.json"
HEIS = ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json"
OUT = ROOT / "artifacts" / "firewall_combinatorics_analysis.json"


def is_binomial(n: int, max_row: int = 30) -> List[Tuple[int, int]]:
    matches = []
    for r in range(max_row + 1):
        for k in range(r + 1):
            if math.comb(r, k) == n:
                matches.append((r, k))
    return matches


def try_sum_of_two_binomials(n: int, max_row: int = 30):
    for r1 in range(max_row + 1):
        for k1 in range(r1 + 1):
            v1 = math.comb(r1, k1)
            if v1 >= n:
                continue
            rem = n - v1
            if is_binomial(rem, max_row):
                return (r1, k1, rem)
    return None


def main():
    data = json.loads(IN.read_text(encoding="utf-8"))
    heis = json.loads(HEIS.read_text(encoding="utf-8"))

    single = data.get("single_triad_contributions", {})
    fiber_list = heis.get("fiber_triads_e6id", [])

    entries = []
    ints = []
    for tri in fiber_list:
        key = tuple(sorted(tri))
        key_s = str(key)
        mag = single.get(key_s, {}).get("e6", 0.0)
        scaled6 = int(round(mag * 6))
        ints.append(scaled6)
        # get common u coordinate
        u = heis["e6id_to_heisenberg"][str(tri[0])]["u"]
        entries.append({"triad": tri, "e6_mag": mag, "scaled6": scaled6, "u": u})

    # simple statistics
    arr = np.array([e["e6_mag"] for e in entries])
    mean = float(np.mean(arr))
    std = float(np.std(arr))

    # check for binomial matches
    binomial_matches = {}
    for e in entries:
        n = e["scaled6"]
        matches = is_binomial(n, max_row=40)
        binomial_matches[str(e["triad"])] = {"scaled6": n, "binomial_matches": matches}

    # correlation with u coords
    uvals = np.array([e["u"][0] * 3 + e["u"][1] for e in entries])
    mags = np.array([e["e6_mag"] for e in entries])
    corr = float(np.corrcoef(uvals, mags)[0, 1])

    out = {
        "summary": {
            "count": len(entries),
            "mean_e6": mean,
            "std_e6": std,
            "u_e6_corr": corr,
        },
        "entries": entries,
        "binomial_matches": binomial_matches,
        "scaled_integers": ints,
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
