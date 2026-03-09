#!/usr/bin/env python3
"""Report on the live GitHub Pages site.

The repository now keeps a single site source of truth:
    docs/index.html
"""

from __future__ import annotations

from pathlib import Path


DOCS = Path(__file__).parent
OUTPUT = DOCS / "index.html"


def main() -> None:
    html = OUTPUT.read_text(encoding="utf-8")
    print(f"{OUTPUT} is the sole site source — {len(html.splitlines())} lines")


if __name__ == "__main__":
    main()
