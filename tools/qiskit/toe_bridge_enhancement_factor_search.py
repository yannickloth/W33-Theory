#!/usr/bin/env python3
"""Grover-style search over the exact external-enhancement wall.

This refines the diagnostic-order bridge shell by replacing the old two-state
glue dichotomy with the exact three-state enhancement hierarchy:

- current refined K3 zero-orbit object;
- minimal exact enhancement datum;
- formal completion avatar.

All other theorem-backed bridge factors remain exact and unchanged.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter

from toe_bridge_diagnostic_order_search import (
    exceptional_orderings,
    exceptional_weight_states,
    hyperbolic_orderings,
    hyperbolic_weight_states,
    interleaving_patterns,
    line_states,
    marked_exceptional_order,
    marked_hyperbolic_order,
    merge_factor_permutation,
)
from toe_bridge_line_factor_search import HEAD_LINE, SUPPORT_ITEMS, strict_support_marked_permutations
from toe_bridge_split_weight_filter_search import EXCEPTIONAL_PASS, HYPERBOLIC_PASS


MODE_CURRENT_K3 = "current-k3-zero-orbit"
MODE_MINIMAL_ENHANCEMENT = "minimal-external-enhancement"
MODE_FORMAL_COMPLETION = "formal-completion-avatar"

CURRENT_K3_ZERO_ORBIT = "current_k3_zero_orbit"
MINIMAL_EXTERNAL_ENHANCEMENT = "minimal_external_enhancement"
FORMAL_COMPLETION_AVATAR = "formal_completion_avatar"


def enhancement_states() -> list[str]:
    return [
        CURRENT_K3_ZERO_ORBIT,
        MINIMAL_EXTERNAL_ENHANCEMENT,
        FORMAL_COMPLETION_AVATAR,
    ]


def target_enhancement_state(mode: str) -> str:
    mapping = {
        MODE_CURRENT_K3: CURRENT_K3_ZERO_ORBIT,
        MODE_MINIMAL_ENHANCEMENT: MINIMAL_EXTERNAL_ENHANCEMENT,
        MODE_FORMAL_COMPLETION: FORMAL_COMPLETION_AVATAR,
    }
    try:
        return mapping[mode]
    except KeyError as exc:
        raise ValueError(f"Unsupported mode: {mode}") from exc


def grover_iteration_count(search_space_size: int, marked_count: int) -> int:
    if marked_count <= 0:
        raise ValueError("marked_count must be positive")
    return max(1, int(round((math.pi / 4.0) * math.sqrt(search_space_size / marked_count))))


def build_marked_indices(
    mode: str,
) -> tuple[
    list[tuple[str, ...]],
    list[tuple[int, int, int, int, str, str, str]],
    set[int],
]:
    if mode not in {
        MODE_CURRENT_K3,
        MODE_MINIMAL_ENHANCEMENT,
        MODE_FORMAL_COMPLETION,
    }:
        raise ValueError(f"Unsupported mode: {mode}")

    support_permutations = list(itertools.permutations(SUPPORT_ITEMS))
    interleavings = interleaving_patterns()
    hyper_orders = hyperbolic_orderings()
    exceptional_orders = exceptional_orderings()
    bridge_states = list(
        itertools.product(
            range(len(support_permutations)),
            range(len(interleavings)),
            range(len(hyper_orders)),
            range(len(exceptional_orders)),
            line_states(),
            hyperbolic_weight_states(),
            exceptional_weight_states(),
            enhancement_states(),
        )
    )

    support_marks = {
        support_permutations.index(perm) for perm in strict_support_marked_permutations(support_permutations)
    }
    hyper_target = hyper_orders.index(marked_hyperbolic_order())
    exceptional_target = exceptional_orders.index(marked_exceptional_order())
    enhancement_target = target_enhancement_state(mode)

    marked_indices = {
        idx
        for idx, (
            support_idx,
            _interleaving_idx,
            hyper_idx,
            exceptional_idx,
            line_state,
            hyper_weight_state,
            exceptional_weight_state,
            enhancement_state,
        ) in enumerate(bridge_states)
        if support_idx in support_marks
        and hyper_idx == hyper_target
        and exceptional_idx == exceptional_target
        and line_state == HEAD_LINE
        and hyper_weight_state == HYPERBOLIC_PASS
        and exceptional_weight_state == EXCEPTIONAL_PASS
        and enhancement_state == enhancement_target
    }
    return support_permutations, bridge_states, marked_indices


def decode_states(
    counts: Counter[str],
    support_permutations: list[tuple[str, ...]],
    bridge_states: list[tuple[int, int, int, int, str, str, str, str]],
    marked_indices: set[int],
    top: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    interleavings = interleaving_patterns()
    hyper_orders = hyperbolic_orderings()
    exceptional_orders = exceptional_orderings()

    target_hits: list[dict[str, object]] = []
    nontarget_valid: list[dict[str, object]] = []
    invalid: list[dict[str, object]] = []

    for bitstring, count in counts.most_common(top):
        index = int(bitstring, 2)
        payload: dict[str, object] = {"bitstring": bitstring, "index": index, "count": count}
        if index >= len(bridge_states):
            invalid.append(payload)
            continue

        (
            support_idx,
            interleaving_idx,
            hyper_idx,
            exceptional_idx,
            line_state,
            hyper_weight_state,
            exceptional_weight_state,
            enhancement_state,
        ) = bridge_states[index]

        interleaving = interleavings[interleaving_idx]
        hyper_order = hyper_orders[hyper_idx]
        exceptional_order = exceptional_orders[exceptional_idx]

        payload["support_permutation"] = list(support_permutations[support_idx])
        payload["interleaving_pattern"] = list(interleaving)
        payload["hyperbolic_order"] = list(hyper_order)
        payload["exceptional_order"] = list(exceptional_order)
        payload["factor_permutation"] = list(
            merge_factor_permutation(hyper_order, exceptional_order, interleaving)
        )
        payload["line_state"] = line_state
        payload["hyperbolic_weight_state"] = hyper_weight_state
        payload["exceptional_weight_state"] = exceptional_weight_state
        payload["enhancement_state"] = enhancement_state

        if index in marked_indices:
            target_hits.append(payload)
        else:
            nontarget_valid.append(payload)

    return target_hits, nontarget_valid, invalid


def theorem_sources_for_mode(mode: str) -> list[str]:
    common = [
        "exploration/w33_selector_a4_weight_hierarchy_bridge.py",
        "exploration/w33_global_local_carrier_split_bridge.py",
        "exploration/w33_u1_head_compatible_line_bridge.py",
        "exploration/w33_common_line_exact_image_bridge.py",
        "exploration/w33_external_enhancement_hierarchy_bridge.py",
    ]
    if mode == MODE_CURRENT_K3:
        return common + [
            "exploration/w33_transport_rigid_split_avatar_bridge.py",
            "exploration/w33_refined_k3_zero_orbit_bridge.py",
        ]
    if mode == MODE_MINIMAL_ENHANCEMENT:
        return common + [
            "exploration/w33_minimal_external_completion_data_bridge.py",
            "exploration/w33_transport_unique_nonzero_cocycle_orbit_bridge.py",
        ]
    return common + [
        "exploration/w33_formal_external_completion_avatar_bridge.py",
        "exploration/w33_transport_internal_operator_normal_form_match_bridge.py",
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the exact TOE bridge enhancement-factor Grover search.")
    parser.add_argument(
        "--mode",
        choices=[
            MODE_CURRENT_K3,
            MODE_MINIMAL_ENHANCEMENT,
            MODE_FORMAL_COMPLETION,
        ],
        default=MODE_FORMAL_COMPLETION,
        help="Which exact external-enhancement state to target",
    )
    parser.add_argument("--shots", type=int, default=256, help="Number of simulator shots")
    parser.add_argument("--iterations", type=int, default=None, help="Explicit Grover iteration count")
    parser.add_argument("--top", type=int, default=8, help="Number of top decoded states to keep")
    parser.add_argument("--seed", type=int, default=7, help="Aer simulator and transpiler seed")
    return parser


def main() -> None:
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from permutation_grover_search import build_grover_circuit, normalize_counts

    args = build_parser().parse_args()

    support_permutations, bridge_states, marked_indices = build_marked_indices(args.mode)
    search_space_size = 1 << math.ceil(math.log2(len(bridge_states)))
    num_qubits = int(math.log2(search_space_size))
    iterations = args.iterations or grover_iteration_count(search_space_size, len(marked_indices))

    circuit = build_grover_circuit(num_qubits, marked_indices, iterations)
    simulator = AerSimulator(seed_simulator=args.seed)
    compiled = transpile(circuit, simulator, optimization_level=1, seed_transpiler=args.seed)
    result = simulator.run(compiled, shots=args.shots, seed_simulator=args.seed).result()
    counts = Counter(result.get_counts())

    decoded_target, decoded_nontarget_valid, decoded_invalid = decode_states(
        counts,
        support_permutations,
        bridge_states,
        marked_indices,
        args.top,
    )

    summary = {
        "search_name": "toe_bridge_enhancement_factor_search",
        "mode": args.mode,
        "theorem_sources": theorem_sources_for_mode(args.mode),
        "support_permutation_count": len(support_permutations),
        "interleaving_pattern_count": len(interleaving_patterns()),
        "hyperbolic_order_count": len(hyperbolic_orderings()),
        "exceptional_order_count": len(exceptional_orderings()),
        "enhancement_state_count": len(enhancement_states()),
        "bridge_state_count": len(bridge_states),
        "search_space_size": search_space_size,
        "num_qubits": num_qubits,
        "grover_iterations": iterations,
        "shots": args.shots,
        "seed": args.seed,
        "marked_count": len(marked_indices),
        "top_counts": normalize_counts(counts, args.shots)[: args.top],
        "decoded_target_hits": decoded_target,
        "decoded_nontarget_valid_hits": decoded_nontarget_valid,
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
