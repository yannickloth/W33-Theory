"""Quick smoke tests for w33_universal_search.py.

These checks exercise the command-line interface with a tiny cycle bound so
that running `pytest` remains fast.  The heavy search is intentionally
restricted under test; developers can run the full search manually when
needed.
"""

import subprocess
import sys
import os
import json

def test_universal_search_smoke():
    """Run the search with --max-length 4 and verify output JSON is produced."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    cmd = [sys.executable, "scripts/w33_universal_search.py",
           "--max-length", "4", "--output", "data/test_ca_cycles.json"]
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert res.returncode == 0, f"search failed: {res.stderr}"
    assert os.path.exists("data/test_ca_cycles.json"), "output file missing"
    data = json.load(open("data/test_ca_cycles.json"))
    # expect at least one cycle of length <=4 (we know length-3 exists)
    assert any(len(rec[0]) <= 4 for rec in data), "no short cycles found"
    # also verify filtering to a known rule (15) works
    res2 = subprocess.run(cmd + ["--rule", "15"], env=env, capture_output=True, text=True)
    assert res2.returncode == 0, f"filtered search failed: {res2.stderr}"
    data2 = json.load(open("data/test_ca_cycles.json"))
    assert len(data2) > 0, "no cycles found for rule 15, filter may be broken"
    # clean up
    os.remove("data/test_ca_cycles.json")
