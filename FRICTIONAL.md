# FRICTIONAL: Job-Search Agent 1

My log for JS1. Claude Code organized each day's entry from my own messages, picks and commands that day; times are Pacific. The decisions are listed with their commits in [DECISIONS.md](DECISIONS.md).

## Friday 2026-10-30

**What I was working on:** the contract, the watch and the Friday baseline, then my labels, the prompt experiment and the action surfaces.

**What I tried and expected**
- Before starting, I made sure the fictional persona could never touch my real profile (nothing is ever sent or applied for in its name), and I chose a plain name for it: Jane Doe.
- I made the contract's decisions in one batch of four multiple-choice questions (years, titles, wrong versions, failure sentence), comparing how many of the 814 live postings each option would keep, and had Claude Code put them into words before any code existed.

**What happened**
- I ran the tests (53 passed) and the planted mistakes (13 of 13 caught) myself before the watch was committed, then approved the commit and the baseline run: at 02:31 it recorded 814 postings, 0 new.
- Labeling took the most care. I checked how to apply my labeling rule to a posting before labeling it; posting 1 (Product Reliability Engineer) was not a match for me at all, so I labeled it a missing specialty. I labeled all 20 myself: the ten the rule rejects in one confirmation, because part 1 of my rule decides them, and the other ten one by one from their requirement lines.
- I asked whether my picks would change the agent itself. They do not change its rule or its verdicts: they measure how often the rule and Claude agree with me, and they decided which prompt to keep.

**What I took from Claude, and what I changed**
- I accepted the options Claude proposed for the design questions: the contract's four choices, the labeling rule, how the 20 postings are picked, the experiment's one change (the specialty point), keeping the baseline prompt, running live run 2 myself, pushing only after review, and running all three action surfaces for real. My 20 labels were my own reads, with nothing suggested.
- I changed the plan where it did not fit how I work: instead of answering a long question sheet, I made the contract's calls in four multiple-choice questions and had Claude draft the text.
- I set how far Claude could go on its own: commit each step on Friday, but never push or open the PR without me.

**What the day showed, and what is still open**
- The revision I picked went from 8 to 10 out of 10 on the development set, then lost to the baseline on the held-out set, 9 to 10. The posting it missed, 11 (Systems Software Engineer, Silicon Bringup), is one I labeled relevant, while the revision called it a missing specialty. I have not decided whether that label or the specialty point is the one to change.
- The rule misses posting 19, which asks for "5+ years" in a sentence without the word "experience". Both prompts caught it.

**Evidence:** commits e989f8b (the contract) to aaccf0d (the docs); the baseline in `runs/2026-10-30T093102Z/`; my labels in `labels/labels.json`; the experiment in `experiment/`.

**Next:** run live run 2 myself on Saturday, then the sign-off.
