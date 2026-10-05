"""Per arm: supporting-passage recall within B=1000 context, gold-string-in-context rate, and F1 on rows where gold is NOT in context (leakage estimate)."""
import json, glob, numpy as np, os
from harness import *
res = {}
for ds in ("musique", "2wiki"):
    f = {"musique": "musique", "2wiki": "2wikimultihopqa"}[ds]; raw = {(q.get("id") or q.get("_id")): q for q in json.load(open(f"data/{f}.json"))}
    qs, docs = load(ds, 50); ix = Index(ds, docs); D = {d: i for i, d in enumerate(docs)}; title = {}
    for i, d in enumerate(docs): title.setdefault(d.split("\n", 1)[0], []).append(i)
    HR = None
    if ds == "musique":
        import hippo_adapter as H
        h, _ = H.build(docs, ds); HR = dict(zip([q["q"] for q in qs], H.ranked_docs(h, docs, [q["q"] for q in qs])))
    rows = {}
    for tag in ("", "prereg"):
        for fn in glob.glob(f"out/{ds}_n50_B1000{tag}_*.json"):
            for r in json.load(open(fn))["rows"]: rows.setdefault((r["method"], tag or "guess"), {})[r["id"]] = r
    for m in ("dense", "bm25", "hybrid", "hybrid_rerank", "hippo"):
        if m == "hippo" and ds != "musique": continue
        rec, ing = [], {}
        for q in qs:
            r = raw[q["id"]]
            if ds == "musique": sup = {title_idx for p in r["paragraphs"] if p["is_supporting"] for title_idx in [D.get(p["title"] + "\n" + p["paragraph_text"])] if title_idx is not None}
            else:
                st = {t for t, _ in r["supporting_facts"]}; sup = {i for t in st for i in title.get(t, [])}
            ranked = HR[q["q"]] if m == "hippo" else METHODS[m](ix, q["q"]); ids, _ = fill(docs, ranked, 1000)
            rec.append(len(sup & set(ids)) / max(1, len(sup))); ing[q["id"]] = any(g.lower() in "\n".join(docs[i] for i in ids).lower() for g in q["gold"])
        out = {"supporting_recall": float(np.mean(rec)), "gold_in_ctx": float(np.mean(list(ing.values())))}
        for tag in ("guess", "prereg"):
            R = rows.get((m, tag), {})
            if R:
                a = [R[i]["f1"] for i in ing if not ing[i] and i in R]; b = [R[i]["f1"] for i in ing if ing[i] and i in R]
                out[f"{tag}_F1_goldNOTinctx"] = (len(a), float(np.mean(a)) if a else None); out[f"{tag}_F1_goldinctx"] = (len(b), float(np.mean(b)) if b else None)
        res[f"{ds}/{m}"] = out; print(ds, m, out, flush=True)
json.dump(res, open("out/recall.json", "w"), indent=1)
