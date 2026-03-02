
#!/usr/bin/env python3
"""run_all.py

Convenience runner: builds W33, builds 480-operator, verifies Ihara–Bass,
then outputs the alpha hinge derivation.
"""

import subprocess, sys

cmds = [
    [sys.executable, "build_w33.py"],
    [sys.executable, "nonbacktracking_480.py"],
    [sys.executable, "ihara_bass_verify.py"],
    [sys.executable, "alpha_from_operator.py"],
]

for cmd in cmds:
    print("\n" + "="*80)
    print("RUN:", " ".join(cmd))
    print("="*80)
    subprocess.check_call(cmd)
