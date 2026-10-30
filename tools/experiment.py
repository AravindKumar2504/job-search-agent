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
        out.append(f"- `{c['label']}` (posting {item['n']}, {c['date']}): **{c['verdict'] or 'no valid judgment'}**. "
                   + (c["justification"] or "; ".join(c["problems"])))
    out.append("")
    return "\n".join(out)


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
