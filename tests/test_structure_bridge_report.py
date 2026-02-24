import subprocess
import sys
from pathlib import Path


def test_bridge_report_generic_monomial(tmp_path):
    # run the bridge report with the monomial-lift option and small q-exp filter
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/w33_monster_structure_bridge_report.py",
            "--include-monomial-lifts",
            "--max-q-exp",
            "2",
        ],
        cwd=str(Path(__file__).parent.parent),
        capture_output=True,
        text=True,
        timeout=30,
    )
    out = proc.stdout + proc.stderr
    # should mention at least one monomial lift or generic lift
    assert "monomial lift" in out
    assert proc.returncode == 0
