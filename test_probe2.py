import json
with open('probe.json') as f:
    data = json.load(f)
for r in data:
    if r['ds'] == '2wiki' and r['cf_follows_ctx']:
        print(r['alt'], "|", r['ans_cf_ctx'])
