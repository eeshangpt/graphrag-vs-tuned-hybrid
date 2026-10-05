import time, json, numpy as np
from harness import *
res = {}
for ds in ("musique", "2wiki"):
    qs, docs = load(ds, 50); ix = Index(ds, docs); ix.rerank(qs[0]["q"])  # warm-up
    for m in ("dense", "bm25", "hybrid", "hybrid_rerank"):
        t = []
        for q in qs: s = time.perf_counter(); METHODS[m](ix, q["q"]); t.append(time.perf_counter() - s)
        res[f"{ds}/{m}"] = {"median_s": float(np.median(t)), "p95_s": float(np.percentile(t, 95)), "mean_s": float(np.mean(t))}
        print(ds, m, res[f"{ds}/{m}"], flush=True)
json.dump(res, open("out/latency_alone.json", "w"), indent=1)
