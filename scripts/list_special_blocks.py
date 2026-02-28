import json

d=json.load(open('block_to_pockets.json'))
print('special blocks len2:', [int(b) for b,m in d.items() if len(m)==2])
print('special pockets for these blocks:', {b:d[b] for b in d if len(d[b])==2})
