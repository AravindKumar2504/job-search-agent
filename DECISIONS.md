# My decisions for JS1

Every choice below was mine, made in the Claude Code app on 2026-10-30 (Pacific time), most of them as multiple-choice picks among options Claude Code laid out. Times are approximate. The commit that applied each one is named, so the split between what I decided and what Claude Code did can be checked in the history. Conversation transcripts stay on my machine, as the brief asks; this log is the record instead.

| When (PT) | Decision | Applied in |
|---|---|---|
| 10/30, earlier chat | The board: OpenAI on Ashby, after comparing it with Databricks. The persona Jane Doe: my situation, none of my identity. Python standard library only. Claude through Claude Code on my seat, no API key. | CONTRACT.md, persona/ |
| 01:45 | Contract picks: up to 3 years and a posting that states no years passes; software-engineering titles; all four wrong versions; the watch failure sentence. | e989f8b |
| 01:50 | Framing: the contract reads as mine, and SOURCES.md says Claude Code wrote the wording from my decisions. | e989f8b, SOURCES.md |
| 01:58 | "Commit it": CONTRACT.md is the first commit. | e989f8b |
| 02:26 to 02:31 | I ran the tests (53 passed) and the planted mistakes (13 of 13 caught) myself. | 304c0a0 |
| 02:31 | "Yes, commit and run": the watch committed, then the Friday baseline. | 304c0a0, 629a279 |
| 02:40 | Claude Code may commit each step on 10/30 without asking each time; pushes and the PR still need me. | all later commits |
| 02:40 | Labeling rule: the seven checks plus seniority in words; a required specialty Jane lacks makes a posting not relevant; 20 engineering postings, 10 + 10 by the rule, seed 7375. | b6b2b13 |
| 03:05 to 03:15 | My 20 hand labels: one pick per posting for the ten the rule passes, read from their requirement lines and the sheet; one confirmation for the ten the rule rejects, which part 1 of my labeling rule decides. | 882909e |
| 03:27 | The prompt experiment's one change: add the specialty point. | 117b177 |
| 03:32 | The agent keeps the baseline prompt; I run live run 2 myself on Saturday; GitHub waits for Saturday, after review; the action surfaces are run for real, all three. | bc2bf6f |
