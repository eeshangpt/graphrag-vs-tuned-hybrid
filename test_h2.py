import json, numpy as np

def load_f1(file):
    with open(file) as f:
        data = json.load(f)
    if isinstance(data, list):
        return np.array([d['f1'] for d in data])
    elif 'results' in data:
        return np.array([d['f1'] for d in data['results']])
    else:
        return np.array([d['f1'] for d in data.values()])

graph = load_f1('musique_n50_B1000prereg_hippo.json')
hybrid = load_f1('musique_n50_B1000prereg_bm25-hybrid-hybrid_rerank.json')

diff = graph - hybrid
mean_diff = np.mean(diff)
print(f"Graph mean: {np.mean(graph):.4f}")
print(f"Hybrid mean: {np.mean(hybrid):.4f}")
print(f"Mean Diff: {mean_diff:.4f}")

# Paired bootstrap
np.random.seed(42)
B = 10000
n = len(diff)
boot_diffs = [np.mean(np.random.choice(diff, size=n, replace=True)) for _ in range(B)]
l90, u90 = np.percentile(boot_diffs, [5, 95])
l95, u95 = np.percentile(boot_diffs, [2.5, 97.5])
print(f"90% CI: [{l90:.4f}, {u90:.4f}]")
print(f"95% CI: [{l95:.4f}, {u95:.4f}]")
