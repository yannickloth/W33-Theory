#!/usr/bin/env python3
import json
from math import gcd

def compose(p,q): return tuple(p[i] for i in q)

def order(p):
    n=len(p)
    used=[False]*n
    o=1
    for i in range(n):
        if not used[i]:
            j=i; cnt=0
            while not used[j]:
                used[j]=True; j=p[j]; cnt+=1
            if cnt>0:
                o=o*cnt//gcd(o,cnt)
    return o

sols=json.load(open('unrestricted_solutions.json'))['solutions']
special=[170,224,239,296]
for idx in special:
    r=[tuple(sols[idx][i]) for i in range(4)]
    t=compose(r[3],compose(r[2],compose(r[1],r[0])))
    print(idx,'order t',order(t))
