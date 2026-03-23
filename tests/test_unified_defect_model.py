import json
import math
import subprocess
from pathlib import Path

from w33_defect_unified import DefectPacket


def test_unified_defect_model_matches_bundle_jsons():
    # This test verifies that the various v22-v37 bundles are numerically consistent
    # with a single underlying defect model.
    packet = DefectPacket()

    # Basic core quantities
    assert abs(packet.R - math.sqrt(20721) / 201.0) < 1e-15
    assert abs(packet.D - packet.R / 100.0) < 1e-15

    # For each session bundle, ensure its key scalar field aligns with the packet
    for v in range(22, 38):
        dirpath = Path(f"toe_session_20260316_v{v}")
        results_glob = list(dirpath.rglob("*results_v*.json"))
        if not results_glob:
            continue
        for results_path in results_glob:
            data = json.loads(results_path.read_text(encoding="utf-8"))
            if "x" in data:
                try:
                    x_val = float(data["x"])
                except Exception:
                    x_val = None
                if x_val is not None:
                    assert abs(x_val - packet.x) < 1e-15
            if "D" in data:
                try:
                    D_val = float(data["D"])
                except Exception:
                    D_val = None
                if D_val is not None:
                    assert abs(D_val - packet.D) < 1e-15
            # Some bundles report D under other keys
            if "delta" in data:
                try:
                    delta_val = float(data["delta"])
                except Exception:
                    delta_val = None
                if delta_val is not None:
                    assert abs(delta_val - packet.D) < 1e-12

            # Check that any reported eigenvalue columns agree with x^weight
            if "walsh_diagonal_eigenvalues" in data and "subset_weights" in data:
                for w, val in zip(data["subset_weights"], data["walsh_diagonal_eigenvalues"]):
                    assert abs(val - packet.factor_x_power(w)) < 1e-12

            # Check that any reported observable eigenvalues follow the expected weight mapping
            if "observable_eigenvalues" in data:
                expected = {
                    "Vus": 1,
                    "Vcb": 2,
                    "Vub": 4,
                    "Vus*Vcb": 3,
                    "Vus*Vub": 5,
                    "Vcb*Vub": 6,
                    "J": 7,
                }
                for obs, w in expected.items():
                    if obs in data["observable_eigenvalues"]:
                        assert abs(data["observable_eigenvalues"][obs] - packet.factor_x_power(w)) < 1e-12

    # Verify the primal/dual mass tower closure via eta
    eta = packet.dual_eta()
    assert abs(packet.mc_over_mt() - packet.mc_over_mt_from_eta()) < 1e-15
    assert abs(packet.mu_over_mt() - packet.mu_over_mt_from_eta()) < 1e-15

    # Verify the CE2 clock ratio R is recovered from eta as well
    assert abs(packet.R - packet.R_from_eta(eta)) < 1e-15
