import json, random, math

def load_f1(file):
    with open(file) as f:
        data = json.load(f)
    return [r['f1'] for r in data['rows']]

graph = load_f1('musique_n50_B1000prereg_hippo.json')
hybrid = load_f1('musique_n50_B1000prereg_bm25-hybrid-hybrid_rerank.json')

diff = [g - h for g, h in zip(graph, hybrid)]
mean_diff = sum(diff) / len(diff)
print(f"n: {len(diff)}")
print(f"Graph mean: {sum(graph)/len(graph):.4f}")
print(f"Hybrid mean: {sum(hybrid)/len(hybrid):.4f}")
print(f"Mean Diff: {mean_diff:.4f}")
print(f"SD: {math.sqrt(sum((x - mean_diff)**2 for x in diff) / (len(diff)-1)):.4f}")

random.seed(42)
B = 1000
n = len(diff)
boot_diffs = []
for _ in range(B):
    s = sum(random.choice(diff) for _ in range(n)) / n
    boot_diffs.append(s)

boot_diffs.sort()
l90 = boot_diffs[int(0.05 * B)]
u90 = boot_diffs[int(0.95 * B)]
l95 = boot_diffs[int(0.025 * B)]
u95 = boot_diffs[int(0.975 * B)]
print(f"90% CI: [{l90:.4f}, {u90:.4f}]")
print(f"95% CI: [{l95:.4f}, {u95:.4f}]")
