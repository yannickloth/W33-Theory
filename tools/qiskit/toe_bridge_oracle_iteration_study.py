#!/usr/bin/env python3
"""Run small seeded iteration studies for TOE-specific Qiskit bridge oracles."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_QISKIT_PYTHON = "/home/wiljd/.venvs/qiskit-local/bin/python"

TARGETS = {
    "support": {
        "script": ROOT / "tools" / "qiskit" / "toe_support_hierarchy_search.py",
        "base_args": [],
    },
    "support-diagnostic": {
        "script": ROOT / "tools" / "qiskit" / "toe_support_diagnostic_search.py",
        "base_args": [],
    },
    "double-interleaving-exact": {
        "script": ROOT / "tools" / "qiskit" / "toe_double_interleaving_shadow_search.py",
        "base_args": ["--relaxation", "exact"],
    },
    "double-interleaving-support-relaxed": {
        "script": ROOT / "tools" / "qiskit" / "toe_double_interleaving_shadow_search.py",
        "base_args": ["--relaxation", "support-interleaving-relaxed"],
    },
    "product": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_product_search.py",
        "base_args": ["--mode", "formal-completion"],
    },
    "line-factor": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_line_factor_search.py",
        "base_args": ["--mode", "formal-completion"],
    },
    "weight-filter": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_weight_filter_search.py",
        "base_args": ["--mode", "formal-completion"],
    },
    "split-weight": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_split_weight_filter_search.py",
        "base_args": ["--mode", "formal-completion"],
    },
    "diagnostic-order": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_order_search.py",
        "base_args": ["--mode", "formal-completion"],
    },
    "diagnostic-relaxation-exact": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_relaxation_search.py",
        "base_args": ["--mode", "formal-completion", "--relaxation", "exact"],
    },
    "diagnostic-relaxation-exceptional": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_relaxation_search.py",
        "base_args": ["--mode", "formal-completion", "--relaxation", "exceptional-order-relaxed"],
    },
    "diagnostic-relaxation-hyperbolic": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_relaxation_search.py",
        "base_args": ["--mode", "formal-completion", "--relaxation", "hyperbolic-order-relaxed"],
    },
    "diagnostic-relaxation-both": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_relaxation_search.py",
        "base_args": ["--mode", "formal-completion", "--relaxation", "both-orders-relaxed"],
    },
    "enhancement-factor": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_enhancement_factor_search.py",
        "base_args": ["--mode", "formal-completion-avatar"],
    },
    "cocycle-compatibility-all": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_cocycle_compatibility_search.py",
        "base_args": ["--focus", "all-compatible"],
    },
    "cocycle-compatibility-nonzero": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_cocycle_compatibility_search.py",
        "base_args": ["--focus", "nonzero-compatible"],
    },
    "diagnostic-enhancement-exact": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_enhancement_relaxation_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "exact"],
    },
    "diagnostic-enhancement-exceptional": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_enhancement_relaxation_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "exceptional-order-relaxed"],
    },
    "diagnostic-enhancement-hyperbolic": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_enhancement_relaxation_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "hyperbolic-order-relaxed"],
    },
    "diagnostic-enhancement-both": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_enhancement_relaxation_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "both-orders-relaxed"],
    },
    "diagnostic-slot-exact": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_enhancement_slot_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "exact"],
    },
    "diagnostic-slot-exceptional": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_enhancement_slot_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "exceptional-order-relaxed"],
    },
    "diagnostic-slot-hyperbolic": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_enhancement_slot_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "hyperbolic-order-relaxed"],
    },
    "diagnostic-slot-both": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_enhancement_slot_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "both-orders-relaxed"],
    },
    "enhancement-relaxation-exact": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_enhancement_relaxation_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "exact"],
    },
    "enhancement-relaxation-exceptional": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_enhancement_relaxation_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "exceptional-order-relaxed"],
    },
    "enhancement-relaxation-hyperbolic": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_enhancement_relaxation_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "hyperbolic-order-relaxed"],
    },
    "enhancement-relaxation-both": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_enhancement_relaxation_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "both-orders-relaxed"],
    },
    "support-enhancement-exact": {
        "script": ROOT / "tools" / "qiskit" / "toe_support_enhancement_relaxation_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "exact"],
    },
    "support-enhancement-interleaving": {
        "script": ROOT / "tools" / "qiskit" / "toe_support_enhancement_relaxation_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "interleaving-relaxed"],
    },
    "support-enhancement-core": {
        "script": ROOT / "tools" / "qiskit" / "toe_support_enhancement_relaxation_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "core-order-relaxed"],
    },
    "support-enhancement-both": {
        "script": ROOT / "tools" / "qiskit" / "toe_support_enhancement_relaxation_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "both-relaxed"],
    },
    "support-cocycle-nonzero-exact": {
        "script": ROOT / "tools" / "qiskit" / "toe_support_cocycle_compatibility_relaxation_search.py",
        "base_args": ["--focus", "nonzero-compatible", "--relaxation", "exact"],
    },
    "support-cocycle-nonzero-interleaving": {
        "script": ROOT / "tools" / "qiskit" / "toe_support_cocycle_compatibility_relaxation_search.py",
        "base_args": ["--focus", "nonzero-compatible", "--relaxation", "interleaving-relaxed"],
    },
    "support-cocycle-nonzero-core": {
        "script": ROOT / "tools" / "qiskit" / "toe_support_cocycle_compatibility_relaxation_search.py",
        "base_args": ["--focus", "nonzero-compatible", "--relaxation", "core-order-relaxed"],
    },
    "support-cocycle-nonzero-both": {
        "script": ROOT / "tools" / "qiskit" / "toe_support_cocycle_compatibility_relaxation_search.py",
        "base_args": ["--focus", "nonzero-compatible", "--relaxation", "both-relaxed"],
    },
    "diagnostic-cocycle-nonzero-exact": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_cocycle_compatibility_relaxation_search.py",
        "base_args": ["--focus", "nonzero-compatible", "--relaxation", "exact"],
    },
    "diagnostic-cocycle-nonzero-exceptional": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_cocycle_compatibility_relaxation_search.py",
        "base_args": ["--focus", "nonzero-compatible", "--relaxation", "exceptional-order-relaxed"],
    },
    "diagnostic-cocycle-nonzero-hyperbolic": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_cocycle_compatibility_relaxation_search.py",
        "base_args": ["--focus", "nonzero-compatible", "--relaxation", "hyperbolic-order-relaxed"],
    },
    "diagnostic-cocycle-nonzero-both": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_cocycle_compatibility_relaxation_search.py",
        "base_args": ["--focus", "nonzero-compatible", "--relaxation", "both-orders-relaxed"],
    },
    "diagnostic-enhancement-slot-current-both": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_enhancement_slot_search.py",
        "base_args": ["--mode", "current-k3-zero-orbit", "--relaxation", "both-orders-relaxed"],
    },
    "diagnostic-enhancement-slot-minimal-both": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_enhancement_slot_search.py",
        "base_args": ["--mode", "minimal-external-enhancement", "--relaxation", "both-orders-relaxed"],
    },
    "diagnostic-enhancement-slot-formal-both": {
        "script": ROOT / "tools" / "qiskit" / "toe_bridge_diagnostic_enhancement_slot_search.py",
        "base_args": ["--mode", "formal-completion-avatar", "--relaxation", "both-orders-relaxed"],
    },
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Study target-hit probability near a chosen Grover iteration window.")
    parser.add_argument("--target", choices=sorted(TARGETS), required=True, help="Which TOE oracle to study")
    parser.add_argument("--iterations", nargs="+", type=int, required=True, help="Iteration counts to probe")
    parser.add_argument("--seeds", nargs="+", type=int, required=True, help="Seeds to probe")
    parser.add_argument("--shots", type=int, default=256, help="Shots per run")
    parser.add_argument("--top", type=int, default=6, help="Top decoded entries to keep")
    return parser


def run_one(target: str, iteration: int, seed: int, shots: int, top: int) -> dict[str, Any]:
    config = TARGETS[target]
    python_cmd = (
        os.environ.get("QISKIT_PYTHON")
        or shutil.which("qiskit-python")
        or DEFAULT_QISKIT_PYTHON
    )
    cmd = [
        python_cmd,
        str(config["script"]),
        *config["base_args"],
        "--shots",
        str(shots),
        "--top",
        str(top),
        "--seed",
        str(seed),
        "--iterations",
        str(iteration),
    ]
    text = subprocess.check_output(cmd, cwd=ROOT, text=True)
    return json.loads(text)


def main() -> None:
    args = build_parser().parse_args()

    rows = []
    for iteration in args.iterations:
        runs = [
            run_one(args.target, iteration=iteration, seed=seed, shots=args.shots, top=args.top)
            for seed in args.seeds
        ]
        probs = [run["target_hit_probability"] for run in runs]
        rows.append(
            {
                "iterations": iteration,
                "seeds": args.seeds,
                "target_probabilities": probs,
                "mean_target_hit_probability": statistics.mean(probs),
                "min_target_hit_probability": min(probs),
                "max_target_hit_probability": max(probs),
            }
        )

    payload = {
        "study_name": "toe_bridge_oracle_iteration_study",
        "target": args.target,
        "shots": args.shots,
        "top": args.top,
        "rows": rows,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
