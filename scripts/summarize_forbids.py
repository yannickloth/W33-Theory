#!/usr/bin/env python3
"""Summarize checks/PART_CVII_forbids.json into a compact hotspot report.
Writes checks/PART_CVII_forbids_summary.json and prints a human summary.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

CHECKS = Path("checks")
FORB = CHECKS / "PART_CVII_forbids.json"
OUT = CHECKS / "PART_CVII_forbids_summary.json"

if not FORB.exists():
    print("No forbids file found")
    raise SystemExit(0)

j = json.loads(FORB.read_text(encoding="utf-8"))
sets = j.get("obstruction_sets", [])
edge_counts = Counter()
root_counts = Counter()
size_counts = Counter()
entries = []
for s in sets:
    st = tuple(s.get("set", []))
    roots = tuple(s.get("roots", []))
    timestamp = s.get("timestamp")
    entries.append({"set": st, "roots": roots, "timestamp": timestamp})
    edge_counts.update(st)
    root_counts.update(roots)
    size_counts.update([len(st)])

summary = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "num_entries": len(entries),
    "size_counts": dict(size_counts),
    "top_edges": edge_counts.most_common(10),
    "top_roots": root_counts.most_common(10),
    "entries": entries,
}
OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

# human-friendly print
print(f"Forbids entries: {summary['num_entries']}")
print("Set size distribution:", summary["size_counts"])
print("\nTop edges (edge_index:count):")
for e, c in summary["top_edges"]:
    print(f"  {e}: {c}")
print("\nTop roots (root_index:count):")
for r, c in summary["top_roots"]:
    print(f"  {r}: {c}")
print("\nWrote summary to", OUT)
