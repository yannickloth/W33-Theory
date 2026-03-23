import json
import math
import subprocess
from pathlib import Path


def test_boolean_heat_duality_v37_macwilliams_and_spectrum():
    script = Path("toe_session_20260316_v37") / "toe_session_20260316_v37" / "w33_boolean_heat_duality_v37.py"
    assert script.exists(), f"Expected v37 solver at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v37") / "toe_session_20260316_v37" / "w33_boolean_heat_duality_results_v37.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    x = data["x"]
    eta = data["eta_dual"]

    # Verify dual variable formula
    assert abs(eta - (1 - x) / (1 + x)) < 1e-15

    # Verify Walsh spectrum is x^weight
    for row in data["weighted_walsh_spectrum"]:
        w = row["weighted_degree"]
        assert abs(row["heat_eigenvalue"] - (x ** w)) < 1e-15

    # Verify MacWilliams self-duality relation for the [8,4,4] enumerator
    lhs = data["macwilliams_check"]["lhs_W_x"]
    rhs = data["macwilliams_check"]["rhs_transformed_W_eta"]
    assert abs(lhs - rhs) < 1e-12
