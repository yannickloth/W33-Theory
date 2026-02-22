import json
from pathlib import Path

s = Path("artifacts/sign_consistent_summary.json")
arr = json.load(s.open())
print([int(item["W_idx"]) for item in arr])
