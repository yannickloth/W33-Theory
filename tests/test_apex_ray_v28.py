import json
import subprocess
from pathlib import Path


def test_apex_ray_v28_apex_definition():
    script = Path("toe_session_20260316_v28") / "toe_session_20260316_v28" / "w33_apex_ray_v28.py"
    assert script.exists(), f"Expected v28 script at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v28") / "toe_session_20260316_v28" / "w33_apex_ray_v28_results.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    # Check the key structural statements
    assert abs(data["rho_bar"]) > 0
    assert abs(data["eta_bar"]) > 0
    assert abs(data["apex_radius"] - (data["rho_bar"]**2 + data["eta_bar"]**2)**0.5) < 1e-12

    # Verify the apex is near the predicted direction delta=atan(2)
    assert abs(data["phase_defect_deg"]) < 0.1

    # verify the ray scaling is close to the series approximation (within ~0.001)
    assert abs(data["ray_scale_exact"] - data["ray_scale_series"]) < 0.001

    # the apex direction should be extremely close to the old Schläfli phase (delta=atan(2))
    assert abs(data["phase_defect_deg"]) < 0.05
