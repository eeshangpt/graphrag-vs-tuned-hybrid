import json, glob, numpy as np, collections
from harness import boot
by = {}
for f in glob.glob("out/*_n50_B1000prereg_*.json"):
    for r in json.load(open(f))["rows"]: by.setdefault((r["ds"], r["method"]), {})[r["id"]] = r
raw = {q["_id"]: q["type"] for q in json.load(open("data/2wikimultihopqa.json"))}
for ds in ("musique", "2wiki"):
    print(f"\n## {ds} (prereg prompt: 'unanswerable' allowed)"); 
    for m in ["nocontext", "dense", "bm25", "hybrid", "hybrid_rerank", "hippo"]:
        if (ds, m) not in by: continue
        R = list(by[(ds, m)].values()); f = boot([r["f1"] for r in R]); un = np.mean(["unanswerable" in r["ans"].lower() for r in R])
        print(f"{m} | n={len(R)} | F1 {f[0]:.3f} [{f[1]:.3f},{f[2]:.3f}] | EM {np.mean([r['em'] for r in R]):.3f} | unanswerable {un:.2f} | ctx {np.mean([r['ctx_tok'] for r in R]):.0f}")
    base = by.get((ds, "dense"))
    for m in ["bm25", "hybrid", "hybrid_rerank", "hippo"]:
        if (ds, m) in by and base:
            ids = list(base); x = np.array([by[(ds, m)][i]["f1"] - base[i]["f1"] for i in ids]); b = boot(x); print(f"paired {m}-dense {b[0]:+.3f} [{b[1]:+.3f},{b[2]:+.3f}] SD {x.std(ddof=1):.2f}")
    h = by.get((ds, "hybrid_rerank"))
    if h and (ds, "hippo") in by:
        x = np.array([by[(ds, "hippo")][i]["f1"] - h[i]["f1"] for i in h]); b = boot(x); print(f"paired hippo-hybrid_rerank {b[0]:+.3f} [{b[1]:+.3f},{b[2]:+.3f}] SD {x.std(ddof=1):.2f}")
print("\n## 2wiki by question type, dense, guess-prompt (pilot) vs prereg-prompt")
g = {}
for f in glob.glob("out/2wiki_n50_B1000_*.json"):
    if "prereg" in f: continue
    for r in json.load(open(f))["rows"]: g.setdefault(r["method"], {})[r["id"]] = r
for m in ("nocontext", "dense", "hybrid_rerank"):
    for name, src in (("guess", g), ("prereg", {k[1]: v for k, v in by.items() if k[0] == "2wiki"})):
        if m not in src: continue
        t = collections.defaultdict(list)
        for i, r in src[m].items(): t[raw[i]].append(r["f1"])
        print(m, name, {k: (len(v), round(float(np.mean(v)), 2)) for k, v in sorted(t.items())})
