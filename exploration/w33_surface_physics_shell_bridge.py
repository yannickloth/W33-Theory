"""Exact torus/Klein shell as a Standard Model / QCD / topology packet.

The promoted torus side already carries the exact single-surface flag shell

    84 = q(q+1) Phi_6(q) = 3 * 4 * 7.

This module packages the same shell in physics-facing language using only
already-promoted exact data:

    k = 12 = dim(SU(3) x SU(2) x U(1)) = 8 + 3 + 1,
    beta_0(QCD) = Phi_6(q) = 7,
    dim(G_2) = 14,
    q^3 + 1 = (q+1) Phi_6(q) = 28.

Therefore

    84  = 12 * 7,
    168 = 12 * 14,
    336 = 12 * 28.

So the toroidal shell is already the Standard Model gauge packet dressed by
the QCD selector, the octonionic G2 packet, and the promoted topological shell.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_curvature_cyclotomic_lock_bridge import build_curvature_cyclotomic_lock_summary
from w33_heawood_shell_ladder_bridge import build_heawood_shell_ladder_summary
from w33_klein_clifford_topological_bridge import build_klein_clifford_topological_summary
from w33_qcd_beta_phi6_bridge import build_qcd_beta_phi6_summary
from w33_srg_rosetta_lock_bridge import build_srg_rosetta_lock_summary
from w33_surface_hurwitz_flag_bridge import build_surface_hurwitz_flag_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_surface_physics_shell_bridge_summary.json"


@lru_cache(maxsize=1)
def build_surface_physics_shell_summary() -> dict[str, Any]:
    srg = build_srg_rosetta_lock_summary()
    qcd = build_qcd_beta_phi6_summary()
    surface = build_surface_hurwitz_flag_summary()
    heawood = build_heawood_shell_ladder_summary()
    curvature = build_curvature_cyclotomic_lock_summary()
    klein = build_klein_clifford_topological_summary()

    k = int(srg["srg_data"]["k"])
    q = int(srg["srg_data"]["q_from_lambda_plus_one"])
    lam = int(srg["srg_data"]["lambda"])
    mu = int(srg["srg_data"]["mu"])
    phi6 = int(srg["srg_data"]["phi6_from_k_minus_lambda_minus_mu_plus_one"])

    gluons = k - mu
    weak_triplet = q
    hypercharge = q - lam

    beta0 = int(qcd["qcd_beta_dictionary"]["beta0_su3"]["exact"])
    single_surface_flags = int(surface["surface_hurwitz_dictionary"]["single_surface_flags"])
    dual_pair_flags = int(surface["surface_hurwitz_dictionary"]["dual_pair_flags"])
    heawood_full_order = int(surface["surface_hurwitz_dictionary"]["heawood_full_order"])
    shared_six_channel = int(surface["surface_hurwitz_dictionary"]["shared_six_channel"])
    g2_dimension = int(heawood["heawood_shell_dictionary"]["g2_dimension"])
    topological_shell = int(curvature["cyclotomic_factors"]["q_cubic_plus_1"])
    quartic_e7_packet = int(klein["clifford_quartic_lift"]["klein_quartic_triangle_count"])

    return {
        "status": "ok",
        "standard_model_gauge_dictionary": {
            "q": q,
            "k": k,
            "lambda": lam,
            "mu": mu,
            "gluons": gluons,
            "weak_triplet": weak_triplet,
            "hypercharge_singlet": hypercharge,
            "gauge_dimension": k,
            "gauge_dimension_decomposition": [gluons, weak_triplet, hypercharge],
            "beta0_qcd": beta0,
            "shared_six_channel": shared_six_channel,
            "g2_dimension": g2_dimension,
            "topological_shell": topological_shell,
            "quartic_e7_packet": quartic_e7_packet,
        },
        "surface_physics_shell_dictionary": {
            "single_surface_flags": single_surface_flags,
            "dual_pair_flags": dual_pair_flags,
            "full_heawood_order": heawood_full_order,
        },
        "exact_factorizations": {
            "gauge_dimension_equals_8_plus_3_plus_1": k == gluons + weak_triplet + hypercharge,
            "beta0_qcd_equals_phi6": beta0 == phi6,
            "single_surface_flags_equals_gauge_dimension_times_beta0": (
                single_surface_flags == k * beta0
            ),
            "single_surface_flags_equals_q_times_mu_times_phi6": (
                single_surface_flags == q * mu * phi6
            ),
            "single_surface_flags_equals_g2_dimension_times_shared_six": (
                single_surface_flags == g2_dimension * shared_six_channel
            ),
            "dual_pair_flags_equals_gauge_dimension_times_g2_dimension": (
                dual_pair_flags == k * g2_dimension
            ),
            "dual_pair_flags_equals_shared_six_times_topological_shell": (
                dual_pair_flags == shared_six_channel * topological_shell
            ),
            "dual_pair_flags_equals_two_single_surface_packets": (
                dual_pair_flags == 2 * single_surface_flags
            ),
            "full_heawood_order_equals_gauge_dimension_times_topological_shell": (
                heawood_full_order == k * topological_shell
            ),
            "full_heawood_order_equals_shared_six_times_quartic_e7_packet": (
                heawood_full_order == shared_six_channel * quartic_e7_packet
            ),
            "full_heawood_order_equals_two_dual_pair_packets": (
                heawood_full_order == 2 * dual_pair_flags
            ),
            "topological_shell_equals_mu_times_phi6": topological_shell == mu * phi6,
            "quartic_e7_packet_equals_two_times_topological_shell": (
                quartic_e7_packet == 2 * topological_shell
            ),
        },
        "bridge_verdict": (
            "The torus/Klein shell is already physics-facing. The same single-surface "
            "packet is exactly 84 = 12*7 = 14*6, so it is simultaneously the "
            "Standard Model gauge dimension times the one-loop QCD selector "
            "beta_0 = Phi_6 and the octonionic G2 packet times the shared six-"
            "channel core. Doubling gives 168 = 12*14 = 6*28, and doubling again "
            "gives 336 = 12*28 = 6*56, where 28 = q^3+1 = (q+1)Phi_6 is the "
            "promoted topological/bitangent shell and 56 is the quartic/E7 packet. "
            "Equally, the same 84 still factors as q(q+1)Phi_6 = 3*4*7, so the "
            "toroidal selector is already the color/electroweak/cyclotomic packet "
            "inside the live W33 physics layer."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_surface_physics_shell_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
