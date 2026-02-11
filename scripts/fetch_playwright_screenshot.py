#!/usr/bin/env python3
"""Run Playwright screenshot via Docker MCP and extract the PNG bytes from output.
Saves the screenshot to checks/mcp_playwright_example.png in the workspace.

Usage:
  python scripts/fetch_playwright_screenshot.py [--outfile path]
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys

DEFAULT_OUT = os.path.join("checks", "mcp_playwright_example.png")
DOCKER_EXE = r"C:\Program Files\Docker\Docker\resources\bin\docker.exe"


def run_screenshot(outfile: str) -> int:
    args = [
        DOCKER_EXE,
        "mcp",
        "tools",
        "call",
        "browser_take_screenshot",
        f"type=png",
        f"filename={outfile}",
    ]
    try:
        proc = subprocess.run(
            args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
        )
    except FileNotFoundError:
        print(f"Docker executable not found at {DOCKER_EXE}", file=sys.stderr)
        return 2

    out = proc.stdout.decode(errors="ignore")
    # Try to find a bracketed decimal byte array that looks like a PNG (137 80 78 71)
    candidates = re.findall(r"\[([0-9,\s]+)\]", out)
    png_bytes = None
    for c in candidates:
        if "137 80 78 71" in c:
            nums = re.findall(r"\d+", c)
            try:
                data = bytes(int(x) for x in nums)
                # sanity check: PNG magic header
                if data.startswith(b"\x89PNG\r\n\x1a\n"):
                    png_bytes = data
                    break
            except Exception:
                continue

    if png_bytes is None:
        print(
            "Failed to locate PNG bytes in tool output. Full output below:\n",
            file=sys.stderr,
        )
        print(out, file=sys.stderr)
        return 1

    # Ensure output dir exists
    outdir = os.path.dirname(outfile) or "."
    os.makedirs(outdir, exist_ok=True)
    with open(outfile, "wb") as f:
        f.write(png_bytes)

    print(f"WROTE {outfile} ({len(png_bytes)} bytes)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outfile", default=DEFAULT_OUT)
    args = parser.parse_args()
    return run_screenshot(args.outfile)


if __name__ == "__main__":
    raise SystemExit(main())
