from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_QISKIT = ROOT / "tools" / "qiskit"
if str(TOOLS_QISKIT) not in sys.path:
    sys.path.insert(0, str(TOOLS_QISKIT))

from toe_bridge_enhancement_factor_search import (  # noqa: E402
    CURRENT_K3_ZERO_ORBIT,
    FORMAL_COMPLETION_AVATAR,
    MINIMAL_EXTERNAL_ENHANCEMENT,
    MODE_CURRENT_K3,
    MODE_FORMAL_COMPLETION,
    MODE_MINIMAL_ENHANCEMENT,
    build_marked_indices,
    enhancement_states,
)


def test_enhancement_state_factor_has_exact_three_state_space() -> None:
    assert enhancement_states() == [
        CURRENT_K3_ZERO_ORBIT,
        MINIMAL_EXTERNAL_ENHANCEMENT,
        FORMAL_COMPLETION_AVATAR,
    ]


def test_bridge_state_count_is_exact() -> None:
    _, bridge_states, _ = build_marked_indices(MODE_FORMAL_COMPLETION)
    assert len(bridge_states) == 345600


def test_marked_count_is_exact_in_all_modes() -> None:
    for mode in [MODE_CURRENT_K3, MODE_MINIMAL_ENHANCEMENT, MODE_FORMAL_COMPLETION]:
        _, _, marked_indices = build_marked_indices(mode)
        assert len(marked_indices) == 20
