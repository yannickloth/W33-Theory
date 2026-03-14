"""Exact operator-projector bridge for the l6 exceptional channel package.

The recent curved bridges already reconstructed the promoted exceptional data
from scalar refinement coefficients:

    320   = 40 * 8,
    12480 = 240 * 52 = 40 * 6 * 52,
    2240  = 40 * 56.

What was still missing was an actual operator-level package behind the
``40 / 6 / 8`` split. This module provides it on the live l6 spinor action.

Key exact statements:

1. If the corrected l6 spinor operators are grouped by their support type
   ``E6 / A2 / Cartan``, then their Frobenius column spaces in
   ``End(S_48) ~= R^(48x48)`` are pairwise orthogonal exactly.
2. Those three orthogonal channel spaces have exact ranks

       rank(P_E6) = 40,
       rank(P_A2) = 6,
       rank(P_h)  = 8,

   so the full spinor gauge-return package has orthogonal projector rank

       40 + 6 + 8 = 54.
3. The promoted curved coefficients are now exact rank dressings of these
   operator projectors:

       c_EH,cont = rank(P_E6) * rank(P_h) = 40 * 8 = 320
       c_6       = rank(P_E6) * rank(P_A2) * F4 = 40 * 6 * 52 = 12480
       c_1       = rank(P_E6) * E7_fund = 40 * 56 = 2240

   while the same A2 projector rank gives both the firewall/tomotope sixfold
   channel and ``|Aut(T)| = 16 * rank(P_A2) = 96``.

So the discrete-to-continuum bridge is now operator-level on the internal
side: the curved scalar coefficients are exact dressings of genuine orthogonal
projectors on the live l6 exceptional operator package.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "exploration", ROOT / "tools", ROOT / "scripts"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from w33_algebraic_spine import build_algebraic_spine
from w33_exceptional_channel_continuum_bridge import (
    build_exceptional_channel_continuum_bridge_summary,
)
from w33_l6_chiral_gauge_bridge import l6_spinor_operator_48
from w33_l6_exceptional_gauge_return import _l6_scan, build_l6_exceptional_gauge_return_certificate
from w33_quark_firewall_obstruction import build_quark_firewall_obstruction


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_exceptional_operator_projector_bridge_summary.json"
FLOAT_TOL = 1e-10
CHANNEL_SCAN_KEYS = {
    "e6": "e6_support",
    "a2": "a2_support",
    "cartan": "cartan_support",
}


def _rounded_rank(matrix: np.ndarray) -> int:
    return int(np.linalg.matrix_rank(matrix.astype(float), tol=FLOAT_TOL))


@lru_cache(maxsize=None)
def channel_operator_columns(channel: str) -> np.ndarray:
    if channel not in CHANNEL_SCAN_KEYS:
        raise KeyError(f"Unsupported channel: {channel}")
    support_indices = _l6_scan()[CHANNEL_SCAN_KEYS[channel]]
    columns = [np.rint(l6_spinor_operator_48(mode_index)).astype(int).reshape(-1) for mode_index in support_indices]
    return np.stack(columns, axis=1)


@lru_cache(maxsize=None)
def channel_projector_basis(channel: str) -> np.ndarray:
    columns = channel_operator_columns(channel).astype(float)
    u, singular_values, _ = np.linalg.svd(columns, full_matrices=False)
    rank = int(np.sum(singular_values > FLOAT_TOL))
    return u[:, :rank]


def _fractionless_bool(value: np.ndarray, target: np.ndarray) -> bool:
    return bool(np.allclose(value, target, atol=FLOAT_TOL))


@lru_cache(maxsize=1)
def build_exceptional_operator_projector_summary() -> dict[str, Any]:
    exceptional = build_algebraic_spine().exceptional_parameter_dictionary
    channel_continuum = build_exceptional_channel_continuum_bridge_summary()
    l6 = build_l6_exceptional_gauge_return_certificate()
    firewall = build_quark_firewall_obstruction()

    bases = {channel: channel_projector_basis(channel) for channel in CHANNEL_SCAN_KEYS}
    columns = {channel: channel_operator_columns(channel) for channel in CHANNEL_SCAN_KEYS}
    channel_ranks = {channel: int(basis.shape[1]) for channel, basis in bases.items()}

    gram_zero = {
        f"{left}_{right}": bool(
            np.array_equal(
                columns[left].T @ columns[right],
                np.zeros((columns[left].shape[1], columns[right].shape[1]), dtype=int),
            )
        )
        for left in CHANNEL_SCAN_KEYS
        for right in CHANNEL_SCAN_KEYS
        if left != right
    }

    orthonormality = {
        channel: _fractionless_bool(
            basis.T @ basis,
            np.eye(basis.shape[1], dtype=float),
        )
        for channel, basis in bases.items()
    }
    basis_orthogonality = {
        f"{left}_{right}": _fractionless_bool(
            bases[left].T @ bases[right],
            np.zeros((bases[left].shape[1], bases[right].shape[1]), dtype=float),
        )
        for left in CHANNEL_SCAN_KEYS
        for right in CHANNEL_SCAN_KEYS
        if left != right
    }

    combined_basis = np.concatenate([bases["e6"], bases["a2"], bases["cartan"]], axis=1)
    combined_rank = _rounded_rank(combined_basis)
    projector_traces = {channel: float(np.trace(basis.T @ basis)) for channel, basis in bases.items()}

    continuum = channel_ranks["e6"] * channel_ranks["cartan"]
    discrete = channel_ranks["e6"] * channel_ranks["a2"] * exceptional.f4_dim
    topological = channel_ranks["e6"] * exceptional.e7_fund_dim
    tomotope_aut = 16 * channel_ranks["a2"]

    return {
        "status": "ok",
        "operator_space": {
            "spinor_operator_dimension": 48 * 48,
            "support_sizes": {
                "e6": len(_l6_scan()["e6_support"]),
                "a2": len(_l6_scan()["a2_support"]),
                "cartan": len(_l6_scan()["cartan_support"]),
            },
            "channel_ranks": channel_ranks,
            "frobenius_cross_gram_zero_exactly": gram_zero,
            "frobenius_channels_are_pairwise_orthogonal_exactly": all(gram_zero.values()),
        },
        "orthogonal_projectors": {
            "basis_orthonormality": orthonormality,
            "basis_pairwise_orthogonality": basis_orthogonality,
            "projector_traces": projector_traces,
            "projector_traces_equal_ranks": all(
                abs(projector_traces[channel] - channel_ranks[channel]) < FLOAT_TOL
                for channel in CHANNEL_SCAN_KEYS
            ),
            "combined_gauge_package_rank": combined_rank,
            "combined_rank_matches_spinor_total_rank": combined_rank == l6.spinor_total_rank,
        },
        "generation_channel_alignment": {
            "e6_generation_preserving": l6.e6_generation_preserving,
            "a2_generation_mixing_only": l6.a2_generation_mixing_only,
            "cartan_generation_preserving": l6.cartan_generation_preserving,
            "spinor_action_ranks": l6.spinor_action_ranks,
        },
        "curved_rank_dressing": {
            "continuum_from_projector_ranks": continuum,
            "discrete_from_projector_ranks_and_f4": discrete,
            "topological_from_projector_rank_and_e7_fund": topological,
            "tomotope_from_a2_projector_rank": tomotope_aut,
            "firewall_triplet_fibers_from_a2_projector_rank": channel_ranks["a2"],
            "continuum_matches_live_bridge": (
                continuum
                == channel_continuum["base_continuum_channel"]["continuum_eh_coefficient"]
            ),
            "discrete_matches_live_bridge": (
                discrete
                == channel_continuum["discrete_curvature_channel"]["discrete_6_mode_coefficient"]
            ),
            "topological_matches_live_bridge": (
                topological
                == channel_continuum["topological_channel"]["topological_1_mode_coefficient"]
            ),
            "tomotope_matches_live_bridge": (
                tomotope_aut
                == channel_continuum["tomotope_triality_bridge"]["tomotope_automorphism_order"]
            ),
            "firewall_matches_live_bridge": (
                channel_ranks["a2"]
                == channel_continuum["shared_six_channel"]["firewall_triplet_fibers"]
            ),
            "firewall_full_clean_quark_block_exists": firewall.full_clean_quark_block_exists,
        },
        "bridge_verdict": (
            "The promoted exceptional channel data now has an internal projector "
            "theorem. On End(S_48), the corrected l6 spinor operator package "
            "splits into pairwise Frobenius-orthogonal channel spaces of exact "
            "ranks 40, 6, and 8 for E6, A2, and Cartan. So the curved bridge is "
            "no longer only coefficient-level: the continuum coefficient 320, the "
            "discrete six-mode coefficient 12480, and the topological coefficient "
            "2240 are exact rank dressings of genuine orthogonal projectors on the "
            "live internal exceptional operator package. The same A2 projector rank "
            "still matches the transport/firewall/tomotope sixfold channel and "
            "reconstructs the tomotope automorphism order 96 = 16*6."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_exceptional_operator_projector_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
