from scripts.ce2_global_cocycle import _derive_simple_family_tables, _derive_naive_tables, _eval_f3_poly_sw, _fit_f3_poly_sw

d=(0,1)
actual_e, actual_c0, _ = _derive_simple_family_tables()
naive_e, naive_c0, _ = _derive_naive_tables()
delta_vals={}
for s in range(3):
    for w in range(3):
        act=_eval_f3_poly_sw(s,w,actual_c0[1][d])
        nai=_eval_f3_poly_sw(s,w,naive_c0[1][d])
        delta_vals[(s,w)]=(act-nai)%3
poly=_fit_f3_poly_sw(delta_vals)
print('ΔC0 poly for d',d,poly)
