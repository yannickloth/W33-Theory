import subprocess
from pathlib import Path


def test_generate_conjugators_matches_committed(tmp_path: Path) -> None:
    out = tmp_path / "conjugators_generated.lean"
    subprocess.run(
        ["python", "scripts/generate_conjugators_lean.py", "--out", str(out)],
        check=True,
    )
    committed = Path("proofs/lean/conjugators_generated.lean").read_text(
        encoding="utf-8"
    )
    generated = out.read_text(encoding="utf-8")
    assert generated == committed
