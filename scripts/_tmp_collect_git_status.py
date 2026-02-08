#!/usr/bin/env python3
import subprocess
from pathlib import Path
out = Path('checks') / '_tmp_git_status.txt'
proc = subprocess.run(['git','status','--porcelain','--untracked-files=all'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
out.write_text(proc.stdout, encoding='utf-8')
print('Wrote', out)
