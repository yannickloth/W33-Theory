import sys
lines=open('scripts/w33_universal_search.py','rb').read().splitlines(True)
for i in range(64,74):
    b=lines[i]
    print(i+1, b)
    print('hex', b.hex())
