#!/usr/bin/env python3
import glob
import json
import re

files = sorted(glob.glob("checks/dd_targeted_50_51_seed*.json"))
if not files:
    print("No dd_targeted files found.")
    raise SystemExit(0)

for f in files:
    try:
        j = json.load(open(f, "r", encoding="utf-8"))
    except Exception as e:
        print("BAD JSON", f, e)
        continue
    m = re.search(r"seed(\d+)_", f)
    seed = int(m.group(1)) if m else int(j.get("seed"))
    print(f'Seed {seed}: status={j.get("status")}, file={f}')
