import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def test_phase_lift_inspector_on_11a(tmp_path):
    # prepare JSON with 11A generators in cycle notation
    data = {
        "11A": [[1, 4], [3, 10], [5, 11], [6, 12], [1, 8, 9], [2, 3, 4], [5, 12, 11], [6, 10, 7]]
    }
    file = tmp_path / "gens.json"
    file.write_text(json.dumps(data), encoding="utf-8")

    # run inspector as a subprocess to simulate CLI
    proc = subprocess.run(
        [sys.executable, "scripts/phase_lift_inspector.py", str(file)],
        cwd=str(Path(__file__).parent.parent),
        capture_output=True,
        text=True,
        timeout=10,
    )
    out = proc.stdout + proc.stderr
    assert "monomial group order" in out
    # expect number somewhere in output
    assert "190080" in out
    assert proc.returncode == 0
