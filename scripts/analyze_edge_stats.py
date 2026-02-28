#!/usr/bin/env python3
import json
from collections import Counter
j=json.load(open('unrestricted_search_results.json'))
stats=j['edge_stats']
print(f"collected {len(stats)} samples")
c=Counter()
for s in stats:
    c[tuple(s)] +=1
print("distinct orbit patterns",len(c))
for pat,count in c.most_common(5):
    print(count,pat[:10],'...')
