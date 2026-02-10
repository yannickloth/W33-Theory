#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.ddmin_z3_candidate import process_candidate

p = Path('committed_artifacts') / 'PART_CVII_z3_candidate_1770606880_01.npz'
res = process_candidate(p, max_checks=500, time_limit=30)
print('Result:', res)
