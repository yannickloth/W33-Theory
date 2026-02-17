#!/usr/bin/env python3
from pathlib import Path

p = Path("artifacts/ce2_rational_local_solutions.json")
if not p.exists():
    print("MISSING")
    raise SystemExit(1)
key = "0,0:1,1:21,2"
with p.open("r", encoding="utf-8") as f:
    for n, line in enumerate(f, start=1):
        if key in line:
            print("FOUND", key, "on line", n)
            print(line.strip())
            raise SystemExit(0)
print("NOT FOUND")
