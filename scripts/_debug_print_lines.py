import sys
lines=open('scripts/w33_universal_search.py','rb').read().splitlines()
for i,l in enumerate(lines,1):
    if 70<=i<=90:
        print(i, repr(l))
