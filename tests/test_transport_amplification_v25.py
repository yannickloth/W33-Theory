import json
import subprocess
from pathlib import Path


def test_transport_amplification_v25_gain_and_rebuild():
    script = Path("toe_session_20260316_v25") / "toe_session_20260316_v25" / "w33_transport_amplification_v25.py"
    assert script.exists(), f"Expected v25 script at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v25") / "toe_session_20260316_v25" / "w33_transport_amplification_results_v25.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    G_exact = data["G_exact"]
    G_asym = data["G_asym"]
    rel_err = abs(data["G_rel_error"])

    # Strong structure: amplification factor is almost exactly the asymptotic W33 scalar.
    assert abs(G_exact - 12.698966462264) < 1e-6
    assert abs(G_asym - 12.693924415423) < 1e-6
    # relative deviation between exact and asymptotic is small (~4e-4)
    assert rel_err < 1e-3

    # The rebuild formula should match the dressed Cabibbo target extremely closely.
    assert abs(data["rebuild_exact_error"]) < 1e-12
    assert abs(data["rebuild_asym_error"]) < 5e-6
