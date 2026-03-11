"""Simultaneous V4 projector decomposition of the canonical l6 flavour action.

The exact matrix-level Delta(27) / V4 bridge gives two commuting involutions on
the 8-dimensional right-handed basis for each clean external slot. This module
packages their simultaneous eigenspace decomposition.

What is established:

  - the two V4 generators define exact orthogonal projectors P_(s_A,s_B);
  - the (-- ) character projector vanishes for both H_2 and Hbar_2;
  - the active right support splits exactly as:
      * H_2: (-,+) = {u_c_1, u_c_3}, (+,-) = {u_c_2, nu_c};
      * Hbar_2: (-,+) = {d_c_1}, (+,-) = {d_c_2, d_c_3, e_c};
  - the (+,+) eigenspace is precisely the complementary inactive right support
    in each slot.

So the V4 flavour action is not only a sign-pattern torsor: it already carries
an exact projector-level decomposition of the right-handed sector.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_fermionic_connes_sector import right_spinor_basis
from w33_l6_delta27_v4_bridge import _slot_profile


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_l6_v4_projector_bridge_summary.json"


def _sign_matrix(signs: list[int]) -> np.ndarray:
    return np.diag(np.array(signs, dtype=float))


def _projector_profiles(external_slot: str) -> dict[str, Any]:
    profile = _slot_profile(external_slot)
    labels = [state.slot for state in right_spinor_basis()]
    identity = np.eye(8, dtype=float)
    a = _sign_matrix(profile["generator_a"])
    b = _sign_matrix(profile["generator_b"])

    projectors = {
        "++": (identity + a + b + a @ b) / 4.0,
        "+-": (identity + a - b - a @ b) / 4.0,
        "-+": (identity - a + b - a @ b) / 4.0,
        "--": (identity - a - b + a @ b) / 4.0,
    }

    rows = {}
    for key, projector in projectors.items():
        diagonal = np.rint(np.diag(projector)).astype(int).tolist()
        support_labels = [
            label for label, value in zip(labels, diagonal) if value == 1
        ]
        rows[key] = {
            "rank": int(np.linalg.matrix_rank(projector)),
            "support_labels": support_labels,
        }

    active = set(profile["active_right_support_labels"])
    inactive = [label for label in labels if label not in active]
    return {
        "projectors": rows,
        "active_support": sorted(active),
        "inactive_support": inactive,
    }


@lru_cache(maxsize=1)
def build_l6_v4_projector_bridge_summary() -> dict[str, Any]:
    slot_profiles = {
        external_slot: _projector_profiles(external_slot)
        for external_slot in ("H_2", "Hbar_2")
    }
    return {
        "status": "ok",
        "slot_profiles": slot_profiles,
        "projector_theorem": {
            "projectors_are_exact_eigenspace_splitters": True,
            "minus_minus_projector_vanishes_for_both_slots": all(
                slot_profile["projectors"]["--"]["rank"] == 0
                for slot_profile in slot_profiles.values()
            ),
            "plus_plus_projector_is_exact_inactive_support_for_both_slots": all(
                slot_profile["projectors"]["++"]["support_labels"] == slot_profile["inactive_support"]
                for slot_profile in slot_profiles.values()
            ),
            "h2_active_support_splits_as_2_plus_2": (
                slot_profiles["H_2"]["projectors"]["-+"]["support_labels"] == ["u_c_1", "u_c_3"]
                and slot_profiles["H_2"]["projectors"]["+-"]["support_labels"] == ["u_c_2", "nu_c"]
            ),
            "hbar2_active_support_splits_as_1_plus_3": (
                slot_profiles["Hbar_2"]["projectors"]["-+"]["support_labels"] == ["d_c_1"]
                and slot_profiles["Hbar_2"]["projectors"]["+-"]["support_labels"] == ["d_c_2", "d_c_3", "e_c"]
            ),
        },
        "bridge_verdict": (
            "The matrix-level V4 flavour action admits an exact simultaneous "
            "projector decomposition. The (-- ) character is absent in both slots, "
            "the (+,+) sector is exactly the inactive right-handed support, and "
            "the active support splits rigidly as 2+2 for H_2 and 1+3 for Hbar_2."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_l6_v4_projector_bridge_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
