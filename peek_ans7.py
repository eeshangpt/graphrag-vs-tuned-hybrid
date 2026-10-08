import json, glob

for file in glob.glob("*prereg*.json"):
    with open(file) as f:
        data = json.load(f)
        if 'rows' not in data: continue
        methods = {}
        refs = {}
        for r in data['rows']:
            m = r['method']
            methods[m] = methods.get(m, 0) + 1
            if r['ans'].strip().lower() == 'unanswerable':
                refs[m] = refs.get(m, 0) + 1
        for m in methods:
            print(f"{file} - {m}: {refs.get(m, 0)}/{methods[m]} ({refs.get(m, 0)/methods[m]*100}%)")
