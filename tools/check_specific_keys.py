#!/usr/bin/env python3
import json
from pathlib import Path
art = json.loads(Path('artifacts/edge_to_e8_root_combined.json').read_text(encoding='utf-8'))
for k in ['(25, 17)', '(17, 25)', '(17, 18)', '(18, 17)', '(34, 37)', '(37, 34)', '(20, 35)', '(35, 20)']:
    print(k, k in art)
