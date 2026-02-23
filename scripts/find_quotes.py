import re
import sys
for i,l in enumerate(open('scripts/w33_universal_search.py'),1):
    if '"""' in l:
        sys.stdout.write(f"{i}: {l}")
