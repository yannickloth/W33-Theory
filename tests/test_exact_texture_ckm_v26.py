import json
import math
import subprocess
from pathlib import Path


def test_exact_texture_ckm_v26_closure():
    script = Path("toe_session_20260316_v26") / "toe_session_20260316_v26" / "w33_exact_texture_ckm_v26.py"
    assert script.exists(), f"Expected v26 script at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v26") / "toe_session_20260316_v26" / "w33_exact_texture_ckm_results_v26.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    R = data["R"]
    r_d = data["r_d_m_d_over_m_s"]
    r_u = data["r_u_m_u_over_m_c"]

    # Exact claimed relations
    assert abs(r_d - 1/20) < 1e-12
    assert abs(r_u - (R**3 / 200.0)) < 1e-12

    # Angles from tan(theta)=sqrt(r)
    theta_d = math.atan(math.sqrt(r_d))
    theta_u = math.atan(math.sqrt(r_u))
    assert abs(theta_d - data["theta_d_exact_rad"]) < 1e-12
    assert abs(theta_u - data["theta_u_exact_rad"]) < 1e-12

    # Verify the exact normalized texture formula reproduces the dressed Cabibbo target
    assert abs(data["Vus_exact_from_texture"] - data["sin_theta_C_target"]) < 1e-15
    assert abs(data["Vus_exact_from_compact_formula"] - data["sin_theta_C_target"]) < 1e-15

    # Phase should be near 100 degrees and differ from GST shadow by ~8 degrees
    assert abs(data["phi_exact_texture_deg"] - 100.16946) < 0.001
    assert abs(data["phi_exact_texture_deg"] - data["phi_gst_shadow_deg"]) > 7.5
