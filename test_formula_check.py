from scripts.ce2_global_cocycle import _evaluate_delta_e, _derive_simple_family_tables, _derive_naive_tables, _eval_f3_poly_sw

terms = { (2,2): [(1,0,0,0,0,0),(1,0,0,0,1,0),(2,0,0,0,2,0),(2,1,0,0,0,1),(2,1,0,1,0,1),(2,2,0,0,0,0),(1,2,0,0,0,1)] }
B=[[2,1],[2,0]]
p,q=B[0]
r,s=B[1]
t=1
mat=_evaluate_delta_e(p,q,r,s,t)
print('formula matrix',mat)
actual_e,actual_c0,_=_derive_simple_family_tables()
naive_e,naive_c0,_=_derive_naive_tables()
d=(2,2)
print('actual e coeffs',actual_e[t][d])
print('naive e coeffs',naive_e[t][d])
print('grid:')
for s0 in range(3):
    for w0 in range(3):
        act=_eval_f3_poly_sw(s0,w0,actual_e[t][d])
        nai=_eval_f3_poly_sw(s0,w0,naive_e[t][d])
        print(s0,w0,(act-nai)%3)
