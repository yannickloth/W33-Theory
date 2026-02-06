import json
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / "artifacts"


def test_canonical_forbid_choice_file_exists_and_matches_report():
    p = ART / "canonical_forbid_choice.json"
    assert p.exists(), "canonical_forbid_choice.json missing"
    data = json.loads(p.read_text(encoding="utf-8"))
    cf = data.get("canonical_forbid")
    assert isinstance(cf, list) and len(cf) == 3
    # make sure the report and anchor file exist for the chosen forbid
    report = (
        Path(__file__).resolve().parents[1]
        / "reports"
        / f"anchor_forbid_{cf[0]}-{cf[1]}-{cf[2]}.md"
    )
    assert (
        report.exists()
    ), f"Anchor report for chosen canonical forbid not found: {report}"
