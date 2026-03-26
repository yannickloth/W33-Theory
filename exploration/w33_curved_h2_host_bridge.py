"""Exact external H^2 host theorem for the curved bridge seeds.

The current explicit curved bridge uses two concrete 4D simplicial seeds:

- ``CP2_9`` with Betti profile ``(1,0,1,0,1)`` and signature ``+1``;
- ``K3_16`` with Betti profile ``(1,0,22,0,1)`` and signature ``-16``.

This module extracts the precise part of the global bridge ambiguity that is
already gone:

1. a genuine rank-2 harmonic ``H^2`` branch cannot live on ``CP2_9`` alone,
   because ``b2 = 1`` there;
2. ``K3_16`` is the first explicit seed in the repo with enough harmonic
   2-form capacity to host such a branch, since ``b2 = 22``;
3. the harmonic-sign split is already exact at the seed level:
   ``b2^+ = (b2 + tau)/2`` and ``b2^- = (b2 - tau)/2`` give
   ``(1,0)`` for ``CP2_9`` and ``(3,19)`` for ``K3_16``;
4. the exact barycentric six-mode has sign matching the seed signature on both
   explicit seeds.

So the external ambiguity is no longer "which current seed could possibly host
the live rank-2 branch?" Among the explicit seeds already checked in the repo,
that host is forced onto the K3 side. The remaining theorem is the actual
selection / counting / orientation of the relevant 2-plane inside the refined
K3 tower.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
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

from w33_curved_4d_curvature_budget import build_curved_4d_curvature_budget_summary
from w33_explicit_curved_4d_complexes import build_explicit_curved_4d_complexes_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_h2_host_bridge_summary.json"


@dataclass(frozen=True)
class CurvedH2HostProfile:
    name: str
    vertices: int
    betti_numbers: tuple[int, int, int, int, int]
    signature: int
    h2_dimension: int
    b2_plus: int
    b2_minus: int
    six_mode: Fraction
    rank2_h2_branch_available: bool
    mixed_sign_h2_plane_available: bool
    six_mode_sign_matches_signature: bool

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["six_mode"] = _fraction_dict(self.six_mode)
        return data


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def six_mode_from_vertices(n_vertices: int) -> Fraction:
    n = Fraction(n_vertices)
    return -n * (n - 1) * (5 * n - 58) / Fraction(114)


def h2_signature_split(b2: int, signature: int) -> tuple[int, int]:
    numerator_plus = b2 + signature
    numerator_minus = b2 - signature
    if numerator_plus % 2 != 0 or numerator_minus % 2 != 0:
        raise ValueError("b2/signature parity does not define an integral H^2 split")
    return numerator_plus // 2, numerator_minus // 2


def _profile(
    name: str,
    vertices: int,
    betti_numbers: tuple[int, int, int, int, int],
    signature: int,
) -> CurvedH2HostProfile:
    h2_dimension = int(betti_numbers[2])
    b2_plus, b2_minus = h2_signature_split(h2_dimension, signature)
    six_mode = six_mode_from_vertices(vertices)
    return CurvedH2HostProfile(
        name=name,
        vertices=vertices,
        betti_numbers=betti_numbers,
        signature=signature,
        h2_dimension=h2_dimension,
        b2_plus=b2_plus,
        b2_minus=b2_minus,
        six_mode=six_mode,
        rank2_h2_branch_available=h2_dimension >= 2,
        mixed_sign_h2_plane_available=(b2_plus > 0 and b2_minus > 0),
        six_mode_sign_matches_signature=((six_mode > 0 and signature > 0) or (six_mode < 0 and signature < 0)),
    )


def build_curved_h2_host_bridge_summary() -> dict[str, Any]:
    complexes = build_explicit_curved_4d_complexes_summary()["profiles"]
    budgets = {entry["name"]: entry for entry in build_curved_4d_curvature_budget_summary()["curved_seeds"]}

    profiles = [
        _profile(
            name="CP2_9",
            vertices=int(complexes[0]["vertices"]),
            betti_numbers=tuple(int(value) for value in complexes[0]["betti_numbers"]),
            signature=int(budgets["CP2"]["signature"]),
        ),
        _profile(
            name="K3_16",
            vertices=int(complexes[1]["vertices"]),
            betti_numbers=tuple(int(value) for value in complexes[1]["betti_numbers"]),
            signature=int(budgets["K3"]["signature"]),
        ),
    ]
    cp2, k3 = profiles

    return {
        "status": "ok",
        "seed_profiles": [profile.to_dict() for profile in profiles],
        "bridge_constraints": {
            "cp2_is_not_rank2_h2_host": not cp2.rank2_h2_branch_available,
            "k3_is_rank2_h2_host": k3.rank2_h2_branch_available,
            "cp2_has_definite_h2_signature": not cp2.mixed_sign_h2_plane_available,
            "k3_has_indefinite_h2_signature": k3.mixed_sign_h2_plane_available,
            "six_mode_sign_matches_signature_on_both_explicit_seeds": all(
                profile.six_mode_sign_matches_signature for profile in profiles
            ),
            "first_explicit_rank2_h2_host_is_k3": (
                (not cp2.rank2_h2_branch_available) and k3.rank2_h2_branch_available
            ),
        },
        "bridge_verdict": (
            "The explicit curved seeds already kill part of the global bridge "
            "ambiguity. CP2_9 has only one harmonic 2-form and definite H^2 "
            "signature, so it cannot by itself host a genuine rank-2 harmonic "
            "bridge branch. K3_16 has twenty-two harmonic 2-forms with exact "
            "split (b2+, b2-) = (3,19), so it is the first explicit seed in the "
            "repo that can host such a branch and already carries both harmonic "
            "signs. Moreover the exact barycentric six-mode is positive on CP2_9 "
            "and negative on K3_16, matching the seed signatures. So the "
            "remaining external problem is no longer 'which current seed could "
            "host the branch?' but rather the actual selection, counting, and "
            "orientation of the relevant 2-plane inside the K3 refinement tower."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_h2_host_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
