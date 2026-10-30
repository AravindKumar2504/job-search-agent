# FRICTIONAL: Job-Search Agent 1

My log for JS1. Claude Code organized each day's entry from my own messages, picks and commands that day; times are Pacific. The decisions are listed with their commits in [DECISIONS.md](DECISIONS.md).

## Friday 2026-10-30

**What I was working on:** the contract, the watch and the Friday baseline, then my labels, the prompt experiment and the action surfaces.

**What I tried and expected**
- Before starting, I asked whether the fictional persona would affect my own profile in any way, and whether it could have a plain name like Jane Doe. It cannot (nothing is ever sent or applied for in its name), and Jane Doe is the name.
- I wanted AI to draft the contract, and a long question sheet felt like too many questions. Instead I made the contract's decisions in one batch of four multiple-choice questions (years, titles, wrong versions, failure sentence), each option showing how many of the 814 live postings it would keep.
- I asked that the contract read as mine, because its decisions are mine. SOURCES.md says the contract came first, that I made its calls, and that Claude Code put them into words.

**What happened**
- I ran the tests (53 passed) and the planted mistakes (13 of 13 caught) myself before the watch was committed, then said "commit and run": the baseline at 02:31 recorded 814 postings, 0 new.
- Labeling is where I got stuck. I asked what I should do, then asked Claude to do the labels for me. It said the labels have to be mine, because they are the answer key Claude is graded against, and made labeling faster instead: one confirmation for the ten postings the rule rejects, and each of the other ten with its requirement lines shown word for word. Posting 1 (Product Reliability Engineer) seemed not a match for me at all; I labeled it a missing specialty.
- I asked whether my picks would change the agent. They do not change its rule or its verdicts: they measure how often the rule and Claude agree with me, and they decided which prompt to keep.
- I thought questions were being skipped. When I typed a message while a batch of questions was open, the app closed the batch; each batch came back, and nothing was lost.

**What I took from Claude, and what I changed**
- On every design question I picked the option Claude marked as recommended: the contract's four choices, the labeling rule, how the 20 postings are picked, the experiment's one change (add the specialty point), keeping the baseline prompt, running live run 2 myself, pushing only on Saturday after review, and running all three action surfaces for real. My labels were my own reads; no label was suggested to me.
- I changed how the work is credited: the contract reads as mine, and I had a line removed from SOURCES.md and the rest reworded so it says the contract came first.
- I let Claude Code commit each step on Friday without asking each time; pushes and the PR still wait for me.

**What the day showed, and what is still open**
- The revision I picked went from 8 to 10 out of 10 on the development set, then lost to the baseline on the held-out set, 9 to 10. The posting it missed, 11 (Systems Software Engineer, Silicon Bringup), is one I labeled relevant, while the revision called it a missing specialty. I have not decided whether that label or the specialty point is the one to change.
- The rule misses posting 19, which asks for "5+ years" in a sentence without the word "experience". Both prompts caught it.

**Evidence:** commits e989f8b (the contract) to aaccf0d (the docs); the baseline in `runs/2026-10-30T093102Z/`; my labels in `labels/labels.json`; the experiment in `experiment/`.

**Next:** run live run 2 myself on Saturday, then the sign-off.
