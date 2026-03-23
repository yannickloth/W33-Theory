import json
import subprocess
from pathlib import Path


def test_hypercube_info_closure_v34_spectrum():
    script = Path("toe_session_20260316_v34") / "toe_session_20260316_v34" / "w33_hypercube_info_closure_v34.py"
    assert script.exists(), f"Expected v34 solver at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v34") / "toe_session_20260316_v34" / "w33_hypercube_info_results_v34.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    x = data["x"]
    eigen = data["walsh_diagonal_eigenvalues"]

    # Eigenvalues should match x^weight for each subset weight in the report.
    weights = data["subset_weights"]
    for weight, val in zip(weights, eigen):
        assert abs(val - (x ** weight)) < 1e-12

    # Observable map should match expected weights (same as v33 mapping)
    expected = {
        "Vus": 1,
        "Vcb": 2,
        "Vub": 4,
        "Vus*Vcb": 3,
        "Vus*Vub": 5,
        "Vcb*Vub": 6,
        "J": 7,
    }
    for obs, weight in expected.items():
        assert abs(data["observable_eigenvalues"][obs] - (x ** weight)) < 1e-12

    # Total capacity should equal sum of individual capacities
    total = data["total_capacity_bits"]
    capacities = data["capacities_bits"]
    assert abs(total - sum(capacities)) < 1e-12
