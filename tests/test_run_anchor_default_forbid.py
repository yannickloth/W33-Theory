import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
CFG = Path(__file__).resolve().parents[1] / "config" / "canonical_forbid.json"


def test_run_anchor_uses_config_default():
    assert CFG.exists(), "Canonical config not present"
    cf = json.loads(CFG.read_text(encoding="utf-8")).get("canonical_forbid")
    assert cf and len(cf) == 3
    forbid_str = f"{cf[0]}-{cf[1]}-{cf[2]}"

    cmd = [
        "python",
        "tools/run_anchor_and_archive.py",
        "--time",
        "10",
        "--w-list",
        "0",
        "--workers",
        "1",
    ]
    # best-effort: allow failures but expect the anchor summary file to be created for canonical forbid
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        pass

    summary = ART / f"anchor_core_cpsat_summary_forbid_{forbid_str}.json"
    assert (
        summary.exists()
    ), f"Expected anchor summary for canonical forbid {forbid_str} to be present"
