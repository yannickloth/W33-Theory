#!/usr/bin/env python3
"""Driver to run bounded-LSQ helper and capture its printed output.
"""
from __future__ import annotations

import importlib

if __name__ == "__main__":
    mod = importlib.import_module("tools.constrained_lsq_mixed_patch")
    mod.main()
