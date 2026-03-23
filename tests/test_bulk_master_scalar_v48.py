import json
import math
import subprocess
from pathlib import Path


def test_bulk_master_scalar_v48_master_scalar_chain():
    script = Path("toe_session_20260316_v48") / "toe_session_20260316_v48" / "w33_bulk_master_scalar_v48.py"
    assert script.exists(), f"Expected v48 solver at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v48") / "toe_session_20260316_v48" / "w33_bulk_master_scalar_results_v48.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    r = data["r"]
    Xi = data["Xi"]
    pi = data["pi"]
    beta = data["beta"]
    Delta = data["Delta"]
    tau3 = data["tau3"]

    # Core closure: Xi -> pi -> beta -> Delta -> tau3
    pi_est = r * (Xi - 1.0) / (1.0 + r * (Xi - 1.0))
    assert abs(pi - pi_est) < 1e-15

    beta_est = math.sqrt(r / (1.0 + r * (Xi - 1.0))) * (math.sqrt(Xi) - 1.0)
    assert abs(beta - beta_est) < 1e-15

    assert abs(Delta - beta * beta) < 1e-15

    tau3_est = 4.0 * beta * beta / (1.0 + beta * beta) ** 2
    assert abs(tau3 - tau3_est) < 1e-15

    # Verify theta is related via beta
    theta = data["theta_rad"]
    assert abs(theta - 2.0 * math.atan(beta)) < 1e-15
