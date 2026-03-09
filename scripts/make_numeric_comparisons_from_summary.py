import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.json_safe import dump_json

SUMMARY_CANDIDATES = [
    ROOT / "SUMMARY_RESULTS.json",
    ROOT / "claude_workspace" / "SUMMARY_RESULTS.json",
]


def as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def comparison_name(measured_key: str, predicted_key: str) -> str:
    measured_key = measured_key.lower()
    predicted_key = predicted_key.lower()
    if "w0" in measured_key or "w0" in predicted_key:
        return "DESI w0"
    return f"{measured_key} vs {predicted_key}"


def collect_pairs(node, filename: str, out: list[dict]) -> None:
    if isinstance(node, list):
        for item in node:
            collect_pairs(item, filename, out)
        return
    if not isinstance(node, dict):
        return

    keys = list(node.keys())
    measured_keys = [
        key
        for key in keys
        if any(token in key.lower() for token in ("meas", "observ", "experimental"))
    ]
    predicted_keys = [
        key
        for key in keys
        if any(token in key.lower() for token in ("pred", "w33", "theory"))
    ]

    for measured_key in measured_keys:
        measured = as_float(node.get(measured_key))
        if measured is None:
            continue
        for predicted_key in predicted_keys:
            predicted = as_float(node.get(predicted_key))
            if predicted is None:
                continue
            diff = predicted - measured
            out.append(
                {
                    "file": filename,
                    "name": comparison_name(measured_key, predicted_key),
                    "measured": measured,
                    "predicted": predicted,
                    "diff": diff,
                    "pct": (abs(diff) / abs(measured) * 100.0) if measured else None,
                }
            )

    for value in node.values():
        collect_pairs(value, filename, out)


def load_summary(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def summary_entries(summary: dict) -> list[tuple[str, object]]:
    summaries = summary.get("summaries")
    if isinstance(summaries, dict) and summaries:
        return list(summaries.items())
    entries = []
    for path in ROOT.glob("PART_*.json"):
        with path.open("r", encoding="utf-8") as handle:
            entries.append((path.name, json.load(handle)))
    return entries


def main() -> None:
    summary_path = next((path for path in SUMMARY_CANDIDATES if path.exists()), None)
    if summary_path is None:
        raise FileNotFoundError(
            "SUMMARY_RESULTS.json not found in repo root or claude_workspace"
        )

    summary = load_summary(summary_path)
    comparisons: list[dict] = []
    for filename, payload in summary_entries(summary):
        collect_pairs(payload, filename, comparisons)

    out = summary_path.parent / "NUMERIC_COMPARISONS.json"
    dump_json(comparisons, out, indent=2, sort_keys=True)
    print(f"Wrote {out} with {len(comparisons)} numeric comparisons")


if __name__ == "__main__":
    main()
