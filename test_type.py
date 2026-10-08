import json

with open('2wiki_n50_B1000_dense-bm25-hybrid-nocontext.json') as f:
    rows = json.load(f)['rows']

types = {}
for r in rows:
    if r['method'] not in ['dense', 'nocontext']: continue
    t = r['gen']['type'] if 'type' in r['gen'] else r.get('q_type', 'unknown')
    if t == 'unknown' and 'type' in r:
        t = r['type']
    
    if t not in types: types[t] = {'n':0, 'dense':[], 'nocontext':[]}
    types[t][r['method']].append(r['f1'])

for t, d in types.items():
    if len(d['dense']) > 0:
        d_mean = sum(d['dense'])/len(d['dense'])
        n_mean = sum(d['nocontext'])/len(d['nocontext'])
        print(f"{t} {len(d['dense'])} ({n_mean:.2f} / {d_mean:.2f})")
