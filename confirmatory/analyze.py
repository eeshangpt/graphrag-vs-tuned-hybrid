"""Pre-registered confirmatory analysis for #162 (prereg.md + amendment 1 + amendment 2). Run: <expdir>/.venv/bin/python analyze.py  (cwd = experiment repo).
Confirmatory = permutation positions 51-1000 (n=950); positions 1-50 = exploratory slice, reported separately (A2.1). B=1000, refusal prompt."""
import json, random, re, string, collections, glob, os, sys, statistics, hashlib
import numpy as np, tiktoken
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.getcwd(); SEED = 20261005
ARMS = ["nocontext", "dense", "bm25", "hybrid", "hybrid_rerank", "hippo"]
ENC = tiktoken.get_encoding("cl100k_base"); ntok = lambda s: len(ENC.encode(s))
def norm(s):
    s = s.lower(); s = "".join(c for c in s if c not in set(string.punctuation)); s = re.sub(r"\b(a|an|the)\b", " ", s); return " ".join(s.split())
def f1(p, g):
    p, g = norm(p).split(), norm(g).split(); c = sum((collections.Counter(p) & collections.Counter(g)).values())
    if not p or not g or c == 0: return float(p == g)
    pr, rc = c / len(p), c / len(g); return 2 * pr * rc / (pr + rc)
def boot_d(x, n=10000, seed=0):
    """percentile bootstrap of the mean (prereg sec 5): returns mean, (L95,U95), (L90,U90). Paired = bootstrap of per-question differences."""
    x = np.asarray(x, float); m = np.random.default_rng(seed).choice(x, (n, len(x))).mean(1)
    return float(x.mean()), tuple(np.percentile(m, [2.5, 97.5])), tuple(np.percentile(m, [5, 95]))
out = {}; L = []
def P(s=""): L.append(s); print(s)
def load(ds):
    f = {"musique": "musique", "2wiki": "2wikimultihopqa"}[ds]; qs = json.load(open(f"{EXP}/data/{f}.json"))
    idx = random.Random(SEED).sample(range(len(qs)), len(qs)); key = "id" if ds == "musique" else "_id"
    G = {q[key]: [q["answer"]] + list(q.get("answer_aliases") or []) for q in qs}; T = {q[key]: q.get("type") for q in qs}
    return [qs[i][key] for i in idx], G, T
def rows(ds):
    R = collections.defaultdict(dict)
    for fn in glob.glob(f"{EXP}/out/{ds}_n1000_B1000prereg_*.json"):
        for r in json.load(open(fn))["rows"]: R[r["method"]][r["id"]] = r
    return R
def ci(b): return f"{b[0]:.3f} [{b[1][0]:.3f}, {b[1][1]:.3f}]"
def dci(b): return f"{b[0]*100:+.1f} F1 [95% {b[1][0]*100:+.1f}, {b[1][1]*100:+.1f}; 90% {b[2][0]*100:+.1f}, {b[2][1]*100:+.1f}]"
# published / measured cost inputs (see report for provenance)
PRICE = (0.15, 0.60)  # gpt-4o-mini reference $/M in,out (prereg sec 5)
CPU_RATE_H = 0.20     # DECLARED ASSUMPTION $/hour for one 4-vCPU on-demand instance (A2.4b), not measured
OPENIE = {"musique": dict(i=9.2e6, o=3.0e6, src="published, 2502.14802 Table 12 (Llama-3.3-70B)", build_s=2173, bs_src="pilot-measured"),
          "2wiki": dict(i=15973702, o=3456099, src="measured here, Claude Sonnet via claude -p (06-2wiki-openie.log), priced at the reference table", build_s=None, bs_src="confirmatory run")}
FILTER = dict(i=437 + 1821 + 106 + 60, o=60)  # per query: system 437 + 10 demos 1821 (tiktoken on best_dspy_prompt) + question+5 candidate facts ~106 + wrapper ~60; output ~41+20. ESTIMATE
RET_S_HIPPO = {"musique": 181 / 1000, "2wiki": 123 / 1000}  # mean s/query from the tqdm 'Retrieving 1000/1000 [03:01]' / [02:03] lines of queue/out/01 and 07 logs (query encode + PPR)
for ds in ("musique", "2wiki"):
    order, G, T = load(ds); conf, expl = order[50:], order[:50]; R = rows(ds); o = out[ds] = {}
    P(f"\n## {ds}")
    # --- integrity
    assert all(len(R[m]) == 1000 and set(R[m]) == set(order) for m in ARMS), "row set mismatch"
    bad = sum(1 for m in ARMS for r in R[m].values() if abs(max(f1(r["ans"], g) for g in G[r["id"]]) - r["f1"]) > 1e-9)
    P(f"integrity: 6 arms x 1000 ids = permutation; F1 recomputed from ans+gold(+aliases) mismatches: {bad}")
    o["f1_recompute_mismatch"] = bad
    rr = json.load(open(f"{HERE}/retrieval_{ds}.json")) if os.path.exists(f"{HERE}/retrieval_{ds}.json") else None
    # --- table 1: per arm
    P("\n| arm | n | F1 [95% CI] | EM | 'unanswerable' share | mean ctx tok | retrieval s/q median (p95) |\n|---|---|---|---|---|---|---|")
    for m in ARMS:
        rs = [R[m][i] for i in conf]; b = boot_d([r["f1"] for r in rs]); em = np.mean([r["em"] for r in rs]); un = np.mean(["unanswerable" in r["ans"].lower() for r in rs])
        rt = [r["ret_s"] for r in rs]; lat = "lookup (batched; mean %.2f s/q)" % RET_S_HIPPO[ds] if m == "hippo" else ("n/a" if m == "nocontext" else f"{np.median(rt):.3f} ({np.percentile(rt,95):.3f})")
        P(f"| {m} | {len(rs)} | {ci(b)} | {em:.3f} | {un:.2f} | {np.mean([r['ctx_tok'] for r in rs]):.0f} | {lat} |")
        o.setdefault("arms", {})[m] = dict(f1=b[0], ci95=b[1], em=float(em), unans=float(un), ctx=float(np.mean([r['ctx_tok'] for r in rs])))
    # --- exploratory slice
    P("\nExploratory slice (positions 1-50, n=50; used for design, NOT confirmatory): F1 " + ", ".join(f"{m} {np.mean([R[m][i]['f1'] for i in expl]):.3f}" for m in ARMS))
    # --- paired
    P("\nPaired differences on the 950 (F1 points; percentile bootstrap 10,000, seed 0):")
    for base in ("dense", "hybrid_rerank"):
        for m in ARMS[1:]:
            if m == base: continue
            b = boot_d([R[m][i]["f1"] - R[base][i]["f1"] for i in conf]); o.setdefault("paired", {})[f"{m}-{base}"] = b; P(f"- {m} - {base}: {dci(b)}")
    # --- hypotheses
    d = boot_d([R["hippo"][i]["f1"] - R["hybrid_rerank"][i]["f1"] for i in conf]); o["graph_minus_hybrid"] = d; sd = float(np.std([R["hippo"][i]["f1"] - R["hybrid_rerank"][i]["f1"] for i in conf], ddof=1))
    P(f"\nGraph (HippoRAG 2-lite) minus tuned hybrid (hybrid+rerank): {dci(d)}; paired SD {sd:.3f}")
    if ds == "musique":
        eq = d[2][0] > -0.04 and d[2][1] < 0.04; gb = d[1][0] > 0.04; hb = d[1][1] < -0.04
        cls = "equivalent (within +/-4 F1)" if eq else "graph-better (by more than 4 F1)" if gb else "hybrid-better (by more than 4 F1)" if hb else "inconclusive"
        P(f"H2 (amendment 1 sec 2, margin +/-4 F1; TOST 90% CI): **{cls}**"); o["H2"] = cls
    else:
        cls = "graph-better" if d[1][0] > 0 else "not shown (95% CI lower bound <= 0)"; P(f"H1 (amended: graph superior to tuned hybrid on the full sample, L95 > 0): **{cls}**"); o["H1"] = cls
    o["kill_leg"] = bool(d[0] > 0.05 and d[1][0] > 0); P(f"Kill-rule leg (point > +5 F1 and L95 > 0): {o['kill_leg']}")
    # superseded original H1/H2 for reference only
    ph = np.mean([R['hybrid_rerank'][i]['f1'] for i in conf]); pd_ = np.mean([R['dense'][i]['f1'] for i in conf]); pg = np.mean([R['hippo'][i]['f1'] for i in conf])
    P(f"Superseded original forms (descriptive only): graph - hybrid+rerank = {100*(pg-ph):+.1f} F1; share of the dense-to-graph gap closed by the hybrid = {(ph-pd_)/(pg-pd_) if pg!=pd_ else float('nan'):.2f} (original H1 asked >= 0.5; gap {100*(pg-pd_):+.1f} F1)")
    # --- retrieval diagnostics + leakage gate (needs re-run retrieval)
    if rr:
        ok = [sum(1 for k, v in rr.items() if k.startswith(m + "|") and v[f]) for m in ARMS[1:] for f in ("cache_hit",)]
        tot = {f: sum(1 for v in rr.values() if v[f]) for f in ("cache_hit", "ans_same", "tok_same")}; P(f"\nRetrieval re-run reproduces the generation run (rebuilt prompt hash exists in generator cache with identical answer; ctx token count equal): {tot} of {len(rr)} arm-rows"); o["repro"] = dict(tot, n=len(rr))
        P("\n| arm | supporting-passage recall (all 950) | gold string in context (excl. yes/no golds) | F1 on rows with no gold string in ctx (n) [GATE < 0.10] | F1 on rows with gold in ctx |\n|---|---|---|---|---|")
        for m in ARMS:
            recs, gin, fn_, fy = [], [], [], []
            for i in conf:
                g = G[i]
                v = rr.get(f"{m}|{i}"); ctx = norm(v["ctx"]) if v else ""
                if v and v["sup_n"]: recs.append(v["sup_hit"] / v["sup_n"])  # recall: all 950 rows
                if norm(g[0]) in ("yes", "no"): continue  # yes/no golds excluded from the gold-string columns and the gate only (amendment 1 sec 1)
                has = any(norm(x) and norm(x) in ctx for x in g); gin.append(has)
                (fy if has else fn_).append(R[m][i]["f1"])
            rec = f"{np.mean(recs):.2f}" if recs else "n/a"; gate = float(np.mean(fn_)) if fn_ else float("nan")
            P(f"| {m} | {rec} | {np.mean(gin):.2f} | {gate:.3f} ({len(fn_)}) {'PASS' if gate < 0.10 else 'FAIL'} | {np.mean(fy) if fy else float('nan'):.3f} ({len(fy)}) |")
            o.setdefault("gate", {})[m] = dict(f1_no_gold=gate, n=len(fn_), gold_in_ctx=float(np.mean(gin)), recall=(float(np.mean(recs)) if recs else None))
    # --- 2wiki by type (exploratory)
    if ds == "2wiki":
        P("\nExploratory (A1 sec 1): by 2Wiki question type on the 950; graph minus hybrid+rerank and arm F1")
        for t in sorted({T[i] for i in conf}):
            ids = [i for i in conf if T[i] == t]; b = boot_d([R["hippo"][i]["f1"] - R["hybrid_rerank"][i]["f1"] for i in ids])
            P(f"- {t} (n={len(ids)}): dense {np.mean([R['dense'][i]['f1'] for i in ids]):.2f}, hybrid+rerank {np.mean([R['hybrid_rerank'][i]['f1'] for i in ids]):.2f}, graph {np.mean([R['hippo'][i]['f1'] for i in ids]):.2f}; graph-hybrid {dci(b)}")
    # --- H3 cost
    em = json.load(open(glob.glob(f"{EXP}/out/{ds}_n1000_B1000prereg_dense*.json")[0])); hp = glob.glob(f"{EXP}/out/{ds}_n1000_B1000prereg_hippo.json")
    idx_emb_s = em["index_emb_s"]; hid = json.load(open(hp[0])).get("hippo_index_s") if hp else None
    gb_s = OPENIE[ds]["build_s"] or hid
    def per_q(m):
        pin = [rr[f"{m}|{i}"]["prompt_tok"] for i in conf] if rr else [0]; pout = [ntok(R[m][i]["ans"]) for i in conf]
        return np.mean(pin), np.mean(pout), (np.mean(pin) * PRICE[0] + np.mean(pout) * PRICE[1]) / 1e6
    if rr:
        hin, hout, hq = per_q("hybrid_rerank"); gin_, gout, gq = per_q("hippo")
        ret_h = float(np.mean([R["hybrid_rerank"][i]["ret_s"] for i in conf])); ret_g = RET_S_HIPPO[ds]
        idx_g_llm = (OPENIE[ds]["i"] * PRICE[0] + OPENIE[ds]["o"] * PRICE[1]) / 1e6
        fq = (FILTER["i"] * PRICE[0] + FILTER["o"] * PRICE[1]) / 1e6; cpu = lambda s: s / 3600 * CPU_RATE_H
        P(f"\nH3 cost inputs ({ds}): reference price ${PRICE[0]}/${PRICE[1]} per M in/out tokens; generator prompt tokens/answer tokens per query: hybrid+rerank {hin:.0f}/{hout:.1f}, graph {gin_:.0f}/{gout:.1f}")
        P(f"graph indexing LLM tokens {OPENIE[ds]['i']/1e6:.2f}M in / {OPENIE[ds]['o']/1e6:.2f}M out ({OPENIE[ds]['src']}) = ${idx_g_llm:.2f} at the reference price; CPU: embedding {idx_emb_s:.0f} s (shared), graph build {gb_s:.0f} s ({OPENIE[ds]['bs_src']}); retrieval s/q hybrid+rerank {ret_h:.2f} (CPU reranker), graph {ret_g:.2f}")
        P(f"estimated LLM triple-filter cost per graph query (not run; ESTIMATE from the paper's filter prompt): {FILTER['i']} in / {FILTER['o']} out tokens = ${fq:.5f}")
        def vstar(prem, idx_h, qh, qg):
            if qg > qh: return "undefined (graph per-query cost exceeds hybrid's)"
            return f"{max(0.0, (prem / 0.10 - idx_h) / qh):,.0f}"
        P("\n| scenario | indexing premium (graph - hybrid) $ | hybrid per-query $ | graph per-query $ | V* (graph premium < 10% of hybrid total) | graph/hybrid total cost at V=1000 |\n|---|---|---|---|---|---|")
        for name, flt, cp in (("as run: no filter, local compute $0", 0, 0), ("A2.4a: + estimated LLM triple filter", 1, 0),
                              ("A2.4b: local compute priced at $%.2f/h (declared), no filter" % CPU_RATE_H, 0, 1), ("A2.4a+b: filter and CPU priced", 1, 1)):
            ih = cpu(idx_emb_s) if cp else 0.0; ig = idx_g_llm + ((cpu(idx_emb_s) + cpu(gb_s)) if cp else 0.0)
            qh = hq + (cpu(ret_h) if cp else 0.0); qg = gq + (fq if flt else 0.0) + (cpu(ret_g) if cp else 0.0); prem = ig - ih
            P(f"| {name} | {prem:.2f} | {qh:.5f} | {qg:.5f} | {vstar(prem, ih, qh, qg)} | {(ig + 1000*qg)/(ih + 1000*qh):,.1f}x |")
            o.setdefault("h3", {})[name] = dict(prem=prem, qh=qh, qg=qg, V=vstar(prem, ih, qh, qg), ratio1000=(ig + 1000*qg)/(ih + 1000*qh))
json.dump(out, open(f"{HERE}/results.json", "w"), indent=1, default=str); open(f"{HERE}/results.md", "w").write("\n".join(L))
