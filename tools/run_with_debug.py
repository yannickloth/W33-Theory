#!/usr/bin/env python3
from importlib import import_module
import traceback

try:
    m = import_module('tools.suggest_nearest_canonical_for_top_edges')
    m.main()
except Exception:
    traceback.print_exc()
    raise
