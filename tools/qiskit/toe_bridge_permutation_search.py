#!/usr/bin/env python3
"""Grover-style search for exact TOE bridge orderings.

This keeps the first Qiskit TOE search targets conservative by marking only
permutations forced by already-promoted bridge theorems.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter

MODE_FIVE_FACTOR = "five-factor-hierarchy"
MODE_SUPPORT = "support-hierarchy"


def five_factor_items() -> list[str]:
    return ["U1", "U2", "U3", "E8_1", "E8_2"]


def five_factor_predicate(ordering: tuple[str, ...]) -> bool:
    pos = {name: idx for idx, name in enumerate(ordering)}
    return pos["U3"] < pos["U1"] < pos["U2"] and pos["E8_2"] < pos["E8_1"]


def support_items() -> list[str]:
    return ["head_line", "u1_plane", "transport_avatar", "u3_local", "e8_2_local"]


def support_predicate(ordering: tuple[str, ...]) -> bool:
    pos = {name: idx for idx, name in enumerate(ordering)}
    return pos["head_line"] < pos["u1_plane"] < pos["transport_avatar"]


def marked_permutations(mode: str) -> tuple[list[str], list[str], list[str], list[tuple[str, ...]]]:
    if mode == MODE_FIVE_FACTOR:
        items = five_factor_items()
        constraints = [
            "hyperbolic packet order: U3 before U1 before U2",
            "exceptional packet order: E8_2 before E8_1",
        ]
        sources = [
            "exploration/w33_selector_a4_weight_hierarchy_bridge.py",
            "exploration/w33_global_local_carrier_split_bridge.py",
        ]
        predicate = five_factor_predicate
    elif mode == MODE_SUPPORT:
        items = support_items()
        constraints = [
            "support hierarchy: head_line before u1_plane before transport_avatar",
            "u3_local and e8_2_local remain free in relative order",
        ]
        sources = [
            "exploration/w33_e13_a4_support_stratification_bridge.py",
            "exploration/w33_yukawa_transport_coupling_hierarchy_bridge.py",
        ]
        predicate = support_predicate
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    perms = list(itertools.permutations(items))
    marks = [perm for perm in perms if predicate(perm)]
    return items, constraints, sources, marks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run an exact TOE bridge permutation Grover search.")
    parser.add_argument(
        "--mode",
        choices=[MODE_FIVE_FACTOR, MODE_SUPPORT],
        default=MODE_FIVE_FACTOR,
        help="Theorem-backed permutation oracle to use",
    )
    parser.add_argument("--shots", type=int, default=512, help="Number of simulator shots")
    parser.add_argument("--iterations", type=int, default=None, help="Explicit Grover iteration count")
    parser.add_argument("--top", type=int, default=8, help="Number of top bitstrings to decode")
    return parser


def main() -> None:
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    from permutation_grover_search import (
        build_grover_circuit,
        decode_counts,
        grover_iterations,
        normalize_counts,
    )

    args = build_parser().parse_args()

    items, constraints, sources, marked = marked_permutations(args.mode)
    permutations = list(itertools.permutations(items))
    permutation_to_index = {perm: idx for idx, perm in enumerate(permutations)}
    marked_indices = {permutation_to_index[perm] for perm in marked}

    search_space_size = 1 << math.ceil(math.log2(len(permutations)))
    num_qubits = int(math.log2(search_space_size))
    iterations = args.iterations or grover_iterations(search_space_size, len(marked_indices))

    circuit = build_grover_circuit(num_qubits, marked_indices, iterations)
    simulator = AerSimulator()
    compiled = transpile(circuit, simulator, optimization_level=1)
    result = simulator.run(compiled, shots=args.shots).result()
    counts = Counter(result.get_counts())
    decoded_valid, decoded_invalid = decode_counts(counts, permutations, args.top)

    summary = {
        "search_name": "toe_bridge_permutation_search",
        "oracle_mode": args.mode,
        "items": items,
        "theorem_constraints": constraints,
        "theorem_sources": sources,
        "permutation_count": len(permutations),
        "marked_count": len(marked_indices),
        "marked_fraction_of_permutations": len(marked_indices) / len(permutations),
        "search_space_size": search_space_size,
        "num_qubits": num_qubits,
        "grover_iterations": iterations,
        "shots": args.shots,
        "marked_permutations": [list(perm) for perm in marked],
        "marked_indices": sorted(marked_indices),
        "top_counts": normalize_counts(counts, args.shots)[: args.top],
        "decoded_valid_hits": decoded_valid,
        "decoded_invalid_hits": decoded_invalid,
        "target_hit_count": sum(
            count for bitstring, count in counts.items() if int(bitstring, 2) in marked_indices
        ),
        "target_hit_probability": sum(
            count for bitstring, count in counts.items() if int(bitstring, 2) in marked_indices
        )
        / args.shots,
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
