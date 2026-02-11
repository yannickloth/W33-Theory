#!/usr/bin/env python3
import json
from pathlib import Path

p = Path("checks/PART_CVII_forbids.json")
if not p.exists():
    print("No forbids file found")
    raise SystemExit(0)

j = json.loads(open(p, encoding="utf-8").read())
sets = j.get("obstruction_sets", [])
seen = {}
clean = []
for s in sets:
    key = tuple(sorted(s.get("set", [])))
    if key in seen:
        if s.get("timestamp", 0) < seen[key].get("timestamp", 10**18):
            seen[key] = s
    else:
        seen[key] = s

for k, v in sorted(seen.items(), key=lambda kv: kv[1].get("timestamp", 0)):
    clean.append(v)

out = {"obstruction_sets": clean}
open(p, "w", encoding="utf-8").write(json.dumps(out, indent=2))
print("Wrote cleaned forbids file with", len(clean), "entries")
# mirror to committed_artifacts
(Path("committed_artifacts") / p.name).write_text(
    open(p, encoding="utf-8").read(), encoding="utf-8"
)
print("Mirrored cleaned forbids")
