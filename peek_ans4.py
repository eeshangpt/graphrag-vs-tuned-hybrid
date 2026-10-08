import json

with open('musique_n50_B1000prereg_hippo.json') as f:
    rows = json.load(f)['rows']
    refusals = sum(1 for r in rows if r['ans'].strip().lower() == 'unanswerable')
    print("hippo refusals:", refusals)
