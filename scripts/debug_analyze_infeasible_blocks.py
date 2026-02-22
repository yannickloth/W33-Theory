#!/usr/bin/env python3
"""Debug helper for analyze_infeasible_blocks.py: list INFEASIBLE local seeds and block_edges info
"""
import glob
import json
import time
from pathlib import Path

local_files = sorted(glob.glob("checks/PART_CVII_e8_bijection_local_seed_*.json"))
info = {"stamp": int(time.time()), "checked": []}
for f in local_files:
    j = json.loads(open(f, encoding="utf-8").read())
    s = j.get("status")
    be = j.get("block_edges") if isinstance(j.get("block_edges"), list) else None
    info["checked"].append(
        {
            "file": f,
            "status": s,
            "has_block_edges": bool(be),
            "block_size": len(be) if be else None,
            "start_vertex": j.get("start_vertex"),
        }
    )

out = Path("checks") / f'PART_CVII_infeasible_debug_{info["stamp"]}.json'
out.write_text(json.dumps(info, indent=2), encoding="utf-8")
print("Wrote", out)
