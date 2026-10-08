import json, glob

for file in glob.glob("*prereg*.json"):
    with open(file) as f:
        data = json.load(f)
        if 'rows' not in data: continue
        rows = data['rows']
        refusals = sum(1 for r in rows if r['ans'].strip().lower() == 'unanswerable')
        print(f"{file}: {refusals}/50 ({refusals/50*100}%)")
