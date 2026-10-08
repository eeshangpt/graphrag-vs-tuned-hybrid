import json

with open('2wiki_n50_B1000_dense-bm25-hybrid-nocontext.json') as f:
    rows = json.load(f)['rows']
    print(rows[0].keys())
    print(rows[0])
