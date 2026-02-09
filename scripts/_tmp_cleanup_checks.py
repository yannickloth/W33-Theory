#!/usr/bin/env python3
"""Move transient _tmp_* files from checks/ into checks/archive/ and write a JSON log.
"""
import json
import shutil
import time
from pathlib import Path

CHECKS = Path("checks")
ARCH = CHECKS / "archive"
ARCH.mkdir(parents=True, exist_ok=True)

moved = []
# Patterns matching transient tmp files at top-level of checks
for p in sorted(CHECKS.glob("_tmp*")):
    if p.is_file():
        dest = ARCH / p.name
        shutil.move(str(p), str(dest))
        moved.append({"src": str(p), "dst": str(dest)})
# Also move any files matching *_tmp_*.json
for p in sorted(CHECKS.glob("*_tmp_*.json")):
    if p.is_file():
        dest = ARCH / p.name
        shutil.move(str(p), str(dest))
        moved.append({"src": str(p), "dst": str(dest)})

stamp = int(time.time())
log = CHECKS / f"PART_CVII_repo_cleanup_log_{stamp}.json"
log.write_text(
    json.dumps({"moved": moved, "timestamp": stamp}, indent=2), encoding="utf-8"
)
print("Moved", len(moved), "files. Log at", log)
