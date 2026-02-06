#!/usr/bin/env python3
"""
List modification times for a selected set of important files (tools/*.py, artifacts/*.json, top-level *.md, *.py).
Writes results to artifacts/recent_selected.json and prints them.
"""
import glob
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
patterns = ["tools/*.py", "tools/*.g*", "artifacts/*.json", "*.md", "*.py"]
paths = []
for pat in patterns:
    paths += glob.glob(pat)
paths = sorted(set(paths))
out = []
for p in paths:
    try:
        m = os.path.getmtime(p)
        out.append(
            {
                "path": p,
                "mtime": m,
                "mtime_iso": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(m)),
                "size": os.path.getsize(p),
            }
        )
    except Exception as e:
        out.append({"path": p, "error": str(e)})
# print and write artifact
for it in out:
    if "mtime_iso" in it:
        print(it["mtime_iso"], it["size"], it["path"])
    else:
        print("ERR", it["path"], it.get("error"))

(Path("artifacts") / "recent_selected.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
print("\nWrote artifacts/recent_selected.json")
