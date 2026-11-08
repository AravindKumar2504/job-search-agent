# Boundary tests: the permission policy (GATE.md)

The 19 cases test the permission policy in GATE.md v1.0: which hosts, paths and methods a request may use, where the agent may write and read, and which writes need my `--approve`.

**My predictions** are the words I typed in chat on 2026-11-08 at 4:50 PM ET, before any boundary test was written or run: allow (it goes ahead), refuse (it is blocked), or approval (it is blocked unless I pass `--approve`). Claude Code wrote the 19 cases on 2026-11-07 and this table; the predictions are mine, copied word for word. The Actual column comes later, from running `tests/test_boundary.py`.

| # | Action | My prediction | Actual | Match |
|---:|---|---|---|---|
| 1 | GET `https://evil.example/posting-api/job-board/openai` | refuse | (not run yet) | |
| 2 | GET `https://api.lever.co.evil.example/v0/postings/palantir?mode=json` | refuse | (not run yet) | |
| 3 | GET `https://api.lever.co@evil.example/v0/postings/palantir?mode=json` | refuse | (not run yet) | |
| 4 | GET `http://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true` (http) | refuse | (not run yet) | |
| 5 | GET `https://api.lever.co/v0/postings/palantir/abc123/apply` | refuse | (not run yet) | |
| 6 | POST `https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true` | refuse | (not run yet) | |
| 7 | GET `https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true` | allow | (not run yet) | |
| 8 | api.lever.co answers with a redirect to another host | allow | (not run yet) | |
| 9 | Write `runs/../persona/jane-doe.json` | refuse | (not run yet) | |
| 10 | Write `runs-evil/report.md` (a folder beside `runs/`) | refuse | (not run yet) | |
| 11 | Write `runs/out-link/report.md`, where `out-link` is a symlink to a folder outside the repo | refuse | (not run yet) | |
| 12 | Write `/tmp/report.md` | refuse | (not run yet) | |
| 13 | Read `persona/jane-doe.json` | allow | (not run yet) | |
| 14 | Write `persona/jane-doe.json` | refuse | (not run yet) | |
| 15 | Write the first state for a board that has none (`state/greenhouse-verkada.json`) | allow | (not run yet) | |
| 16 | Add newly seen ids to a board's existing state, removing none | allow | (not run yet) | |
| 17 | Replace a board's state with one that drops ids, without `--approve` | approval | (not run yet) | |
| 18 | Same as 17, with `--approve "reason"` | allow | (not run yet) | |
| 19 | Delete a board's state file, without `--approve` | approval | (not run yet) | |
