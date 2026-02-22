#!/usr/bin/env python3
"""Enumerate minimal XOR unsat cores (MUSes) for sign-unsatisfiable opt mappings.

For each entry in artifacts/sign_unsat_cores.json with solvable==False,
we enumerate all minimal unsatisfiable subsets (w.r.t. XOR parity clauses) of
its `certificate_rows` using pycryptosat.

Outputs:
 - artifacts/cryptosat_mus_W{W_idx}.json (per-W MUS list)
 - artifacts/cryptosat_mus_all.json (combined summary)
 - artifacts/cryptosat_mus_report.md (human-friendly summary)

Note: brute-force subset enumeration is used (up to 2^n checks where n<=10 in
our cases), with pruning by skipping supersets of found MUSes.
"""
from __future__ import annotations

import json
import time
from itertools import combinations
from pathlib import Path
from typing import List

from pycryptosat import Solver

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"

SUNC = ART / "sign_unsat_cores.json"
SOLUTION = ART / "e6_cubic_sign_gauge_solution.json"
OUT_ALL = ART / "cryptosat_mus_all.json"
OUT_MD = ART / "cryptosat_mus_report.md"

if not SUNC.exists():
    print("Missing:", SUNC)
    raise SystemExit(1)
if not SOLUTION.exists():
    print("Missing:", SOLUTION)
    raise SystemExit(1)

suns = json.loads(SUNC.read_text(encoding="utf-8"))
sdata = json.loads(SOLUTION.read_text(encoding="utf-8"))

d_map_sign = {
    tuple(sorted(t["triple"])): t["sign"] for t in sdata["solution"]["d_triples"]
}
D_BITS = {
    t: (True if s == -1 else False) for t, s in d_map_sign.items()
}  # parity True=1

summary = []

for entry in suns:
    if entry.get("solvable", False):
        continue
    rows = entry.get("certificate_rows")
    if not rows:
        continue
    W_idx = entry.get("W_idx")
    n = len(rows)
    print(f"Enumerating MUSes for {entry.get('file')} (W={W_idx}) with {n} rows")
    start = time.time()
    found_mus: List[List[int]] = []  # store index lists
    checks = 0
    # iterate by subset size increasing so that when we find a MUS of size k we can prune supersets
    for k in range(1, n + 1):
        if k > n:
            break
        for comb in combinations(range(n), k):
            # skip supersets of already-found MUSes
            skip = False
            for m in found_mus:
                if set(m).issubset(comb):
                    skip = True
                    break
            if skip:
                continue
            # build solver for subset comb
            s = Solver()
            checks += 1
            for idx in comb:
                tri = tuple(sorted(rows[idx]))
                rhs = D_BITS.get(tri, False)
                s.add_xor_clause([tri[0] + 1, tri[1] + 1, tri[2] + 1], rhs)
            res = s.solve()
            if not res[0]:
                # unsat -> comb is an unsat subset; because we iterate by increasing k and pruned supersets,
                # comb is minimal by construction
                found_mus.append(list(comb))
        # small optimization: if we already found MUSes of size 1 then no need to check larger k
        if any(len(m) == 1 for m in found_mus):
            break
    elapsed = time.time() - start
    # translate mus index lists to triad lists for output
    mus_triads = [[rows[i] for i in mus] for mus in found_mus]
    out = {
        "file": entry.get("file"),
        "W_idx": W_idx,
        "n_rows": n,
        "checks": checks,
        "time_seconds": elapsed,
        "mus_count": len(found_mus),
        "mus_indices": found_mus,
        "mus_triads": mus_triads,
    }
    # write per-W artifact
    (ART / f"cryptosat_mus_W{W_idx}.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    summary.append(out)
    print(f"  found {len(found_mus)} MUS(es) in {elapsed:.2f}s (checks={checks})")

# combined output
OUT_ALL.write_text(json.dumps(summary, indent=2), encoding="utf-8")

# small human report
lines = ["# CryptoMiniSat MUS enumeration report", ""]
for r in summary:
    lines.append(
        f"- W={r['W_idx']}: {r['mus_count']} MUS(es), checks={r['checks']}, time={r['time_seconds']:.2f}s"
    )
    for i, mus in enumerate(r["mus_triads"]):
        lines.append(f"  - MUS {i+1} (size {len(mus)}): {mus}")
OUT_MD.write_text("\n".join(lines), encoding="utf-8")
print("Wrote", OUT_ALL, "and", OUT_MD)
