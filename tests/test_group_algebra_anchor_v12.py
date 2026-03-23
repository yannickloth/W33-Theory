import json
import subprocess
from pathlib import Path


def test_group_algebra_anchor_v12_bridge_structure():
    script = Path("toe_session_20260316_v12") / "toe_session_20260316_v12" / "w33_group_algebra_anchor_v12.py"
    assert script.exists(), f"Expected v12 script at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v12") / "toe_session_20260316_v12" / "w33_group_algebra_anchor_results_v12.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    bridge = data["bridge_normal_forms"]
    assert bridge["rank_reduced"] == 1
    assert bridge["rank_162"] == 27
    assert bridge["rank_163"] == 28

    # lock the reduced bridge to the fermionic packet (J2 raising operator) in the cyclic basis.
    mat = bridge["reduced_bridge_cyclic_basis"]
    assert len(mat) == 6

    # compute expected N ⊗ J2 over GF(3)
    import numpy as np

    C = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=int)
    N = (np.eye(3, dtype=int) + C + (C @ C) % 3) % 3
    J2 = np.array([[0, 1], [0, 0]], dtype=int)
    expected = np.kron(N, J2) % 3

    mat_np = np.array(mat, dtype=int) % 3
    assert np.array_equal(mat_np, expected)
