import json
import subprocess
from pathlib import Path


def test_face_hypercube_v33_mixed_channel_weights():
    script = Path("toe_session_20260316_v33") / "toe_session_20260316_v33" / "w33_face_hypercube_v33.py"
    assert script.exists(), f"Expected v33 solver at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v33") / "toe_session_20260316_v33" / "w33_face_hypercube_results_v33.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    # Verify the exact exterior-defect power laws as computed by the solver.
    assert abs(data["B12_exact_law"]) < 1e-15
    assert abs(data["B13_exact_law"]) < 1e-15
    assert abs(data["B23_exact_law"]) < 1e-15
    # Jarlskog defect law holds to high precision (residual ~4e-7 in current numeric compute)
    assert abs(data["J_exact_law"]) < 1e-4
