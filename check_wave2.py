import json, math, random

# 1. Check paired CI
def get_f1s(file):
    with open(file) as f:
        return [r['f1'] for r in json.load(f)['rows']]

hippo = get_f1s('musique_n50_B1000prereg_hippo.json')
hybrid = get_f1s('musique_n50_B1000prereg_bm25-hybrid-hybrid_rerank.json')
diff = [h - y for h, y in zip(hippo, hybrid)]

mean_diff = sum(diff) / len(diff)
print(f"Paired CI diff mean: {mean_diff:.3f}")
random.seed(42)
B = 10000
boot_diffs = []
for _ in range(B):
    boot_diffs.append(sum(random.choice(diff) for _ in range(50)) / 50)
boot_diffs.sort()
print(f"95% CI: [{boot_diffs[int(0.025*B)]:.3f}, {boot_diffs[int(0.975*B)]:.3f}]")
# "HippoRAG-2-lite ties the tuned baseline again, with a CI of about +/-13 F1" (13 F1 = 0.13)
# CI half-width is about (0.22 - -0.07)/2 = 0.145.

# 2. Refusal rates
for name, f in [("hippo", 'musique_n50_B1000prereg_hippo.json'), ("hybrid", 'musique_n50_B1000prereg_bm25-hybrid-hybrid_rerank.json')]:
    with open(f) as fp:
        rows = json.load(fp)['rows']
        refusals = sum(1 for r in rows if r['gen'].get('answer', '').strip().lower() == 'unanswerable')
        print(f"{name} refusals: {refusals}/50 ({refusals/50*100}%)")

# "The generator refuses on about 55-60% of questions"
# Let's check 2wiki too
for name, f in [("2w_dense", '2wiki_n50_B1000prereg_nocontext-dense.json'), ("2w_hybrid", '2wiki_n50_B1000prereg_bm25-hybrid-hybrid_rerank.json')]:
    with open(f) as fp:
        rows = json.load(fp)['rows']
        refusals = sum(1 for r in rows if r['gen'].get('answer', '').strip().lower() == 'unanswerable')
        print(f"{name} refusals: {refusals}/50 ({refusals/50*100}%)")

