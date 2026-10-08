import json

with open('probe.json') as f:
    data = json.load(f)
    print("probe items:", len(data))
    for r in data[:2]:
        print(r.keys())
        break
