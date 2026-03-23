import json
import subprocess
from pathlib import Path

from w33_defect_unified import DefectPacket


def test_bulk_master_scalar_chain_matches_unified_model():
    packet = DefectPacket()

    # Run v48 solver to get chain output
    script = Path("toe_session_20260316_v48") / "toe_session_20260316_v48" / "w33_bulk_master_scalar_v48.py"
    assert script.exists(), f"Expected v48 solver at {script}"
    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v48") / "toe_session_20260316_v48" / "w33_bulk_master_scalar_results_v48.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    r = data["r"]
    Xi = data["Xi"]
    pi = data["pi"]
    beta = data["beta"]
    tau3 = data["tau3"]
    theta = data["theta_rad"]

    # The chain should close exactly via the unified model formulas.
    assert abs(pi - packet.pi_from_Xi(Xi, r)) < 1e-15
    assert abs(beta - packet.beta_from_Xi(Xi, r)) < 1e-15
    assert abs(tau3 - packet.tau3_from_beta(beta)) < 1e-15
    assert abs(theta - packet.theta_from_beta(beta)) < 1e-15

    # beta and Delta relationships
    assert abs(data["Delta"] - beta * beta) < 1e-15
