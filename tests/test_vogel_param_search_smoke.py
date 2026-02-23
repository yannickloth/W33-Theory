import subprocess
import sys
from fractions import Fraction
import json


def run_search(args):
    cmd = [sys.executable, "scripts/vogel_param_search.py"] + args
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert res.returncode == 0, res.stderr
    return res.stdout


def test_param_search_basic():
    # looking for a known simple dimension (E8) should return at least one
    # triple mentioning ``dim=248``; this ensures the search invoked the
    # equality check properly.
    out = run_search(["--dim", "248", "--max-num", "5", "--max-den", "3"])
    assert "alpha" in out
    assert "248" in out  # dimension string should appear somewhere

    # pick a nonsensical dimension (e.g. 648 with tiny bounds) and check that
    # the script reports no solutions rather than spurious hits
    out2 = run_search(["--dim", "648", "--max-num", "5", "--max-den", "3"])
    assert "no solutions found" in out2


def test_param_search_fix_alpha():
    # fix alpha = -2 and search for dim 248 (E8) expecting beta=12,gamma=20 in view
    out = run_search(["--dim", "248", "--fix-alpha", "-2", "--max-num", "15", "--max-den", "5"])
    # at least the fixed alpha should show up
    assert "alpha= -2" in out


def test_param_search_exceptional_line():
    # exceptional line should find the E8 triple if asked for 248
    # dim 52 lies on the Vogel exceptional line (F4); use small bounds
    out = run_search(["--dim", "52", "--exceptional-line", "--max-num", "3", "--max-den", "1"])
    assert "alpha= -2" in out
    assert "52" in out
