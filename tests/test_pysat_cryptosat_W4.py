import json
import subprocess
import sys

import pytest

pytest.importorskip("pycryptosat")
pytest.importorskip("pysat")


def test_pysat_cryptosat_w4_finds_valid_mapping():
    # run the prototype script; it writes artifact on success
    res = subprocess.run([sys.executable, "tools/pysat_cryptosat_mapping_W4.py"])
    assert res.returncode == 0
    data = json.load(
        open("artifacts/pysat_cryptosat_W4_mapping_signs.json", "r", encoding="utf-8")
    )
    assert data.get("sat") is True
    assert data.get("valid") is True
