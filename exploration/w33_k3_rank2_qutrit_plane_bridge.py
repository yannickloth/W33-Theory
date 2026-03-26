"""Exact rank-2 qutrit plane types inside the K3 middle-degree host.

The explicit K3-side middle-degree qutrit host is

    81 x H^2(K3)

with exact signature split

    H^2(K3): (b2+, b2-) = (3, 19).

This is strong enough to classify the minimal rank-2 harmonic branch types that
can already occur inside the checked explicit host:

- positive-definite rank-2 plane: type (2,0),
- mixed-sign rank-2 plane: type (1,1),
- negative-definite rank-2 plane: type (0,2).

Tensoring any such rank-2 plane with the exact 81-dimensional qutrit matter
sector gives a 162-dimensional minimal branch packet. In the mixed-sign case
the split is exactly 81 positive plus 81 negative qutrit modes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_curved_h2_qutrit_bridge import build_curved_h2_qutrit_bridge_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_k3_rank2_qutrit_plane_bridge_summary.json"


@dataclass(frozen=True)
class Rank2PlaneType:
    plane_type: str
    positive_h2_directions: int
    negative_h2_directions: int
    positive_qutrit_modes: int
    negative_qutrit_modes: int
    total_qutrit_modes: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_k3_rank2_qutrit_plane_bridge_summary() -> dict[str, Any]:
    k3 = build_curved_h2_qutrit_bridge_summary()["seed_profiles"][1]
    logical_qutrits = int(k3["logical_qutrits"])
    b2_plus = int(k3["b2_plus"])
    b2_minus = int(k3["b2_minus"])

    plane_types = [
        Rank2PlaneType(
            plane_type="positive_rank2",
            positive_h2_directions=2,
            negative_h2_directions=0,
            positive_qutrit_modes=2 * logical_qutrits,
            negative_qutrit_modes=0,
            total_qutrit_modes=2 * logical_qutrits,
        ),
        Rank2PlaneType(
            plane_type="mixed_rank2",
            positive_h2_directions=1,
            negative_h2_directions=1,
            positive_qutrit_modes=logical_qutrits,
            negative_qutrit_modes=logical_qutrits,
            total_qutrit_modes=2 * logical_qutrits,
        ),
        Rank2PlaneType(
            plane_type="negative_rank2",
            positive_h2_directions=0,
            negative_h2_directions=2,
            positive_qutrit_modes=0,
            negative_qutrit_modes=2 * logical_qutrits,
            total_qutrit_modes=2 * logical_qutrits,
        ),
    ]

    return {
        "status": "ok",
        "k3_middle_degree_host": {
            "logical_qutrits": logical_qutrits,
            "b2_plus": b2_plus,
            "b2_minus": b2_minus,
            "total_middle_degree_qutrit_channel": int(k3["total_middle_degree_qutrit_channel"]),
        },
        "rank2_plane_types": [plane.to_dict() for plane in plane_types],
        "bridge_constraints": {
            "k3_supports_positive_rank2_plane": b2_plus >= 2,
            "k3_supports_mixed_rank2_plane": (b2_plus >= 1 and b2_minus >= 1),
            "k3_supports_negative_rank2_plane": b2_minus >= 2,
            "minimal_rank2_qutrit_branch_dimension": 2 * logical_qutrits,
            "mixed_rank2_qutrit_split": [logical_qutrits, logical_qutrits],
            "minimal_rank2_branch_matches_transport_extension_size": (2 * logical_qutrits == 162),
        },
        "bridge_verdict": (
            "The explicit K3-side host already supports three exact minimal "
            "rank-2 harmonic branch types: positive, mixed, and negative. "
            "Tensoring any such rank-2 plane with the exact 81-dimensional "
            "qutrit matter sector gives a 162-dimensional minimal branch packet. "
            "In particular, the mixed-sign branch has exact split 81 + 81, so "
            "the first exact external rank-2 branch package is numerically "
            "compatible with the already-promoted internal 81 -> 162 -> 81 "
            "transport extension."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_rank2_qutrit_plane_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
