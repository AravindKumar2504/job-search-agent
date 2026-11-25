# The JS4 file formats

Written on 2026-11-25, after PLAN.md v1.0 was approved and before any JS4 code. These are the files a
JS4 run (`python3 -m job_agent search`) writes and reads. The independent checker, `tools/check_claims.py`, is built
from this file, PLAN.md and GATE.md's field mapping alone, never from the agent's code, so its readers are its own.

All JSON is UTF-8. Times are UTC, ISO 8601, ending in `Z`. A SHA-256 is lower-case hex of the exact bytes named.

## A run folder: `runs/<run id>/`

The run id is `YYYY-MM-DDTHHMMSS.ffffffZ-<worker>`, for example `2026-11-26T150000.123456Z-W1`.

| File | What it holds |
|---|---|
| `trace.jsonl` | one JSON object per line: `{"at": <time>, "event": <name>, ...}` (events below) |
| `boards/<system>-<name>/attempt-<n>.json.gz` | a board's answer, byte for byte, gzip-compressed; the SHA-256 is of the uncompressed bytes |
| `boards/<system>-<name>/attempt-<n>.meta.json` | `url`, `status`, `received_at`, `bytes`, `sha256`, `retry`, `source`, `body_file` |
| `diff.json` | S3's result (below) |
| `verdicts.json` | S4's records (below) |
| `summary.json`, `summary.md` | S5's summary (below); the Markdown is a view of the JSON |
| `evidence.json`, `evidence.md` | the checker's output, written by the watcher |
| `report.json`, `report.md` | S9's report: the exit first |

### Trace events the checker may read

| Event | Fields |
|---|---|
| `run_start` | `run_id`, `worker`, `source` ("live", "replay of runs/<id>", "seeded: ...", "staged: ..."), `plan_version`, `budgets`, `code_sha256`, `git_head` |
| `memory_read` | `board` (`<system>-<name>`), `version` (0 for the schema-2 file), `file` (repo-relative), `sha256` |
| `notes_read` | `version`, `file`, `sha256` |
| `answer` | `board`, `attempt`, `status`, `bytes`, `sha256`, `file` (repo-relative path of the `.json.gz`) |
| `no_answer` | `board`, `attempt`, `why`, `transient` |
| `board_status` | `board`, `status` ("read", "unverified", "not visited"), `reason`, `attempt` (the attempt that was read, when read) |
| `filter` | `filter_version` ("1.1"), `section7_sha256` |
| `checker` | `checker_sha256`, `exit`, `output_sha256`, `seconds` |
| `notes_write`, `memory_write` | `version` created, or `refused` with the version that already existed |
| `exit` | `status`, `code`, `reasons` |

The answer that counts for a board is the attempt named by its `board_status` event.

## `summary.json` (S5)

```json
{
  "run_id": "2026-11-26T150000.123456Z-W1",
  "worker": "W1",
  "source": "live",
  "boards": [
    {
      "board": "ashby-openai",
      "status": "read",
      "reason": "",
      "answer_sha256": "<sha256 of the answer read>",
      "memory_version_read": 0,
      "memory_sha256_read": "<sha256 of that memory file>",
      "counts": {"postings": 860, "new": 42, "gone": 150, "kept": 90, "rejected": 768, "cannot_tell": 2}
    }
  ],
  "claims": [
    {
      "board": "ashby-openai",
      "posting_id": "<id>",
      "title": "<as posted>",
      "new": true,
      "live": true,
      "location": {"category": "preferred", "places": ["San Francisco"]},
      "work_authorization": {"sentences": ["<sentence as posted>"], "r5_phrases_found": false},
      "pay": {"sentence": "<sentence as posted>", "amounts": [230000, 385000], "currency": "USD"}
    }
  ],
  "gone": [
    {"board": "ashby-openai", "posting_id": "<id>", "title": "<as last listed>", "last_seen_run": "<run id>"}
  ]
}
```

- `boards` lists every board of the watcher. For a board that is not "read", `counts` is `null`.
- `claims` holds one entry per **new kept** posting. `location.category` is one of "preferred", "other US",
  "US remote", "cannot tell". `pay` is `null` when no pay sentence was found. `work_authorization.sentences` lists the
  sentences the producer found about status, sponsorship or export control, word for word from the posting's text.
- `gone` holds one entry per gone posting.
- In a replay, `live` is replaced by `"listed_on": "<date of the replayed answer>"`.

## `diff.json` (S3) and `verdicts.json` (S4)

- `diff.json`: `{"boards": {"<board>": {"memory_version": N, "new": [<id>...], "gone": [<id>...], "listed": [<id>...]}}}`.
- `verdicts.json`: `{"filter_version": "1.1", "section7_sha256": "...", "records": [{"board", "id", "title", "fate"
  ("kept", "rejected", "cannot_tell"), "failed_rules", "score", "rules": [{"rule", "result", "quote"}]}]}`.

## The memory: `state/<system>-<name>.v<N>.json` (schema 3)

Version 0 is the old-format file, `state/<system>-<name>.json` (schema 2: `seen_ids`, `last_run` with `posting_ids`
and `titles`, `runs`). Versions 1 and up:

```json
{
  "schema": 3,
  "system": "ashby",
  "name": "openai",
  "version": 1,
  "written_by": "<run id>",
  "written_at": "<time>",
  "previous_version": 0,
  "previous_sha256": "<sha256 of the version-0 file>",
  "source": "live",
  "seen": {
    "<id>": {"first_seen_run": "<run id>", "first_seen_answer_sha256": "<sha256 or null>",
             "label": "answer | rebuilt from runs/<run id> | carried over from schema 2"}
  },
  "runs": [
    {"run_id": "<run id>", "source": "live", "started_at": "<time>", "answer_sha256": "<sha256>",
     "postings": 860, "listed_ids": ["<id>"], "titles": {"<id>": "<title>"}}
  ]
}
```

- A version never changes once it exists. A board's memory is its highest version.
- `runs` is in order, oldest first, and each entry's `listed_ids` is stored once and never changed. Entries carried
  over from version 0 have `listed_ids` only for version 0's last run; older ones keep their counts only.
- An id is **listed in a version** when it is in the `listed_ids` of the version's last run that has `listed_ids`
  (for version 0: `last_run.posting_ids`). It is **seen** when it is a key of `seen` (version 0: in `seen_ids`).

## The notes: `state/notes.v<N>.json` (schema 1)

```json
{
  "schema": 1,
  "version": 3,
  "written_by": "<run id, or null for version 0>",
  "written_at": "<time>",
  "previous_sha256": "<sha256 of version 2, or null>",
  "notes": [
    {"key": "ashby-openai|<posting id>|gone|<last seen run>", "board": "ashby-openai", "posting_id": "<id>",
     "kind": "gone", "last_seen_run": "<run id>", "run": "<run id that wrote it>", "worker": "W1",
     "source": "memory v0 and answer <sha256>", "quoted": {"title": "<text as posted>"}}
  ]
}
```

- `kind` is "new kept", "new cannot tell" or "gone"; `last_seen_run` is "" unless the kind is "gone".
- Text from a posting appears only inside `quoted`. Notes are never read as instructions by any step.

## `evidence.json` (the checker's output)

The checker prints this JSON on its standard output; the watcher writes it to `evidence.json`.

```json
{
  "checker": "tools/check_claims.py",
  "run_id": "<run id>",
  "results": [
    {"claim": "<name>", "board": "<board>", "posting_id": "<id or null>", "claimed": <value>, "found": <value>,
     "result": "pass | fail | not checked", "blocking": true, "why": "<one line>", "source": "<file read>"}
  ],
  "blocking_failed": 0,
  "blocking_not_checked": 0
}
```

Claim names: `board status`, `counts.postings`, `counts.new`, `counts.gone`, `counts.kept+rejected+cannot_tell`,
`new`, `gone`, `live`, `location`, `work authorization`, `pay`. Blocking: the first eight. Exit codes of the checker:
0 when every blocking claim passed, 1 when one failed or was not checked, 2 when the run folder cannot be read.
