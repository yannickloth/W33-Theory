#!/usr/bin/env python3
import json
from collections import Counter

s = json.load(open("checks/PART_CVII_e8_embedding_attempt_seed.json"))
roots = [sd["root_index"] for sd in s.get("seed_edges", [])]
print("seed edges:", len(roots), "unique roots:", len(set(roots)))
for r, n in Counter(roots).items():
    if n > 1:
        print("duplicate root", r, "count", n)
