#!/usr/bin/env python3
"""Grover-style search over small permutation sets.

This is a reusable experiment driver for small permutation search problems.
It encodes permutations by index, marks one or more target permutations, runs a
manual Grover loop on an Aer simulator, and emits JSON for easy iteration.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter
from typing import Iterable

from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import DiagonalGate
from qiskit_aer import AerSimulator


def grover_iterations(search_space_size: int, marked_count: int) -> int:
    if marked_count <= 0:
        raise ValueError("marked_count must be positive")
    return max(1, int(round((math.pi / 4.0) * math.sqrt(search_space_size / marked_count))))


def permutation_index_map(items: list[str]) -> list[tuple[str, ...]]:
    return list(itertools.permutations(items))


def parse_mark(mark: str, item_count: int) -> tuple[str, ...]:
    parts = tuple(part.strip() for part in mark.split(",") if part.strip())
    if len(parts) != item_count:
        raise ValueError(f"Marked permutation '{mark}' has length {len(parts)}; expected {item_count}")
    return parts


def build_phase_oracle(num_qubits: int, marked_indices: set[int]) -> QuantumCircuit:
    amplitudes = [1.0] * (1 << num_qubits)
    for idx in marked_indices:
        amplitudes[idx] = -1.0
    oracle = QuantumCircuit(num_qubits, name="phase_oracle")
    oracle.append(DiagonalGate(amplitudes), range(num_qubits))
    return oracle


def build_diffuser(num_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits, name="diffuser")
    qc.h(range(num_qubits))
    qc.x(range(num_qubits))
    if num_qubits == 1:
        qc.z(0)
    else:
        qc.h(num_qubits - 1)
        qc.mcx(list(range(num_qubits - 1)), num_qubits - 1)
        qc.h(num_qubits - 1)
    qc.x(range(num_qubits))
    qc.h(range(num_qubits))
    return qc


def build_grover_circuit(num_qubits: int, marked_indices: set[int], iterations: int) -> QuantumCircuit:
    oracle = build_phase_oracle(num_qubits, marked_indices)
    diffuser = build_diffuser(num_qubits)

    qc = QuantumCircuit(num_qubits, num_qubits)
    qc.h(range(num_qubits))
    for _ in range(iterations):
        qc.compose(oracle, inplace=True)
        qc.compose(diffuser, inplace=True)
    qc.measure(range(num_qubits), range(num_qubits))
    return qc


def normalize_counts(counts: Counter[str], shots: int) -> list[dict[str, object]]:
    entries = []
    for bitstring, count in counts.most_common():
        entries.append(
            {
                "bitstring": bitstring,
                "count": count,
                "probability": count / shots,
            }
        )
    return entries


def decode_counts(
    counts: Counter[str],
    permutations: list[tuple[str, ...]],
    top: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    valid = []
    invalid = []
    for bitstring, count in counts.most_common(top):
        index = int(bitstring, 2)
        payload = {"bitstring": bitstring, "index": index, "count": count}
        if index < len(permutations):
            payload["permutation"] = list(permutations[index])
            valid.append(payload)
        else:
            invalid.append(payload)
    return valid, invalid


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a small Grover-style permutation search with Qiskit Aer.")
    parser.add_argument("--items", nargs="+", required=True, help="Items to permute, for example: A B C D")
    parser.add_argument(
        "--mark",
        action="append",
        required=True,
        help="Comma-separated marked permutation, repeatable. Example: --mark A,B,C",
    )
    parser.add_argument("--shots", type=int, default=1024, help="Number of simulator shots")
    parser.add_argument("--iterations", type=int, default=None, help="Explicit Grover iteration count")
    parser.add_argument("--top", type=int, default=8, help="Number of top bitstrings to decode")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    items = args.items
    permutations = permutation_index_map(items)
    permutation_to_index = {perm: idx for idx, perm in enumerate(permutations)}
    marked_permutations = [parse_mark(mark, len(items)) for mark in args.mark]

    missing = [perm for perm in marked_permutations if perm not in permutation_to_index]
    if missing:
        raise ValueError(f"Marked permutations are not valid permutations of the provided items: {missing}")

    marked_indices = {permutation_to_index[perm] for perm in marked_permutations}
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
        "items": items,
        "permutation_count": len(permutations),
        "search_space_size": search_space_size,
        "num_qubits": num_qubits,
        "grover_iterations": iterations,
        "shots": args.shots,
        "marked_permutations": [list(perm) for perm in marked_permutations],
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
