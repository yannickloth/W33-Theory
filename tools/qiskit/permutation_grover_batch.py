#!/usr/bin/env python3
"""Batch runner for small Grover-style permutation searches."""

from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a sweep of permutation Grover experiments.")
    parser.add_argument("--min-size", type=int, default=3, help="Minimum item count")
    parser.add_argument("--max-size", type=int, default=5, help="Maximum item count")
    parser.add_argument("--shots", type=int, default=1024, help="Shots per experiment")
    parser.add_argument("--top", type=int, default=8, help="Top decoded entries to keep")
    parser.add_argument(
        "--mark-mode",
        choices=["identity", "identity-reverse", "identity-adjacent-swap"],
        default="identity-reverse",
        help="How to choose marked permutations for each size",
    )
    parser.add_argument(
        "--iteration-offsets",
        nargs="*",
        type=int,
        default=[0],
        help="Offsets to apply around the auto Grover iteration count",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional JSON output path for the batch summary",
    )
    return parser


def marks_for_mode(items: list[str], mode: str) -> list[str]:
    identity = ",".join(items)
    reverse = ",".join(reversed(items))
    if mode == "identity":
        return [identity]
    if mode == "identity-reverse":
        return [identity, reverse]
    if mode == "identity-adjacent-swap":
        swapped = items[:]
        if len(swapped) >= 2:
            swapped[0], swapped[1] = swapped[1], swapped[0]
        return [identity, ",".join(swapped)]
    raise ValueError(f"Unsupported mark mode: {mode}")


def run_one(
    repo_root: Path,
    items: list[str],
    marks: list[str],
    shots: int,
    top: int,
    iteration_offset: int,
) -> dict[str, object]:
    script = repo_root / "tools" / "qiskit" / "permutation_grover_search.py"
    cmd = [sys.executable, str(script), "--items", *items]
    for mark in marks:
        cmd += ["--mark", mark]
    cmd += ["--shots", str(shots), "--top", str(top)]

    baseline = json.loads(
        subprocess.check_output(cmd, cwd=repo_root, text=True)
    )
    explicit_iterations = max(1, int(baseline["grover_iterations"]) + iteration_offset)
    if iteration_offset != 0:
        cmd += ["--iterations", str(explicit_iterations)]
        summary = json.loads(subprocess.check_output(cmd, cwd=repo_root, text=True))
    else:
        summary = baseline

    summary["iteration_offset"] = iteration_offset
    summary["marked_count"] = len(summary["marked_permutations"])
    summary["invalid_hit_probability"] = sum(
        entry["count"] for entry in summary["decoded_invalid_hits"]
    ) / summary["shots"]
    return summary


def score(summary: dict[str, object]) -> tuple[float, float]:
    return (
        float(summary["target_hit_probability"]),
        -float(summary["invalid_hit_probability"]),
    )


def main() -> None:
    args = build_parser().parse_args()
    repo_root = Path(__file__).resolve().parents[2]

    results = []
    for size in range(args.min_size, args.max_size + 1):
        items = [str(i) for i in range(size)]
        marks = marks_for_mode(items, args.mark_mode)
        size_runs = []
        for offset in args.iteration_offsets:
            size_runs.append(run_one(repo_root, items, marks, args.shots, args.top, offset))
        size_runs.sort(key=score, reverse=True)
        best = size_runs[0]
        results.append(
            {
                "size": size,
                "items": items,
                "marks": marks,
                "runs": size_runs,
                "best_run": best,
            }
        )

    payload = {
        "mark_mode": args.mark_mode,
        "shots": args.shots,
        "top": args.top,
        "iteration_offsets": args.iteration_offsets,
        "sizes": results,
    }

    text = json.dumps(payload, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
