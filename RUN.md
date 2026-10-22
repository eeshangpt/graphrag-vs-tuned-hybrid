# How the confirmatory run was executed

The run was queued at tag `prereg-162-frozen` as plain shell jobs, executed in order from the repo root. Each job resumes from `cache/` after an interruption, because every generator call is cached by prompt hash.

| job | what it does |
|---|---|
| `queue/01-musique-B1000.sh` | MuSiQue, n=1000, B=1000, all six arms (the graph arm uses the authors' shipped OpenIE file) |
| `queue/03-2wiki-B1000.sh` | 2WikiMultiHopQA, n=1000, B=1000, the five non-graph arms |
| `queue/06-2wiki-openie.sh` | OpenIE for all 6,119 2Wiki passages with `claude -p` (`openie_2wiki.py`) |
| `queue/07-2wiki-B1000-hippo.sh` | 2Wiki graph arm, built on the triples from job 06 |

`queue-later/` holds jobs that were written but never run: the B=2000 sensitivity runs (`02`, `04`) and the guess-prompt secondary (`05`). `deviations.md` lists them as unmet commitments.

Jobs 06 and 07 were added after the freeze, because the 2Wiki graph arm needed code that did not exist at the time of amendment 1 (amendment 1, section 6, item 1). `deviations.md` has the details.
