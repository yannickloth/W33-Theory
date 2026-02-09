import json
from pathlib import Path


def test_verified_seed_type_if_present():
    base = Path.cwd()
    art_dir = base / "committed_artifacts"
    if not art_dir.exists():
        return
    files = sorted(art_dir.glob("PART_CVII_dd_pair_obstruction_*.json"))
    for f in files:
        j = json.loads(f.read_text(encoding="utf-8"))
        if "verified_seed" in j:
            assert isinstance(
                j["verified_seed"], int
            ), f"verified_seed in {f} must be int"
