#!/usr/bin/env python3
"""Classify a dirty worktree for safe repo cleanup.

This is intentionally non-destructive. It helps separate:

- active source work
- generated artifacts
- archive churn
- root-level drop bundles / deliverables

from one another before any cleanup pass.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]


def git_status_lines() -> list[str]:
    out = subprocess.check_output(
        ["git", "status", "--porcelain=v1"],
        cwd=ROOT,
        text=True,
    )
    return [line for line in out.splitlines() if line]


def classify_path(path: str) -> str:
    top = path.split("/", 1)[0]
    root_level = "/" not in path

    if root_level and path in {
        "README.md",
        "LICENSE",
        "Makefile",
        "CITATION.cff",
        "CONTRIBUTING.md",
    }:
        return "repo_entrypoint"
    if root_level and path == "Pasted text.txt":
        return "root_drop"
    if root_level and path.endswith(".zip"):
        return "root_drop"
    if root_level and path.startswith("TOE_") and (
        "deliverable" in path or "bundle" in path
    ):
        return "root_drop"
    if root_level and path.endswith(".py") and (
        path.startswith("SOLVE_") or path.replace(".py", "").isupper()
    ):
        return "legacy_root_script"
    if path.startswith("archive/"):
        return "archive"
    if path.startswith("bundles/"):
        return "generated_artifact"
    if path.startswith("data/"):
        return "generated_artifact"
    if path.startswith("tools/artifacts/"):
        return "generated_artifact"
    if path.startswith("V") and "_output" in path:
        return "generated_artifact"
    if top in {"docs", "README.md", "exploration", "tests", "tools", "scripts"}:
        return "source_surface"
    if root_level and path.endswith((".md", ".py", ".txt", ".json")):
        return "root_loose_file"
    return "other"


def build_report(lines: Iterable[str]) -> dict[str, object]:
    status_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    top_level_counts: Counter[str] = Counter()
    by_category: dict[str, list[dict[str, str]]] = defaultdict(list)

    for line in lines:
        status = line[:2]
        path = line[3:]
        category = classify_path(path)
        top = path.split("/", 1)[0]

        status_counts[status] += 1
        category_counts[category] += 1
        top_level_counts[top] += 1
        by_category[category].append({"status": status, "path": path})

    return {
        "repo_root": str(ROOT),
        "total_dirty_entries": sum(status_counts.values()),
        "status_counts": dict(status_counts),
        "category_counts": dict(category_counts),
        "top_level_counts": dict(top_level_counts.most_common()),
        "examples": {
            category: items[:20] for category, items in sorted(by_category.items())
        },
        "verdict": (
            "Use this report to clean generated and drop-in content first. "
            "Do not hide or delete source_surface files without an explicit decision."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of a text summary",
    )
    args = parser.parse_args()

    report = build_report(git_status_lines())
    if args.json:
        print(json.dumps(report, indent=2))
        return

    print(f"Repo root: {report['repo_root']}")
    print(f"Dirty entries: {report['total_dirty_entries']}")
    print("\nStatus counts:")
    for status, count in report["status_counts"].items():
        print(f"  {status!r}: {count}")
    print("\nCategory counts:")
    for category, count in sorted(
        report["category_counts"].items(),
        key=lambda item: (-item[1], item[0]),
    ):
        print(f"  {category}: {count}")
    print("\nTop-level counts:")
    for top, count in list(report["top_level_counts"].items())[:20]:
        print(f"  {top}: {count}")
    print("\nExamples:")
    for category, items in report["examples"].items():
        print(f"  [{category}]")
        for item in items[:5]:
            print(f"    {item['status']} {item['path']}")
    print(f"\n{report['verdict']}")


if __name__ == "__main__":
    main()
