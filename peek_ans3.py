import json

with open('musique_n50_B1000prereg_hippo.json') as f:
    rows = json.load(f)['rows']
    print(rows[0].keys())
