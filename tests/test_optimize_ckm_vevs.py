"""Tests for the CKM optimization helper script."""

import subprocess
import sys
import os
import json
import re


def test_optimize_runs_and_improves():
    # ensure input data exists by running the main blocks script first
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    subprocess.run([sys.executable, "scripts/w33_yukawa_blocks.py"], env=env, cwd=os.getcwd())
    # run optimizer
    res = subprocess.run([sys.executable, "scripts/optimize_ckm_vevs.py"],
                         env=env, capture_output=True, text=True)
    assert res.returncode == 0, f"optimizer failed: {res.stderr}"
    out = res.stdout
    # baseline error should appear
    m = re.search(r"baseline CKM error = ([0-9\.]+)", out)
    assert m, "did not find baseline error"
    baseline = float(m.group(1))
    m2 = re.search(r"best error ([0-9\.]+) for up/down", out)
    assert m2, "did not find best error"
    best = float(m2.group(1))
    assert best < baseline, "optimizer did not find improvement"
    # the search should reduce the error significantly; historical minimum ~0.09
    assert best < 0.1, "optimizer improvement is too small (expected <0.1)"
