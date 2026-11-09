# Job-Search Agent 2: The Loop, the Tools, and the Diff

INFO 7375, Prompt Engineering for Generative AI, Fall 2026. Aravind Sundaravadivelu (GitHub: AravindKumar2504). Assignment JS2.

This is layer 2 of the job-search agent I started in JS1. Layer 1 watched one board. Layer 2 is a bounded loop: one run visits four boards (OpenAI on Ashby, Verkada on Greenhouse, Palantir on Lever, and a made-up Greenhouse board that fails on purpose) under the exits, budgets, repeat rule, error policy and permission policy in [GATE.md](GATE.md), which I approved before any JS2 code was written. As in JS1, each new posting is judged twice: by my rule (a record anyone can recompute) and by Claude (a judgment, labeled as one), now within a budget of 20 Claude calls per run. The agent never applies, emails, messages or logs in.

**What I started from:** my own JS1 agent (final commit `d8b3896`; its documents are in [js1/](js1/)). No code from Lectern or the Reallocation Engine; [SOURCES.md](SOURCES.md) says what was looked at and used.

**Jane Doe is fictional.** Her résumé (`persona/jane-doe.json`, unchanged since JS1) has a situation like mine (F-1 student, not a U.S. person, needs H-1B sponsorship later, earliest full-time start May 2027, backend new grad) but none of my identity, an `@example.com` email and a 555-01xx phone number. Nothing is ever sent or applied for in her name.

## Where each part of the brief is

| The brief asks for | Where it is |
|---|---|
| The gate, written first | [GATE.md](GATE.md) v1.0, commit `84d9f4c` (2026-11-07, 1:45 AM ET), before the first JS2 code (`ab2df17`, 2:17 AM ET) |
| The loop: three boards on two or more systems, budgets, an exit status, a record of every observation, a board that fails on purpose | [boards.json](boards.json), `job_agent/loop.py`, and each run's `trace.md` |
| The agent trace of one real run, with the deliberate failure | [runs/2026-11-08T221447Z/trace.md](runs/2026-11-08T221447Z/trace.md): steps 19 to 23 are the made-up board, step 51 its state left alone |
| A finished wrong answer, caught by an independent check | [DEMO.md](runs/demos/finished-wrong-answer/2026-11-08T221447Z/DEMO.md), made by `tools/wrong_answer_demo.py`; the check is `tools/check_run.py` |
| The permission policy in code, with at least 10 predicted boundary cases | `job_agent/policy.py`, [BOUNDARY-TESTS.md](BOUNDARY-TESTS.md) (19 cases, my predictions first), `tests/test_boundary.py` |
| The review packet | [REVIEW-PACKET.md](REVIEW-PACKET.md) |
| The sign-off and the driver's seat | [below](#sign-off) |
| Saved raw responses | `runs/<run id>/boards/<system>-<name>/attempt-N.json.gz`, each with an `attempt-N.meta.json` holding its URL, HTTP status, headers, time and the SHA-256 of the uncompressed answer |
| The commands I ran myself | [MY-CHECKS.md](MY-CHECKS.md) |
| Sources and the split of work; my log | [SOURCES.md](SOURCES.md), [FRICTIONAL.md](FRICTIONAL.md) |

## Language and toolchain

- Python 3.9 or newer, standard library only: nothing to install. The 206 tests pass on Python 3.12.14 and on macOS's own 3.9.6 (run by Claude Code on 2026-11-09; my own runs are in MY-CHECKS.md).
- The Claude judge runs the Claude Code CLI (2.1.317 in JS2, 2.1.309 in JS1), signed in with a claude.ai seat, model `claude-sonnet-5-5`. There is no API key. The CLI is found at the path in `JOB_AGENT_CLAUDE`, as `claude` on the PATH, or as the Claude desktop app's newest copy on a Mac. Only a live run with postings to judge needs it.
- git, for the privacy test's file list (without git it walks the folder).
- The network, only for a live run, and only the three hosts in GATE.md.

## Commands (from the repo root)

These need no network and no Claude, so they work from a fresh clone.

```bash
python3 -m unittest discover -s tests -t .
```
206 offline tests, about 10 seconds. A stand-in plays the network and the CLI.

```bash
python3 tools/mutants.py
```
Plants 61 mistakes in a copy of the code, one at a time, and checks that the tests catch each one: JS1's 37, GATE.md's ten wrong versions (1a, 1b, 1c, 2, 3a, 3b, 3c, 4a, 4b, 4c), and 14 more for layer 2 and contract v0.2. About 7 minutes, because each mistake reruns all the tests.

```bash
python3 tools/check_run.py runs/2026-11-08T221447Z
```
The independent check of one saved run. It imports nothing from the agent: it reads only the saved raw answers and `report.json`, works out each board's status, postings, new and gone by its own reading, and checks the exit. Exit 0 means no disagreement.

```bash
python3 tools/wrong_answer_demo.py runs/2026-11-08T221447Z /tmp/js2-demo
```
Remakes the finished wrong answer in a new folder (the saved demo is never overwritten). Wrong version 1a is planted in a temporary copy of the code and the run's saved answers are replayed through it: exit 0, finished, and wrong. Then the independent check: exit 1, caught. The unchanged code's replay ends incomplete and passes the check. Both replays are labeled as replays; nothing is fetched and no Claude call is made.

```bash
python3 tools/boundary_table.py --check
```
Reruns the 19 boundary cases and checks that BOUNDARY-TESTS.md's Actual column matches.

```bash
python3 tools/explain_rule.py --contract 0.1 runs/2026-10-30T093102Z/response.json 9efcef02-0515-4672-bace-81329944b38b
python3 -m unittest tests.test_years_v02
python3 tools/rule_verdicts.py runs/2026-10-30T093102Z/response.json --flips
```
The review packet: posting 19 under contract v0.1 (the bug: check 7 reads no years; without `--contract 0.1` the tool shows v0.2, which reads "5+ years"), my test, and the two verdicts that contract v0.2 flips on the 2026-10-30 baseline.

A live run (network, and Claude for any postings to judge):

```bash
python3 -m job_agent run
```
One run of the loop. For each board in `boards.json`: check the request against the permission policy and the budgets, GET it, save the raw answer with its SHA-256, read it, and compare it with that board's state in `state/`. Then the rule judges every posting in the run, and Claude judges postings that waited from earlier runs first, then new ones, up to 20 calls. The run writes `runs/<UTC time>/` (report, trace, saved answers, Claude records) and then saves each board's state. Exit codes: 0 finished, 1 incomplete, 4 budget-exhausted, 2 broken input, 3 refused.

- `--max-claude-calls N` (and `--max-boards`, `--max-requests`, `--max-seconds`) lowers a budget for one run; raising one is refused.
- `--approve "<reason>"` allows the writes GATE.md keeps for my approval: replacing or deleting a board's state. The trace records the reason.
- From a fresh clone, a live run compares each board with my last saved state, so it reports only postings that appeared since then.
- `python3 -m job_agent run-one` is layer 1's watch of the OpenAI board, kept as it was; `python3 -m job_agent check-resume` validates Jane Doe's résumé.

## What ran

Every live run below was mine, run in the terminal of the Claude desktop app on my Mac. Times are Eastern; a run's id is its start time in UTC.

| Run (started) | Exit | What happened |
|---|---|---|
| [`2026-11-08T221447Z`](runs/2026-11-08T221447Z/), Sun 11/8, 5:14 PM, with `--approve` | budget-exhausted (4), 62.8 s | OpenAI: 816 postings, 75 new since my JS1 run of 10/31, 69 gone; Claude judged 20 (all valid) and 55 waited. Verkada (343) and Palantir (305) recorded as first states, so none counted as new. The made-up board answered HTTP 404: no retry, unverified, no state written. My JS1 state moved into `state/ashby-openai.json` under my approval (trace steps 3, 47 and 48). |
| [`2026-11-08T222101Z`](runs/2026-11-08T222101Z/), 5:21 PM | budget-exhausted (4), 65.6 s | No new or gone postings. Claude judged 20 waiting postings: 19 valid, and 1 rejected by the validator (a 4-sentence justification, over the contract's 3; never retried). 35 still waited. This run's saved report counts 55 postings as "judged after waiting"; the right number is 20, as its trace's `claude_call` lines show. The report code was fixed with a regression test in `e42796d`; saved runs are never edited. |
| [`2026-11-08T232915Z`](runs/2026-11-08T232915Z/), 6:29 PM | budget-exhausted (4), 62.5 s | Claude judged 20 more (all valid) and agreed with the rule on all 20, including three postings relevant by both. 15 still waited. |
| [`2026-11-08T233158Z`](runs/2026-11-08T233158Z/), 6:31 PM | incomplete (1), 44.9 s | Claude judged the last 15 (all valid, all not relevant by both). Nothing waits now. The exit is incomplete only because the made-up board failed. |
| [`2026-11-09T210704Z`](runs/2026-11-09T210704Z/), Mon 11/9, 4:07 PM | incomplete (1), 39.1 s | 15 new since the last run and 22 gone: OpenAI 811 postings (11 new, 16 gone), Verkada 342 (4 new, 5 gone: the first new postings on a second system), Palantir 304 (0 new, 1 gone). Claude judged all 15 (all valid), and both judges called all 15 not relevant. Nothing waits. The made-up board failed as before. |

- **The independent check** finds no disagreement between the report and the saved answers in any of the five runs. I ran it on the first run (5:19 PM ET on 11/8) and on the 2026-11-09 run (4:12 PM ET); Claude Code ran it on all five on 2026-11-09.
- **New and gone, recomputed:** for the 2026-11-09 run, Claude Code recomputed each board's new and gone postings from the saved answers alone (new: in no earlier saved answer of that board; gone: in the previous run's answer, not in this one), without the agent's code, and got the same 15 new and 22 gone as the report.
- **Labeled replays, not live runs:** the finished-wrong-answer demo replayed the first run's saved answers twice, with wrong version 1a planted and unchanged (I ran it at 5:20 PM ET on 11/8).
- **Contract versions:** the first two runs used contract v0.1 and the last three v0.2, from the review packet's patch (`4b1a418`), which came between the second and third. Each trace's first line records the version.
- **Claude calls in the runs:** 90 (20, 20, 20, 15 and 15), 89 valid. Every record is saved under `runs/<run id>/claude/`.
- **Not evidence, and not kept in the repo:** Claude Code's one GET each to seven real boards and three made-up names on 2026-11-06, to measure them; a rehearsal of the loop from a scratch copy on 2026-11-07 (live boards, no Claude calls); and two Claude calls on 2026-11-08 to find and check the plugin problem. SOURCES.md describes each.
- JS1's two runs (`runs/2026-10-30T093102Z/`, `runs/2026-10-31T231042Z/`) are described in [js1/README.md](js1/README.md).

## Results

- **New postings and both judges.** On 2026-11-08 the rule called 4 of the 75 new OpenAI postings relevant for Jane. Claude agreed on 3: Founding Full Stack Software Engineer, Consulting; Software Engineer, Cyber Safeguards; and Software Engineer, Agent Platform. Its answer on the fourth, EDA Cloud & Developer Infrastructure Engineer, was the one rejected for its length, so that posting has only the rule's verdict. On 2026-11-09 both judges called all 15 new postings (11 OpenAI, 4 Verkada) not relevant. On all 89 valid judgments, Claude's verdict matched the rule's (86 not relevant, 3 relevant). Agreement is not correctness: in JS2 neither judge was checked against hand labels.
- **The budget at work.** With 20 Claude calls per run, the 75 new postings of 2026-11-08 took four runs to clear: 55, 35, 15, then 0 waiting, each report saying how many still waited. The 15 new postings of 2026-11-09 fit in one run.
- **The deliberate failure.** The made-up board answered HTTP 404 in every run. It was never retried and never given a value, none of its postings counted as new or gone, its state was never written, and every report escalated it.
- **The permission policy.** 18 of my 19 predictions matched. Case 8, a redirect to another host, I predicted would be allowed; it is refused, because the policy never follows a redirect, and the board becomes unverified.
- **The review.** Contract v0.2 reads years in every sentence except "N years ago" and "the next N years". On the 2026-10-30 baseline it flips 2 verdicts (95 relevant become 93), where I had guessed 12. I accepted the patch.

## Known limits

- Check 7 still misses some wordings: "a minimum of 5 calendar years", "5+ yrs" and "Five-plus years" read as no years (REVIEW-PACKET.md, part 10).
- Contract v0.2 also reads sentences that are not requirements: "10+ years in the industry is a plus" blocks for Jane, and "We have grown 10x in 2 years" reads as 2 years. Neither changed a verdict in my saved answers, but both can.
- A Claude answer the validator rejects is never retried (the contract's rule), so a posting can end with only the rule's verdict, as the EDA posting did.
- The Greenhouse and Lever mappings are tested on saved answers from one board each, Verkada and Palantir. Other boards on those systems may fill their fields differently; a Greenhouse board with no "Employment Type" field passes check 1 as not stated.
- The retry for transient failures, and the request and time budgets running out, happened only in tests with a stand-in network; no live run hit them. Boundary cases 7 and 8 also use the stand-in, so no real request is sent.
- What Claude Code 2.1.317's built-in plugin `cc-plugin-privacy` does inside a call is not checked. I chose to trust it (`8ca0d4b`).
- No Palantir posting has been new in a live run (its first state on 2026-11-08 counts none as new), so neither judge has judged a Lever posting in a live run. The rule's reading of Lever postings was measured offline on the saved answer (9 relevant for Jane, REVIEW-PACKET.md part 4) and is covered by tests with saved answers.

## Contents

| Path | What it is |
|---|---|
| `GATE.md` | The gate: exits, budgets, repeat rule, error and permission policies, the field mapping, wrong versions |
| `CONTRACT.md` | The contract from JS1, now v0.2 (check 7's years reading, from the review) |
| `boards.json` | The four boards, each a system and a name, never a URL |
| `job_agent/` | The agent. Layer 2: `loop.py`, `providers.py` (the three systems), `policy.py` (the permission policy), `fetch.py`, `gate.py` (the budgets), `board_state.py`, `trace.py`, `loop_report.py`. From layer 1: the rule, the Claude judge, the résumé validator, the watch |
| `tests/` | The 206 offline tests, with fixtures trimmed from real saved answers |
| `tools/` | The independent check, the demo, the boundary table, the review-packet tools, the planted mistakes, and JS1's tools |
| `runs/` | Every live run (saved answers with SHA-256, Claude records, report, trace), the demo under `runs/demos/`, and JS1's two runs |
| `state/` | One state file per board: seen ids, run history, postings waiting for Claude |
| `BOUNDARY-TESTS.md`, `REVIEW-PACKET.md`, `MY-CHECKS.md` | The boundary-test table, the review packet, the commands I ran myself |
| `SOURCES.md`, `FRICTIONAL.md` | The sources and the split of work; my log |
| `js1/` | JS1's README, sources, decisions, log and action-surface comparison, as submitted (only their links to `experiment/` were updated for the new folder) |
| `persona/`, `prompts/`, `labels/`, `experiment/`, `LABELING-RULE.md` | From JS1, unchanged |

## Sign-off

**[Yours to type. Shape from the brief:]**

```text
Sign-off: Job-Search Agent 2
Checked:      which properties, by which of my own tests (name them)
How:          by hand / by a test I wrote before reading Claude's code /
              by recomputation / with Claude's help (say which parts)
Not checked:  at least three real items
Not claiming: what this agent does not show
Signed or withheld: ____________ (name, date)
```

## Driver's seat

For the loop and for the review: what Claude Code did, what I did, and why that part stays mine. The first two columns and the evidence come from the record; **the "why" column is yours to type.**

| Part | What Claude Code did | What I did | Why it stays mine | Evidence |
|---|---|---|---|---|
| The gate's rules | Measured the boards, laid out options with the numbers, proposed defaults, wrote GATE.md's text | Picked the boards, the budgets, the retry rule, the approval rule and the wrong versions; accepted the defaults; approved GATE.md | **[yours]** | `84d9f4c`; GATE.md, "Where these choices come from" |
| The loop's code and tests | Wrote the loop, the policy module, the tests and the planted mistakes | Ran the planted mistakes myself (61 of 61 caught) | **[yours]** | `ab2df17`, `10833a9`, `e569577`; MY-CHECKS.md, 6:02 PM |
| Running on real boards | No live run in `runs/` (only a scratch rehearsal) | Ran all five live runs, and approved moving my JS1 state | **[yours]** | `8aa6075`, `62ef1a6`, `0be7a10`, `84630ab`, **[today's commit]**; trace step 3 of the first run |
| What the policy should do | Wrote the 19 cases and their tests after my predictions were committed | Predicted all 19 before any test existed, then reran the table | **[yours]** | `21f33b7` before `e569577`; `b7b6cc0` |
| Trusting new Claude Code software | Found that the update made the lockdown refuse every call, read one call's startup record, proposed the fix and checked it with a second call | Decided to trust the plugin, knowing what it does is not checked | **[yours]** | `8ca0d4b` |
| Catching the finished wrong answer | Wrote the independent check and the demo tool | Ran the check and the demo on my run | **[yours]** | `14d5868`, `c03eb75` |
| The review: the bug, my guess and my test | Recommended this defect (noted in JS1); wrote `explain_rule.py`; counted the flips after my guess; measured readings A to D and recommended E; drafted my test from my pick | Picked the defect, reproduced it, guessed 12 before any count, picked E, and ran my test failing (4 of 5) before any patch existed | **[yours]** | `ab1c21a`, `e3ea1e2`, `5c788db`, `788852b` |
| The review: the patch and the decision | Wrote the patch; checked my written parts against the code | Ran my test passing, the flips and the planted mistakes; read the diff in my terminal; decided to accept, with my evidence; named the cases my test still misses | **[yours]** | `4b1a418`, `e7fed25`, `958d0a2`, `a04066b`, `6ecf6b0`, `584eac4` |
| Publishing | Prepares the course folder, the PR and the zip | Approves every push, the PR and the Canvas upload | **[yours]** | **[Tuesday]** |
