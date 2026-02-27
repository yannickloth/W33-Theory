#!/usr/bin/env python3
import itertools

# canonical projective points in PG(3,3)
pts=[]
for v in itertools.product(range(3), repeat=4):
    if all(x==0 for x in v):
        continue
    # normalize: first nonzero coordinate to 1
    for x in v:
        if x!=0:
            inv = 1 if x==1 else 2
            norm = tuple((inv*y)%3 for y in v)
            pts.append(norm)
            break
# remove duplicates while preserving order
seen=set()
unique=[]
for p in pts:
    if p not in seen:
        seen.add(p)
        unique.append(p)
pts2=sorted(unique)
print(len(pts2))
print('first13', pts2[:13])
print('rest27', pts2[13:])
print('X0 values', [p[0] for p in pts2])
PYTHON