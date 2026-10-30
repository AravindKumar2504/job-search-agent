# Sources

## How the work was split

The contract came first. I made its calls: the board, the persona, the rule's years and title choices, the four wrong versions and the failure sentence, picking each rule option after seeing how many live postings it kept. Claude Code laid out the options and put my calls into words, and CONTRACT.md was committed before any code existed. Only then did Claude Code write the code, the tests and the other documents against it.

The same holds for the rest: every decision is mine and is logged with its commit in [DECISIONS.md](DECISIONS.md); Claude Code proposed the options for each, wrote the code, tests, tools and documents, and ran every command not listed as mine.

## What Claude Code did, specifically

- Before the contract: fetched the board once with `curl` (not kept) to count postings for the options it offered me, and checked every "sponsor", "citizen", "export" and "ITAR" phrase on it.
- Wrote the agent (`job_agent/`), its 92 tests, the 30 planted mistakes in `tools/mutants.py`, and the other tools.
- Wrote Jane Doe's résumé to match the contract's fields.
- Ran the Friday baseline at my word, and every Claude call in `experiment/` (68 on 2026-10-30).
- Prepared the labeling excerpts. While doing so it read the held-out postings and my held-out labels, before any Claude judge call; the experiment report says so.
- Drafted CONTRACT.md, LABELING-RULE.md, ACTION-SURFACE.md, the experiment reports' conclusions and this file from my decisions and the saved results.

## What I used

- The JS1 brief, in the course repo (`assignments/assignment-js1-the-contract-and-the-watch.md`).
- OpenAI's public job board on Ashby's posting API, `https://api.ashbyhq.com/posting-api/job-board/openai`.
- The Claude Code CLI 2.1.309, signed in with my claude.ai seat (no API key), model `claude-sonnet-5-5`.
- The Reallocation Engine (Nik Bear Brown, MIT license): Jane Doe's résumé layout is adapted from `search/examples/priya-nair/resume.example.json`.
- Klaxon, my own project (github.com/AravindKumar2504/klaxon): the locked-down Claude Code adapter (`src/klaxon/agent/claude_code.py`: the lockdown flags, the checks on Claude Code's init event, the small environment, the fullwidth at sign) and the mutation runner (`scripts/mutation_check.py`: exact text swaps on a copy) were adapted here. The stream-json event shapes the tests copy come from a recorded Klaxon call of 2026-10-21.
- Ideas, not code, from a friend's job-tracker kit (not public): the first pull of a board reports nothing new; the counts line shows even when nothing is new; every id seen is recorded.
- The Wilson score interval, the standard formula for a binomial proportion.
