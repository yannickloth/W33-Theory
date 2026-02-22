#!/usr/bin/env python3
"""Run PySAT+CryptoMiniSat mapping sweep across sign-consistent W indices.

For each W in artifacts/sign_consistent_summary.json, run:
 - python tools/pysat_cryptosat_mapping_W4.py --w-index <W> (XOR-enabled)
 - python tools/pysat_cryptosat_mapping_W4.py --w-index <W> --no-xor (CNF-only)

Collect per-W results and write artifacts/pysat_cryptosat_sweep_summary.json.

The script is safe to re-run; it will overwrite the per-W artifact if present.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
TOOLS = ROOT / "tools"

SCRIPTPATH = TOOLS / "pysat_cryptosat_mapping_W4.py"
if not SCRIPTPATH.exists():
    print("Missing script:", SCRIPTPATH)
    raise SystemExit(1)

summary_file = ART / "sign_consistent_summary.json"
if not summary_file.exists():
    print(
        "Missing sign_consistent_summary.json; run sign consistency preprocessing first"
    )
    raise SystemExit(1)

summary = json.load(open(summary_file, "r", encoding="utf-8"))
W_list = [int(entry["W_idx"]) for entry in summary]

results = []

# check optional deps
deps = {"pycryptosat": False, "pysat": False}
try:
    import pycryptosat

    deps["pycryptosat"] = True
except Exception:
    pass
try:
    import pysat

    deps["pysat"] = True
except Exception:
    pass

print("Dependency check:", deps)
if not deps["pycryptosat"]:
    print(
        "Warning: pycryptosat not available; parity checks and XOR clauses will not function (CNF-only runs still fine if pysat is available)"
    )

# per-run timeout
per_run_timeout = 1800  # seconds per run

for W in W_list:
    entry = {"W_idx": W, "xor_run": {}, "cnf_only_run": {}}
    # XOR-enabled run
    cmd = [sys.executable, str(SCRIPTPATH), "--w-index", str(W)]
    print("Running XOR-enabled mapping for W", W, "cmd:", " ".join(cmd))
    t0 = time.monotonic()
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=per_run_timeout)
        elapsed = time.monotonic() - t0
        entry["xor_run"]["returncode"] = proc.returncode
        entry["xor_run"]["elapsed"] = elapsed
        entry["xor_run"]["stdout"] = proc.stdout.decode("utf-8", errors="replace")[
            :2000
        ]
        entry["xor_run"]["stderr"] = proc.stderr.decode("utf-8", errors="replace")[
            :2000
        ]
        # read artifact if present
        art = ART / f"pysat_cryptosat_W{W}_mapping_signs.json"
        if art.exists():
            entry["xor_run"]["artifact"] = json.load(open(art, "r", encoding="utf-8"))
    except subprocess.TimeoutExpired:
        entry["xor_run"]["timeout"] = True
    except Exception as e:
        entry["xor_run"]["error"] = str(e)

    # CNF-only run
    cmd = [sys.executable, str(SCRIPTPATH), "--w-index", str(W), "--no-xor"]
    print("Running CNF-only mapping for W", W, "cmd:", " ".join(cmd))
    t0 = time.monotonic()
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=per_run_timeout)
        elapsed = time.monotonic() - t0
        entry["cnf_only_run"]["returncode"] = proc.returncode
        entry["cnf_only_run"]["elapsed"] = elapsed
        entry["cnf_only_run"]["stdout"] = proc.stdout.decode("utf-8", errors="replace")[
            :2000
        ]
        entry["cnf_only_run"]["stderr"] = proc.stderr.decode("utf-8", errors="replace")[
            :2000
        ]
        # read artifact if present
        art = ART / f"pysat_cryptosat_W{W}_mapping_signs.json"
        if art.exists():
            entry["cnf_only_run"]["artifact"] = json.load(
                open(art, "r", encoding="utf-8")
            )
        # check sign_unsat_cores modification
        snc = ART / "sign_unsat_cores.json"
        if snc.exists():
            entry["cnf_only_run"]["sign_unsat_cores"] = json.load(
                open(snc, "r", encoding="utf-8")
            )
    except subprocess.TimeoutExpired:
        entry["cnf_only_run"]["timeout"] = True
    except Exception as e:
        entry["cnf_only_run"]["error"] = str(e)

    results.append(entry)
    # write intermediate summary each iteration
    (ART / "pysat_cryptosat_sweep_summary.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )

print(
    "Sweep completed; summary written to artifacts/pysat_cryptosat_sweep_summary.json"
)
sys.exit(0)
