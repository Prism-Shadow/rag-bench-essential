# FDABench Hard v2 - App Review Breadth Audit

This fixture is a compact FDABench-style analytical task over heterogeneous
sources. The answer requires joining a structured app-review corpus with the
method notes in `data/docs/`; neither side is sufficient alone.

## Data

Read `data/README.md` first, then inspect the CSV files and the documents under
`data/docs/`.

- `playstore.csv` contains app catalogue metadata.
- `user_reviews.csv` contains review-level sentiment fields.
- `docs/` contains one market/context packet and one analytical-methods packet.

## Business question

The catalogue team needs the rounded review-subjectivity excess score for apps
whose store genre metadata indicates that the app is packaged across more than
one content genre.

Use the scoring convention that applies to this audit packet. Report one scalar
rounded to 2 decimals.

## Working rules

- Work only from `task.md` and `data/`.
- Do not rely on memory or outside facts about this dataset.
- Decide from the sources which document supplies the scoring method, which
  document supplies market context, which rows belong to the requested app
  segment, and which review rows have usable scores.
- Be careful with catalogue duplication: app listings and app reviews are not
  the same unit of analysis.
- Write any helper script inside the current workspace.

## Output contract

Produce `answers.json`:

```json
{ "answer": ["0.00"] }
```

After writing the file, report the final value.
