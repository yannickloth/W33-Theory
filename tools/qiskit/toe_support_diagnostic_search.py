#!/usr/bin/env python3
"""Grover-style search on the factorized TOE support shell.

This refines the original support-hierarchy search by factorizing the exact
`5`-item support permutation into three theorem-localized pieces:

- an interleaving pattern choosing which `3` of `5` slots carry the exact
  bridge core;
- an order on the core support levels `head_line`, `u1_plane`,
  `transport_avatar`;
- a free order on the local context pair `u3_local`, `e8_2_local`.

So the exact identity is:

`5! = C(5,3) * 3! * 2! = 10 * 6 * 2`.

The marked sector keeps the strict bridge hierarchy:

- the core occupies slots `(0,1,2)`;
- the core order is `(head_line, u1_plane, transport_avatar)`;
- the local context order remains free.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter


SUPPORT_CORE_ITEMS = [
    "head_line",
    "u1_plane",
    "transport_avatar",
]
LOCAL_CONTEXT_ITEMS = [
    "u3_local",
    "e8_2_local",
]


def support_interleavings() -> list[tuple[int, int, int]]:
    return list(itertools.combinations(range(5), 3))


def support_core_orderings() -> list[tuple[str, str, str]]:
    return list(itertools.permutations(SUPPORT_CORE_ITEMS))


def local_context_orderings() -> list[tuple[str, str]]:
    return list(itertools.permutations(LOCAL_CONTEXT_ITEMS))


def merge_support_permutation(
    interleaving: tuple[int, int, int],
    core_order: tuple[str, str, str],
    local_order: tuple[str, str],
) -> tuple[str, ...]:
    slots: list[str | None] = [None] * 5
    for slot, item in zip(interleaving, core_order):
        slots[slot] = item
    tail_slots = [idx for idx, item in enumerate(slots) if item is None]
    for slot, item in zip(tail_slots, local_order):
        slots[slot] = item
    return tuple(item for item in slots if item is not None)


def marked_support_interleaving() -> tuple[int, int, int]:
    return (0, 1, 2)


def marked_support_core_order() -> tuple[str, str, str]:
    return tuple(SUPPORT_CORE_ITEMS)


def build_support_states() -> list[tuple[int, int, int]]:
    return list(
        itertools.product(
            range(len(support_interleavings())),
            range(len(support_core_orderings())),
            range(len(local_context_orderings())),
        )
    )


def build_marked_indices() -> tuple[list[tuple[int, int, int]], set[int]]:
    states = build_support_states()
    target_interleaving = support_interleavings().index(marked_support_interleaving())
    target_core = support_core_orderings().index(marked_support_core_order())

    marked = {
        idx
        for idx, (interleaving_idx, core_idx, _local_idx) in enumerate(states)
        if interleaving_idx == target_interleaving and core_idx == target_core
    }
    return states, marked


def decode_support_states(
    counts: Counter[str],
    states: list[tuple[int, int, int]],
    marked_indices: set[int],
    top: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    target_hits: list[dict[str, object]] = []
    nontarget_valid: list[dict[str, object]] = []
    invalid: list[dict[str, object]] = []

    interleavings = support_interleavings()
    core_orders = support_core_orderings()
    local_orders = local_context_orderings()

    for bitstring, count in counts.most_common(top):
        index = int(bitstring, 2)
        payload: dict[str, object] = {"bitstring": bitstring, "index": index, "count": count}
        if index >= len(states):
            invalid.append(payload)
            continue

        interleaving_idx, core_idx, local_idx = states[index]
        interleaving = interleavings[interleaving_idx]
        core_order = core_orders[core_idx]
        local_order = local_orders[local_idx]
        payload["interleaving"] = list(interleaving)
        payload["core_order"] = list(core_order)
        payload["local_order"] = list(local_order)
        payload["support_permutation"] = list(
            merge_support_permutation(interleaving, core_order, local_order)
        )

        if index in marked_indices:
            target_hits.append(payload)
        else:
            nontarget_valid.append(payload)

    return target_hits, nontarget_valid, invalid


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the factorized TOE support Grover search.")
    parser.add_argument("--shots", type=int, default=1024, help="Number of simulator shots")
    parser.add_argument("--iterations", type=int, default=None, help="Explicit Grover iteration count")
    parser.add_argument("--top", type=int, default=8, help="Number of decoded states to keep")
    parser.add_argument("--seed", type=int, default=7, help="Aer simulator and transpiler seed")
    return parser


def grover_iteration_count(search_space_size: int, marked_count: int) -> int:
    if marked_count <= 0:
        raise ValueError("marked_count must be positive")
    return max(1, int(round((math.pi / 4.0) * math.sqrt(search_space_size / marked_count))))


def main() -> None:
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from permutation_grover_search import build_grover_circuit, normalize_counts

    args = build_parser().parse_args()

    states, marked_indices = build_marked_indices()
    search_space_size = 1 << math.ceil(math.log2(len(states)))
    num_qubits = int(math.log2(search_space_size))
    iterations = (
        args.iterations
        if args.iterations is not None
        else grover_iteration_count(search_space_size, len(marked_indices))
    )

    circuit = build_grover_circuit(num_qubits, marked_indices, iterations)
    simulator = AerSimulator(seed_simulator=args.seed)
    compiled = transpile(circuit, simulator, optimization_level=1, seed_transpiler=args.seed)
    result = simulator.run(compiled, shots=args.shots, seed_simulator=args.seed).result()
    counts = Counter(result.get_counts())

    decoded_target, decoded_nontarget_valid, decoded_invalid = decode_support_states(
        counts, states, marked_indices, args.top
    )

    summary = {
        "search_name": "toe_support_diagnostic_search",
        "theorem_surface": (
            "factorized support shell: support interleaving, line/plane/avatar core order, free local order"
        ),
        "support_interleaving_count": len(support_interleavings()),
        "support_core_order_count": len(support_core_orderings()),
        "local_context_order_count": len(local_context_orderings()),
        "state_count": len(states),
        "search_space_size": search_space_size,
        "num_qubits": num_qubits,
        "grover_iterations": iterations,
        "shots": args.shots,
        "seed": args.seed,
        "marked_count": len(marked_indices),
        "marked_support_interleaving": list(marked_support_interleaving()),
        "marked_support_core_order": list(marked_support_core_order()),
        "free_local_orders": [list(order) for order in local_context_orderings()],
        "top_counts": normalize_counts(counts, args.shots)[: args.top],
        "decoded_target_hits": decoded_target,
        "decoded_nontarget_valid_hits": decoded_nontarget_valid,
        "decoded_invalid_hits": decoded_invalid,
        "target_hit_count": sum(
            count for bitstring, count in counts.items() if int(bitstring, 2) in marked_indices
        ),
        "target_hit_probability": sum(
            count for bitstring, count in counts.items() if int(bitstring, 2) in marked_indices
        ) / args.shots,
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
