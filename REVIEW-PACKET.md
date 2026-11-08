# Review packet: the years rule misses posting 19

One non-trivial change I asked Claude Code to make, reviewed the way the JS2 brief asks: the bug reproduced, my test written before the patch, the diff read as a change in behavior, whether it stayed in scope, the commands I ran myself, and my decision with the evidence. Text marked as mine is my own, sent in chat and copied word for word; Claude Code adds the facts, commands and outputs around it.

## 1. The bug

Contract v0.1, check 7, reads years of experience only in sentences that contain the word "experience". Posting 19 of my JS1 labels, OpenAI's "Software Engineer, Workload Enablement" (`9efcef02-0515-4672-bace-81329944b38b`), states its requirement without that word:

> - 5+ years in one or more of: ML systems, performance engineering, distributed systems, or HPC.

So the rule reads no years at all and calls the posting relevant for Jane Doe, who has 3. This miss was first noted in JS1 (js1/FRICTIONAL.md, Friday entry).

## 2. Reproduced (2026-11-08, 5:24 PM ET, by me)

```text
python3 tools/explain_rule.py runs/2026-10-30T093102Z/response.json 9efcef02-0515-4672-bace-81329944b38b
```

Output (as logged in MY-CHECKS.md): "Rule verdict (record): relevant" and "Check 7 (years of experience): passes. Posting descriptionPlain states no years of experience, which is not a requirement".

**What I ran and saw (mine):** Running explain_rule.py on posting 19 from the October 30 saved answer showed that the rule marked it relevant because check 7 only checks sentences containing the word "experience" and missed the actual requirement of "5+ years". Consequently, the agent failed to catch that Jane only has 3 years of experience and incorrectly let the posting pass.

## 3. My prediction, before any count (2026-11-08, 5:40 PM ET)

The question: of the 95 postings my rule calls relevant on the 2026-10-30 baseline (814 postings), how many flip to not relevant once years are also read outside "experience" sentences?

**My guess (mine):** I guess 12, because while 60 total postings state years without the word "experience", most of those are already rejected by earlier checks on job title or level.

## 4. How years should be read (contract v0.2): to come

## 5. My test, written before the patch: to come

## 6. The patch, and the diff read as a change in behavior: to come

## 7. Scope: to come

## 8. Commands I ran myself: to come

## 9. My decision (accept, revise or reject) and the evidence: to come

## 10. One case my test would still miss: to come
