# My verification of review 1

The reviewer's text is in [REVIEW-1.md](REVIEW-1.md). Claude Code summarized its twelve real problems for me in chat
on 2026-11-25, and checked the factual claims it could against the code and the saved runs: the permission module
refuses `boards-w1.json` and `FILTER.md`; every writer uses the same temporary file name; run ids go only to the
second; OpenAI's memory holds 907 seen ids and 811 listed; Verkada posting 5302623007 says "This role does not offer
visa sponsorship." and none of R5's sponsorship phrases matches it; R2's quote "London, UK; Munich, Germany; Paris,
France" is not in that posting's text. All of those held. My decisions and reasons are below, word for word as I sent
them on 2026-11-25. What each one changed is in PLAN.md v1.0, under "Changes".

## The twelve problems

1. A — Two writers must not be able to overwrite the same version; creating the version file exclusively prevents the lost update.
2. A — Notes should only be written after checks pass, and refused notes must not leave inconsistent board memory.
3. A — Approval must happen before any new-format write, and migration must never silently drop existing IDs.
4. A — Replays and planted runs must use isolated copies so they cannot overwrite live data.
5. A — Checks need independent, accurate patterns; otherwise they repeat the filter’s mistakes and miss important cases.
6. A — Deliberately staging overlapping runs is necessary to test whether stale memory writes are actually refused.
7. A — Keeping every memory version and committing state preserves the evidence needed to reproduce and review past runs.
8. A — The permission module must allow the plan to read its required files, with any expanded access documented.
9. A — Quote verification must account for mapped fields, joined location values, and extracted HTML text.
10. A — Run IDs need enough uniqueness to prevent simultaneous watchers from colliding.
11. A — Crashes, unchecked blocking claims, unchanged retries, and missing reports must all have explicit failure outcomes.
12. A — Each budget needs one clear owner, and exceeding the notes limit must stop the run without writing partial results.

**My qualification on item 3:** "I accept that approval is checked too late and that migration must not silently drop
IDs. However, approval is essential before the first write or migration—not necessarily before a strictly read-only
fetch. Requiring approval before fetching is a more conservative design choice."

So the plan checks for the approval before the first write to `state/`, not before the fetch: a run without it may
fetch, diff, filter and check, and then stops before it writes any note or memory.

## The smaller problems and the matters of taste

Claude Code told me it would take the review's smaller fixes unless I objected, and I did not: FILTER.md pinned to
v1.1 with the SHA-256 of its own Section 7; GATE.md's repeat rule kept (a repeated board is skipped and reported);
each run's listed ids stored once and never changed; ids carried over from the old memory format labeled with the
run that first saw them, rebuilt from the saved answers, or "carried over from schema 2"; a board with no answer at
all handled at S2; JS4 refusing to start while JS1's `state/seen.json` exists; testable conditions for the injection
case; the fallback for the two-day run; and no development run against the live `state/`. The four matters of taste
stay as version 0.1 had them.

*Aravind, 2026-11-25. My decisions and reasons are mine, word for word; Claude Code wrote the first paragraph, this
section's list and the sentence after my qualification.*
