#!/usr/bin/env python3
"""Grover-style search for the exact TOE bridge support hierarchy.

This is the first repo-specific Qiskit search target. It searches over support
permutations and marks exactly those compatible with the currently proved bridge
hierarchy:

- the central 2E13 image channel lives on the head-compatible line
- the first family-sensitive A4 packet has minimal carrier U1
- the transport completion lives on the full avatar
- the local U3 and E8_2 packets remain free in relative order
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter

from qiskit import transpile
from qiskit_aer import AerSimulator

from permutation_grover_search import (
    build_grover_circuit,
    decode_counts,
    grover_iterations,
    normalize_counts,
)


SUPPORT_ITEMS = [
    "head_line",
    "u1_plane",
    "transport_avatar",
    "u3_local",
    "e8_2_local",
]


def marked_support_permutations(permutations: list[tuple[str, ...]]) -> list[tuple[str, ...]]:
    return [
        perm
        for perm in permutations
        if perm[0] == "head_line" and perm[1] == "u1_plane" and perm[2] == "transport_avatar"
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the TOE bridge support-hierarchy Grover search.")
    parser.add_argument("--shots", type=int, default=1024, help="Number of simulator shots")
    parser.add_argument("--iterations", type=int, default=None, help="Explicit Grover iteration count")
    parser.add_argument("--top", type=int, default=8, help="Number of top bitstrings to decode")
    parser.add_argument("--seed", type=int, default=7, help="Aer simulator and transpiler seed")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    permutations = list(itertools.permutations(SUPPORT_ITEMS))
    marked = marked_support_permutations(permutations)
    permutation_to_index = {perm: idx for idx, perm in enumerate(permutations)}
    marked_indices = {permutation_to_index[perm] for perm in marked}

    search_space_size = 1 << math.ceil(math.log2(len(permutations)))
    num_qubits = int(math.log2(search_space_size))
    iterations = args.iterations or grover_iterations(search_space_size, len(marked_indices))

    circuit = build_grover_circuit(num_qubits, marked_indices, iterations)
    simulator = AerSimulator(seed_simulator=args.seed)
    compiled = transpile(circuit, simulator, optimization_level=1, seed_transpiler=args.seed)
    result = simulator.run(compiled, shots=args.shots, seed_simulator=args.seed).result()
    counts = Counter(result.get_counts())

    decoded_valid, decoded_invalid = decode_counts(counts, permutations, args.top)
    decoded_target = [entry for entry in decoded_valid if entry["index"] in marked_indices]
    decoded_nontarget_valid = [entry for entry in decoded_valid if entry["index"] not in marked_indices]

    summary = {
        "search_name": "toe_support_hierarchy",
        "support_items": SUPPORT_ITEMS,
        "constraints": {
            "slot_0": "head_line",
            "slot_1": "u1_plane",
            "slot_2": "transport_avatar",
            "slot_3_4": "u3_local / e8_2_local free order",
        },
        "permutation_count": len(permutations),
        "search_space_size": search_space_size,
        "num_qubits": num_qubits,
        "grover_iterations": iterations,
        "shots": args.shots,
        "seed": args.seed,
        "marked_permutations": [list(perm) for perm in marked],
        "marked_indices": sorted(marked_indices),
        "marked_count": len(marked_indices),
        "top_counts": normalize_counts(counts, args.shots)[: args.top],
        "decoded_target_hits": decoded_target,
        "decoded_nontarget_valid_hits": decoded_nontarget_valid,
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
