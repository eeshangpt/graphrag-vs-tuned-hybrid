# History of this repo

This repo started as one folder of a private repo. I extracted that folder's history with `git filter-repo --subdirectory-filter`, so the 19 commits below are the original ones with the same author and committer dates. Everything after the commit `5e2fa2c` ("confirmatory analysis") was added on 2026-10-23 to prepare this repo.

## What was changed in the history

- Commit messages: I dropped the `Claude-Session:` trailer lines (they are private session links), removed issue numbers of the private repo, and replaced the name of an internal tool with "second-model audit". The `Co-Authored-By` lines stay. The table at the bottom of this file has the old commit id next to the new one. No message was changed beyond that.
- Author and committer e-mail: replaced with the GitHub no-reply address, using a mailmap. The name stays.
- File content: untouched in the history. `prereg.md`, `prereg-amendment-1.md` and `prereg-amendment-2.md` have the same git blob ids as in the private repo (checked, see below), so the frozen text is the original text.
- Dates: not touched.
- Tags: `prereg-162-frozen` and `prereg-162-amendment-2-frozen` point at the same commits as before (new ids, same content and dates). Both are lightweight tags, so they carry no date of their own.

Things left in the history on purpose, because changing them would have meant editing frozen files or rewriting content: the frozen documents mention a private issue number (162), a link to a private repo and the word "owner" for me. The audit records name the `agy` command line tool. None of these is a secret. A scan for tokens and keys (gitleaks over all 19 commits plus a regex pass) found nothing.

Checks you can run:

```bash
git rev-parse 680d0f7:prereg.md                          # cc83c508c1b196e7fc6e31bfbc35cf3375ac22f3, the blob id in the private repo as well
git rev-parse prereg-162-frozen:prereg-amendment-1.md    # c1f9e035e290944e3fca0736f1056a9b35ee4332
git rev-parse prereg-162-amendment-2-frozen:prereg-amendment-2.md   # 01497f7f4cbb5329ca52e44086c46f27e1b76c4c
```

## Files added after the extraction

- `harness.py`, `hippo_adapter.py`, `report.py`, `openie_2wiki.py`, `e2e5.py`, `queue/`, `queue-later/`: copied from my working directory. The private repo never had the final harness, and the working directory had a local git history of its own. `harness.py` here adds a retry for a hung generator call (committed locally on 2026-10-08 18:59 IST, after job 01 ran and before job 03). `hippo_adapter.py` here adds the 2Wiki switch.
- `out/` (rows, 2Wiki triples, generator cache), `confirmatory/retrieval_*.json` (ids only), `scripts/`, `SHA256SUMS.*`.
- `README.md`, `HISTORY.md`, `DATA.md`, `LICENSE`. The old `README.md` is `HARNESS-NOTES.md`.
- Removed from the tree (still in history): eight one-off `peek_*.py` scratch scripts. A few internal paths and tool names were replaced in non-frozen files.

## When did things happen

All local times are IST (+05:30). "Server time" is what GitHub recorded, converted to IST in brackets. A commit's committer date on GitHub comes from the commit object as I pushed it, so it proves nothing by itself. The `referenced` event on the issue is created by GitHub when the commit arrives, so it is the closest thing to a third-party timestamp. It marks the latest the commit could have been created. I did not find an earlier server record for any row.

| event | local time | server time (UTC, IST) | source |
|---|---|---|---|
| `prereg.md` committed (original commit, before the later rebase) | 2026-10-05 13:04:19 | none, never pushed | `git reflog` and the commit object `fbbd082` in the private repo; GitHub has no such commit |
| first pilot results file (MuSiQue, n=50) written | 2026-10-05 13:36:13 | none | file time in the working directory; a log at 13:20 holds no results |
| same commit after `git pull --rebase`, pushed | 2026-10-05 13:55:25 | 08:25:29Z, 13:55:29 | issue `referenced` event |
| harness and pilot results pushed | 2026-10-05 14:17:30 | 08:54:12Z, 14:24:12 | issue `referenced` event |
| amendment 1 first draft pushed | 2026-10-05 15:05:48 | 09:39:37Z, 15:09:37 | issue `referenced` event |
| amendment 1 revised after audits | 2026-10-06 10:37 to 10:41 | 05:07:32Z to 05:11:22Z, 10:37 to 10:41 | issue `referenced` events |
| prereg and amendment 1 frozen (`prereg-162-frozen`) | 2026-10-06 13:01:22 | 07:31:25Z, 13:01:25 | issue `referenced` event; the tag exists on GitHub and points at this commit, tag creation time not exposed |
| queue of the confirmatory run pushed | 2026-10-06 13:01:39 | 07:31:42Z, 13:01:42 | issue `referenced` event |
| amendment 2 draft pushed (n=950 split, before any confirmatory output) | 2026-10-06 19:46:13 | 14:16:17Z, 19:46:17 | issue `referenced` event |
| first answer cached after the freeze (a 2Wiki OpenIE test) | 2026-10-06 23:37:56 | none | file time in `cache/` |
| first confirmatory answer cached | 2026-10-07 02:36:24 | none | file time in `cache/`; none exists between the freeze and 23:37 on 10-06 except the one above |
| MuSiQue n=1000 rows finished (job 01) | 2026-10-08 03:37:02 | none | file time of `out/` and the job log |
| 2Wiki n=1000 rows finished (job 03) | 2026-10-09 05:01:08 | none | same |
| 2Wiki triples finished (job 06) | 2026-10-10 03:34:24 | none | same |
| 2Wiki graph arm finished (job 07) | 2026-10-10 04:03:51 | none | same |
| amendment 2 frozen (`prereg-162-amendment-2-frozen`) | 2026-10-11 16:59:07 | 11:32:05Z, 17:02:05 | issue `referenced` event; the tag was never pushed to GitHub (the ref lookup returns 404), so the tag exists only from this repo on |
| A2.3 pre-commitment written, after the F1 preview was read | 2026-10-11 17:43 | none | `deviations.md` item 11 |
| analysis outputs and commit | 2026-10-11 19:44 and 19:50:01 | 14:20:15Z, 19:50:15 | file time; issue `referenced` event |

What this means for the claims:

- Amendment 1 and the original protocol were on the server at 13:01:25 on 2026-10-06. The first confirmatory answer was cached at 02:36 on 2026-10-07, about 13.5 hours later. No answers were cached in between except the one 2Wiki OpenIE test at 23:37. The confirmatory protocol therefore existed before the confirmatory data, according to a server record.
- Amendment 2 was on the server as a draft at 19:46 on 2026-10-06, before the first confirmatory answer, and frozen on 2026-10-11, after the MuSiQue and 2Wiki rows were finished. Its text between draft and freeze differs only in the header: `git diff aaa4f50:prereg-amendment-2-DRAFT.md prereg-162-amendment-2-frozen:prereg-amendment-2.md` shows one changed hunk at the top, and sections A2.1 to A2.4 are identical (`deviations.md` item 2).
- The first pilot file (13:36) is earlier than the first server record of `prereg.md` (13:55). The 13:04 time rests on my local git record. A local copy of the original commit has the identical file (same blob id), and author dates in git can be set by hand, so read 13:04 as my own record. The pilot is exploratory and does not feed the headline numbers.

## Old and new commit ids

| id here | id in the private repo | local time | subject |
|---|---|---|---|
| `680d0f7` | `ddeef0b` | 2026-10-05 13:04 | research: graphrag-hybrid pre-registration (before pilot) |
| `12c25d7` | `c80b2b1` | 2026-10-05 14:17 | research: graphrag-hybrid harness, pilot n=50 results |
| `9cab2cd` | `1e5a416` | 2026-10-05 14:17 | fix pct |
| `41fed5e` | `301a3f9` | 2026-10-05 14:21 | research: audit r1 fixes |
| `33d76cb` | `ba9e1b7` | 2026-10-05 14:22 | research: audit r2 fixes |
| `3a477c8` | `bc02c32` | 2026-10-05 15:05 | research: wave 2 bug check, leakage test, amendment 1 draft |
| `dc17dcd` | `7bab791` | 2026-10-05 15:24 | research: wave 2 audit r1 fixes, recall and leakage table |
| `4f1fe44` | `24b9b8f` | 2026-10-05 15:27 | research: wave 2 audit r2 fixes |
| `cb7f7be` | `036d26a` | 2026-10-05 15:30 | research: wave 2 audit r3 fixes, logs |
| `a56e3b1` | `2a0528b` | 2026-10-06 10:37 | research: audit round 1 of amendment 1 (CHANGES, 3 findings) |
| `1d61714` | `db45b28` | 2026-10-06 10:40 | research: amendment 1 revised after audit round 1; audit round 2 |
| `b50a9ee` | `e0257e6` | 2026-10-06 10:41 | research: amendment 1 approved by the independent audit in round 3 |
| `852effb` | `d9896ec` | 2026-10-06 13:01 | research: freeze prereg + amendment 1 (all author decisions in) |
| `577de94` | `95b45a3` | 2026-10-06 13:01 | research: queue confirmatory run; RUN.md |
| `aaa4f50` | `73340d0` | 2026-10-06 19:46 | research: independent audit of wave 2 (CHANGES), amendment 2 draft |
| `de1f95f` | `2b5899a` | 2026-10-06 23:40 | research: deviations log (2Wiki OpenIE by Claude, not gpt-4o-mini) |
| `c11bfbb` | `efe33ab` | 2026-10-08 18:58 | research: logs, audit records, helper scripts |
| `2102016` | `c73fe24` | 2026-10-11 16:59 | research: freeze amendment 2 (n=950 confirmatory) |
| `5e2fa2c` | `23dcb71` | 2026-10-11 19:50 | research: confirmatory analysis (ITERATE), independent audit APPROVE r2 |
