# Job-Search Agent 1: The Contract and the Watch

INFO 7375, Prompt Engineering for Generative AI, Fall 2026. Aravind Sundaravadivelu (GitHub: AravindKumar2504). Assignment JS1.

One public job board, one fictional résumé, new postings only, and every verdict justified twice: once by a written rule (a record anyone can recompute) and once by Claude (a judgment, labeled as one). It is also the first layer of the agent I will use for my own new-grad search; my real résumé and data are never in this repo.

**Jane Doe is fictional.** Her résumé (`persona/jane-doe.json`) has a situation like mine (F-1 student, not a U.S. person, needs H-1B sponsorship later, earliest full-time start May 2027, backend new grad) but none of my identity, an `@example.com` email and a 555-01xx phone number. Nothing is ever sent or applied for in her name.

## Language and toolchain

- Python 3.9 or newer, standard library only: nothing to install. Tested with Python 3.12.14 and macOS's own 3.9.6.
- The Claude judge runs the Claude Code CLI (tested with 2.1.309) signed in with a claude.ai seat. There is no API key. The CLI is found as `claude` on the PATH, as the Claude desktop app's copy on a Mac, or at the path in `JOB_AGENT_CLAUDE`.
- git, for the privacy test's file list (without git it walks the folder).

## Commands (from the repo root)

```bash
python3 -m unittest discover -s tests -t .
```
99 offline tests. No network and no Claude: a stand-in plays the CLI, and the tests point the real one at a path that does not exist.

```bash
python3 tools/mutants.py
```
Plants 37 mistakes in a copy of the code, one at a time, including the contract's four wrong versions (W1 to W4), and checks that the tests catch every one.

```bash
python3 -m job_agent check-resume
```
Validates Jane Doe's résumé and runs nothing else.

```bash
python3 -m job_agent run
```
One live run: fetch the board (allow-listed host only), save the raw response with its SHA-256, compare with `state/seen.json`, judge each new posting both ways, write `runs/<UTC time>/report.md`, then save the state. The first run is a baseline that reports none as new. Exit codes: 0 done, 1 no answer from the board, 2 broken input, 3 refused.

```bash
python3 tools/recompute_new.py runs/2026-10-30T093102Z/response.json runs/<run 2>/response.json runs/<run 2>/report.json
```
Recomputes run 2's new and gone postings from the two saved responses, without the agent's code, and checks the report (the contract's failure sentence).

```bash
python3 tools/select_postings.py --check
```
Shows that the 20 labeled postings are exactly what the seeded selection rule gives.

```bash
python3 tools/experiment.py report
```
Rebuilds the sampling report and the experiment report from the saved Claude calls, offline, scoring every saved reply with the contract's validator.

The saved calls in `experiment/` came from these commands, run once each on 2026-10-30. They call Claude live, and the experiment tool refuses to run a set twice, so nothing above needs them:

```text
python3 tools/claude_check.py
python3 tools/experiment.py sample --times 5
python3 tools/experiment.py run prompts/baseline.txt development
python3 tools/experiment.py run prompts/revision-specialty.txt development
python3 tools/experiment.py run prompts/baseline.txt held_out
python3 tools/experiment.py run prompts/revision-specialty.txt held_out
python3 tools/action_surfaces.py file
python3 tools/action_surfaces.py agent
```

## What ran

- **Baseline, Friday 2026-10-30 5:31 AM ET** (09:31Z): `runs/2026-10-30T093102Z/`, 814 postings recorded, 0 new.
- **Run 2, Saturday 2026-10-31:** not run yet; I run it myself.
- **Claude calls on 2026-10-30 (68):** a lockdown check (`experiment/check/`); the sampling report, 5 postings x 5 fresh calls (`experiment/sampling/`); the prompt experiment, 2 prompts x 10 development postings, then the same 2 prompts once on the 10 held-out postings; the action-surface runs (`experiment/surfaces/`).

## Results

- **The rule** on the baseline board: 95 of 814 postings relevant for Jane.
- **Sampling** ([experiment/SAMPLING.md](experiment/SAMPLING.md)): repeated verdicts were repeatable, not right: postings 1 and 4 got "relevant" on every valid try, and I labeled both not relevant. On posting 5 the verdict flipped inside three broken replies, each holding a "not_relevant" answer and then a "corrected" "relevant" one; the validator rejected them.
- **Prompt experiment** ([experiment/EXPERIMENT.md](experiment/EXPERIMENT.md)), scored with the contract's validator and my current labels: development set, baseline 8/10, revision 10/10; held-out set, baseline 8/10, revision 9/10; rule 8/10 on both; majority class 7/10 on both. The revision's held-out edge rests on one posting I relabeled after seeing the results, and the report shows every other scoring. Ten cases cannot separate these prompts.
- **Action surfaces** ([ACTION-SURFACE.md](ACTION-SURFACE.md)): pasted text (the agent's design), a file to read, and an agent with fetch and write tools, which could not read the 13.5 MB board and still gave a verdict.

## Known limits of the rule

- Check 7 reads years only in sentences that contain "experience", so "5+ years in one or more of: ML systems..." is skipped; 2 of the 95 rule-relevant postings on the baseline board ask for years that way.
- Check 7 takes the contract's patterns literally: "up to 5 years" reads as 5, "three-to-five years" as 5, and "2.5+ years", "1 year" and months are not read.
- Check 6 never fired on the baseline board. Its sentence split separates a month written "Jan. 2027" from its year.
- Locations count only through a US address's region or city, or an exact remote string from Jane's list.
- The privacy scan recognizes US phone formats only.

## Contents

| Path | What it is |
|---|---|
| `CONTRACT.md` | The contract, the first commit |
| `job_agent/` | The agent: allow-list, fetch, board, evidence, state, résumé validator, rule, Claude judge, report, watch, command line |
| `persona/jane-doe.json` | The fictional persona |
| `prompts/` | `baseline.txt`, the prompt contract the agent uses; `revision-specialty.txt`, the experiment's one change |
| `LABELING-RULE.md`, `labels/` | My labeling rule, the seeded selection, the labeling sheet, my 20 labels |
| `experiment/` | The sampling and experiment reports and every saved Claude call |
| `ACTION-SURFACE.md` | The three ways, with their records |
| `runs/`, `state/` | Raw responses with SHA-256, reports, and the seen-ids state |
| `tools/` | The mutants, recomputation, selection, experiment, lockdown check and action-surface tools |
| `tests/` | The offline tests |
| `DECISIONS.md`, `SOURCES.md`, `FRICTIONAL.md` | My decisions, the sources and the split of work, my log |
