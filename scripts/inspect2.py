import sys
lines=open('scripts/w33_universal_search.py','rb').read().splitlines(True)
for i,l in enumerate(lines,1):
    if 80<=i<=86:
        print(i, l)
        print(list(l))
