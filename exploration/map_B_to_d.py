from itertools import product

Bs=[((0,1),(2,0)),((0,2),(1,0)),((1,0),(2,1)),((1,0),(1,1)),((2,0),(0,2)),((2,0),(2,2)),((2,0),(1,2))]

def apply(B,u):
    (p,q),(r,s)=B
    x,y=u
    return ((p*x+q*y)%3,(r*x+s*y)%3)

for B in Bs:
    ds=[]
    for d in product(range(3),repeat=2):
        if d==(0,0): continue
        if apply(B,d)==(1,0):
            ds.append(d)
    print('B',B,'works for d',ds)
