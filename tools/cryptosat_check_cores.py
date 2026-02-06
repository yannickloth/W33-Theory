"""Verify unsat cores using pycryptosat XOR clauses"""

import json
import time
from pathlib import Path

from pycryptosat import Solver

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"

suns = json.load(open(ART / "sign_unsat_cores.json", "r", encoding="utf-8"))
with open(ART / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8") as f:
    sdata = json.load(f)
d_map_sign = {
    tuple(sorted(t["triple"])): t["sign"] for t in sdata["solution"]["d_triples"]
}
D_BITS = {
    t: (True if s == -1 else False) for t, s in d_map_sign.items()
}  # parity True=1

for entry in suns:
    if entry.get("solvable", False):
        print("Skipping solvable entry", entry.get("file"))
        continue
    rows = entry.get("certificate_rows")
    if not rows:
        print("Skipping entry with no certificate_rows:", entry.get("file"))
        continue
    print(
        "\nEntry file", entry["file"], "W_idx", entry["W_idx"], "core_size", len(rows)
    )
    s = Solver()
    t0 = time.time()
    for tri in rows:
        tri_t = tuple(sorted(tri))
        rhs = D_BITS.get(tri_t, False)
        # variables are 1-based
        vs = [tri_t[0] + 1, tri_t[1] + 1, tri_t[2] + 1]
        s.add_xor_clause(vs, rhs)
    res = s.solve()
    dt = time.time() - t0
    print("  solve returned", res, "time", dt)
    try:
        print("  conflict:", s.get_conflict())
    except Exception as e:
        print("  get_conflict error:", e)
