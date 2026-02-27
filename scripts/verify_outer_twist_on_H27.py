#!/usr/bin/env python3
"""Verify the outer twist action on H27 using the closed-form formulas.

Requires a bundle directory named "H27_OUTER_TWIST_ACTION_BUNDLE_v01" with
one of the artifacts:
  - outer_twist_action_on_H27.json   (mapping dict)
  - outer_twist_action_table.csv     (explicit 27-row table)

The formulas under test are
    u' = A u + b   with A=[[1,2],[2,0]], b=(0,2)
    t' = 2*t + (2+2*x+y) mod 3

The script compares each entry and returns 0 if all match.
"""

import json, os, sys
import csv
import numpy as np

ROOT = os.getcwd()
bundle = os.path.join(ROOT, "H27_OUTER_TWIST_ACTION_BUNDLE_v01")
if not os.path.isdir(bundle):
    print(f"missing bundle directory {bundle}")
    sys.exit(1)

A = np.array([[1, 2], [2, 0]], dtype=int) % 3
b = np.array([0, 2], dtype=int) % 3

def formula(u,t):
    up = tuple(int(x) for x in (A @ np.array(u) + b) % 3)
    x,y = u
    tp = (2 * t + (2 + 2 * x + y)) % 3
    return up, int(tp)

# load table
mapping = {}
json_path = os.path.join(bundle, "outer_twist_action_on_H27.json")
csv_path = os.path.join(bundle, "outer_twist_action_table.csv")
if os.path.exists(json_path):
    mapping = json.load(open(json_path))
elif os.path.exists(csv_path):
    with open(csv_path) as f:
        rdr = csv.reader(f)
        for row in rdr:
            # expect x,y,t,xp,yp,tp
            x,y,t,xp,yp,tp = map(int, row)
            mapping[(x,y,t)] = ((xp,yp), tp)
else:
    print("no action artifact found in bundle")
    sys.exit(1)

for key, val in mapping.items():
    u = (key[0], key[1])
    t = key[2]
    expected = tuple(val[0]), val[1]
    got = formula(u, t)
    if got != expected:
        print("mismatch", key, got, expected)
        sys.exit(2)

print("ALL CHECKS PASSED: affine u-map and t-map reproduce the full table.")
sys.exit(0)
