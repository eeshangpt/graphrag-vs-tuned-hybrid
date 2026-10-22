set -e
# full 2Wiki OpenIE (6119 passages x 2 claude -p calls; resumable via cache/openie_2wiki/); fails loudly if any passage failed 3x
.venv/bin/python openie_2wiki.py --workers 6 --out out/openie_2wiki.json
.venv/bin/python -c "import json;s=json.load(open('out/openie_2wiki.json.stats.json'));assert s['n_failed']==0,s"
