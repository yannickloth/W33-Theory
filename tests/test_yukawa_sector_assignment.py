import subprocess
import sys
import os
import json


def test_sector_assignment_runs():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    res = subprocess.run([sys.executable, "scripts/yukawa_sector_assignment.py"], env=env)
    assert res.returncode == 0
    assert os.path.exists("data/yukawa_sector_assignment.json")


def test_best_assignment_structure():
    data = json.load(open("data/yukawa_sector_assignment.json"))
    best = data.get("best")
    assert best is not None
    assert "perm" in best and "sectors" in best
    # ensure the permutation is length 3 with unique entries
    perm = tuple(best["perm"])
    assert len(perm) == 3 and set(perm) == {0,1,2}
    # ensure sectors list matches
    sectors = best["sectors"]
    assert len(sectors) == 3
