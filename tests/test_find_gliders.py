"""Smoke tests for find_gliders.py"""

import subprocess
import sys
import os


def test_glider_script_runs():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    res = subprocess.run([sys.executable, "scripts/find_gliders.py", "--rule", "totalistic", "--steps", "10"],
                         env=env, capture_output=True, text=True)
    assert res.returncode == 0, f"glider script failed:{res.stderr}"
    # output should mention 'gliders' or 'no single-site gliders'
    out = res.stdout.lower()
    assert "gliders" in out
