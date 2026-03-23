import json
import subprocess
from pathlib import Path

import sympy as sp


def test_relative_gst_phase_v24_cos_phi_and_quadrature():
    script = Path("toe_session_20260316_v24") / "toe_session_20260316_v24" / "w33_relative_gst_phase_v24.py"
    assert script.exists(), f"Expected v24 script at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v24") / "toe_session_20260316_v24" / "w33_relative_gst_phase_results_v24.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    cos_phi = sp.simplify(sp.sympify(data["cos_phi"]))
    phi = sp.simplify(sp.sympify(data["phi"]))

    # Ensure relative phase is close to pi/2 (within ~2.5 degrees) and cos(phi) is near -1/29.
    assert abs(float(sp.N(phi - sp.pi/2, 20))) < 0.05
    assert abs(float(sp.N(cos_phi + sp.Rational(1, 29), 20))) < 0.02

    # Ensure dressed Cabibbo is approximately quadrature sum of seeds.
    cab = float(sp.N(sp.sympify(data["cabibbo_dressed"]), 20))
    quad = float(sp.N(sp.sympify(data["cabibbo_quadrature"]), 20))
    assert abs(cab - quad) < 0.01
