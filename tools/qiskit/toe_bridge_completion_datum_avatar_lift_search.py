#!/usr/bin/env python3
"""Diagnostic-relaxation shell refined by the shared nonzero datum/avatar lift.

Inside the live nonzero wall there are exactly two completion-side lift states:

- ``slot_replacement_datum``
- ``formal_completion_object``

They share the same nonzero cocycle orbit and the same completion normal form.
The difference is role: datum-only versus minimal common external object.

This oracle tensors that binary lift factor with the corrected
``57600``-state diagnostic-relaxation shell, giving ``115200`` states on
``17`` qubits.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter

from toe_bridge_diagnostic_relaxation_search import (
    RELAXATION_BOTH,
    RELAXATION_EXCEPTIONAL,
    RELAXATION_EXACT,
    RELAXATION_HYPERBOLIC,
    build_relaxation_states,
    expected_marked_count,
    relaxation_modes,
)
from toe_bridge_enhancement_factor_search import theorem_sources_for_mode
from toe_bridge_line_factor_search import MODE_FORMAL_COMPLETION


MODE_SLOT_REPLACEMENT_DATUM = "slot-replacement-datum"
MODE_FORMAL_COMPLETION_OBJECT = "formal-completion-object"

SLOT_REPLACEMENT_DATUM = "slot_replacement_datum"
FORMAL_COMPLETION_OBJECT = "formal_completion_object"


def lift_states() -> list[str]:
    return [SLOT_REPLACEMENT_DATUM, FORMAL_COMPLETION_OBJECT]


def target_lift_state(mode: str) -> str:
    mapping = {
        MODE_SLOT_REPLACEMENT_DATUM: SLOT_REPLACEMENT_DATUM,
        MODE_FORMAL_COMPLETION_OBJECT: FORMAL_COMPLETION_OBJECT,
    }
    try:
        return mapping[mode]
    except KeyError as exc:
        raise ValueError(f"Unsupported mode: {mode}") from exc


def grover_iteration_count(search_space_size: int, marked_count: int) -> int:
    if marked_count <= 0:
        raise ValueError("marked_count must be positive")
    return max(1, int(round((math.pi / 4.0) * math.sqrt(search_space_size / marked_count))))


def build_states() -> tuple[
    list[tuple[str, ...]],
    list[tuple[int, int, int, int, str, str, str, str]],
    list[tuple[int, str]],
]:
    support_permutations, diagnostic_states = build_relaxation_states()
    bridge_states = list(itertools.product(range(len(diagnostic_states)), lift_states()))
    return support_permutations, diagnostic_states, bridge_states


def build_marked_indices(
    mode: str,
    relaxation: str,
) -> tuple[
    list[tuple[str, ...]],
    list[tuple[int, int, int, int, str, str, str, str]],
    list[tuple[int, str]],
    set[int],
]:
    if mode not in {MODE_SLOT_REPLACEMENT_DATUM, MODE_FORMAL_COMPLETION_OBJECT}:
        raise ValueError(f"Unsupported mode: {mode}")
    if relaxation not in relaxation_modes():
        raise ValueError(f"Unsupported relaxation mode: {relaxation}")

    support_permutations, diagnostic_states = build_relaxation_states()
    from toe_bridge_diagnostic_relaxation_search import build_marked_indices as build_base_marked_indices

    _support_permutations, _diagnostic_states, base_marked = build_base_marked_indices(
        MODE_FORMAL_COMPLETION,
        relaxation,
    )
    bridge_states = list(itertools.product(range(len(diagnostic_states)), lift_states()))
    target = target_lift_state(mode)
    marked = {
        idx
        for idx, (diagnostic_idx, lift_state) in enumerate(bridge_states)
        if diagnostic_idx in base_marked and lift_state == target
    }
    return support_permutations, diagnostic_states, bridge_states, marked


def build_mode_conjugacy_permutation(src_mode: str, dst_mode: str) -> list[int]:
    _support_permutations, diagnostic_states, bridge_states = build_states()
    state_to_index = {state: idx for idx, state in enumerate(bridge_states)}
    src_target = target_lift_state(src_mode)
    dst_target = target_lift_state(dst_mode)
    return [
        state_to_index[(diagnostic_idx, dst_target if lift_state == src_target else src_target)]
        for diagnostic_idx, lift_state in bridge_states
    ]


def marked_lift_projection(mode: str, relaxation: str) -> set[str]:
    _support_permutations, _diagnostic_states, bridge_states, marked = build_marked_indices(
        mode, relaxation
    )
    return {bridge_states[idx][1] for idx in marked}


def decode_states(
    counts: Counter[str],
    support_permutations: list[tuple[str, ...]],
    diagnostic_states: list[tuple[int, int, int, int, str, str, str, str]],
    bridge_states: list[tuple[int, str]],
    marked_indices: set[int],
    top: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    from toe_bridge_diagnostic_relaxation_search import decode_relaxation_states

    target_hits: list[dict[str, object]] = []
    nontarget_valid: list[dict[str, object]] = []
    invalid: list[dict[str, object]] = []

    for bitstring, count in counts.most_common(top):
        index = int(bitstring, 2)
        payload: dict[str, object] = {"bitstring": bitstring, "index": index, "count": count}
        if index >= len(bridge_states):
            invalid.append(payload)
            continue

        diagnostic_idx, lift_state = bridge_states[index]
        base_target, base_nontarget, _base_invalid = decode_relaxation_states(
            Counter({format(diagnostic_idx, "b"): count}),
            support_permutations,
            diagnostic_states,
            {diagnostic_idx},
            top=1,
        )
        base_payload = (base_target or base_nontarget)[0]
        base_payload.pop("bitstring", None)
        base_payload.pop("index", None)
        base_payload.pop("count", None)
        payload.update(base_payload)
        payload["lift_state"] = lift_state

        if index in marked_indices:
            target_hits.append(payload)
        else:
            nontarget_valid.append(payload)

    return target_hits, nontarget_valid, invalid


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the shared-nonzero datum/avatar lift Grover search."
    )
    parser.add_argument(
        "--mode",
        choices=[MODE_SLOT_REPLACEMENT_DATUM, MODE_FORMAL_COMPLETION_OBJECT],
        default=MODE_FORMAL_COMPLETION_OBJECT,
    )
    parser.add_argument("--relaxation", choices=relaxation_modes(), default=RELAXATION_EXACT)
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--iterations", type=int, default=None)
    parser.add_argument("--top", type=int, default=8)
    parser.add_argument("--seed", type=int, default=7)
    return parser


def main() -> None:
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from permutation_grover_search import build_grover_circuit, normalize_counts

    args = build_parser().parse_args()
    support_permutations, diagnostic_states, bridge_states, marked_indices = (
        build_marked_indices(args.mode, args.relaxation)
    )
    search_space_size = 1 << math.ceil(math.log2(len(bridge_states)))
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

    decoded_target, decoded_nontarget_valid, decoded_invalid = decode_states(
        counts,
        support_permutations,
        diagnostic_states,
        bridge_states,
        marked_indices,
        args.top,
    )

    summary = {
        "search_name": "toe_bridge_completion_datum_avatar_lift_search",
        "mode": args.mode,
        "relaxation": args.relaxation,
        "theorem_sources": theorem_sources_for_mode(MODE_FORMAL_COMPLETION)
        + [
            "exploration/w33_minimal_external_completion_data_bridge.py",
            "exploration/w33_formal_external_completion_avatar_bridge.py",
            "exploration/w33_completion_datum_avatar_lift_bridge.py",
        ],
        "diagnostic_state_count": len(diagnostic_states),
        "lift_state_count": len(lift_states()),
        "bridge_state_count": len(bridge_states),
        "search_space_size": search_space_size,
        "num_qubits": num_qubits,
        "grover_iterations": iterations,
        "shots": args.shots,
        "seed": args.seed,
        "marked_count": len(marked_indices),
        "expected_marked_count": expected_marked_count(args.relaxation),
        "marked_count_matches_exact_sector_formula": (
            len(marked_indices) == expected_marked_count(args.relaxation)
        ),
        "lift_states": lift_states(),
        "target_lift_state": target_lift_state(args.mode),
        "marked_lift_projection": sorted(marked_lift_projection(args.mode, args.relaxation)),
        "exact_mode_relation": "Marked_diagnostic_relaxation(relaxation) x {lift_state(mode)}",
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
