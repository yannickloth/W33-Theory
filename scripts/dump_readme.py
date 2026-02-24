from pathlib import Path
lines = Path('README.md').read_text(encoding='utf-8').splitlines()
for i in range(130,190):
    print(f"{i+1:4d}: {lines[i]}")
