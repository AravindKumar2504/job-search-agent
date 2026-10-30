"""The sampling report and the prompt experiment (the brief's Step 4, parts 1 and 2).

  python3 tools/experiment.py sample [--times 5]        repeated calls, baseline prompt, the 5 development
                                                         postings the rule passes (the other 5 fail on location
                                                         or title, which leaves Claude nothing to weigh)
  python3 tools/experiment.py run PROMPT development     one call per development posting
  python3 tools/experiment.py run PROMPT held_out        only once both development runs exist, and only once
  python3 tools/experiment.py report                     rebuild experiment/SAMPLING.md and EXPERIMENT.md
                                                         from the saved calls alone (offline, no Claude)

Every call is a fresh conversation (a new CLI process, no saved session) and is saved before it is counted.
An answer the validator rejects counts as a miss. Labels come from labels/labels.json, paired by posting id.
"""

from __future__ import annotations

import difflib
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from job_agent import claude_judge, rule  # noqa: E402
from job_agent import resume as resume_mod  # noqa: E402

EXPERIMENT = REPO / "experiment"
BASELINE_RESPONSE = REPO / "runs" / "2026-10-30T093102Z" / "response.json"
SETS = ("development", "held_out")
Z = 1.96  # 95% Wilson interval

# The written conclusions. Drafted by Claude Code from the saved calls on 2026-10-30; the calls never change
# (the tool refuses to re-run a set), so the numbers they cite stay true.
SAMPLING_CONCLUSIONS = (
    "Repeating a verdict shows repeatability, not correctness. Postings 1 and 4 got \"relevant\" on all five tries, "
    "and my label says \"not_relevant\" (a required specialty Jane lacks): the prompt applies its seven checks the "
    "same way every time, and those checks say nothing about specialties. Postings 7 and 8 got my label's verdict on "
    "all five tries.\n\n"
    "The variation that did appear was in the format, not the verdict. Three of the five replies on posting 5 held "
    "two answers: a first JSON object saying \"not_relevant\" with a confused justification, then a line beginning "
    "\"Correction\", then a second object saying \"relevant\". The validator rejected all three as not one JSON "
    "object, as the contract requires, so they count as no valid judgment; a looser parser would have kept one of "
    "the two answers without saying so. Both valid replies on posting 5 matched my label.\n\n"
    "What these 25 calls cannot show: five tries per posting cannot pin down a rate (3 of 5 has a 95% Wilson interval "
    "of 23% to 88%); the five postings come from one board on one day, chosen because the rule passes them, not at "
    "random; and another model, prompt or day could behave differently. Agreement with my label is agreement with "
    "one person's reading."
)
EXPERIMENT_CONCLUSIONS = (
    "On the development set the revision scored 10 of 10 and the baseline 8 of 10. That gain was expected: the one "
    "change was chosen after seeing the baseline's two development misses (postings 1 and 4, both labeled as a "
    "missing specialty), so the development set is no longer a fair test of it.\n\n"
    "On the held-out set, run once per prompt after both development runs, the order reversed: the baseline scored "
    "10 of 10 and the revision 9 of 10. The revision's one held-out miss is posting 11 (Systems Software Engineer, "
    "Silicon Bringup), which it judged a missing specialty (\"it asks for silicon bringup and validation\"); I "
    "labeled it relevant. Whether that is the prompt's error, or a posting my own labeling rule's specialty part "
    "would also reject, is a question about the label that this run cannot settle.\n\n"
    "The rule (a record) scored 8 of 10 and 9 of 10. Its held-out miss is posting 19, whose requirement \"5+ years "
    "in one or more of: ML systems, performance engineering, distributed systems, or HPC.\" never says "
    "\"experience\", so check 7 as written skips it. Both prompts called it not relevant; the baseline's reply cites "
    "the \"5+ years\". The majority class scored 7 of 10 and 6 of 10.\n\n"
    "How little ten cases show: one posting moves a pass rate by 10 points; every interval above overlaps the "
    "others; and each prompt answered each posting once, while the sampling report shows that a single reply can "
    "break the format. This experiment cannot say that either prompt is better. It does show the specialty point "
    "flipping verdicts in both directions on real postings.\n\n"
    "Disclosure: Claude Code read the held-out postings' text and my held-out labels while preparing my labeling "
    "questions, before any Claude judge call. I chose the one change from the development results, and the "
    "held-out set ran only after both development runs, as tools/experiment.py enforces."
)


def load():
    jobs = {j["id"]: j for j in json.loads(BASELINE_RESPONSE.read_bytes())["jobs"]}
    labels = json.loads((REPO / "labels" / "labels.json").read_text(encoding="utf-8"))["labels"]
    jane = resume_mod.load(REPO / "persona" / "jane-doe.json")
    return jobs, labels, jane


def sampling_postings(jobs, labels, jane):
    return [l for l in labels if l["set"] == "development" and rule.judge(jobs[l["id"]], jane)["verdict"] == "relevant"]


def call(posting, jane, prompt: Path, folder: Path, label: str, model: str):
    verdict = claude_judge.judge(posting, jane, prompt_path=prompt, record_dir=folder, model=model, label=label)
    print(f"  {label}: {verdict['verdict'] or 'no valid judgment'}"
          + ("" if verdict["valid"] else f" ({verdict.get('reason', '')[:120]})"))
    return verdict


def sample(times: int, model: str) -> int:
    jobs, labels, jane = load()
    folder = EXPERIMENT / "sampling"
    if folder.exists():
        print(f"refused: experiment/{folder.name} exists; saved calls are never replaced")
        return 3
    for item in sampling_postings(jobs, labels, jane):
        print(f"posting {item['n']}: {item['title']}")
        for attempt in range(1, times + 1):
            call(jobs[item["id"]], jane, REPO / "prompts" / "baseline.txt", folder, f"n{item['n']:02d}-try{attempt}", model)
    return 0


def run(prompt: Path, part: str, model: str) -> int:
    if part not in SETS:
        print(f"the set must be one of {SETS}")
        return 2
    prompt = prompt if prompt.is_absolute() else (REPO / prompt)
    folder = EXPERIMENT / f"{prompt.stem}-{part}"
    if folder.exists():
        print(f"refused: experiment/{folder.name} exists; each prompt runs on each set once")
        return 3
    if part == "held_out":
        developed = sorted(p.name[: -len("-development")] for p in EXPERIMENT.glob("*-development"))
        if "baseline" not in developed or len(developed) != 2 or prompt.stem not in developed:
            print("refused: the held-out set runs only after the baseline and exactly one revision ran on the "
                  f"development set, and only for those two prompts (found: {developed})")
            return 3
    jobs, labels, jane = load()
    print(f"{prompt.name} on the {part} set:")
    for item in (l for l in labels if l["set"] == part):
        call(jobs[item["id"]], jane, prompt, folder, f"n{item['n']:02d}", model)
    return 0


# Reports, from the saved calls only.

def wilson(k: int, n: int):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denominator = 1 + Z * Z / n
    centre = (p + Z * Z / (2 * n)) / denominator
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / denominator
    return (max(0.0, centre - half), min(1.0, centre + half))


def records(folder: Path):
    found = []
    for path in sorted(folder.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        answer = None
        if data.get("validation", {}).get("valid"):
            answer = json.loads(data["answer_text"])
        found.append({"file": f"{folder.name}/{path.name}", "label": data.get("label", ""), "id": data["posting_id"],
                      "answer_text": data.get("answer_text") or "",
                      "valid": data.get("validation", {}).get("valid", False), "verdict": (answer or {}).get("verdict"),
                      "justification": (answer or {}).get("justification"), "model": data.get("model"),
                      "date": (data.get("started_at") or "")[:10], "problems": data.get("validation", {}).get("problems", []),
                      "prompt_sha256": data.get("prompt", {}).get("sha256")})
    return found


def pct(k, n):
    return f"{k}/{n} ({100 * k / n:.0f}%)" if n else "0/0"


def interval(k, n):
    low, high = wilson(k, n)
    return f"{100 * low:.0f}% to {100 * high:.0f}%"


def sampling_report(jobs, labels, jane) -> str:
    folder = EXPERIMENT / "sampling"
    calls = records(folder) if folder.exists() else []
    by_id = {l["id"]: l for l in labels}
    out = ["# Sampling report", "",
           "Generated by `python3 tools/experiment.py report` from the saved calls in `experiment/sampling/`.", "",
           "The baseline prompt contract (`prompts/baseline.txt`), asked about the same posting in fresh "
           "conversations: each call is a new Claude Code process with no saved session. The postings are the five "
           "development postings the rule passes; the other five fail on location or title, which leaves Claude "
           "nothing to weigh. Every verdict is Claude's judgment, compared with my hand label.", "",
           "| # | Posting | My label | Claude's verdicts, in order | Same as my label | Unanimous |",
           "|---|---|---|---|---|---|"]
    total = same = unanimous = 0
    for item in sampling_postings(jobs, labels, jane):
        mine = [c for c in calls if c["id"] == item["id"]]
        said = [c["verdict"] or "invalid" for c in mine]
        agree = sum(1 for s in said if s == item["label"])
        total, same = total + len(said), same + agree
        unanimous += len(set(said)) == 1
        out.append(f"| {item['n']} | {item['title']} | {item['label']} | {', '.join(said)} | {agree} of {len(said)} | "
                   f"{'yes' if len(set(said)) == 1 else 'no'} |")
    models = sorted({c["model"] for c in calls if c["model"]})
    dates = sorted({c["date"] for c in calls})
    out += ["", f"Calls: {len(calls)} ({', '.join(models) or 'no model'}; {', '.join(dates) or 'no date'}). "
            f"Invalid answers: {sum(1 for c in calls if not c['valid'])}. "
            f"Same as my label: {pct(same, total)}. Postings with one verdict on every try: {unanimous} of "
            f"{len(sampling_postings(jobs, labels, jane))}.", ""]
    out += ["## Each justification, as received", ""]
    for c in calls:
        item = by_id[c["id"]]
        said = c["justification"] or ("; ".join(c["problems"]) + ". The reply, as received, begins: "
                                      + json.dumps(c["answer_text"][:160]) + " and later says: "
                                      + json.dumps(_correction(c["answer_text"])))
        out.append(f"- `{c['label']}` (posting {item['n']}, {c['date']}): **{c['verdict'] or 'no valid judgment'}**. {said}")
    out += ["", "## What this shows, and what it cannot", "", SAMPLING_CONCLUSIONS, ""]
    return "\n".join(out)


def _correction(text: str) -> str:
    at = text.find("Correction")
    return text[at: at + 120] if at >= 0 else "(no correction line)"


def experiment_report(jobs, labels, jane) -> str:
    runs = {}
    for part in SETS:
        for folder in sorted(EXPERIMENT.glob(f"*-{part}")):
            runs[(folder.name[: -len(f"-{part}")], part)] = records(folder)
    prompts = sorted({stem for stem, _ in runs}, key=lambda s: (s != "baseline", s))
    out = ["# Prompt experiment", "",
           "Generated by `python3 tools/experiment.py report` from the saved calls in `experiment/<prompt>-<set>/`.", "",
           "My 20 hand labels (`labels/labels.json`) are the answer key. Each prompt was asked once per posting; a "
           "pass is a valid answer equal to my label, and an answer the validator rejected counts as a miss. The "
           "majority-class baseline answers `not_relevant` every time. The rule's record is computed from the same "
           "postings for comparison.", ""]
    for part in SETS:
        mine = [l for l in labels if l["set"] == part]
        n = len(mine)
        majority = sum(1 for l in mine if l["label"] == "not_relevant")
        rule_ok = sum(1 for l in mine if rule.judge(jobs[l["id"]], jane)["verdict"] == l["label"])
        out += [f"## {'Development' if part == 'development' else 'Held-out'} set ({n} postings: "
                f"{n - majority} relevant, {majority} not relevant by my labels)", "",
                "| Judge | Pass rate | 95% Wilson interval |", "|---|---|---|",
                f"| Majority class (always not_relevant) | {pct(majority, n)} | {interval(majority, n)} |",
                f"| Rule (record) | {pct(rule_ok, n)} | {interval(rule_ok, n)} |"]
        for stem in prompts:
            calls = runs.get((stem, part))
            if calls is None:
                out.append(f"| Claude, {stem} prompt | not run | |")
                continue
            ok = sum(1 for l in mine for c in calls if c["id"] == l["id"] and c["verdict"] == l["label"])
            invalid = sum(1 for c in calls if not c["valid"])
            out.append(f"| Claude, {stem} prompt | {pct(ok, n)}{f', {invalid} invalid' if invalid else ''} | {interval(ok, n)} |")
        out += ["", "| # | Posting | My label | Rule | " + " | ".join(f"Claude, {s}" for s in prompts) + " |",
                "|---|---|---|---|" + "---|" * len(prompts)]
        for l in mine:
            row = [str(l["n"]), l["title"], l["label"], rule.judge(jobs[l["id"]], jane)["verdict"]]
            for stem in prompts:
                calls = runs.get((stem, part)) or []
                c = next((c for c in calls if c["id"] == l["id"]), None)
                row.append("not run" if c is None else (c["verdict"] or "invalid"))
            out.append("| " + " | ".join(row) + " |")
        out.append("")
    revisions = [s for s in prompts if s != "baseline"]
    if revisions:
        diff = difflib.unified_diff((REPO / "prompts" / "baseline.txt").read_text(encoding="utf-8").splitlines(),
                                    (REPO / "prompts" / f"{revisions[0]}.txt").read_text(encoding="utf-8").splitlines(),
                                    "prompts/baseline.txt", f"prompts/{revisions[0]}.txt", lineterm="", n=0)
        out += ["## The one change", "", "```diff", *diff, "```", ""]
    out += ["## What this shows, and what it cannot", "", EXPERIMENT_CONCLUSIONS, ""]
    return "\n".join(out)


def report() -> int:
    jobs, labels, jane = load()
    (EXPERIMENT / "SAMPLING.md").write_text(sampling_report(jobs, labels, jane), encoding="utf-8")
    (EXPERIMENT / "EXPERIMENT.md").write_text(experiment_report(jobs, labels, jane), encoding="utf-8")
    print("wrote experiment/SAMPLING.md and experiment/EXPERIMENT.md")
    return 0


def main(argv) -> int:
    model = argv[argv.index("--model") + 1] if "--model" in argv else claude_judge.DEFAULT_MODEL
    if argv[:1] == ["sample"]:
        return sample(int(argv[argv.index("--times") + 1]) if "--times" in argv else 5, model)
    if argv[:1] == ["run"] and len(argv) >= 3:
        return run(Path(argv[1]), argv[2], model)
    if argv[:1] == ["report"]:
        return report()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
