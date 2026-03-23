import json
import subprocess
from pathlib import Path

import sympy as sp


def test_up_sector_inverse_packet_v23_defect_control():
    script = Path("toe_session_20260316_v23") / "toe_session_20260316_v23" / "w33_up_sector_inverse_packet_v23.py"
    assert script.exists(), f"Expected v23 script at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v23") / "toe_session_20260316_v23" / "w33_up_sector_inverse_packet_results_v23.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    delta = float(sp.N(sp.sympify(data["delta"]), 30))
    u = float(sp.N(sp.sympify(data["u"]), 30))
    epsilon_u = float(sp.N(sp.sympify(data["epsilon_u"]), 30))
    theta_u = float(sp.N(sp.sympify(data["theta_u_decimal"]), 30))

    # The defect delta should control the up-sector breaking strength.
    # Allow small numerical rounding; the theory predicts epsilon_u ≈ delta
    # Up-sector breaking epsilon_u should be extremely close to delta (within rounding tolerance).
    assert abs(epsilon_u - delta) < 1e-4

    # The up-sector mixing should be tiny (O(0.003)), and significantly smaller than Cabibbo.
    assert 0 < theta_u < 0.01

    # u should be close to delta^4 * (Theta^mu/2) as specified in the theory notes.
    # Theta^mu/2 = 10^4 / 2 = 5000
    assert abs(u - (5000 * delta**4)) < 1e-6
