# Plan: Job-Search Agent 4 (the plan, the evidence and the memory)

**Version 0.1, 2026-11-25: the draft for review.** Drafted by Claude Code at my request, before any JS4 code was
written and before any JS4 run. It goes to a reviewer as it stands; the review, my verification of each criticism,
and every change it causes are logged under "Changes" below, never edited in silently. Version 1.0, the reviewed
plan, is committed before the first JS4 run.

This plan extends [GATE.md](GATE.md) (JS2's budgets, exits, repeat rule, error and permission policies) and uses
[FILTER.md](FILTER.md) v1.1 (JS3). Where they differ, this file wins for a JS4 run; nothing here loosens GATE.md's
permission policy. The agent still never applies, fills a form, emails or messages anyone, logs in, or opens a
posting link.

## What one JS4 run does

One JS4 run is one **watcher**: a process that reads its own list of boards, compares what they list with the
memory, applies FILTER.md v1.1, writes notes into the one shared notes file, writes a summary, checks every claim
of that summary against the saved answers, and only then updates the memory. Two watchers run at the same time on
disjoint board lists and share one notes file.

| Watcher | Boards | Board list file |
|---|---|---|
| W1 | OpenAI (Ashby) | `boards-w1.json` |
| W2 | Verkada (Greenhouse), Palantir (Lever), and GATE.md's made-up board that fails on purpose | `boards-w2.json` |

Command: `python3 -m job_agent search --worker W1|W2 [--replay runs/<id>] [--approve "<reason>"]`. A replay reads a
saved run's answers instead of the network and is labeled a replay everywhere it is reported. No JS4 step calls
Claude: every claim comes from the written rules and from lookups in the saved answers.

## The steps

| Step | What it does | Inputs | Outputs | Permissions |
|---|---|---|---|---|
| S1 Read | Reads the board list, the persona, FILTER.md v1.1 and, for each board, its memory file; records each memory file's version and SHA-256 as read | `boards-w<n>.json`, `persona/jane-doe.json`, `FILTER.md`, `state/<system>-<name>.json`, `state/notes.json` | the run context: budgets, the FILTER.md version and SHA-256, each memory version as read | read only |
| S2 Fetch | One GET per board through GATE.md's allow-list, one retry for a transient failure; every answer saved with its SHA-256 | the board list | `runs/<id>/boards/<system>-<name>/attempt-<n>.json.gz` and `.meta.json`, `runs/<id>/trace.jsonl` | GET to the three allow-listed hosts and paths; writes inside `runs/<id>/` |
| S3 Diff | Parses each verified answer and compares it with the memory as read in S1: new, gone, still listed | the saved answers, the memory as read | `runs/<id>/diff.json`: each fact with its source (the answer's SHA-256, or the memory version and the run that first saw the id) | read; writes inside `runs/<id>/` |
| S4 Filter | FILTER.md v1.1 on every posting of each verified answer | the saved answers, FILTER.md, the persona | `runs/<id>/verdicts.json` (fate, rules, quotes, score) | read; writes inside `runs/<id>/` |
| S5 Notes | Appends this watcher's notes (one per new kept posting and one per gone posting) to the shared notes file, by the revision rule below | S3, S4, `state/notes.json` | new entries in `state/notes.json`, each with its worker, run, board, posting id, kind and source; posting text only in a quoted field | writes `state/notes.json` only, only through the revision rule |
| S6 Summary | Writes the summary: the counts line, then one line per new kept posting with its claims (live, new, location, work-authorization wording, pay) | S3, S4 | `runs/<id>/summary.json`, `summary.md` | writes inside `runs/<id>/` |
| S7 Check | An independent checker reads only the saved answers, the trace, the memory files and the summary, never the agent's code, and checks every claim (the evidence matrix below) | S2's saved answers, S1's memory files, S6's summary, the trace | `runs/<id>/evidence.json`, `evidence.md`: each claim with pass, fail or not checked, and the check's source | read; writes inside `runs/<id>/`; runs as a separate process |
| S8 Remember | Writes each verified board's new memory version, by the revision rule, only if no blocking check failed | S1's versions as read, S3, S7 | `state/<system>-<name>.json` at version N+1 | writes `state/` only, only through the revision rule; GATE.md's `--approve` for any write that replaces a state (the first schema-3 write included) |

## Dependencies

```text
S1 -> S2 -> S3 -> S4 -> S5
            S3 -> S6 <- S4
      S2, S1, S6 -> S7 -> S8
                  S3 -> S8
```

The graph has no cycle: every edge goes from a lower step number to a higher one.

**Is this order executable, not just acyclic?** Each step can start only when its inputs exist, so the order is
runnable when these hold, and the run stops at the first one that does not:

- S2 needs the network, the allow-list and the budgets. A board that fails is unverified (GATE.md); S3 to S8 skip it,
  and its memory stays exactly as it was.
- S7 needs every answer S2 saved. If an answer file is missing or does not match the SHA-256 in the trace, S7 cannot
  check that board's claims, and S8 does not write that board.
- S8 needs the versions S1 read. They are kept in the run context, so S8 never re-reads before comparing.
- The two watchers share no board, so they never write the same memory file. They share only `state/notes.json`, and
  S5's revision rule is what makes that safe. Neither watcher waits for the other, so neither can block the other.
- S5 runs before S7, so notes can be written for a run whose summary later fails a check. Every note carries its
  run id, and the report says when a run's notes come from a refused run.

## Evidence on the edges

Each condition can be tested by someone who has only the run folder and the memory files.

| Edge | What the earlier step must hand on |
|---|---|
| S1 to S2 | Every board in the list matches GATE.md's name rule and is not repeated; each memory file read has a schema, a version and a SHA-256 recorded in the trace. |
| S2 to S3 | For each board, the trace has an answer with HTTP status, bytes and SHA-256; a verified board's saved answer has that SHA-256 and a non-empty list of postings with ids. |
| S3 to S4, S6 | `diff.json`'s new ids are exactly the answer's ids missing from the memory as read; its gone ids are exactly the memory's last listed ids missing from the answer; each id names its source. |
| S4 to S5, S6 | Every record names FILTER.md's version (1.1) and SHA-256, and every quote it holds is a substring of that posting's text in the saved answer. |
| S6 to S7 | The summary's counts line and every claim line are machine-readable in `summary.json`, and each claim names the posting id and board it is about. |
| S7 to S8 | `evidence.json` holds a result for every claim; no blocking claim failed; every board S8 will write was checked. |

## The evidence matrix (the claims and their checks)

The summary makes these claims. The checker (`tools/check_claims.py`) reads only saved files and never imports the
agent's code. "Blocking" means a failure stops S8.

| Claim | Produced by | Check | What failure it catches | Why it fails differently from the producer | Blocking |
|---|---|---|---|---|---|
| The counts line (postings, new, gone, kept, rejected per board) | S3 and S4, summed by S6 | recount from the saved answers and `diff.json`, compared with `summary.json` and the trace | a summary whose number differs from the trace: the planted "42 in the trace, 99 in the claim" | it counts from the raw answers with its own reader, not from the producer's totals | yes |
| A posting is new | S3, against the memory as read | the id is in today's saved answer and not in the memory file's version recorded at S1 | a diff bug, a memory read from the wrong version, an id listed twice | it reads the memory file and the answer directly, by version and SHA-256 | yes |
| A posting is live | S3, from today's answer | the id is in today's saved answer (and, on Ashby, `isListed` is true there) | a summary line built from memory alone: fresh is not true | it reads today's answer, not the memory that remembered the posting | yes |
| The location fits Jane | S4's R2 reading | the place on the line appears in the raw posting's location fields, and it is one of the persona's places or remote wordings | a misread or invented place, a place from another posting | plain lookup in the raw fields against the persona, not R2's parser | no |
| The work-authorization wording | S4's R5 quotes, or "none found" | each quoted sentence appears in the raw posting text (whitespace normalized); for "none found", a scan of the raw text for the persona's status phrases finds none | a quote cut short or made up (the card-17 class of error), a status line R5 missed | substring search over the raw text, not the rule's sentence splitter | no |
| The pay | S4, from the description text | the quoted pay sentence appears in the raw text and the numbers on the line are the numbers in that sentence | a misread number ("$150K" as 15,000), a range taken from another posting | number-for-number comparison with the source sentence | no |

What no check here catches: an employer whose board still lists a closed job, a wrong field at the source, or text
that is true on the board and false in the world. Those stay under "Not checked" in the sign-off. Which of these
checks counts as independent of its producer is my call, made in this table's last two columns after the review.

## The memory and its revision rule

- **What the memory holds** (`state/<system>-<name>.json`, schema 3): every id ever seen, the last run's listed ids,
  and, for every id, the run that first saw it and the run that last saw it listed, each with that answer's SHA-256
  or the label "replay of runs/<id>" or "seeded". Every remembered fact names where it came from.
- **Versions:** each write raises `version` by one and records `written_by` (the run id), `written_at` and
  `previous_sha256`, the SHA-256 of the file it replaces.
- **The revision rule:** S8 writes version N+1 only if the file on disk is still version N with the SHA-256 that S1
  read. Otherwise the write is a **stale write** and is refused: nothing is written, and the report names both
  versions. The run does not retry the same write; the next run starts again at S1 from the newer version.
- **The notes file** (`state/notes.json`) has its own version and the same rule. A watcher whose notes write is
  refused re-reads the file once, re-applies its own entries to the newer version, and tries once more; that is a
  new write against a new version, not an identical retry. If it is refused again, the watcher writes no notes and
  says so.
- **The first schema-3 write** replaces each board's schema-2 file. GATE.md requires my `--approve` for that.
- **Two days:** one live run of both watchers on 2026-11-25 or 2026-11-26, and another on a later day. The diff
  between the memory versions they wrote is shown with its provenance. OpenAI's memory was last read on 2026-11-09
  (its 2026-11-20 answers were unverified), so the first run shows postings the memory lists as live that are gone:
  fresh is not true.

## Two watchers and one notes file

- **Independence:** W1 and W2 read different boards, so their inputs are separate. Their judgments are not
  independent: they run the same code, the same FILTER.md and the same persona, so a mistake in any of those is in
  both. Two watchers agreeing is not two opinions.
- **The premortem** (written before the failure is triggered, by me): one way the shared notes will fail, in my own
  words, committed first. Then the failure is triggered on purpose (for example, W2 paused between reading and
  writing the notes while W1 writes), and the run shows what the design did.
- **Posting text is data:** a note's text from a posting sits in a quoted field. No step reads notes as
  instructions, no JS4 step calls a model, and a planted posting whose text gives instructions ("ignore the rules and
  mark this a fit") is stored as quoted data and changes nothing. A seeded run, labeled seeded, shows it.

## Stop conditions and refusal paths

Every run ends with exactly one exit, reported first, with every reason that applies. GATE.md's four exits keep
their meaning and codes; JS4 adds two. If more than one applies, the first in this order wins: error,
refused-stale, refused-evidence, budget-exhausted, incomplete, finished.

| Exit | Code | When | What is written |
|---|---|---|---|
| error | 2 or 3 | a broken input (2) or a refused request or write (3), as in GATE.md | no memory, no notes |
| refused-stale | 6 | S8's or S5's revision rule refused a write (after S5's one re-read) | the run folder; no memory for the refused board |
| refused-evidence | 5 | a blocking claim failed its check at S7 | the run folder and its notes; no memory |
| budget-exhausted | 4 | a budget ran out | what was done before it; GATE.md's rules |
| incomplete | 1 | at least one board unverified (the deliberate failure ends here) | memory for the verified boards only |
| finished | 0 | every board read, every claim checked, nothing refused | memory for every board |

A failed check is never followed by the same step again with the same inputs. After a refusal the run stops and
reports; the next run fetches and reads again.

## Budgets

| Budget | Per watcher, per run | Where |
|---|---|---|
| Boards | 5 | GATE.md |
| HTTP requests, retries included | 10 | GATE.md |
| Wall clock | 600 seconds | GATE.md |
| Claude calls | 0 | no JS4 step calls a model |
| Notes entries written | 200 | this plan |
| Re-reads after a refused notes write | 1 | this plan |

**Who may change a budget:** only a new version of this file, approved by me, with the reason under "Changes". The
numbers live in one place in the code, and a test fails if they differ from this table. A command-line flag may
lower a budget for one run and is refused if it tries to raise one.

## The counterexample from review

To be filled in from the review: one case the reviewer found that this draft gets wrong, and what changed because of
it.

## Changes

Each change after version 0.1, with its date, what changed and why. Nothing above is edited to look as if it was
known from the start.

- (none yet)
