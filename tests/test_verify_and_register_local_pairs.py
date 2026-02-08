import importlib.util
from pathlib import Path


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_pairs", "scripts/verify_and_register_local_pairs.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_write_seed_for_pair(tmp_path):
    mod = load_module()
    fp = tmp_path / "seed.json"
    mod.write_seed_for_pair(37, 22, 38, 23, fp)
    assert fp.exists()
    j = fp.read_text(encoding="utf-8")
    assert "seed_edges" in j
    assert "edge_index" in j
    assert "root_index" in j
