import subprocess
import sys


def test_yukawa_analysis_runs():
    # script should execute without crashing and produce exit code 0
    import os
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # run without capturing output to avoid encoding headaches
    res = subprocess.run([sys.executable, "scripts/yukawa_analysis.py"], env=env)
    assert res.returncode == 0, "yukawa_analysis exited with non-zero status"
