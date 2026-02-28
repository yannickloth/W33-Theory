import csv
with open('edges_270_transport.csv') as f:
    for r in csv.DictReader(f):
        if int(r['qid'])==0:
            print(r)
