import json
s=json.load(open('spa_triality_summary.json'))
for bi,(v,w) in enumerate(zip(s['spa'],s['spa_after_t4'])):
    if v is not None and w is not None:
        print(bi,v,'->',w)
