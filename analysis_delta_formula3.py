# script to emit Python dict for delta E polynomial terms
# reuse formulas from previous run (manually transcribed from output)
formulas = {
    (0,0): ['2*p^0q^0r^0s^0t^0', '2*p^0q^0r^0s^1t^0', '2*p^0q^0r^0s^1t^1', '1*p^0q^0r^0s^2t^0', '2*p^0q^0r^1s^0t^0', '2*p^0q^0r^1s^0t^1', '1*p^0q^0r^1s^1t^0', '1*p^0q^0r^2s^0t^0', '2*p^0q^0r^2s^0t^1', '2*p^0q^1r^0s^0t^0', '2*p^0q^1r^0s^0t^1'],
    (0,1): ['1*p^0q^0r^0s^0t^0', '2*p^0q^0r^0s^1t^1', '1*p^0q^0r^0s^2t^0', '1*p^0q^0r^1s^0t^0', '2*p^0q^0r^1s^0t^1', '2*p^0q^0r^1s^1t^0', '2*p^0q^0r^2s^0t^1', '2*p^0q^1r^0s^0t^0', '2*p^0q^1r^0s^0t^1'],
    (0,2): ['2*p^0q^0r^0s^1t^0', '2*p^0q^0r^0s^1t^1', '1*p^0q^0r^1s^0t^0', '1*p^0q^0r^1s^0t^1', '1*p^0q^0r^1s^1t^0', '2*p^0q^0r^2s^0t^0'],
    (1,0): ['2*p^0q^0r^0s^1t^1', '1*p^0q^0r^0s^2t^1', '2*p^0q^0r^1s^0t^1', '1*p^0q^0r^1s^1t^0', '1*p^0q^0r^1s^1t^1', '2*p^0q^0r^2s^0t^0', '2*p^0q^1r^0s^0t^1'],
    (1,1): ['2*p^0q^0r^0s^0t^0', '1*p^0q^0r^0s^0t^1', '2*p^0q^0r^0s^2t^0', '1*p^0q^0r^1s^0t^0', '1*p^0q^0r^1s^0t^1', '2*p^0q^0r^1s^1t^1', '1*p^0q^0r^2s^0t^1'],
    (1,2): ['2*p^0q^0r^0s^1t^1', '1*p^0q^0r^0s^2t^1', '1*p^0q^0r^1s^0t^1', '1*p^0q^0r^1s^1t^1', '1*p^0q^0r^2s^0t^1', '2*p^0q^1r^0s^0t^1'],
    (2,0): ['1*p^0q^0r^0s^0t^1', '2*p^0q^0r^0s^2t^1', '2*p^0q^0r^1s^1t^1', '1*p^0q^0r^2s^0t^1'],
    (2,1): ['1*p^0q^0r^0s^0t^1', '2*p^0q^0r^1s^0t^1', '1*p^0q^0r^2s^0t^1', '1*p^0q^1r^0s^0t^1'],
    (2,2): [],
}

# convert into structured dictionary with tuples
structured={}
for k,terms in formulas.items():
    lst=[]
    for term in terms:
        coef,rest=term.split('*')
        coef=int(coef)%3
        powers={'p':0,'q':0,'r':0,'s':0,'t':0}
        parts=rest.split('t^')
        # parse by splitting on each variable
        import re
        for var,exp in re.findall(r'([pqrs])\^(\d)',rest):
            powers[var]=int(exp)
        if 't^' in rest:
            powers['t']=int(rest.split('t^')[1])
        lst.append((coef,powers['p'],powers['q'],powers['r'],powers['s'],powers['t']))
    structured[k]=lst

print('deltaE_terms = ' + repr(structured))
