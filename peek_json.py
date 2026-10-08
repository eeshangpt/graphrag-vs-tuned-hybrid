import json

with open('musique_n50_B1000prereg_hippo.json') as f:
    d = json.load(f)
    print("hippo:", type(d))
    if type(d) == dict:
        print("keys:", list(d.keys())[:5])
        k = list(d.keys())[0]
        print("value0:", d[k])
        
with open('musique_n50_B1000prereg_bm25-hybrid-hybrid_rerank.json') as f:
    d = json.load(f)
    print("hybrid:", type(d))
    if type(d) == dict:
        print("keys:", list(d.keys())[:5])
        k = list(d.keys())[0]
        print("value0:", d[k])
