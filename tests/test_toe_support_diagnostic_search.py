from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_QISKIT = ROOT / "tools" / "qiskit"
if str(TOOLS_QISKIT) not in sys.path:
    sys.path.insert(0, str(TOOLS_QISKIT))

from toe_support_diagnostic_search import (  # noqa: E402
    LOCAL_CONTEXT_ITEMS,
    SUPPORT_CORE_ITEMS,
    build_marked_indices,
    build_support_states,
    local_context_orderings,
    marked_support_core_order,
    marked_support_interleaving,
    merge_support_permutation,
    support_core_orderings,
    support_interleavings,
)


def test_support_shell_factorization_is_exact() -> None:
    assert len(support_interleavings()) == 10
    assert len(support_core_orderings()) == 6
    assert len(local_context_orderings()) == 2
    assert len(build_support_states()) == 120


def test_marked_support_sector_has_exact_two_free_local_orders() -> None:
    _, marked_indices = build_marked_indices()
    assert len(marked_indices) == 2


def test_marked_support_factor_reconstructs_strict_hierarchy() -> None:
    interleaving = marked_support_interleaving()
    core_order = marked_support_core_order()
    reconstructed = {
        merge_support_permutation(interleaving, core_order, local_order)
        for local_order in local_context_orderings()
    }
    assert reconstructed == {
        (
            "head_line",
            "u1_plane",
            "transport_avatar",
            "u3_local",
            "e8_2_local",
        ),
        (
            "head_line",
            "u1_plane",
            "transport_avatar",
            "e8_2_local",
            "u3_local",
        ),
    }


def test_support_factor_items_match_the_exact_bridge_roles() -> None:
    assert tuple(SUPPORT_CORE_ITEMS) == (
        "head_line",
        "u1_plane",
        "transport_avatar",
    )
    assert tuple(LOCAL_CONTEXT_ITEMS) == ("u3_local", "e8_2_local")
