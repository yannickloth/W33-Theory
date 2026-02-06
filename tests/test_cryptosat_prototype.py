import subprocess
import sys

import pytest

# Skip test if pycryptosat not available in CI (we may not want to install it there)
pytest.importorskip("pycryptosat")


def test_cryptosat_detects_cores_quickly():
    res = subprocess.run([sys.executable, "tools/cryptosat_check_cores.py"])
    assert res.returncode == 0
