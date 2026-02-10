#!/usr/bin/env python3
"""
Watch `artifacts/more_new_work_extracted` for new or modified ChatGPT bundles
and run `tools/auto_ingest_bundle.py` on detection.

Usage:
  py -3 tools/watch_chatgpt52.py --interval 30 --push

Behavior:
  - Polls the directory every `--interval` seconds.
  - Tracks mtimes of `toe_coupling_strengths_*.json` files and triggers processing
    when a file is new or its mtime changes.
  - Writes `artifacts/bundle_watch_state.json` and per-run logs to `artifacts/auto_watch_reports/`.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SEARCH_ROOT = ROOT / "artifacts" / "more_new_work_extracted"
STATE_FILE = ROOT / "artifacts" / "bundle_watch_state.json"
LOG_DIR = ROOT / "artifacts" / "auto_watch_reports"


def load_state() -> Dict[str, float]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(state: Dict[str, float]):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def find_coupling_files() -> Dict[str, float]:
    res = {}
    if not SEARCH_ROOT.exists():
        return res
    for p in SEARCH_ROOT.rglob("toe_coupling_strengths_*.json"):
        try:
            res[str(p)] = p.stat().st_mtime
        except Exception:
            continue
    return res


def run_auto_ingest(bundle_dir: Path, push: bool = False, extended_repair: bool = False, dry_run: bool = False):
    out_dir = ROOT / "artifacts" / "bundles" / bundle_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "tools/auto_ingest_bundle.py", "--bundle-dir", str(bundle_dir), "--out-dir", str(out_dir)]
    if push:
        cmd.append("--push")
    if extended_repair:
        cmd.append("--extended-repair")
    if dry_run:
        cmd.append("--dry-run")
    print("Triggering auto-ingest for:", bundle_dir)
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    log = {
        "bundle": str(bundle_dir),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "ts": time.time(),
    }
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logpath = LOG_DIR / f"ingest_{bundle_dir.name}_{int(time.time())}.json"
    logpath.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"Wrote log: {logpath}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--interval", type=int, default=30)
    p.add_argument("--push", action="store_true")
    p.add_argument("--extended-repair", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    print("Watching for ChatGPT bundle updates under:", SEARCH_ROOT)

    state = load_state()
    try:
        while True:
            files = find_coupling_files()
            for fpath, mtime in files.items():
                prev = state.get(fpath)
                if prev is None or float(mtime) > float(prev):
                    # Trigger processing on bundle directory
                    bundle_dir = Path(fpath).parent
                    print("Detected new/updated coupling file:", fpath)
                    run_auto_ingest(bundle_dir, push=args.push, extended_repair=args.extended_repair, dry_run=args.dry_run)
                    state[fpath] = mtime
                    save_state(state)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Watcher stopped by user")


if __name__ == "__main__":
    main()
