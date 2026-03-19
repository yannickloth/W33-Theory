"""Exact toroidal K7 spectral shell on the Csaszar/Szilassi dual pair.

The first nontrivial toroidal dual value is not just a genus-count coincidence.
Both sides of the explicit toroidal dual pair already realize the same complete
graph shell:

    - the Csaszar seed has vertex graph K7;
    - the Szilassi seed has face-adjacency graph K7.

Therefore the pair shares the exact spectra

    spec(A_K7) = {6, (-1)^6},
    spec(L_K7) = {0, 7^6}.

This is the clean operator form of the toroidal selector:

    - one selector line;
    - six identical nontrivial modes;
    - nontrivial Laplacian eigenvalue 7 = Phi_6 = beta_0(QCD).

The compressed affine shell is then recovered as an operator trace rather than
only as arithmetic:

    Tr(L_K7) = 6 * 7 = 42,
    Tr(A_K7^2) = 42.

So the toroidal route already carries the same one-plus-six selector structure
that reappears on the promoted physics-facing side.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_qcd_beta_phi6_bridge import build_qcd_beta_phi6_summary
from w33_surface_neighborly_bridge import build_surface_neighborly_summary
from w33_surface_physics_shell_bridge import build_surface_physics_shell_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_toroidal_k7_spectral_bridge_summary.json"


def _complete_graph_adjacency_spectrum(n: int) -> list[int]:
    return [n - 1] + [-1] * (n - 1)


def _complete_graph_laplacian_spectrum(n: int) -> list[int]:
    return [0] + [n] * (n - 1)


@lru_cache(maxsize=1)
def build_toroidal_k7_spectral_summary() -> dict[str, Any]:
    surface = build_surface_neighborly_summary()
    physics = build_surface_physics_shell_summary()
    qcd = build_qcd_beta_phi6_summary()

    csaszar = surface["seeds"][0]
    szilassi = surface["seeds"][1]

    n = int(csaszar["vertices"])
    adjacency_spectrum = _complete_graph_adjacency_spectrum(n)
    laplacian_spectrum = _complete_graph_laplacian_spectrum(n)
    selector_line_dimension = 1
    shared_six_channel = int(physics["standard_model_gauge_dictionary"]["shared_six_channel"])
    phi6 = int(qcd["qcd_beta_dictionary"]["beta0_su3"]["exact"])
    adjacency_square_trace = sum(eig * eig for eig in adjacency_spectrum)
    laplacian_trace = sum(laplacian_spectrum)

    return {
        "status": "ok",
        "toroidal_k7_dictionary": {
            "toroidal_seed_order": n,
            "csaszar_vertex_graph": csaszar["one_skeleton_graph"],
            "szilassi_face_graph": szilassi["face_adjacency_graph"],
            "adjacency_spectrum": adjacency_spectrum,
            "laplacian_spectrum": laplacian_spectrum,
            "selector_line_dimension": selector_line_dimension,
            "shared_six_channel": shared_six_channel,
            "phi6": phi6,
            "adjacency_square_trace": adjacency_square_trace,
            "laplacian_trace": laplacian_trace,
        },
        "exact_factorizations": {
            "csaszar_vertex_graph_is_k7": csaszar["one_skeleton_graph"] == "K7",
            "szilassi_face_graph_is_k7": szilassi["face_adjacency_graph"] == "K7",
            "selector_plus_shared_six_equals_toroidal_seed_order": (
                selector_line_dimension + shared_six_channel == n
            ),
            "nontrivial_laplacian_mode_equals_phi6": all(
                eig == phi6 for eig in laplacian_spectrum[1:]
            ),
            "nontrivial_adjacency_multiplicity_equals_shared_six": (
                len(adjacency_spectrum) - 1 == shared_six_channel
            ),
            "laplacian_trace_equals_shared_six_times_phi6": (
                laplacian_trace == shared_six_channel * phi6
            ),
            "adjacency_square_trace_equals_shared_six_times_phi6": (
                adjacency_square_trace == shared_six_channel * phi6
            ),
        },
        "bridge_verdict": (
            "The first toroidal dual seed is already an operator shell, not only "
            "a genus count. The Csaszar vertex graph and the Szilassi face-"
            "adjacency graph are both exactly K7, so the shared toroidal shell "
            "has adjacency spectrum {6,(-1)^6} and Laplacian spectrum {0,7^6}. "
            "That means the toroidal route already carries one selector line plus "
            "six identical nontrivial modes at Phi_6 = 7 = beta_0(QCD). The "
            "compressed affine packet 42 is then recovered as the total "
            "nontrivial spectral weight Tr(L_K7) = Tr(A_K7^2) = 6*7, so the "
            "toroidal dual pair is already the same one-plus-six selector "
            "structure that keeps reappearing on the live physics side."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_toroidal_k7_spectral_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
