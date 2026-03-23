import json
import subprocess
from pathlib import Path


def test_generation_symmetry_v08_computes_3_generation_decomposition():
    script = Path("toe_session_20260316_v08") / "toe_session_20260316_v08" / "w33_generation_symmetry_v08.py"
    assert script.exists(), f"Expected script at {script}"

    proc = subprocess.run(["py", "-3", str(script)], capture_output=True, text=True, check=True)
    # script prints JSON to stdout
    data = json.loads(proc.stdout)

    # Expect the H1 splitting into 27+27+27
    mults = data.get("h1_eigenvalue_multiplicities", {})
    assert mults.get("1") == 27
    assert mults.get("omega") == 27
    assert mults.get("omega2") == 27

    # verify trace zero condition
    assert data.get("h1_trace") == 0

    # ensure the fixed simplex is a tetrahedron
    fixed_tet = data.get("fixed_tetrahedron")
    assert fixed_tet and len(fixed_tet) == 4
