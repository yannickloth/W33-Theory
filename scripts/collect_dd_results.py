#!/usr/bin/env python3
import glob
import json
from pathlib import Path

out = {}
for p in glob.glob("checks/PART_CVII_dd_shrink_result_*.json"):
    j = json.load(open(p, encoding="utf-8"))
    src = j["source_conf_entry"]["file"]
    res = j.get("result", [])
    out.setdefault(src, []).append(
        {
            "path": p,
            "result": res,
            "result_size": j.get("result_size"),
            "time_seconds": j.get("time_seconds"),
        }
    )

s = "\n".join(f"{k} -> {v}" for k, v in out.items())
with open("checks/dd_collect_results.txt", "w", encoding="utf-8") as f:
    f.write(s + "\n\nSummary: total dd_shrink outputs=" + str(len(out)) + "\n")
print("Wrote checks/dd_collect_results.txt")
