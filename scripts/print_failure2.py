import csv
with open('edges_270_transport.csv') as f:
    for r in csv.DictReader(f):
        if int(r['qid'])==3 and r['gen']=='g8':
            print(r)
            break
