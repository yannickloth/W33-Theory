import importlib
import sys
from pathlib import Path

# Add pillars/ and exploration/ to import path so test files
# can import from THEORY_PART_* modules after repo reorganization.
_root = Path(__file__).resolve().parent
for _subdir in ("pillars", "exploration"):
    _p = str(_root / _subdir)
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Detect availability of optional heavy dependencies
_optional_modules = {
    "pandas": False,
    "sage": False,
}

import re

_skip_triggers = {
    "pandas": [re.compile(r"^\s*(import|from)\s+pandas\b", re.M)],
    "sage": [
        re.compile(r"^\s*(import|from)\s+sage\b", re.M),
        re.compile(r"from\s+sage\.all", re.M),
    ],
}


def pytest_ignore_collect(path, config):
    """Skip collecting test files that reference optional heavy dependencies
    which are not available in the current environment. This prevents
    the test run from failing with ImportError on machines without
    those optional packages (e.g., CI runners without Sage or user venvs
    without pandas)."""
    p = Path(str(path))

    # Only apply this heuristic to Python test files. Scanning the entire repo can be
    # very noisy and slow, and can trigger surprising capture/log issues.
    if not (p.suffix == ".py" and p.name.startswith("test_")):
        return None

    # Local exploratory tests (kept untracked) should not affect canonical runs.
    if p.name in {"test_yukawa_mass_ratios.py"}:
        return True

    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

    for mod, triggers in _skip_triggers.items():
        if not _optional_modules.get(mod, False):
            for trig in triggers:
                # trig is a compiled regex pattern, use .search to test
                if trig.search(text):
                    # skip collecting this test file
                    if getattr(config.option, "verbose", 0) > 0:
                        print(f"Skipping {path} (requires {mod})")
                    return True
    return None


def main():
    for m in list(_optional_modules.keys()):
        try:
            importlib.import_module(m)
            _optional_modules[m] = True
        except Exception:
            _optional_modules[m] = False


# Initialize optional dependency detection at import time so collection behaves as intended.
main()
