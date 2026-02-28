import csv
from collections import Counter

with open('edges_270_transport.csv') as f:
    r=csv.DictReader(f)
    guesses=[int(row['block_guess']) for row in r]
print('unique guesses',len(set(guesses)), Counter(guesses))
