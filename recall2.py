import json, glob, numpy as np
from harness import *
qs, docs = load("2wiki", 50); ix = Index("2wiki", docs); out = {}
rows = {}
for tag in ("", "prereg"):
    for fn in glob.glob(f"out/2wiki_n50_B1000{tag}_*.json"):
        for r in json.load(open(fn))["rows"]: rows.setdefault((r["method"], tag or "guess"), {})[r["id"]] = r
for m in ("dense", "bm25", "hybrid"):
    for tag in ("guess", "prereg"):
        a = []; mism = 0
        for q in qs:
            ids, t = fill(docs, METHODS[m](ix, q["q"]), 1000); r = rows[(m, tag)][q["id"]]; mism += (t != r["ctx_tok"])
            if q["gold"][0].lower() in ("yes", "no"): continue
            if not any(g.lower() in "\n".join(docs[i] for i in ids).lower() for g in q["gold"]): a.append(r["f1"])
        out[f"{m}/{tag}"] = {"n_not_in_ctx_excl_yesno": len(a), "F1": float(np.mean(a)), "ctx_tok_mismatches_vs_logged": mism}
        print(m, tag, out[f"{m}/{tag}"], flush=True)
json.dump(out, open("out/recall2.json", "w"), indent=1)
