#!/usr/bin/env python3
import glob
import json

files = sorted(glob.glob("checks/PART_CVII_dd_shrink_result_*.json"))
errs = 0
for p in files:
    try:
        json.load(open(p, "r", encoding="utf-8"))
    except Exception as e:
        print("BAD JSON:", p, "->", e)
        errs += 1
print("Done, errors:", errs)
