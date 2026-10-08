import json

with open('musique_n50_B1000prereg_nocontext-dense.json') as f:
    rows = json.load(f)['rows']
    methods = {}
    for r in rows:
        m = r['method']
        methods[m] = methods.get(m, 0) + 1
        if r['ans'].strip().lower() == 'unanswerable':
            methods[m + '_ref'] = methods.get(m + '_ref', 0) + 1
    print(methods)
