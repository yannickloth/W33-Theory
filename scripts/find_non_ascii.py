#!/usr/bin/env python3
"""Find non-ASCII characters in one or more files."""

from __future__ import annotations

import argparse
from pathlib import Path


def scan(path: Path) -> list[tuple[int, int, int, str]]:
    text = path.read_text(encoding="utf-8")
    rows: list[tuple[int, int, int, str]] = []
    line = 1
    col = 0
    for idx, ch in enumerate(text):
        if ch == "\n":
            line += 1
            col = 0
            continue
        col += 1
        if ord(ch) > 127:
            rows.append((idx, line, col, ch))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[Path("proofs/lean/z22_exclusion.lean")],
    )
    args = parser.parse_args()

    found = False
    for path in args.paths:
        rows = scan(path)
        if not rows:
            print(f"{path}: clean (ASCII-only)")
            continue
        found = True
        print(f"{path}: {len(rows)} non-ASCII characters")
        for idx, line, col, ch in rows[:50]:
            escaped = ch.encode("unicode_escape").decode("ascii")
            print(
                f"  idx={idx} line={line} col={col} char='{escaped}' codepoint=U+{ord(ch):04X}"
            )
        if len(rows) > 50:
            print(f"  ... and {len(rows) - 50} more")

    if found:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
