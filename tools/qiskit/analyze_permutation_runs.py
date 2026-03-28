#!/usr/bin/env python3
"""Summarize batch Grover permutation search results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze JSON output from permutation_grover_batch.py")
    parser.add_argument("input", type=Path, help="Batch JSON file")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))

    sizes = payload["sizes"]
    best_overall = max(
        (entry["best_run"] for entry in sizes),
        key=lambda run: (run["target_hit_probability"], -run["invalid_hit_probability"]),
    )

    summary = {
        "input": str(args.input),
        "mark_mode": payload["mark_mode"],
        "shots": payload["shots"],
        "size_count": len(sizes),
        "mean_target_hit_probability": sum(entry["best_run"]["target_hit_probability"] for entry in sizes)
        / len(sizes),
        "mean_invalid_hit_probability": sum(entry["best_run"]["invalid_hit_probability"] for entry in sizes)
        / len(sizes),
        "best_overall": {
            "items": best_overall["items"],
            "target_hit_probability": best_overall["target_hit_probability"],
            "invalid_hit_probability": best_overall["invalid_hit_probability"],
            "grover_iterations": best_overall["grover_iterations"],
            "iteration_offset": best_overall["iteration_offset"],
            "marked_permutations": best_overall["marked_permutations"],
        },
        "per_size": [
            {
                "size": entry["size"],
                "target_hit_probability": entry["best_run"]["target_hit_probability"],
                "invalid_hit_probability": entry["best_run"]["invalid_hit_probability"],
                "grover_iterations": entry["best_run"]["grover_iterations"],
                "iteration_offset": entry["best_run"]["iteration_offset"],
            }
            for entry in sizes
        ],
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
