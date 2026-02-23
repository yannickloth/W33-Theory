"""Tests for the ca_on_cycle helper script."""

import subprocess
import sys
import os
import json


def test_cycle_script_and_rule():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # use test_ca_cycles.json produced by earlier smoke test; run w33_universal_search quickly
    subprocess.run([sys.executable, "scripts/w33_universal_search.py", "--max-length", "4", "--output", "data/test_ca_cycles.json"], env=env)
    data = json.load(open("data/test_ca_cycles.json"))
    assert data, "no cycles generated"
    cycle = data[0][0]
    # invoke script on this cycle
    cycle_str = ",".join(map(str, cycle))
    res = subprocess.run([sys.executable, "scripts/ca_on_cycle.py", "--cycle", cycle_str], env=env, capture_output=True, text=True)
    assert res.returncode == 0, f"script failed: {res.stderr}"
    # output should mention 'rule' or 'not circulant'
    assert "rule" in res.stdout.lower() or "not circulant" in res.stdout.lower()
    # clean up
    os.remove("data/test_ca_cycles.json")
