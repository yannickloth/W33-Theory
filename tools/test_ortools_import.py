#!/usr/bin/env python3
import traceback

try:
    import ortools

    print("ORTOOLS OK", ortools.__version__)
except Exception:
    traceback.print_exc()
