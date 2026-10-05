"""Counterfactual-context probe: replace the gold answer inside the supporting passages by a substitute; the model answering the substitute reads the context, the original answers from memory."""
import json, random, re, sys
from harness import *
def sub_for(a, pool):
    c = [x for x in pool if x != a and x[:1].isdigit() == a[:1].isdigit() and abs(len(x) - len(a)) < 8]
    return random.Random(a).choice(c) if c else None
out = []
for ds in ("musique", "2wiki"):
    f = {"musique": "musique", "2wiki": "2wikimultihopqa"}[ds]; raw = json.load(open(f"data/{f}.json"))
    qs, _ = load(ds, 1000); byid = {(q["id"] if ds == "musique" else q["_id"]): q for q in raw}
    pool = [q["gold"][0] for q in qs if q["gold"][0].lower() not in ("yes", "no")]
    n = 0
    for q in qs:  # random order from seed
        r = byid[q["id"]]; a = q["gold"][0]
        if a.lower() in ("yes", "no") or (ds == "2wiki" and r["type"] != "compositional"): continue
        if ds == "musique": sup = [p["title"] + "\n" + p["paragraph_text"] for p in r["paragraphs"] if p["is_supporting"]]
        else:
            st = {t for t, _ in r["supporting_facts"]}; sup = [t + "\n" + " ".join(s) for t, s in r["context"] if t in st]
        if not any(a in p for p in sup): continue
        alt = sub_for(a, pool)
        if not alt: continue
        cf = [p.replace(a, alt) for p in sup]; n += 1
        out.append((ds, q["q"], a, alt, "\n\n".join(sup), "\n\n".join(cf)))
        if n == 20: break
from concurrent.futures import ThreadPoolExecutor
def run(o):
    ds, q, a, alt, orig, cf = o; return gen_claude(q, orig)[0], gen_claude(q, cf)[0]
with ThreadPoolExecutor(4) as ex: res = list(ex.map(run, out))
rows = []
for o, (ao, ac) in zip(out, res):
    ds, q, a, alt = o[:4]
    rows.append({"ds": ds, "q": q, "gold": a, "alt": alt, "ans_orig_ctx": ao, "ans_cf_ctx": ac, "cf_follows_ctx": norm(ac) == norm(alt) or f1(ac, alt) > .5, "cf_memory": norm(ac) == norm(a) or f1(ac, a) > .5})
json.dump(rows, open("out/probe.json", "w"), indent=1)
for ds in ("musique", "2wiki"):
    R = [r for r in rows if r["ds"] == ds]
    print(ds, len(R), "orig-ctx correct", sum(f1(r["ans_orig_ctx"], r["gold"]) > .5 for r in R), "cf follows ctx", sum(r["cf_follows_ctx"] for r in R), "cf answers memory", sum(r["cf_memory"] for r in R))
