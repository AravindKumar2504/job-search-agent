# Review 1 of PLAN.md v0.1, word for word

- **Reviewer:** Claude (Claude Code's read-only planning agent, model Claude Opus 5.5), started by Claude Code on 2026-11-25 with a fresh context: it saw the assignment, PLAN.md v0.1 (commit `4ae45c8`), GATE.md, FILTER.md, the code and the saved runs, and none of the conversation in which the plan was drafted. It could read files and run read-only commands, and changed nothing.
- **The brief it was given:** to list concrete criticisms with a counterexample for each, most serious first; to check executability, the edges' evidence, the stop and refusal paths, the revision rule under every interleaving of two processes, whether each check fails differently from its producer, the budgets, and conflicts with GATE.md and the code; to separate real problems from matters of taste; and to end with the one counterexample that should most change the plan.
- **Received:** 2026-11-25. The text below is its final message, unedited. Aravind's verification of each criticism is in `VERIFICATION.md`.

---

# Review of PLAN.md v0.1 (commit 4ae45c8)

I checked the plan against GATE.md, FILTER.md v1.1, the code in `job_agent/`, `tools/check_run.py`, the three files in `state/` and the saved answers in `runs/2026-11-20T114036Z/`. The numbers below come from read-only runs of the existing code on those answers: FILTER.md v1.1 applied in memory, and `files_policy()` asked about the plan's paths. Nothing was written.

**Short answers to your checklist**
- **Order:** it has no cycles, but it cannot run as written (items 1, 8 and 9, and the S7 inputs line under "Smaller real problems").
- **Edges:**
  - S1→S2 fails on day 1.
  - S2→S3 has a gap for a board that never answers.
  - S3→S4/S6 cannot be re-tested once S8 has run.
  - S4→S5/S6 is false on real data.
  - S5's output has no edge at all.
- **Revision rule:** it does not reject a stale write in every interleaving (item 1).
- **Evidence matrix:** two checks fail the same way as what they check (item 5).
- **Budgets:** stated, but with two owners (item 12).
- **Conflicts with GATE.md or the code:** items 1, 3, 4, 8, 10 and 11.
- **Feasibility:** the two-day run and the fresh-is-not-true case are feasible once items 3, 6 and 7 are fixed. The injection case needs a sandbox and a testable condition.

## Real problems, most serious first

### 1. The revision rule checks, then writes in a separate step
**Where:** "The memory and its revision rule"; S5; S8; the S8 bullet under "Is this order executable".

**What is wrong:** "S8 writes version N+1 only if the file on disk is still version N with the SHA-256 that S1 read" describes a comparison followed by a rename. Nothing makes the two one step, so the other process can write in between. The existing writer, `board_state.save`, also gives every writer the same temp file name, `<file>.tmp`.

**Counterexample** (the notes file is at v3 with SHA A):
1. W2 at S5 re-reads the disk and finds v3 with SHA A. It matches.
2. W1 at S5 re-reads the disk and finds v3 with SHA A. It matches.
3. W1 renames its v4 (its notes added to v3) into place.
4. W2 renames its v4 (its notes added to v3) into place.

W1's notes are gone, both traces say "wrote v4", and nothing was refused.

If steps 3 and 4 overlap, both processes write `state/notes.json.tmp`:
- W2's truncate-and-write lands in the file W1 has just renamed.
- W2's own `os.replace` then fails with FileNotFoundError.
- `notes.json` ends up as one writer's bytes or a mix of both. A mixed file stops both watchers at S1 with broken input (exit 2) on every later run.

The planned trigger ("W2 paused between reading and writing the notes") finds this only if the pause comes after S5's comparison. If W2 pauses after S1's read, the demonstration shows the rule working and misses the hole.

Three more gaps in the same rule:
- **No base case.**
  - All three memory files are schema 2 and have no `version` key. So the S1→S2 condition ("each memory file read has a schema, a version and a SHA-256") is false on day 1.
  - `state/notes.json` does not exist. On day 1 both watchers see no file and both create it, which is the likeliest moment for the lost update.
  - If S5 goes through `Files.check_state_write`, the second watcher to create the file gets NeedsApproval ("a state file is already there") and exits 3, whatever approval was given.
- **The second notes attempt.** "The same rule" compares against the version S1 read. After the re-read, the disk is never that version. Implemented literally, every second attempt is refused, so in every concurrent run the watcher that reaches S5 second ends refused-stale.
- **"S8 never re-reads before comparing."** The existing `check_state_write` compares the new state with the copy read at the start (`board.on_disk`) and never looks at the disk again. If the rule is built that way, it can never refuse anything.

**Smallest fix:** make the write itself the check.
- Write each version to its own file, `state/<name>.v<N+1>.json`: write a temp file with a name unique to the process, then `os.link` it to the version name.
- The link fails if that name already exists, and that failure is the stale-write refusal. The memory is the highest version present.
- A lock also works: an exclusive `flock` on a separate file that is never replaced, held from the re-read through the rename, with per-process temp names and a wait limited by the wall clock. But a lock keeps no old versions.

Also:
- Hash and parse the same bytes, from a single read.
- Define a schema-2 file as version 0.
- Commit an empty notes file at version 0 before the first run, and treat a missing notes file as broken input.
- Say that the second notes attempt compares with the version it re-read.
- Put the premortem's pause between the comparison and the write, behind a flag a stranger can pass and the trace records.

### 2. Notes and memory are not committed together, so refused runs leave duplicate or missing notes
**Where:** S5, S8, Dependencies, and the exits table ("refused-evidence: the run folder and its notes"; "refused-stale: no memory for the refused board").

**What is wrong:**
- S5 writes the shared notes before S7 has checked anything.
- Nothing depends on S5 (it is a dead end in the graph), so S8 writes memory whether or not S5 succeeded.
- Notes have no key, so nothing stops the same fact from being written twice.

**Counterexample A (duplicate notes):**
- On the saved 11-20 answer, W1 would write 102 notes: 99 for postings that the 11-09 memory lists and the answer lacks, and 3 for new kept postings.
- If day 1's S7 then fails a blocking claim, the notes are written but the memory is not.
- Day 2 compares against the same 11-09 memory and notes the same 99 or more postings as gone a second time.

**Counterexample B (notes lost for good):**
- W2's notes write is refused twice because W1 wrote twice in between, as the premortem may arrange. W2 writes no notes and exits 6.
- The exits table withholds memory only for "the refused board", and notes belong to no board, so S8 writes Verkada and Palantir anyway.
- Their new and gone postings are now in memory, the next diff does not report them, and their notes are never written.

**Smallest fix:**
- Move S5 after S7.
- Give every note a key: board, posting id, kind, and for gone notes the run that last saw the posting listed. Never write a key that is already present.
- Add an S5→S8 edge with the condition: "this run's notes are in the notes file at the version S5 wrote; if S5 was refused, S8 writes no memory for any of this watcher's boards".

### 3. The approval for the first schema-3 write is checked too late, and it approves more than it names
**Where:** S8's permissions; "The first schema-3 write"; the exits table ("error ... no memory, no notes").

**Counterexample 1 (approval checked too late):**
- On day 1, `search --worker W1` is run without `--approve`. S1 to S7 run, and S5 appends the notes.
- S8 tries to replace a schema-2 file, gets NeedsApproval, and the run exits 3.
- The exits table says an error leaves no notes, but the notes are there. Re-running with `--approve` writes them again.
- `loop.py` avoids exactly this for the JS1 state move by checking the approval "before anything is fetched".

**Counterexample 2 (approval too broad):**
- `policy.replaces()` returns at the first difference it finds ("its schema would change") and never checks for dropped ids or changed runs. With `--approve`, the write is simply "approved".
- So a migration that builds the seen ids from `last_run.posting_ids` (811 for OpenAI) instead of `seen_ids` (907) silently drops 96 ids.
- The trace records only the reason given for the approval. Every later "new" check compares against the same damaged memory, so no check in the matrix can see the loss.

**Smallest fix:**
- At S1, work out which S8 writes will need approval (any schema-2 file on disk), and refuse before S2 if `--approve` is missing.
- With approval given, still refuse a write that drops a seen id or changes an earlier run: check every condition in `replaces()`, not just the first.
- Record what the approval covered: schema 2 to 3, and whether Palantir's 12 `pending_claude` ids are dropped.

### 4. Replays, seeded runs and planted runs write to the live memory and notes
**Where:** the command line; the memory labels "replay of runs/<id>" and "seeded"; the injection case; the planted error in the evidence matrix.

**What is wrong:** the command has no `--state` or `--runs` options. Today's command line refuses a replay aimed at the default folders ("a replay needs its own --state and --runs, so it never mixes with the live runs"). The plan's labels suggest replayed facts go into the live memory.

**Counterexample:**
- After day 1, OpenAI's v1 lists day 1's ids. Someone then runs `search --worker W1 --replay runs/2026-11-09T210704Z`, which compares the 11-09 answer with v1.
- Every posting first listed after 11-09 and still listed on day 1 is reported gone; 136 such new postings were already in the 11-20 answer. Each gets a "gone" note in the real notes file.
- The replay's S8 then writes v2 with the 11-09 listing as "last listed". Day 2 reports the 99 or more old gone postings a second time, and misses postings first listed after 11-09 that disappeared by day 2.
- The two-day diff is now between a live version and a replayed one.
- The injection's planted posting and the planted 42/99 run would land in the real notes file the same way.

**Smallest fix:**
- Keep today's rule: a replay, seeded or planted run needs its own `--state` and `--runs` folders, filled from copies of the live files. Then "replay" and "seeded" labels never appear in the live `state/`.
- Say how the 42/99 error is planted: a mutant copy of the code, run as a labeled replay. That is how GATE.md's wrong versions and `runs/demos/finished-wrong-answer/` were done.

### 5. Several checks fail the same way as what they check, and two claims have no check at all
**Where:** the evidence matrix. Examples come from `runs/2026-11-20T114036Z/` with FILTER.md v1.1 applied in memory.

- **Counts line.**
  - New and gone are recounted "from the saved answers and diff.json", but `diff.json` is S3's own output. A planted S3 bug that drops half the gone ids leaves `diff.json` and the summary in agreement, so the check passes.
  - Kept and rejected cannot be recounted without running FILTER, which the checker may not import. They can only be compared with `verdicts.json`.
  - *Fix:*
    - Recompute new and gone from the raw answer and the memory as read (item 7).
    - Label the kept/rejected comparison as a copying check only.
    - Add a cannot_tell count to the counts line. OpenAI's posting with no title (`1ae64ddb-…`) was in the 11-20 answer, so kept plus rejected does not add up to the number of postings.
- **Work authorization.**
  - The persona has no status phrases: its `work_authorization` holds only `status`, `us_person` and `needs_sponsorship`. The only phrase lists are FILTER.md v1.1's `status_us_person_phrases` and `status_sponsorship_phrases`, which are R5's own. So the "none found" scan is just R5 run a second time.
  - Verkada posting 5302623007 says "This role does not offer visa sponsorship." None of R5's nine sponsorship phrases matches that sentence. R5 rejected the posting only because another sentence requires U.S. citizenship.
  - A posting with only that sentence would be kept, the summary would say "none found", and the check would pass it.
  - The claim's wording is also wrong for postings that do address authorization. R5 returns a quote only when it rejects, so every kept posting reads "none found". That includes the 6 kept Verkada postings that say "We do sponsor and take over sponsorship of employment visas for this role.". It also includes 9 kept OpenAI postings whose export-control sentence says candidates "may need to meet certain legal status requirements".
  - None of these 15 postings is new against today's memory. But the wording shows what new postings from these companies will carry.
  - *Fix:*
    - Word the claim as "none of R5's phrases found".
    - Have the checker list every sentence that matches its own, broader pattern: sponsor, visa, citizen, clearance, authorized to work, export control, legal status.
    - Make "none found" fail whenever such a sentence exists.
- **Pay.**
  - The check confirms that the quoted sentence is in the text and that its numbers match. It does not confirm that the sentence is about pay.
  - The kept Verkada postings carry a company sentence ("a $5.8B valuation, more than $1 billion in annualized bookings") as well as the pay line ("$135,000—$160,000 USD"). A producer that takes the first dollar sentence would pass.
  - 85 of the 86 kept OpenAI postings have no dollar sentence in `descriptionPlain` from this endpoint, so "none found" passes there without testing anything.
  - *Fix:*
    - Require a pay pattern: salary, base pay or range, with two amounts and a currency.
    - Compare amounts with their units ($230K is 230,000).
    - Add "pay published outside the description" to the Not checked list.
- **Location.**
  - "Plain lookup in the raw fields against the persona" fails if the summary line names the place as posted.
    - OpenAI's "San Francisco" is not one of the persona's places. R2 matches it to the region California through `address.postalAddress.addressRegion`.
    - "San Mateo, CA United States" needs CA mapped to California.
  - R2 also keeps US places outside Jane's areas (−15) and unclear places (−10). This check would call those failures.
  - *Fix:* make the claim R2's location category, and have the check confirm the category from the raw fields using its own state-code table.
- **Missing rows.**
  - "A posting is gone", which is the fresh-is-not-true fact itself, has no check.
  - Neither does each board's read or unverified status. That is GATE.md's "finished but wrong" case, which `tools/check_run.py` already checks.
  - Add both.
- **What each check still cannot catch** (for the Not checked list):
  - New: a job reposted under a new id, and a memory that was already wrong before the run (item 3).
  - Live: a closed job the board still lists, a cached answer, and a replay's old answer. In a replay, "live" should read "listed on <date>".
  - Work authorization: wording that is in neither phrase list.
  - Pay: pay published outside the description.
  - Counts: FILTER's own verdicts.

### 6. No planned run can produce a stale write of the seen-postings memory
**Where:** "The memory and its revision rule"; "Two watchers and one notes file".

**What is wrong:**
- The assignment calls the seen-postings state shared memory and asks for a stale write of it to be rejected and shown.
- The plan gives each board's memory to a single watcher and triggers its only deliberate failure on the notes file. With one instance per watcher, S8's comparison cannot fail in any planned run.
- The safety argument also depends on something nothing checks: S1 never compares the two board lists.

**Counterexample:**
- Run both days exactly as planned. No stale write of any `state/<system>-<name>.json` is ever attempted, so the submission's "stale-write rejection" can only be a notes rejection.
- Separately: if `boards-w2.json` gains `ashby/openai`, both watchers write `ashby-openai.json`.

**Smallest fix:**
- Plan a labeled stale write on one board's memory file:
  1. Start W1 run A and pause it before S8 (using item 1's flag).
  2. Run W1 run B to the end.
  3. Resume A. It must be refused, with both versions named and no notes written.
- Have S1 read both board lists and refuse if they overlap.

### 7. The memory "as read" disappears at S8, so the edges and the "new" check cannot be re-tested
**Where:** "Each condition can be tested by someone who has only the run folder and the memory files"; S1; S7.

**What is wrong:** S1 keeps only each memory file's version and SHA-256, and S8 then replaces the file.

**Counterexample:**
- After day 1, a stranger runs `tools/check_claims.py` on the day-1 run folder.
- `state/ashby-openai.json` is now v1, which contains every new id. So every "new" claim fails or comes back "not checked".
- The edge condition "gone ids are exactly the memory's last listed ids missing from the answer" cannot be tested, because v1's listed ids are day 1's.
- The two-day diff, and the "state file's versions" the assignment asks for, both depend on committing `state/` after every run. The plan never requires that.

**Smallest fix:**
- Have S1 copy each memory file and the notes file, byte for byte, into `runs/<id>/memory-as-read/`. Each copy's SHA-256 must equal the one in the trace, and S7 reads the copy. Alternatively, adopt item 1's versioned files, which keep every version on disk.
- Commit `state/` after each live run.

### 8. The permission module refuses the plan's own inputs, and the checker writes outside it
**Where:** S1's inputs; S7; "nothing here loosens GATE.md's permission policy".

**Counterexample:**
- Through `files_policy()` in `job_agent/__main__.py`, `check_read` refuses `boards-w1.json`, `boards-w2.json` and `FILTER.md` ("outside the folders the agent may read"). `boards/w1.json` is allowed. So S1 exits 3 before any request is sent.
- FILTER.md is not in GATE.md's read list at all; JS3's filter command reads it without going through the module. Reading it through the module therefore widens GATE.md's reads.
- S7 "never imports the agent's code", so its writes to `evidence.json` and `evidence.md` cannot go through the single checking module GATE.md requires.
- The watcher also has to start S7 as a separate process, and GATE.md lists no such permission.

**Smallest fix:**
- Move the board lists to `boards/w1.json` and `boards/w2.json`.
- Add FILTER.md to the read list, and log that under "Changes" as a widening.
- Have the checker print JSON to its output, as `tools/check_run.py` already does. The watcher then writes `evidence.json` through the module, and records the SHA-256 of the checker file and of its output in the trace.
- Name the one process S7 may start (`python3 -I tools/check_claims.py runs/<id>`) and its timeout.

### 9. The S4 edge is false on real data
**Where:** "S4 to S5, S6: ... every quote it holds is a substring of that posting's text in the saved answer".

**Counterexample:**
- R2 builds quotes that appear in no posting:
  - "London, UK; Munich, Germany; Paris, France" (OpenAI `c0586c46-…`, one of 16 such R2 quotes in the 11-20 answer).
  - "remote, US" (Palantir `0ccbe620-…`).
- For Greenhouse, "the posting's text in the saved answer" is HTML with encoded entities. 27 of 372 quotes taken from Verkada descriptions are not literal substrings of the raw `content` field.
- So either the run stops at S4 every day, or a stranger's test of the edge fails even though the run carried on.

**Smallest fix:**
- Define "the posting's text" as the fields GATE.md maps, with whitespace collapsed.
- Check an R2 quote one part at a time, splitting on "; ".
- Check "remote, US" against `workplaceType` and `country`.

### 10. Two watchers started together collide on the run folder
**Where:** "What one JS4 run does"; the command line.

**Counterexample:**
- `evidence.run_id_for` produces ids like `%Y-%m-%dT%H%M%SZ` (to the second), and a run refuses a folder that already exists.
- `python3 -m job_agent search --worker W1 & python3 -m job_agent search --worker W2` gives both watchers the same id. The second exits 3 ("already exists, and a saved run is never overwritten").
- That is the natural way to start the overlap the premortem needs.

**Smallest fix:** put the worker and sub-second time in the run id, for example `…T150000.123456Z-W1`.

### 11. Some exits and refusals are missing or contradict each other
**Where:** "Stop conditions and refusal paths".

- **No step reports the exit after S8.**
  - refused-stale is decided at S8, but the only report (S6's summary) is written before that.
  - *Fix:* add an S9 that writes report.md and report.json with the exit first, then the trace's exit line.
- **S7's own failures are not covered.**
  - The checker can crash, hang, print nothing, or return "not checked" for a blocking claim.
  - "No blocking claim failed" lets the last case through. Day 1's "new" check against a schema-2 file with no version is exactly that case.
  - *Fix:* say that a blocking claim that is not checked counts as failed, and that a missing, crashed or timed-out checker gives refused-evidence.
- **"The next run fetches and reads again" is an identical retry when nothing has changed.**
  - A re-run minutes after refused-evidence gets byte-identical answers and the same code, and fails the same way.
  - Example: `providers.read` does not filter on Ashby's `isListed` field, but the live check does. A single unlisted posting would refuse every W1 run for as long as Ashby returns it.
  - *Fix:* refuse a run whose answer SHA-256s and code fingerprint (both already in the trace) match those of the refused run, unless the user says what changed.
- **"GATE.md's four exits keep their meaning" cannot hold.**
  - GATE.md's "finished" requires that "every new posting has both verdicts", which a budget of 0 Claude calls rules out.
  - If JS4 reused `loop._judge` with a Claude budget of 0, every run with a new posting would end budget-exhausted. So would every W2 run while Palantir's 12 `pending_claude` ids remain.
  - *Fix:* say that JS4's "finished" drops the Claude condition, and that JS4 does not call `_judge`.

### 12. Budgets have two owners, and the notes budget has no rule for running out
**Where:** "Budgets".

- **Two owners.**
  - The plan says only a new version of PLAN.md may change a budget, but three rows say "Where: GATE.md", and GATE.md says only a new GATE.md changes them.
  - `tests/test_gate.py` ties `gate.MAX_CLAUDE_CALLS` (20) to GATE.md, so the plan's 0 cannot live in that same "one place" in the code.
  - *Fix:* have each row name the file that owns it, and keep JS4's own numbers in one new table in the code, tested against this one.
- **Notes budget.**
  - The budget is 200 notes, but nothing says what happens at the 201st.
  - W1 would write 102 notes on the 11-20 answer alone, and day 1 is later.
  - If the notes are cut at 200 and S8 then runs, the rest are lost for good.
  - *Fix:* a run that would exceed the budget writes no notes and no memory, and exits budget-exhausted.
- **Missing limits.** The checker has no time limit. The command line has no `--max-*` flags, although the text says a flag may lower a budget.

## Smaller real problems
- **S7's inputs leave out what its checks read:** `diff.json` (counts), `verdicts.json` (kept and rejected), the persona (location) and FILTER.md (phrase lists). The graph has no S3→S7 or S4→S7 edge.
- **FILTER.md v1.1 is not pinned.**
  - `filter.load_rules()` with no version reads the newest Section 7, and v1.1 itself lists changes waiting for a later version.
  - Load version "1.1" explicitly, and record the SHA-256 of that Section 7 block rather than of the whole file, which changes with any edit.
- **Repeated boards:** the S1→S2 edge says each board "is not repeated", but GATE.md's repeat rule skips and reports a repeat. Say which one holds.
- **Schema 3 rewrites "the run that last saw it listed"** for about 850 OpenAI ids on every run.
  - That does not "only add" to a board's state in GATE.md's sense, and `policy.replaces()` would not notice.
  - Either store each run's listed ids without ever changing them and derive "last seen" from that, or log the amendment.
- **Migrated ids have no fitting source label.**
  - Schema 2 does not record the run that first saw each id, and "answer SHA-256", "replay" and "seeded" don't fit those ids.
  - The first-seen runs can be rebuilt: the saved answers of the seven runs listed in `ashby-openai.json` contain exactly its 907 seen ids. 814 were first seen on 10-30, 7 on 10-31, 75 on 11-08 and 11 on 11-09.
  - Write that rule down, and label anything that cannot be rebuilt "carried over from schema 2".
- **S2→S3 needs "an answer" for each board,** but a board that times out or fails DNS has none.
- **JS1's `run-one` still writes `state/seen.json`** for the same OpenAI board, using `state.py` (no version, the same fixed temp name). `loop.py` treats two OpenAI states as broken input. Say whether JS4 refuses to start while `state/seen.json` exists.
- **The injection test's "changes nothing" is not a testable condition.**
  - With no model, the real targets are the JSON writer and the Markdown views: a title containing "|" and a line break can add a row to `summary.md`.
  - Suggested conditions:
    - `notes.json` parses to the same structure, with the planted text only inside its quoted field.
    - The Markdown views escape "|" and line breaks, as `_cell` in `trace.py` does.
    - The planted posting's verdict equals the rules' verdict on the same posting without the planted sentence.
  - Add to "Not claiming" what would happen if Claude later read the notes.
- **A fallback for the two-day run, and a hazard to it.**
  - If day 1's OpenAI fetch fails, the saved 11-20 answer compared with the current 11-09 memory already shows 99 postings listed then gone. That can serve as a labeled replay in a sandbox.
  - Any development run against `state/` before the first JS4 run overwrites the 11-09 memory that the fresh-is-not-true case depends on.

## Matters of taste, not defects
- Withholding every board's memory when one board's blocking claim fails. Doing it per board would waste less work; either is fine if stated.
- Writing a note for every gone posting, including ones FILTER never kept (99 of W1's 102 notes on the 11-20 numbers).
- The exit codes 5 and 6, and their order.
- Each watcher gets GATE.md's 10 requests, which doubles the total per round. W1 needs at most 2 and W2 at most 6, so it does not matter here.

## Sound as written
- The graph has no cycles: every edge goes from a lower step to a higher one. It cannot yet run as written (items 1, 8, 9 and the S7 inputs line).
- The independence paragraph is honest and correct.
- The budget numbers fit the measurements: W1 needs at most 2 requests and W2 at most 6.
- The "never" list and the host and method allow-list are unchanged, and the code enforces them.
- The rule that the premortem is written before the trigger, and the Changes log.
- The fresh-is-not-true premise holds: OpenAI's memory is from 11-09, and 99 of its 811 listed ids were already missing on 11-20.

## The counterexample that should most change the plan
1. The notes file is at v3.
2. W2 reaches S5, re-reads the disk, finds v3 with the SHA-256 it expects, and is paused (or is simply slower) before its rename.
3. W1 reaches S5, finds v3, and writes v4 with its notes.
4. W2 resumes and renames its own v4, built on v3, over W1's.

W1's notes are gone, both traces say "wrote v4", and no step refuses anything. This breaks the claim that both the memory section and the two-watcher section rest on. The plan's own trigger misses it if the pause comes before the comparison rather than after it.

Making the creation of version N+1 itself the check closes the hole: link the new file to `v<N+1>`, and refuse if that name already exists. Because every version then stays on disk, the same change also settles item 7 and the assignment's "state file's versions" deliverable.