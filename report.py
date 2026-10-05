import json, glob, sys, numpy as np
from harness import boot
by = {}
for f in glob.glob("out/*_n50_B1000_*.json"):
    d = json.load(open(f))
    for r in d["rows"]: by.setdefault((r["ds"], r["method"]), {})[r["id"]] = r
for ds in ("musique", "2wiki"):
    print(f"\n## {ds}"); print("method | n | F1 [95% CI] | EM | ctx tok | ret s/q | gen cost $/q (notional)")
    ms = [m for (d, m) in by if d == ds]
    for m in ["nocontext", "dense", "bm25", "hybrid", "hybrid_rerank", "hippo"]:
        if (ds, m) not in by: continue
        R = list(by[(ds, m)].values()); f = boot([r["f1"] for r in R]); e = np.mean([r["em"] for r in R])
        print(f"{m} | {len(R)} | {f[0]:.3f} [{f[1]:.3f},{f[2]:.3f}] | {e:.3f} | {np.mean([r['ctx_tok'] for r in R]):.0f} | {np.mean([r['ret_s'] for r in R]):.3f} | {np.mean([r['gen']['cost'] for r in R]):.4f}")
    base = by.get((ds, "dense"))
    for m in ["bm25", "hybrid", "hybrid_rerank", "hippo"]:
        if (ds, m) in by and base:
            ids = [i for i in base if i in by[(ds, m)]]; x = np.array([by[(ds, m)][i]["f1"] - base[i]["f1"] for i in ids]); b = boot(x)
            print(f"paired {m} - dense: {b[0]:+.3f} [{b[1]:+.3f},{b[2]:+.3f}] n={len(ids)}")
    h = by.get((ds, "hybrid_rerank"))
    if h and (ds, "hippo") in by:
        ids = [i for i in h if i in by[(ds, "hippo")]]; x = np.array([by[(ds, "hippo")][i]["f1"] - h[i]["f1"] for i in ids]); b = boot(x)
        print(f"paired hippo - hybrid_rerank: {b[0]:+.3f} [{b[1]:+.3f},{b[2]:+.3f}] n={len(ids)}")
