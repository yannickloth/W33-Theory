#!/usr/bin/env python3
import runpy, traceback
try:
    runpy.run_path('tools/generate_candidates_for_edges.py', run_name='__main__')
except Exception:
    traceback.print_exc()
    raise
