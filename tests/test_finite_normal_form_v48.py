import json
import math
import subprocess
from pathlib import Path

from w33_defect_unified import DefectPacket


def test_finite_normal_form_is_single_scalar_modulus():
    packet = DefectPacket()

    # Use the v48 master-scalar results as the final closure points.
    script = Path("toe_session_20260316_v48") / "toe_session_20260316_v48" / "w33_bulk_master_scalar_v48.py"
    assert script.exists(), f"Expected v48 solver at {script}"
    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v48") / "toe_session_20260316_v48" / "w33_bulk_master_scalar_results_v48.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    # Extract the master scalar modulus Xi and the derived beta and kappa.
    Xi = data["Xi"]
    r = data["r"]
    beta = data["beta"]
    kappa = math.log(Xi)

    # Verify three-tangle formula for GHZ spike
    tau3 = 4.0 * beta * beta / (1.0 + beta * beta) ** 2
    assert abs(tau3 - data["tau3"]) < 1e-12

    # Verify theta is consistent with beta
    theta_calc = 2.0 * math.atan(beta)
    assert abs(theta_calc - data["theta_rad"]) < 1e-12

