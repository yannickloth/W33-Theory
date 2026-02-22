#!/usr/bin/env python3
"""
List top N most recently modified files in the workspace (timestamp, size, path).
Writes to stdout and to artifacts/recent_files.json.
Adds robust exception handling and prints errors to stderr for debugging when run from the terminal.
"""
import argparse
import json
import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--n", type=int, default=200)
args = parser.parse_args()


def main():
    try:
        files = []
        for p in ROOT.rglob("*"):
            try:
                if p.is_file():
                    stat = p.stat()
                    files.append(
                        {"path": str(p), "mtime": stat.st_mtime, "size": stat.st_size}
                    )
            except Exception:
                # capture any file-specific errors
                print("warning: failed to stat", p, file=sys.stderr)
        files.sort(key=lambda x: x["mtime"], reverse=True)
        sel = files[: args.n]
        # format timestamp
        import datetime

        for it in sel:
            it["mtime_iso"] = datetime.datetime.fromtimestamp(it["mtime"]).isoformat(
                sep=" ", timespec="seconds"
            )
        print(
            "\n".join([f"{it['mtime_iso']}\t{it['size']}\t{it['path']}" for it in sel])
        )
        # write json artifact
        outp = ROOT / "artifacts" / "recent_files.json"
        outp.parent.mkdir(exist_ok=True)
        outp.write_text(json.dumps(sel, indent=2), encoding="utf-8")
        print(f"\nWrote {outp}")
    except Exception:
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()

files = []
for p in ROOT.rglob("*"):
    try:
        if p.is_file():
            stat = p.stat()
            files.append({"path": str(p), "mtime": stat.st_mtime, "size": stat.st_size})
    except Exception:
        pass

files.sort(key=lambda x: x["mtime"], reverse=True)
sel = files[: args.n]
# format timestamp
import datetime

for it in sel:
    it["mtime_iso"] = datetime.datetime.fromtimestamp(it["mtime"]).isoformat(
        sep=" ", timespec="seconds"
    )

import sys

print("\n".join([f"{it['mtime_iso']}\t{it['size']}\t{it['path']}" for it in sel]))

# write json artifact
outp = ROOT / "artifacts" / "recent_files.json"
outp.parent.mkdir(exist_ok=True)
outp.write_text(json.dumps(sel, indent=2), encoding="utf-8")
print(f"\nWrote {outp}")
