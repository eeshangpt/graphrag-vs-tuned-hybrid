import json

with open('recall.json') as f:
    data = json.load(f)
for k, v in data.items():
    print(k)
    print(" ", v)
