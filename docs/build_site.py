#!/usr/bin/env python3
"""Publish the GitHub Pages site from the preserved HTML source."""

from __future__ import annotations

from pathlib import Path


DOCS = Path(__file__).parent
SOURCE = DOCS / "index_source.html"
OUTPUT = DOCS / "index.html"


def main() -> None:
    html = SOURCE.read_text(encoding="utf-8")
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"{OUTPUT} written — {len(html.splitlines())} lines")


if __name__ == "__main__":
    main()
