import json
import subprocess
from pathlib import Path


def test_e6_structural_seed_writes_and_is_bijective(tmp_path):
    out = Path("checks") / "PART_CVII_e8_seed_e6_structural_test.json"
    # call script as subprocess to avoid heavy imports in test process
    cmd = [
        "py",
        "-3",
        "scripts/generate_e6_structural_seed.py",
        "--seed",
        "123",
        "--output",
        str(out),
        "--no-check",
    ]
    subprocess.run(cmd, check=True)
    assert out.exists()
    j = json.loads(out.read_text(encoding="utf-8"))
    seed_edges = j.get("seed_edges", [])
    assert len(seed_edges) == 240
    roots = [int(it["root_index"]) for it in seed_edges]
    assert len(set(roots)) == 240, "Root indices must be unique (bijection)"
