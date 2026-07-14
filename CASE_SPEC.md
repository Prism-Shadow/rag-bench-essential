# Case Authoring Spec (env / payload / eval)

This spec defines how to add a new case to this lab so that every coding-agent
runtime runs the same task under the same conditions, and so grading stays
honest and leak-free. It generalizes the conventions already used by the
hard-tier cases (see `spider2lite_f1_overtake_audit_hard` as the worked example
in Section 9).

A case is organized as three orthogonal pieces:

| Piece | Question it answers | On disk | Agent sees it? |
| --- | --- | --- | --- |
| **payload** | What is the task, and what data is given? | `task.md` + `data/` | Yes |
| **env** | What runtime / services does the agent act in? | `env.md` (or `env/`) | Yes (setup only) |
| **eval** | What is the gold answer, and how is it graded? | `truth/` | **Never** |

The hard rule that makes results trustworthy: **only payload and env are copied
into a workspace; `truth/` (eval) is never staged.** Grading runs externally
against `BENCH_TRUTH_DIR`. See `RUN_PROTOCOL.md`.

---

## 1. Canonical Directory Layout

```text
cases/<case_id>/
├── task.md                 # PAYLOAD: the task brief (agent-visible)
├── data/                   # PAYLOAD: input data (agent-visible)
│   ├── README.md           #   data lineage + schema/scale notes
│   └── <data files...>     #   csv / json / sqlite / long .txt / docs/
├── env.md                  # ENV: runtime assumptions (agent-visible)
└── truth/                  # EVAL: isolated answer key (NEVER staged)
    ├── expected.json       #   gold metadata + required evidence + output paths
    ├── validate.py         #   external validator (exit 0/1/2)
    ├── solution.py         #   reference solution that reproduces the gold
    ├── RUBRIC.md           #   per-step rubric for trace audit
    └── expected_variants/  #   optional: per-part / per-variant gold files
```

Mapping to the three pieces:

- **payload** = `task.md` + `data/`
- **env** = `env.md` (a single declaration when the runtime is trivial; promote
  to an `env/` directory only when real provisioning is needed; see Section 4)
- **eval** = `truth/` (kept under this name for compatibility with `validate.py`
  and the staging loop in `RUN_PROTOCOL.md`)

Existing cases authored before this spec may omit `env.md`; that is fine. New
cases should include it even when it only states "no special environment".

---

## 2. PAYLOAD: `task.md` + `data/`

### 2.1 `task.md`

Agent-facing. Preserve the original benchmark wording when the case is adapted
from a real benchmark. It must NOT mention `truth/`, the validator, the expected
answer, or any prior run. Recommended sections:

1. **Title + one-paragraph framing**: what the case is and that it is
   event/method-oriented, not a precomputed answer table.
2. **Data**: point to `data/README.md` and the key files to inspect.
3. **Questions / Parts**: the concrete deliverable questions. Number them if
   there is more than one part.
4. **Definitions**: any load-bearing rule the answer depends on, such as event
   definition, metric formula, or priority order. State it precisely; this is
   where difficulty lives.
5. **Working rules**: e.g. "Work only from `task.md` and `data/`. You may write
   helper scripts in the workspace." Keep harness and hidden-eval reminders out
   of `task.md`; the run protocol already controls what is staged.
6. **Output contract**: the exact files the agent must write. See Section 5.3.

### 2.2 `data/`

- Real input files: `.csv`, `.json`, `.sqlite`, long `.txt` documents, a small
  `docs/` folder of reference material, etc.
- `data/README.md` records **source lineage** (benchmark name, official repo,
  original instance/database id when appropriate), **scale** (rows/tables/size),
  and any **caution** about subtle structure (delimiters, deprecated distractor
  files, unit conventions).
- Everything under `data/` is agent-visible. Never place gold answers, decoys'
  intended values, or validator hints here.

---

## 3. Contamination Caution

Naming exact upstream instance ids (e.g. `local344`) inside agent-visible files
can trigger training-contamination shortcuts. Keep provenance/instance ids in
`truth/` (e.g. `expected.json` and `RUBRIC.md`) unless the id is itself
load-bearing for the public task. In `data/README.md`, keep only benchmark name
and generic lineage when possible.

---

## 4. ENV: `env.md`

Most cases in this lab are static-file data-analysis / RAG tasks: the agent
needs only a shell plus an interpreter, and every "database" is a file queried
in-process. For these, `env.md` is a short declaration, e.g.:

```text
# Environment

Runtime assumptions for this case:
- bash, python3 (>= 3.10)
- sqlite3 (Python stdlib) for the in-process .sqlite file
- pandas (optional)
- Offline. No network, no services, no database server, no containers.
```

Promote `env.md` to a full `env/` directory **only** when a case needs real
provisioning:

- a live database server (real Postgres/MySQL, not a file-backed sqlite);
- a running web service / API / MCP server whose state changes;
- a browser / GUI task;
- any task graded on side effects to a live system.

In that case:

```text
env/
├── setup.sh          # bring the environment up (idempotent)
├── requirements.txt  # or equivalent dependency manifest
└── teardown.sh       # tear it down after the run
```

`RUN_PROTOCOL.md` must call `env/setup.sh` before the run and `env/teardown.sh`
after. Keep `env/` agent-runnable but free of gold answers.

---

## 5. EVAL: `truth/` (isolated)

`truth/` is the answer key and grader. It is **never** copied into a workspace.

### 5.1 Files

- `expected.json`: gold metadata, source lineage, required output file paths,
  key intermediate values, decoy notes, and any gate flags.
- `validate.py`: the external validator. See Section 5.2.
- `solution.py`: a reference solution that reproduces the gold from the public
  payload. Used to prove the case is solvable and the gold is correct.
- `RUBRIC.md`: a per-step table mapping each reasoning step to a scoring
  dimension and naming the silent failure for that step (for trace audit).
- `expected_variants/`: optional; per-part or per-variant gold files when one
  case bundles several sub-questions.

### 5.2 Validator Contract (`validate.py`)

- Resolves truth from `BENCH_TRUTH_DIR` if set, else from its own directory.
- Runs with **cwd = the workspace** (so it reads the agent's outputs by relative
  path) and reads gold from the truth dir.
- Exit codes: `0` pass; `1` answer/evidence/delivery mismatch; `2` missing or
  unreadable required output.
- Scores up to four dimensions. Use what applies; not every case hard-gates all:
  - **D1 final answer**: the numeric/string/list answer matches gold. Use and
    declare a relative tolerance for floats.
  - **D2 evidence binding**: `evidence.json`, when required by `task.md`, binds
    the answer to the actual tables / sections / rules used.
  - **D3 key intermediate**: a load-bearing intermediate quantity is correct,
    i.e. the step that separates the gold from the decoys.
  - **D4 delivery**: every required output file exists and is non-trivial.

### 5.3 Output Contract

Respect the original benchmark's public contract.

- If the original benchmark only asks for `answers.json` or specific CSV files,
  keep that public requirement. Do **not** turn the public task into an
  `answers.json` + `evidence.json` + `report.md` task just to make auditing
  easier. Put trace-audit expectations in `truth/RUBRIC.md`.
- If this lab designs a formal hard case where evidence binding or delivery is
  itself part of the task, `task.md` may explicitly require:
  - `answers/...` or `answers.json`: final answers in the exact shape specified;
  - `evidence.json`: the source trail binding the answer to payload artifacts;
  - `report.md`: a short audit note with method, edge cases, and outputs.

`task.md`'s output contract and `validate.py` must agree on paths exactly.

---

## 6. Difficulty & Decoy Discipline (Hard Tier)

A hard case should break the "everyone passes" ceiling by design:

1. **No step list.** Give the data dictionary / rules, not a numbered recipe, so
   the case tests planning and method emergence, not just execution.
2. **A load-bearing chain.** The gold must require a specific intermediate (the
   D3 step). If a strong model can reach the answer by a shortcut, retighten the
   metric until the intended chain is mandatory.
3. **Stacked silent decoys.** Each plausible misreading should land on a
   different, specific wrong number, and the decoys should be separated from the
   gold. Document each decoy and the misreading that produces it in
   `expected.json` notes or `RUBRIC.md`.
4. **Buried definitions.** Put the load-bearing rule in a doc the agent must
   choose to read (`manual.md`, `methodology_review.md`, a policy section),
   optionally with a routing decoy in a sibling doc.

Before committing, verify three things:

- the reference `solution.py` produces a **PASS** against the gold;
- each decoy value produces a **FAIL**;
- a freshly staged workspace is **leak-free**: only `task.md` + `data/` +
  `env.md`; no `truth/`.

---

## 7. Naming & Registration

- **Case id**: `<benchmark>_<topic>[_<qualifier>]_<tier>`, lowercase snake_case.
  Examples: `longda_nscg_telework_hard`,
  `spider2lite_f1_overtake_audit_hard`,
  `multihiertt_global_products_atoi_share_hard`.
- **README.md**: add a one-line entry under the case roster.
- **RUN_PROTOCOL.md**: add the case id to the hard-tier staging loop so it gets
  a leak-free copy of `task.md + data + env.md`; confirm `truth/` is not copied.

---

## 8. Authoring Checklist

```text
[ ] case_id follows <benchmark>_<topic>_<tier>
[ ] task.md: framing, data pointer, questions, load-bearing definitions,
    working rules, output contract, and NO reference to truth/validator
[ ] data/README.md: lineage + scale + caution; no gold/decoy values
[ ] no upstream instance ids leaked into agent-visible files unless required
[ ] env.md present, or env/ with setup/teardown if real provisioning is needed
[ ] truth/expected.json: output paths, key intermediates, decoys, gate flags
[ ] truth/validate.py: BENCH_TRUTH_DIR, cwd=workspace, exit 0/1/2, D1..D4
[ ] truth/solution.py reproduces gold from the public payload
[ ] truth/RUBRIC.md: per-step rows with silent failures named
[ ] output contract in task.md == paths checked by validate.py
[ ] hard tier: no step list, load-bearing chain, separated decoys
[ ] VERIFY: solution.py PASS; decoys FAIL; staged workspace leak-free
[ ] README.md roster updated
[ ] RUN_PROTOCOL.md staging loop includes the case
```

---

## 9. Worked Example: `spider2lite_f1_overtake_audit_hard`

| Piece | Files | Role |
| --- | --- | --- |
| **payload** | `task.md` | 3-part audit (all pit-data races / first-5-laps / track-only direction), the unified overtake-event definition, the R>P>S>T priority, and the output contract |
| | `data/README.md` | Spider2-Lite lineage + 29-table / 228-col / ~1.94M-row scale + event-oriented caution |
| | `data/f1.sqlite` | the real F1 SQLite database, queried in-process |
| | `data/docs/f1_overtake.md` | the R/P/S/T overtake taxonomy the agent must apply |
| **env** | `env.md` | bash + python3 + sqlite3 stdlib + pandas; offline; no services |
| **eval** | `truth/expected.json` | lineage, output CSV paths, required evidence tables, gate flags |
| | `truth/expected_variants/{local344,local336,local356}` | per-part gold |
| | `truth/validate.py` | D1 answer / D2 evidence / D4 delivery, exit 0/1/2 |
| | `truth/solution.py` | reference solution |
| | `truth/RUBRIC.md` | 9-step rubric, each step's silent failure named |
