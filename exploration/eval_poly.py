from scripts.ce2_global_cocycle import _eval_f3_poly_sw
poly=((1,1,1),(2,2,2),(1,1,1))
print('values:')
for s in range(3):
    for w in range(3):
        print(s,w,_eval_f3_poly_sw(s,w,poly))
