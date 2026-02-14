#!/usr/bin/env python3
"""Monitor exhaustive verifier artifact and push verified artifacts.

Behavior:
- Polls `artifacts/hybrid_linfty_candidate_verification.json` until the
  exhaustive-sector verifier appears to have finished.
- If *all* sectors passed, stages + commits all workspace changes and pushes.
- If verification completed but **failed**, prints the failing-sector details
  and exits without committing the promoted candidate.

This script is intended to be run in the repo root (it uses relative paths).
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "hybrid_linfty_candidate_verification.json"
# expected exhaustive counts (combinatorial)
EXP_G1G1G2 = 262440
EXP_G1G2G2 = 262440
EXP_G2G2G2 = 85320

SLEEP = 15.0

print("monitor: waiting for verifier artifact →", ART)
while True:
    if not ART.exists():
        print("monitor: artifact not present yet — sleeping...")
        time.sleep(SLEEP)
        continue
    try:
        j = json.loads(ART.read_text(encoding="utf-8"))
    except Exception as e:
        print("monitor: failed to read JSON (will retry):", e)
        time.sleep(SLEEP)
        continue

    s = j.get("sectors", {})
    g1 = s.get("g1_g1_g2", {})
    g2 = s.get("g1_g2_g2", {})
    g22 = s.get("g2_g2_g2", {})
    tested_msg = f"g1.tested={g1.get('tested')} g2.tested={g2.get('tested')} g22.tested={g22.get('tested')} elapsed={j.get('elapsed_sec')}"
    print("monitor:", tested_msg)

    # finished & all passed
    if bool(g1.get("passed")) and bool(g2.get("passed")) and bool(g22.get("passed")):
        print("VERIFIER_DONE: ALL SECTORS PASSED — proceeding to commit & push")
        all_passed = True
        break

    # finished but still failing (tested reached combinatorial totals)
    if (
        int(g1.get("tested", 0)) >= EXP_G1G1G2
        and int(g2.get("tested", 0)) >= EXP_G1G2G2
        and int(g22.get("tested", 0)) >= EXP_G2G2G2
    ):
        print("VERIFIER_DONE: run complete but some sectors failed")
        all_passed = False
        break

    # otherwise still running
    time.sleep(SLEEP)

# After the loop: act depending on verification outcome
if not all_passed:
    print("Final sector summaries:")
    print(json.dumps({"g1_g1_g2": g1, "g1_g2_g2": g2, "g2_g2_g2": g22}, indent=2))
    print("No commit/push performed. Inspect failing triples or run targeted repair.")
    sys.exit(2)

# all_passed == True -> commit & push changes
# check for uncommitted changes
st = subprocess.run(
    ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True
)
if not st.stdout.strip():
    print("Nothing to commit (working tree clean). Exiting.")
    sys.exit(0)

# stage everything and commit
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
commit_msg = (
    "Promote rational l3 candidate (triad-3 = 1) — exhaustive verification passed; "
    "add hybrid LSQ→CP‑SAT seeders, CE2→l4 assembly, and verification helpers"
)
cm = subprocess.run(
    ["git", "commit", "-m", commit_msg], cwd=ROOT, capture_output=True, text=True
)
print(cm.stdout)
if cm.returncode != 0:
    print("git commit failed:", cm.stderr)
    sys.exit(cm.returncode)

# push
push = subprocess.run(["git", "push"], cwd=ROOT, capture_output=True, text=True)
print(push.stdout)
if push.returncode == 0:
    print("PUSH_OK — changes are on the remote.")
    sys.exit(0)
else:
    print("git push failed:", push.stderr)
    sys.exit(push.returncode)
