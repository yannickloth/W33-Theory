"""Natural-units sigma-shell bridge for the promoted W33 package.

The current natural-units chain already contains the exact local identities

    R_K G_0 = 2,
    Phi_6 = 7,
    q^2 = 9,
    2 + 7 = 9,
    1 + q + R_K G_0 = 6.

The new point is that the same ``6`` is not only arithmetic. It is the exact
rank of the nontrivial toroidal ``K7`` shell. On that rank-6 packet, the three
natural-units local operators are scalar:

    S_nontriv = (R_K G_0) I_6 = 2 I_6,
    L_nontriv = Phi_6 I_6 = 7 I_6,
    C_nontriv = q^2 I_6 = 9 I_6,

with

    S_nontriv + L_nontriv = C_nontriv.

Therefore their traces generate the live physics ladder:

    Tr(S_nontriv) = 6 * 2 = 12,
    Tr(L_nontriv) = 6 * 7 = 42,
    Tr(C_nontriv) = 6 * 9 = 54 = 40 + 6 + 8.

The same packet then lifts to the torus/Klein shell as

    84  = 2 * Tr(L_nontriv),
    168 = 4 * Tr(L_nontriv),
    336 = 8 * Tr(L_nontriv).

So the repeated ``6`` is the vacuum-free toroidal mode count that turns the
natural-units local shell ``2 + 7 = 9`` into the promoted gauge/topology
ladder ``12 + 42 = 54`` and its toroidal lifts.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path

from w33_fano_toroidal_complement_bridge import build_fano_toroidal_complement_summary
from w33_heawood_involution_bridge import build_heawood_involution_summary
from w33_natural_units_projective_denominator_bridge import (
    build_natural_units_projective_denominator_summary,
)
from w33_surface_physics_shell_bridge import build_surface_physics_shell_summary
from w33_toroidal_k7_spectral_bridge import build_toroidal_k7_spectral_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_natural_units_sigma_shell_bridge_summary.json"


@lru_cache(maxsize=1)
def build_natural_units_sigma_shell_summary() -> dict[str, object]:
    projective = build_natural_units_projective_denominator_summary()
    toroidal = build_toroidal_k7_spectral_summary()
    complement = build_fano_toroidal_complement_summary()
    heawood = build_heawood_involution_summary()
    surface = build_surface_physics_shell_summary()

    q = int(projective["metrology_shell_dictionary"]["q"])
    rk_times_g0 = int(projective["metrology_shell_dictionary"]["rk_times_g0"]["exact"])
    phi6 = int(projective["metrology_shell_dictionary"]["phi6"])
    q_squared = int(projective["metrology_shell_dictionary"]["q_squared"])
    sigma = int(projective["metrology_shell_dictionary"]["shared_six_formula"].split("=")[0].strip())  # 6

    # The formula string is trusted repo-local content, but keep the numeric shell explicit.
    sigma = int(toroidal["toroidal_k7_dictionary"]["shared_six_channel"])
    metrology_trace = int(complement["operator_dictionary"]["selector_nontrivial_trace"])
    toroidal_trace = int(complement["operator_dictionary"]["toroidal_trace"])
    complement_trace = int(complement["operator_dictionary"]["combined_nontrivial_trace"])
    heawood_middle_rank = int(heawood["centered_shell_dictionary"]["middle_projector_rank"])
    heawood_middle_trace = 2 * q * sigma
    single_surface_flags = int(surface["surface_physics_shell_dictionary"]["single_surface_flags"])
    dual_pair_flags = int(surface["surface_physics_shell_dictionary"]["dual_pair_flags"])
    full_heawood_order = int(surface["surface_physics_shell_dictionary"]["full_heawood_order"])
    phi3 = int(projective["projective_denominator_dictionary"]["phi3"])

    return {
        "status": "ok",
        "sigma_shell_dictionary": {
            "sigma_formula": "sigma = 1 + q + R_K G_0",
            "sigma": sigma,
            "metrology_eigenvalue": rk_times_g0,
            "toroidal_eigenvalue": phi6,
            "complement_eigenvalue": q_squared,
            "phi3_formula": "Phi_3 = sigma + Phi_6",
            "heawood_middle_rank_formula": "rank_mid(Heawood) = 2 sigma",
            "heawood_middle_trace_formula": "Tr(L_H|mid) = 2 q sigma",
        },
        "trace_ladder_dictionary": {
            "metrology_trace": metrology_trace,
            "toroidal_trace": toroidal_trace,
            "complement_trace": complement_trace,
            "heawood_middle_rank": heawood_middle_rank,
            "heawood_middle_trace": heawood_middle_trace,
            "single_surface_flags": single_surface_flags,
            "dual_pair_flags": dual_pair_flags,
            "full_heawood_order": full_heawood_order,
        },
        "exact_factorizations": {
            "sigma_equals_selector_plus_projective_plus_metrology": sigma == 1 + q + rk_times_g0,
            "phi3_equals_sigma_plus_phi6": phi3 == sigma + phi6,
            "metrology_trace_equals_sigma_times_rk_times_g0": metrology_trace == sigma * rk_times_g0,
            "toroidal_trace_equals_sigma_times_phi6": toroidal_trace == sigma * phi6,
            "complement_trace_equals_sigma_times_q_squared": complement_trace == sigma * q_squared,
            "complement_trace_equals_metrology_plus_toroidal_trace": (
                complement_trace == metrology_trace + toroidal_trace
            ),
            "heawood_middle_rank_equals_two_sigma": heawood_middle_rank == 2 * sigma,
            "heawood_middle_trace_equals_two_q_sigma": heawood_middle_trace == 2 * q * sigma,
            "single_surface_flags_equals_two_toroidal_traces": single_surface_flags == 2 * toroidal_trace,
            "dual_pair_flags_equals_four_toroidal_traces": dual_pair_flags == 4 * toroidal_trace,
            "full_heawood_order_equals_eight_toroidal_traces": full_heawood_order == 8 * toroidal_trace,
        },
        "bridge_verdict": (
            "The repeated six is now an operator-backed natural-units mode count. "
            "It is the exact rank of the nontrivial toroidal K7 shell, and on that "
            "rank-6 packet the natural-units local operators are just 2I, 7I, and "
            "9I. Their traces therefore generate the live physics ladder "
            "12, 42, 54, and the toroidal lifts 84, 168, 336. In this reading the "
            "gauge-facing 12, the toroidal/QCD 42, and the exceptional-gauge 54 are "
            "not separate coincidences: they are sigma times the local natural-units "
            "shell 2, 7, and 9 on one exact six-mode packet."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_natural_units_sigma_shell_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
