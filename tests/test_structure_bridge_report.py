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
    # report should include a summary section and mention each registered class
    assert "MONOMIAL LIFT SUMMARY" in out
    assert "11A" in out
    assert "identity" in out
    assert proc.returncode == 0


def test_bridge_report_with_ce2_flag(tmp_path):
    # CE2 option adds an extra checkbox to the lift summary
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/w33_monster_structure_bridge_report.py",
            "--include-monomial-lifts",
            "--include-ce2",
            "--max-q-exp",
            "2",
        ],
        cwd=str(Path(__file__).parent.parent),
        capture_output=True,
        text=True,
        timeout=30,
    )
    out = proc.stdout + proc.stderr
    assert "CE2 anomaly" in out
    assert proc.returncode == 0
