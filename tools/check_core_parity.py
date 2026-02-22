#!/usr/bin/env python3
import json
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / "artifacts"
cores = json.load(open(ART / "sign_unsat_cores.json"))
d = json.load(open(ART / "e6_cubic_sign_gauge_solution.json"))
d_map = {
    tuple(sorted(t["triple"])): 0 if t["sign"] == 1 else 1
    for t in d["solution"]["d_triples"]
}
for c in cores:
    core = c["unsat_core"]
    masks = [0] * len(core)
    rhs = [d_map.get(tuple(sorted(t)), 0) for t in core]
    xor = 0
    for idx, t in enumerate(core):
        mask = 0
        for v in t:
            mask |= 1 << v
        masks[idx] = mask
        xor ^= mask
    counts = {
        v: sum(1 for t in core if v in t) for v in sorted({x for t in core for x in t})
    }
    print(
        f"{c['file']}: xor=={xor==0}, sum(rhs)%2={sum(rhs)%2}, rhs={rhs}, counts={counts}"
    )
