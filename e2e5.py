"""5-question end-to-end retrieval check of the 2Wiki graph arm on the 50-passage sample (no LLM calls: retrieval only)."""
import os, json, sys, shutil
os.environ["HIPPO_OPENIE"] = "out/openie_2wiki_sample50.json"
import harness as Hn, hippo_adapter as H, ast
qs, _ = Hn.load("2wiki", 5)
js = json.load(open("out/openie_2wiki_sample50.json")); docs = [r["passage"] for r in js["docs"]]
shutil.rmtree("cache/hippo_2wiki_sample", ignore_errors=True)
H_ds = "2wiki_sample"
h, t = H.build(docs, H_ds); print("index_s", round(t, 1), "n_docs", len(docs))
raw = {q["_id"]: q for q in json.load(open("data/2wikimultihopqa.json"))}
R = H.ranked_docs(h, docs, [q["q"] for q in qs], k=5)
for q, r in zip(qs, R):
    sf = raw[q["id"]]["supporting_facts"]; sf = ast.literal_eval(sf) if isinstance(sf, str) else sf; gold = {t for t, _ in sf}
    gt = [docs[i].split("\n")[0] for i in r]
    print(q["q"], "| gold titles", sorted(gold), "| top5", gt, "| gold in top5:", sorted(gold & set(gt)))
