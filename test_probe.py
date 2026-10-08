import json

with open('probe.json') as f:
    data = json.load(f)

for ds in ['musique', '2wiki']:
    subset = [r for r in data if r['ds'] == ds]
    print(f"--- {ds} ---")
    orig_contains_gold = sum(1 for r in subset if r['gold'].lower() in r.get('ans_orig_ctx', '').lower()) # Wait, original context contains gold or ans_orig_ctx contains gold?
    print(f"Total: {len(subset)}")
    cf_follows = sum(1 for r in subset if r['cf_follows_ctx'])
    cf_memory = sum(1 for r in subset if r['cf_memory'])
    unans = sum(1 for r in subset if r.get('ans_cf_ctx', '').strip().lower() == 'unanswerable')
    
    print(f"cf_follows: {cf_follows}, cf_memory: {cf_memory}, unanswerable: {unans}")

