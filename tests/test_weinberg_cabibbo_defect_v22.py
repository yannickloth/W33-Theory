import json
import subprocess
from pathlib import Path

import sympy as sp


def test_weinberg_cabibbo_defect_v22_closure():
    script = Path("toe_session_20260316_v22") / "toe_session_20260316_v22" / "w33_weinberg_cabibbo_defect_v22.py"
    assert script.exists(), f"Expected v22 script at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v22") / "toe_session_20260316_v22" / "w33_weinberg_cabibbo_defect_results_v22.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    # Parse symbolic expressions and verify the exact closure identities
    x = sp.simplify(sp.Rational(3, 13))
    delta = sp.simplify(sp.sympify(data["delta_doc"]))
    c_doc = sp.simplify(sp.sympify(data["cabibbo_doc"]))
    R = sp.simplify(sp.sympify(data["R"]))
    R_from_delta = sp.simplify(sp.sympify(data["R_from_delta"]))
    u_from_delta = sp.simplify(sp.sympify(data["u_from_delta"]))

    # The defect definition: delta = 1 - sin(theta_C)/sin^2(theta_W)
    assert sp.simplify(1 - c_doc / x - delta) == 0

    # Closure identities claimed: R reconstructs from delta, and up-ratio is delta^4 scaled
    assert sp.simplify(R - R_from_delta) == 0
    assert sp.simplify(u_from_delta - sp.Rational(10**4, 2) * delta**4) == 0

    # sanity: delta should be positive and < 0.1
    assert 0 < float(delta) < 0.1
